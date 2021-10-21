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
    text = ['hello world', 'goodbye', 'third line', 'yet another']
    out = backend.phonemize(text, default_separator, True)
    assert out == ['həloʊ wɜːld', 'ɡʊdbaɪ', 'θɜːd laɪn', 'jɛt ɐnʌðɚ']


def test_stress():
    backend = EspeakBackend('en-us', with_stress=False)
    assert backend.phonemize(
        ['hello world'], default_separator, True) == ['həloʊ wɜːld']

    backend = EspeakBackend('en-us', with_stress=True)
    assert backend.phonemize(
        ['hello world'], default_separator, True) == ['həlˈoʊ wˈɜːld']


def test_french():
    backend = EspeakBackend('fr-fr')
    text = ['bonjour le monde']
    sep = Separator(word=';eword ', syllable=None, phone=' ')
    expected = ['b ɔ̃ ʒ u ʁ ;eword l ə ;eword m ɔ̃ d ;eword ']
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
    text = ['السلام عليكم']
    sep = Separator()

    # Arabic seems to have changed starting at espeak-ng-1.49.3
    if EspeakBackend.version() >= (1, 49, 3):
        expected = ['ʔassalaːm ʕliːkm ']
    else:
        expected = ['ʔassalaam ʕaliijkum ']
    out = backend.phonemize(text, sep, False)
    assert out == expected


# see https://github.com/bootphon/phonemizer/issues/31
def test_phone_separator_simple():
    text = ['The lion and the tiger ran']
    sep = Separator(phone='_')
    backend = EspeakBackend('en-us')

    output = backend.phonemize(text, separator=sep, strip=True)
    expected = ['ð_ə l_aɪə_n æ_n_d ð_ə t_aɪ_ɡ_ɚ ɹ_æ_n']
    assert expected == output

    output = backend.phonemize(text, separator=sep, strip=False)
    expected = ['ð_ə_ l_aɪə_n_ æ_n_d_ ð_ə_ t_aɪ_ɡ_ɚ_ ɹ_æ_n_ ']
    assert expected == output


@pytest.mark.parametrize(
    'text, expected',
    (('the hello but the', 'ð_ə h_ə_l_oʊ b_ʌ_t ð_ə'),
     # ('Here there and everywhere', 'h_ɪɹ ð_ɛɹ æ_n_d ɛ_v_ɹ_ɪ_w_ɛɹ'),
     # ('He was hungry and tired.', 'h_iː w_ʌ_z h_ʌ_ŋ_ɡ_ɹ_i æ_n_d t_aɪɚ_d'),
     ('He was hungry but tired.', 'h_iː w_ʌ_z h_ʌ_ŋ_ɡ_ɹ_i b_ʌ_t t_aɪɚ_d')))
def test_phone_separator(text, expected):
    sep = Separator(phone='_')
    backend = EspeakBackend('en-us')
    output = backend.phonemize([text], separator=sep, strip=True)[0]
    assert output == expected


@pytest.mark.skipif(
    'PHONEMIZER_ESPEAK_LIBRARY' in os.environ,
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
    'PHONEMIZER_ESPEAK_LIBRARY' in os.environ,
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
    'PHONEMIZER_ESPEAK_LIBRARY' in os.environ,
    reason='cannot modify environment')
def test_path_venv():
    try:
        os.environ['PHONEMIZER_ESPEAK_LIBRARY'] = (
            shutil.which('python'))
        with pytest.raises(RuntimeError):
            EspeakBackend('en-us').phonemize(['hello'])
        with pytest.raises(RuntimeError):
            EspeakBackend.version()

        os.environ['PHONEMIZER_ESPEAK_LIBRARY'] = __file__
        with pytest.raises(RuntimeError):
            EspeakBackend.version()

    finally:
        try:
            del os.environ['PHONEMIZER_ESPEAK_LIBRARY']
        except KeyError:
            pass


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='tie only compatible with espeak-ng')
@pytest.mark.parametrize(
    'tie, expected', [
        (False, 'dʒ_æ_k_i_ tʃ_æ_n_ '),
        (True, 'd͡ʒæki t͡ʃæn '),
        ('8', 'd8ʒæki t8ʃæn ')])
def test_tie_simple(caplog, tie, expected):
    backend = EspeakBackend('en-us', tie=tie)
    assert backend.phonemize(
        ['Jackie Chan'],
        separator=Separator(word=' ', phone='_'))[0] == expected

    if tie:
        messages = [msg[2] for msg in caplog.record_tuples]
        assert (
            'cannot use ties AND phone separation, ignoring phone separator'
            in messages)


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='tie only compatible with espeak-ng')
def test_tie_utf8():
    # NOTE this is a bug in espeak to append ties on (en) language switch
    # flags. For now phonemizer does not fix it.
    backend = EspeakBackend('fr-fr', tie=True)

    # used to be 'bɔ̃͡ʒuʁ '
    assert backend.phonemize(['bonjour']) == ['bɔ̃ʒuʁ ']

    # used to be 'ty ɛm lə (͡e͡n͡)fʊtbɔ͡ːl(͡f͡r͡)'
    assert backend.phonemize(
        ['tu aimes le football']) == ['ty ɛm lə (͡e͡n)fʊtbɔːl(͡f͡r) ']

    assert backend.phonemize(
        ['bonjour apple']) == ['bɔ̃ʒuʁ (͡e͡n)apə͡l(͡f͡r) ']


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='tie only compatible with espeak-ng')
def test_tie_bad():
    with pytest.raises(RuntimeError):
        EspeakBackend('en-us', tie='abc')
