# Copyright 2015-2020 Mathieu Bernard
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


import distutils.spawn
import os
import re
import pytest

import phonemizer.separator as separator
from phonemizer.backend import EspeakBackend


@pytest.mark.parametrize(
    'version, expected',
    [('eSpeak text-to-speech: 1.48.03 04.Mar.14 Data at:'
      '/usr/lib/x86_64-linux-gnu/espeak-data', '1.48.03'),
     ('speak text-to-speech: 1.48.03 04.Mar.14 Data at: /usr/local/Cellar/'
      'espeak/1.48.04_1/share/espeak-dat', '1.48.03'),
     ('eSpeak NG text-to-speech: 1.49.2  Data at: /espeak-ng-data', '1.49.2'),
     ('eSpeak NG text-to-speech: 1.51-dev  '
      'Data at: /share/espeak-ng-data', '1.51-dev'),
     ('eSpeak NG text-to-speech: 1.51.1.2.3-dev '
      'Data at: /share/espeak-ng-data', '1.51.1.2.3-dev')])
def test_versions(version, expected):
    found = re.match(EspeakBackend.espeak_version_re, version).group(1)
    assert found == expected


def test_english():
    backend = EspeakBackend('en-us')
    text = u'hello world\ngoodbye\nthird line\nyet another'
    out = '\n'.join(backend._phonemize_aux(
        text, separator.default_separator, True))
    assert out == u'həloʊ wɜːld\nɡʊdbaɪ\nθɜːd laɪn\njɛt ɐnʌðɚ'


def test_stress():
    backend = EspeakBackend('en-us', with_stress=False)
    assert u'həloʊ wɜːld' == backend._phonemize_aux(
        u'hello world', separator.default_separator, True)[0]

    backend = EspeakBackend('en-us', with_stress=True)
    assert u'həlˈoʊ wˈɜːld' == backend._phonemize_aux(
        u'hello world', separator.default_separator, True)[0]


def test_french():
    backend = EspeakBackend('fr-fr')
    text = u'bonjour le monde'
    sep = separator.Separator(word=';eword ', syllable=None, phone=' ')
    expected = [u'b ɔ̃ ʒ u ʁ ;eword l ə ;eword m ɔ̃ d ;eword ']
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


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
def test_language_switch():
    text = '\n'.join([
        "j'aime l'anglais",
        "j'aime le football",
        "football",
        "surtout le real madrid",
        "n'utilise pas google"])

    backend = EspeakBackend('fr-fr', language_switch='keep-flags')
    out = backend._phonemize_aux(text, separator.Separator(), True)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə (en)fʊtbɔːl(fr)',
        '(en)fʊtbɔːl(fr)',
        'syʁtu lə (en)ɹiəl(fr) madʁid',
        'nytiliz pa (en)ɡuːɡəl(fr)']

    # default behavior is to keep the flags
    backend = EspeakBackend('fr-fr')
    out = backend._phonemize_aux(text, separator.Separator(), True)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə (en)fʊtbɔːl(fr)',
        '(en)fʊtbɔːl(fr)',
        'syʁtu lə (en)ɹiəl(fr) madʁid',
        'nytiliz pa (en)ɡuːɡəl(fr)']

    backend = EspeakBackend('fr-fr', language_switch='remove-flags')
    out = backend._phonemize_aux(text, separator.Separator(), True)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə fʊtbɔːl',
        'fʊtbɔːl',
        'syʁtu lə ɹiəl madʁid',
        'nytiliz pa ɡuːɡəl']

    backend = EspeakBackend('fr-fr', language_switch='remove-utterance')
    out = backend._phonemize_aux(text, separator.Separator(), True)
    assert out == ['ʒɛm lɑ̃ɡlɛ']

    with pytest.raises(RuntimeError):
        backend = EspeakBackend('fr-fr', language_switch='foo')


@pytest.mark.parametrize(
    'text, strip, sep',
    ((t, s, u) for t in [
        'a comma a point',
        'a comma. a point.',
        'a comma,, a point.',
        'a comma, , a point.',
        'a comma? a point!']
     for s in (True, False)
     for u in (separator.Separator(), separator.Separator(word='_', phone=' '))
     ))
def test_punctuation(text, strip, sep):
    if sep == separator.Separator():
        expected = 'ɐ kɑːmə ɐ pɔɪnt' if strip else 'ɐ kɑːmə ɐ pɔɪnt '
    else:
        expected = (
            'ɐ_k ɑː m ə_ɐ_p ɔɪ n t' if strip else 'ɐ _k ɑː m ə _ɐ _p ɔɪ n t _')

    output = EspeakBackend('en-us').phonemize(text, strip=strip, separator=sep)
    assert expected == output


# see https://github.com/bootphon/phonemizer/issues/31
def test_phone_separator_simple():
    text = 'The lion and the tiger ran'
    sep = separator.Separator(phone='_')
    backend = EspeakBackend('en-us')

    output = backend.phonemize(text, separator=sep, strip=True)
    expected = 'ð_ə l_aɪə_n æ_n_d ð_ə t_aɪ_ɡ_ɚ ɹ_æ_n'
    assert expected == output

    output = backend.phonemize(text, separator=sep, strip=False)
    expected = 'ð_ə_ l_aɪə_n_ æ_n_d_ ð_ə_ t_aɪ_ɡ_ɚ_ ɹ_æ_n_ '
    assert expected == output

@pytest.mark.parametrize(
    'text, expected',
    (('the hello but the', 'ð_ə h_ə_l_oʊ b_ʌ_t ð_ə'),
     ('Here there and everywhere', 'h_ɪɹ ð_ɛɹ æ_n_d ɛ_v_ɹ_ɪ_w_ɛɹ'),
     ('He was hungry and tired.', 'h_iː w_ʌ_z h_ʌ_ŋ_ɡ_ɹ_i æ_n_d t_aɪɚ_d'),
     ('He was hungry but tired.', 'h_iː w_ʌ_z h_ʌ_ŋ_ɡ_ɹ_i b_ʌ_t t_aɪɚ_d')))
def test_phone_separator(text, expected):
    sep = separator.Separator(phone='_')
    backend = EspeakBackend('en-us')
    output = backend.phonemize(text, separator=sep, strip=True)
    assert output == expected


def test_path_good():
    try:
        binary = distutils.spawn.find_executable('espeak')
        EspeakBackend.set_espeak_path(binary)

        test_english()

    # restore the espeak path to default
    finally:
        EspeakBackend.set_espeak_path(None)


def test_path_bad():
    try:
        # corrupt the default espeak path, try to use python executable instead
        binary = distutils.spawn.find_executable('python')
        EspeakBackend.set_espeak_path(binary)

        with pytest.raises(RuntimeError):
            EspeakBackend('en-us').phonemize('hello')
        with pytest.raises(RuntimeError):
            EspeakBackend.version()

        with pytest.raises(ValueError):
            EspeakBackend.set_espeak_path(__file__)

    # restore the espeak path to default
    finally:
        EspeakBackend.set_espeak_path(None)


@pytest.mark.skipif(
    'PHONEMIZER_ESPEAK_PATH' in os.environ,
    reason='cannot modify environment')
def test_path_venv():
    try:
        os.environ['PHONEMIZER_ESPEAK_PATH'] = distutils.spawn.find_executable('python')
        with pytest.raises(RuntimeError):
            EspeakBackend('en-us').phonemize('hello')
        with pytest.raises(RuntimeError):
            EspeakBackend.version()

        os.environ['PHONEMIZER_ESPEAK_PATH'] = __file__
        with pytest.raises(ValueError):
            EspeakBackend.version()

    finally:
        try:
            del os.environ['PHONEMIZER_ESPEAK_PATH']
        except KeyError:
            pass


def test_sampa_fr():
    list_sampa_examples_plosives = [
        'pont', 'bon', 'temps', 'dans', 'quand', 'gant']
    list_sampa_examples_fricatives = [
        'femme', 'vent', 'sans', 'champ', 'gens', 'ion']
    list_sampa_examples_nasals = [
        'mont', 'nom', 'oignon', 'camping']
    list_sampa_examples_liquids_glides = [
        'long', 'rond', 'coin', 'juin', 'pierre']
    list_sampa_examples_vowels = [
        'si', 'ses', 'seize', 'patte', 'pâte',
        'comme', 'gros', 'doux', 'du', 'deux',
        'neuf', 'justement', 'vin', 'vent', 'bon', 'brun']
    list_sampa = {
        'plosives': list_sampa_examples_plosives,
        'fricatives': list_sampa_examples_fricatives,
        'nasals': list_sampa_examples_nasals,
        'liquids_glides': list_sampa_examples_liquids_glides,
        'vowels': list_sampa_examples_vowels}
    list_sampa_answers = {
        'fricatives': ['fam', 'va~', 'sa~', 'Sa~', 'Za~', 'jo~'],
        'liquids_glides': ['lo~', 'ro~', 'kwe~', 'Zye~', 'pjEr'],
        'nasals': ['mo~', 'no~', 'onjo~', 'kampIN'],
        'plosives': ['po~', 'bo~', 'ta~', 'da~', 'ka~', 'ga~'],
        'vowels': ['si',
                   'se',
                   'sEz',
                   'pat',
                   'pa:t',
                   'kOm',
                   'gro',
                   'du',
                   'dy',
                   'dY',
                   'n9f',
                   'Zystma~',
                   've~',
                   'va~',
                   'bo~',
                   'br9~']}

    backend = EspeakBackend(
        'fr-fr', use_sampa=True, language_switch='remove-flags')
    for category in list_sampa.keys():
        for idx, text in enumerate(list_sampa[category]):
            out = backend.phonemize(text, strip=True)
            assert out == list_sampa_answers[category][idx]
