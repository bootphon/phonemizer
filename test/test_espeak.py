# coding: utf-8

# Copyright 2017 Mathieu Bernard
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
"""Test of the phonemizer.espeak module"""


import re
import pytest

import phonemizer.espeak as espeak
import phonemizer.separator as separator


@pytest.mark.parametrize(
    'version',
    ['eSpeak text-to-speech: 1.48.03 04.Mar.14 Data at:'
     '/usr/lib/x86_64-linux-gnu/espeak-data',
     'speak text-to-speech: 1.48.03 04.Mar.14 Data at: /usr/local/Cellar/'
     'espeak/1.48.04_1/share/espeak-dat',
     'eSpeak NG text-to-speech: 1.49.2  Data at: /usr/lib/espeak-ng-data'])
def test_versions(version):
    expected = '1.49.2' if 'NG' in version else '1.48.03'
    assert re.match(espeak._ESPEAK_VERSION_RE, version).group(1) == expected


def test_english():
    text = u'hello world\ngoodbye\nthird line\nyet another'
    out = '\n'.join(espeak.phonemize(text, strip=True))
    assert out == u'həloʊ wɜːld\nɡʊdbaɪ\nθɜːd laɪn\njɛt ɐnʌðɚ'


def test_french():
    text = u'bonjour le monde'
    sep = separator.Separator(word=';eword ', syllable=None, phone=' ')
    expected = [u'b ɔ̃ ʒ u ʁ ;eword l ə- ;eword m ɔ̃ d ;eword ']
    out = espeak.phonemize(text, language='fr-fr', separator=sep, strip=False)
    assert out == expected
