# coding: utf-8

# Copyright 2017-2018 Mathieu Bernard
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
"""Test of the espeak backend"""


import re
import pytest

import phonemizer.separator as separator
from phonemizer.backend import EspeakBackend


@pytest.mark.parametrize(
    'version',
    ['eSpeak text-to-speech: 1.48.03 04.Mar.14 Data at:'
     '/usr/lib/x86_64-linux-gnu/espeak-data',
     'speak text-to-speech: 1.48.03 04.Mar.14 Data at: /usr/local/Cellar/'
     'espeak/1.48.04_1/share/espeak-dat',
     'eSpeak NG text-to-speech: 1.49.2  Data at: /usr/lib/espeak-ng-data'])
def test_versions(version):
    expected = '1.49.2' if 'NG' in version else '1.48.03'
    version_re = EspeakBackend.espeak_version_re
    assert re.match(version_re, version).group(1) == expected


def test_english():
    backend = EspeakBackend('en-us')
    text = u'hello world\ngoodbye\nthird line\nyet another'
    out = '\n'.join(backend._phonemize_aux(
        text, separator.default_separator, True))
    assert out == u'həloʊ wɜːld\nɡʊdbaɪ\nθɜːd laɪn\njɛt ɐnʌðɚ'


def test_french():
    backend = EspeakBackend('fr-fr')
    text = u'bonjour le monde'
    sep = separator.Separator(word=';eword ', syllable=None, phone=' ')
    expected = [u'b ɔ̃ ʒ u ʁ ;eword l ə- ;eword m ɔ̃ d ;eword ']
    out = backend._phonemize_aux(text, sep, False)
    assert out == expected


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='Arabic is only supported by espeak-ng')
def test_arabic():
    backend = EspeakBackend('ar')
    text = u'السلام عليكم'
    sep = separator.Separator()
    # Arabic seems to have changed starting at espeak-ng-1.49.3
    if tuple(EspeakBackend.version().split('.')) >= ('1', '49', '3'):
        expected = [u'ʔassalaːm ʕliːkm ']
    else:
        expected = [u'ʔassalaam ʕaliijkum ']
    out = backend._phonemize_aux(text, sep, False)
    assert out == expected
