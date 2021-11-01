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
"""Test of the espeak-mbrola backend"""

# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import pytest

from phonemizer.backend import EspeakMbrolaBackend
from phonemizer.separator import Separator


@pytest.fixture(scope='session')
def backend():
    return EspeakMbrolaBackend('mb-fr1')


@pytest.mark.skipif(
    not EspeakMbrolaBackend.is_available() or
    not EspeakMbrolaBackend.is_supported_language('mb-fr1'),
    reason='mbrola or mb-fr1 voice not installed')
@pytest.mark.parametrize(
    'text, expected',
    [
        # plosives
        ('pont', 'po~'),
        ('bon', 'bo~'),
        ('temps', 'ta~'),
        ('dans', 'da~'),
        ('quand', 'ka~'),
        ('gant', 'ga~'),
        # fricatives
        ('femme', 'fam'),
        ('vent', 'va~'),
        ('sans', 'sa~'),
        ('champ', 'Sa~'),
        ('gens', 'Za~'),
        ('ion', 'jo~'),
        # nasals
        ('mont', 'mo~'),
        ('nom', 'no~'),
        ('oignon', 'onjo~'),
        ('ping', 'piN'),
        # liquid glides
        ('long', 'lo~'),
        ('rond', 'Ro~'),
        ('coin', 'kwe~'),
        ('juin', 'Zye~'),
        ('pierre', 'pjER'),
        # vowels
        ('si', 'si'),
        ('ses', 'se'),
        ('seize', 'sEz'),
        ('patte', 'pat'),
        ('pâte', 'pat'),
        ('comme', 'kOm'),
        ('gros', 'gRo'),
        ('doux', 'du'),
        ('du', 'dy'),
        ('deux', 'd2'),
        ('neuf', 'n9f'),
        ('justement', 'Zystma~'),
        ('vin', 've~'),
        ('vent', 'va~'),
        ('bon', 'bo~'),
        ('brun', 'bR9~')])
def test_sampa_fr(backend, text, expected):
    assert expected == backend.phonemize(
        [text], strip=True, separator=Separator(phone=''))[0]


@pytest.mark.skipif(
    not EspeakMbrolaBackend.is_available() or
    not EspeakMbrolaBackend.is_supported_language('mb-fr1'),
    reason='mbrola or mb-fr1 voice not installed')
def test_french_sampa(backend):
    text = ['bonjour le monde']
    sep = Separator(word=None, phone=' ')

    expected = ['b o~ Z u R l @ m o~ d ']
    out = backend.phonemize(text, separator=sep, strip=False)
    assert out == expected

    expected = ['b o~ Z u R l @ m o~ d']
    out = backend.phonemize(text, separator=sep, strip=True)
    assert out == expected

    assert backend.phonemize([''], separator=sep, strip=True) == ['']
    assert backend.phonemize(['"'], separator=sep, strip=True) == ['']


@pytest.mark.skipif(
    not EspeakMbrolaBackend.is_available(),
    reason='mbrola not installed')
def test_mbrola_bad_language():
    assert not EspeakMbrolaBackend.is_supported_language('foo-bar')
