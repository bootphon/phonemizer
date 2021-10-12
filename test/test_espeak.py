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
"""Test of the espeak backend"""

# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import os
import shutil
import pytest

from phonemizer.backend import EspeakBackend
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.separator import Separator, default_separator


def test_english():
    backend = EspeakBackend('en-us')
    text = u'hello world\ngoodbye\nthird line\nyet another'
    out = backend.phonemize(text, default_separator, True)
    assert out == u'həloʊ wɜːld\nɡʊdbaɪ\nθɜːd laɪn\njɛt ɐnʌðɚ'


def test_stress():
    backend = EspeakBackend('en-us', with_stress=False)
    assert backend.phonemize(
        'hello world', default_separator, True) == u'həloʊ wɜːld'

    backend = EspeakBackend('en-us', with_stress=True)
    assert backend.phonemize(
        u'hello world', default_separator, True) == u'həlˈoʊ wˈɜːld'


def test_french():
    backend = EspeakBackend('fr-fr')
    text = u'bonjour le monde'
    sep = Separator(word=';eword ', syllable=None, phone=' ')
    expected = u'b ɔ̃ ʒ u ʁ ;eword l ə ;eword m ɔ̃ d ;eword '
    out = backend.phonemize(text, sep, False)
    assert out == expected


@pytest.mark.skipif(
    (
        not EspeakBackend.is_espeak_ng() or
        # Arabic is not supported by the Windows msi installer from espeak-ng
        # github release
        not EspeakBackend.is_supported_language('ar')),
    reason='Arabic is not supported')
def test_arabic():
    backend = EspeakBackend('ar')
    text = u'السلام عليكم'
    sep = Separator()

    # Arabic seems to have changed starting at espeak-ng-1.49.3
    if tuple(EspeakBackend.version().split('.')) >= ('1', '49', '3'):
        expected = u'ʔassalaːm ʕliːkm '
    else:
        expected = u'ʔassalaam ʕaliijkum '
    out = backend.phonemize(text, sep, False)
    assert out == expected


@pytest.fixture
def langswitch_text():
    return [
        "j'aime l'anglais",
        "j'aime le football",
        "football",
        "surtout le real madrid",
        "n'utilise pas google"]


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize('njobs', [1, 3])
def test_language_switch_keep_flags(caplog, langswitch_text, njobs):
    backend = EspeakBackend('fr-fr', language_switch='keep-flags')
    out = backend.phonemize(
        langswitch_text, separator=Separator(), strip=True, njobs=njobs)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə (en)fʊtbɔːl(fr)',
        '(en)fʊtbɔːl(fr)',
        'syʁtu lə (en)ɹiəl(fr) madʁid',
        'nytiliz pa (en)ɡuːɡəl(fr)']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        '4 utterances containing language switches on lines 2, 3, 4, 5'
        in messages)
    assert (
        'language switch flags have been kept (applying "keep-flags" policy)'
        in messages)


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize('njobs', [1, 3])
def test_language_switch_default(caplog, langswitch_text, njobs):
    # default behavior is to keep the flags
    backend = EspeakBackend('fr-fr')
    out = backend.phonemize(
        langswitch_text, separator=Separator(), strip=True, njobs=njobs)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə (en)fʊtbɔːl(fr)',
        '(en)fʊtbɔːl(fr)',
        'syʁtu lə (en)ɹiəl(fr) madʁid',
        'nytiliz pa (en)ɡuːɡəl(fr)']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        '4 utterances containing language switches on lines 2, 3, 4, 5'
        in messages)
    assert (
        'language switch flags have been kept (applying "keep-flags" policy)'
        in messages)


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize('njobs', [1, 3])
def test_language_switch_remove_flags(caplog, langswitch_text, njobs):
    backend = EspeakBackend('fr-fr', language_switch='remove-flags')
    out = backend.phonemize(
        langswitch_text, separator=Separator(), strip=True, njobs=njobs)
    assert out == [
        'ʒɛm lɑ̃ɡlɛ',
        'ʒɛm lə fʊtbɔːl',
        'fʊtbɔːl',
        'syʁtu lə ɹiəl madʁid',
        'nytiliz pa ɡuːɡəl']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        '4 utterances containing language switches on lines 2, 3, 4, 5'
        in messages)
    assert (
        'language switch flags have been removed '
        '(applying "remove-flags" policy)'
        in messages)


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
@pytest.mark.parametrize('njobs', [1, 3])
def test_language_switch_remove_utterance(caplog, langswitch_text, njobs):
    backend = EspeakBackend('fr-fr', language_switch='remove-utterance')
    out = backend.phonemize(
        langswitch_text, separator=Separator(), strip=True, njobs=njobs)
    assert out == ['ʒɛm lɑ̃ɡlɛ']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        'removed 4 utterances containing language switches '
        '(applying "remove-utterance" policy)'
        in messages)

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
     for u in (Separator(), Separator(word='_', phone=' '))
     ))
def test_punctuation(text, strip, sep):
    if sep == Separator():
        expected = 'ɐ kɑːmə ɐ pɔɪnt' if strip else 'ɐ kɑːmə ɐ pɔɪnt '
    else:
        expected = (
            'ɐ_k ɑː m ə_ɐ_p ɔɪ n t' if strip else 'ɐ _k ɑː m ə _ɐ _p ɔɪ n t _')

    output = EspeakBackend('en-us').phonemize(text, strip=strip, separator=sep)
    assert expected == output


# see https://github.com/bootphon/phonemizer/issues/31
def test_phone_separator_simple():
    text = 'The lion and the tiger ran'
    sep = Separator(phone='_')
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
    sep = Separator(phone='_')
    backend = EspeakBackend('en-us')
    output = backend.phonemize(text, separator=sep, strip=True)
    assert output == expected


@pytest.mark.skipif(
    'PHONEMIZER_ESPEAK_PATH' in os.environ,
    reason='cannot modify environment')
def test_path_good():
    espeak = EspeakBackend.library()
    try:
        EspeakBackend.set_library(None)
        assert espeak == EspeakBackend.library()

        library = EspeakWrapper().library_path
        EspeakBackend.set_library(library)

        test_english()

    # restore the espeak path to default
    finally:
        EspeakBackend.set_library(None)


@pytest.mark.skipif(
    'PHONEMIZER_ESPEAK_PATH' in os.environ,
    reason='cannot modify environment')
def test_path_bad():
    try:
        # corrupt the default espeak path, try to use python executable instead
        binary = shutil.which('python')
        EspeakBackend.set_library(binary)

        with pytest.raises(RuntimeError):
            EspeakBackend('en-us')
        with pytest.raises(RuntimeError):
            EspeakBackend.version()

        EspeakBackend.set_library(__file__)
        with pytest.raises(RuntimeError):
            EspeakBackend('en-us')

    # restore the espeak path to default
    finally:
        EspeakBackend.set_library(None)


@pytest.mark.skipif(
    'PHONEMIZER_ESPEAK_PATH' in os.environ,
    reason='cannot modify environment')
def test_path_venv():
    try:
        os.environ['PHONEMIZER_ESPEAK_PATH'] = (
            shutil.which('python'))
        with pytest.raises(RuntimeError):
            EspeakBackend('en-us').phonemize('hello')
        with pytest.raises(RuntimeError):
            EspeakBackend.version()

        os.environ['PHONEMIZER_ESPEAK_PATH'] = __file__
        with pytest.raises(RuntimeError):
            EspeakBackend.version()

    finally:
        try:
            del os.environ['PHONEMIZER_ESPEAK_PATH']
        except KeyError:
            pass


@pytest.mark.parametrize(
    'tie, expected', [
        (False, 'dʒæki tʃæn '),
        (True, 'd͡ʒæki t͡ʃæn '),
        ('8', 'd8ʒæki t8ʃæn ')])
def test_tie(tie, expected):
    assert EspeakBackend('en-us', tie=tie).phonemize('Jackie Chan') == expected


def test_tie_bad():
    with pytest.raises(RuntimeError):
        EspeakBackend('en-us', tie='abc')
