# Copyright 2015-2021 Mathieu Bernard
#
# This file is part of phonemizer: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Phonemizer is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with phonemizer. If not, see <http://www.gnu.org/licenses/>.
"""Test of the EspeakWrapper class"""

# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import os
import pathlib
import pickle
import sys

import pytest

from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.backend import EspeakMbrolaBackend


@pytest.fixture
def wrapper():
    return EspeakWrapper()


def test_basic(wrapper):
    assert wrapper.version >= (1, 48)
    assert 'espeak' in str(wrapper.library_path)
    assert os.path.isabs(wrapper.library_path)
    assert os.path.isabs(wrapper.data_path)  # not None, no raise


def test_available_voices(wrapper):
    espeak = set(wrapper.available_voices())
    assert espeak

    mbrola = set(wrapper.available_voices('mbrola'))
    # can be empty if no mbrola voice installed (occurs only on Windows, at
    # least within the github CI pipeline)
    if mbrola:
        assert not espeak.intersection(mbrola)


def test_set_get_voice(wrapper):
    assert wrapper.voice is None
    with pytest.raises(RuntimeError) as err:
        wrapper.set_voice('')
    assert 'invalid voice code ""' in str(err)

    wrapper.set_voice('fr-fr')
    assert wrapper.voice.language == 'fr-fr'
    assert wrapper.voice.name in (
        'French (France)',  # >1.48.3
        'french')           # older espeak

    wrapper.set_voice('en-us')
    assert wrapper.voice.language == 'en-us'
    assert wrapper.voice.name in (
        'English (America)',  # >1.48.3
        'english-us')         # older espeak

    # no mbrola voices available on Windows by default (at least on the github
    # CI pipeline)
    if sys.platform != 'win32':
        wrapper.set_voice('mb-af1')
        assert wrapper.voice.language == 'af'
        assert wrapper.voice.name == 'afrikaans-mbrola-1'

    with pytest.raises(RuntimeError) as err:
        wrapper.set_voice('some non existant voice code')
    assert 'invalid voice code' in str(err)


def _test_pickle(voice):
    # the wrapper is pickled when using espeak backend on multiple jobs
    wrapper = EspeakWrapper()
    wrapper.set_voice(voice)

    dump = pickle.dumps(wrapper)
    wrapper2 = pickle.loads(dump)

    assert wrapper.version == wrapper2.version
    assert wrapper.library_path == wrapper2.library_path
    assert wrapper.data_path == wrapper2.data_path
    assert wrapper.voice == wrapper2.voice


def test_pickle_en_us():
    _test_pickle('en-us')


@pytest.mark.skipif(
    not EspeakMbrolaBackend.is_available() or
    not EspeakMbrolaBackend.is_supported_language('mb-fr1'),
    reason='mbrola or mb-fr1 voice not installed')
def test_pickle_mb_fr1():
    _test_pickle('mb-fr1')


def test_twice():
    wrapper1 = EspeakWrapper()
    wrapper2 = EspeakWrapper()

    assert wrapper1.data_path == wrapper2.data_path
    assert wrapper1.version == wrapper2.version
    assert wrapper1.library_path == wrapper2.library_path

    wrapper1.set_voice('fr-fr')
    assert wrapper1.voice.language == 'fr-fr'
    wrapper2.set_voice('en-us')
    assert wrapper2.voice.language == 'en-us'
    assert wrapper1.voice.language == 'fr-fr'

    # pylint: disable=protected-access
    assert wrapper1._espeak._tempdir != wrapper2._espeak._tempdir


@pytest.mark.skipif(sys.platform == 'win32', reason='not supported on Windows')
def test_deletion():
    # pylint: disable=protected-access
    wrapper = EspeakWrapper()
    path = pathlib.Path(wrapper._espeak._tempdir)
    del wrapper
    assert not path.exists()
