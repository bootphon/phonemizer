# Copyright 2015-2021 Thomas Schatz, Xuan Nga Cao, Mathieu Bernard
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
"""Test of the festival backend"""

# pylint: disable=missing-docstring


import os
import pathlib
import shutil

import pytest

from phonemizer.separator import Separator
from phonemizer.backend import FestivalBackend


def _test(text, separator=Separator(
        word=' ', syllable='|', phone='-')):
    backend = FestivalBackend('en-us')
    # pylint: disable=protected-access
    return backend._phonemize_aux(text, 0, separator, True)


@pytest.mark.skipif(
    FestivalBackend.version() <= (2, 1),
    reason='festival-2.1 gives different results than further versions '
    'for syllable boundaries')
def test_hello():
    assert _test(['hello world']) == ['hh-ax|l-ow w-er-l-d']
    assert _test(['hello', 'world']) == ['hh-ax|l-ow', 'w-er-l-d']


@pytest.mark.parametrize('text', ['', ' ', '  ', '(', '()', '"', "'"])
def test_bad_input(text):
    assert _test(text) == []


def test_quote():
    assert _test(["it's"]) == ['ih-t-s']
    assert _test(["its"]) == ['ih-t-s']
    assert _test(["it s"]) == ['ih-t eh-s']
    assert _test(['it "s']) == ['ih-t eh-s']


def test_im():
    sep = Separator(word=' ', syllable='', phone='')
    assert _test(["I'm looking for an image"], sep) \
        == ['aym luhkaxng faor axn ihmaxjh']
    assert _test(["Im looking for an image"], sep) \
        == ['ihm luhkaxng faor axn ihmaxjh']


@pytest.mark.skipif(
    not shutil.which('festival'), reason='festival not in PATH')
def test_path_good():
    try:
        binary = shutil.which('festival')
        FestivalBackend.set_executable(binary)
        assert FestivalBackend('en-us').executable() == pathlib.Path(binary)
    # restore the festival path to default
    finally:
        FestivalBackend.set_executable(None)


@pytest.mark.skipif(
    'PHONEMIZER_FESTIVAL_EXECUTABLE' in os.environ,
    reason='environment variable precedence')
def test_path_bad():
    try:
        # corrupt the default espeak path, try to use python executable instead
        binary = shutil.which('python')
        FestivalBackend.set_executable(binary)

        with pytest.raises(RuntimeError):
            FestivalBackend('en-us').phonemize(['hello'])
        with pytest.raises(RuntimeError):
            FestivalBackend.version()

        with pytest.raises(RuntimeError):
            FestivalBackend.set_executable(__file__)

    # restore the festival path to default
    finally:
        FestivalBackend.set_executable(None)


@pytest.mark.skipif(
    'PHONEMIZER_FESTIVAL_EXECUTABLE' in os.environ,
    reason='cannot modify environment')
def test_path_venv():
    try:
        os.environ['PHONEMIZER_FESTIVAL_EXECUTABLE'] = shutil.which('python')
        with pytest.raises(RuntimeError):
            FestivalBackend('en-us').phonemize(['hello'])
        with pytest.raises(RuntimeError):
            FestivalBackend.version()

        os.environ['PHONEMIZER_FESTIVAL_EXECUTABLE'] = __file__
        with pytest.raises(RuntimeError):
            FestivalBackend.version()

    finally:
        try:
            del os.environ['PHONEMIZER_FESTIVAL_EXECUTABLE']
        except KeyError:
            pass
