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
"""Test of the segments backend"""

# pylint: disable=missing-docstring

import os
import pkg_resources
import pytest

from phonemizer.separator import Separator, default_separator
from phonemizer.backend import SegmentsBackend


def test_multiline():
    backend = SegmentsBackend('cree')
    assert backend.language == 'cree'

    assert backend.phonemize(['a']) == [u'ʌ ']
    assert backend.phonemize(['aa']) == [u'ʌʌ ']
    assert backend.phonemize(['a\n']) == [u'ʌ ']
    assert backend.phonemize(['a\na']) == [u'ʌ ʌ ']
    assert backend.phonemize(['a\na\n']) == [u'ʌ ʌ ']
    assert backend.phonemize(['a', 'a']) == [u'ʌ ', 'ʌ ']
    assert backend.phonemize(['a\n', 'a\n']) == [u'ʌ ', 'ʌ ']


def test_bad_morpheme():
    backend = SegmentsBackend('cree')
    with pytest.raises(ValueError):
        backend.phonemize('A')


def test_separator():
    backend = SegmentsBackend('cree')
    text = ['achi acho']

    sep = default_separator
    assert backend.phonemize(text, separator=sep) == [u'ʌtʃɪ ʌtʃʊ ']
    assert backend.phonemize(text, separator=sep, strip=True) == [u'ʌtʃɪ ʌtʃʊ']


def test_separator_2():
    backend = SegmentsBackend('cree')
    text = ['achi acho']

    sep = Separator(word='_', phone=' ')
    assert backend.phonemize(text, separator=sep) == [u'ʌ tʃ ɪ _ʌ tʃ ʊ _']
    assert backend.phonemize(text, separator=sep, strip=True) \
        == [u'ʌ tʃ ɪ_ʌ tʃ ʊ']


def test_separator_3():
    backend = SegmentsBackend('cree')
    text = ['achi acho']

    sep = Separator(word=' ', syllable=None, phone='_')
    assert backend.phonemize(text, separator=sep) == [u'ʌ_tʃ_ɪ_ ʌ_tʃ_ʊ_ ']
    assert backend.phonemize(text, separator=sep, strip=True) \
        == [u'ʌ_tʃ_ɪ ʌ_tʃ_ʊ']


def test_separator_4():
    backend = SegmentsBackend('cree')
    text = ['achi acho']

    # TODO bug when sep.phone == ' ' with no sep.word
    sep = Separator(phone=' ', word='')
    assert backend.phonemize(text, separator=sep) == [u'ʌ tʃ ɪ ʌ tʃ ʊ ']
    assert backend.phonemize(text, separator=sep, strip=True) \
        == [u'ʌ tʃ ɪʌ tʃ ʊ']


def test_separator_5():
    backend = SegmentsBackend('cree')
    text = ['achi acho']

    sep = Separator(phone=' ', word='_')
    assert backend.phonemize(text, separator=sep) == [u'ʌ tʃ ɪ _ʌ tʃ ʊ _']
    assert backend.phonemize(text, separator=sep, strip=True) \
        == [u'ʌ tʃ ɪ_ʌ tʃ ʊ']


def test_language(tmpdir):
    # check languages by name
    assert SegmentsBackend.is_supported_language('cree')
    assert not SegmentsBackend.is_supported_language('unexisting')

    # check languages by g2p file
    directory = pkg_resources.resource_filename(
        pkg_resources.Requirement.parse('phonemizer'),
        'phonemizer/share/segments')
    assert SegmentsBackend.is_supported_language(
        os.path.join(directory, 'cree.g2p'))
    assert not SegmentsBackend.is_supported_language(
        os.path.join(directory, 'cree'))
    assert not SegmentsBackend.is_supported_language(
        os.path.join(directory, 'unexisting.g2p'))

    # bad syntax in g2p file
    g2p = tmpdir.join('foo.g2p')
    g2p.write('\n'.join(['a a', 'b b b', 'c']))
    assert not SegmentsBackend.is_supported_language(g2p)
