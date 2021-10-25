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
"""Test of the phonemizer.phonemize function"""

# pylint: disable=missing-docstring

import os
import pytest

from phonemizer.phonemize import phonemize
from phonemizer.separator import Separator
from phonemizer.backend import EspeakBackend, EspeakMbrolaBackend


def test_bad_backend():
    with pytest.raises(RuntimeError):
        phonemize('', backend='fetiv')

    with pytest.raises(RuntimeError):
        phonemize('', backend='foo')

    with pytest.raises(RuntimeError):
        phonemize('', tie=True, backend='festival')
    with pytest.raises(RuntimeError):
        phonemize('', tie=True, backend='mbrola')
    with pytest.raises(RuntimeError):
        phonemize('', tie=True, backend='segments')
    with pytest.raises(RuntimeError):
        phonemize(
            '', tie=True, backend='espeak',
            separator=Separator(' ', None, '-'))


def test_bad_language():
    with pytest.raises(RuntimeError):
        phonemize('', language='fr-fr', backend='festival')

    with pytest.raises(RuntimeError):
        phonemize('', language='ffr', backend='espeak')

    with pytest.raises(RuntimeError):
        phonemize('', language='/path/to/nonexisting/file', backend='segments')

    with pytest.raises(RuntimeError):
        phonemize('', language='creep', backend='segments')


def test_text_type():
    text1 = ['one two', 'three', 'four five']
    text2 = os.linesep.join(text1)

    phn1 = phonemize(text1, language='en-us', backend='espeak', strip=True)
    phn2 = phonemize(text2, language='en-us', backend='espeak', strip=True)
    out3 = phonemize(text2, language='en-us', backend='espeak', strip=True,
                     prepend_text=True)
    text3 = [o[0] for o in out3]
    phn3 = [o[1] for o in out3]

    assert isinstance(phn1, list)
    assert isinstance(phn2, str)
    assert os.linesep.join(phn1) == phn2
    assert os.linesep.join(phn3) == phn2
    assert text3 == text1


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
def test_lang_switch():
    text = ['bonjour apple', 'bonjour toi']
    out = phonemize(
        text,
        language='fr-fr',
        backend='espeak',
        prepend_text=True,
        language_switch='remove-utterance')
    assert out == [('bonjour apple', ''), ('bonjour toi', 'bɔ̃ʒuʁ twa ')]


@pytest.mark.parametrize('njobs', [2, 4])
def test_espeak(njobs):
    text = ['one two', 'three', 'four five']

    out = phonemize(
        text, language='en-us', backend='espeak',
        strip=True, njobs=njobs)
    assert out == ['wʌn tuː', 'θɹiː', 'foːɹ faɪv']

    out = phonemize(
        ' '.join(text), language='en-us', backend='espeak',
        strip=False, njobs=njobs)
    assert out == ' '.join(['wʌn tuː', 'θɹiː', 'foːɹ faɪv '])

    out = phonemize(
        os.linesep.join(text), language='en-us', backend='espeak',
        strip=False, njobs=njobs)
    assert out == os.linesep.join(['wʌn tuː ', 'θɹiː ', 'foːɹ faɪv '])


@pytest.mark.skipif(
    not EspeakMbrolaBackend.is_available() or
    not EspeakMbrolaBackend.is_supported_language('mb-fr1'),
    reason='mbrola or mb-fr1 voice not installed')
@pytest.mark.parametrize('njobs', [2, 4])
def test_espeak_mbrola(caplog, njobs):
    text = ['un deux', 'trois', 'quatre cinq']

    out = phonemize(
        text,
        language='mb-fr1',
        backend='espeak-mbrola',
        njobs=njobs,
        preserve_punctuation=True)
    assert out == ['9~d2', 'tRwa', 'katRse~k']

    messages = [msg[2] for msg in caplog.record_tuples]
    assert 'espeak-mbrola backend cannot preserve punctuation' in messages
    assert 'espeak-mbrola backend cannot preserve word separation' in messages


@pytest.mark.parametrize('njobs', [2, 4])
def test_festival(njobs):
    text = ['one two', 'three', 'four five']

    out = phonemize(
        text, language='en-us', backend='festival',
        strip=False, njobs=njobs)
    assert out == ['wahn tuw ', 'thriy ', 'faor fayv ']

    out = phonemize(
        ' '.join(text), language='en-us', backend='festival',
        strip=True, njobs=njobs)
    assert out == ' '.join(['wahn tuw', 'thriy', 'faor fayv'])

    out = phonemize(
        os.linesep.join(text), language='en-us', backend='festival',
        strip=True, njobs=njobs)
    assert out == os.linesep.join(['wahn tuw', 'thriy', 'faor fayv'])


def test_festival_bad():
    # cannot use options valid for espeak only
    text = ['one two', 'three', 'four five']

    with pytest.raises(RuntimeError):
        phonemize(
            text, language='en-us', backend='festival', with_stress=True)

    with pytest.raises(RuntimeError):
        phonemize(
            text, language='en-us', backend='festival',
            language_switch='remove-flags')


@pytest.mark.parametrize('njobs', [2, 4])
def test_segments(njobs):
    # one two three four five in Maya Yucatec
    text = ['untuʼuleʼ kaʼapʼeʼel', 'oʼoxpʼeʼel', 'kantuʼuloʼon chincho']

    out = phonemize(
        text, language='yucatec', backend='segments',
        strip=False, njobs=njobs)
    assert out == [
        'untṵːlḛ ka̰ːpʼḛːl ', 'o̰ːʃpʼḛːl ', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo ']
    out = phonemize(
        ' '.join(text), language='yucatec', backend='segments',
        strip=False, njobs=njobs)
    assert out == ' '.join(
        ['untṵːlḛ ka̰ːpʼḛːl', 'o̰ːʃpʼḛːl', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo '])

    out = phonemize(
        os.linesep.join(text), language='yucatec', backend='segments',
        strip=True, njobs=njobs)
    assert out == os.linesep.join(
        ['untṵːlḛ ka̰ːpʼḛːl', 'o̰ːʃpʼḛːl', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo'])
