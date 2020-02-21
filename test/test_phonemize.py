# Copyright 2015-2020 Thomas Schatz, Xuan Nga Cao, Mathieu Bernard
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

import pytest

from phonemizer.phonemize import phonemize
from phonemizer.backend import EspeakMbrolaBackend


def test_bad_backend():
    with pytest.raises(RuntimeError):
        phonemize('', backend='fetiv')

    with pytest.raises(RuntimeError):
        phonemize('', backend='foo')


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
    t1 = ['one two', 'three', 'four five']
    t2 = '\n'.join(t1)

    p1 = phonemize(t1, language='en-us', backend='espeak', strip=True)
    p2 = phonemize(t2, language='en-us', backend='espeak', strip=True)

    assert isinstance(p1, list)
    assert isinstance(p2, str)
    assert '\n'.join(p1) == p2


@pytest.mark.parametrize('njobs', [2, 4])
def test_espeak(njobs):
    text = ['one two', 'three', 'four five']

    out = phonemize(
        text, language='en-us', backend='espeak',
        strip=True, njobs=njobs)
    assert out == ['wʌn tuː', 'θɹiː', 'foːɹ faɪv']

    out = phonemize(
        text, language='en-us', backend='espeak',
        strip=False, njobs=njobs)
    assert out == ['wʌn tuː ', 'θɹiː ', 'foːɹ faɪv ']

    out = phonemize(
        ' '.join(text), language='en-us', backend='espeak',
        strip=True, njobs=njobs)
    assert out == ' '.join(['wʌn tuː', 'θɹiː', 'foːɹ faɪv'])

    out = phonemize(
        ' '.join(text), language='en-us', backend='espeak',
        strip=False, njobs=njobs)
    assert out == ' '.join(['wʌn tuː', 'θɹiː', 'foːɹ faɪv '])

    out = phonemize(
        '\n'.join(text), language='en-us', backend='espeak',
        strip=True, njobs=njobs)
    assert out == '\n'.join(['wʌn tuː', 'θɹiː', 'foːɹ faɪv'])

    out = phonemize(
        '\n'.join(text), language='en-us', backend='espeak',
        strip=False, njobs=njobs)
    assert out == '\n'.join(['wʌn tuː ', 'θɹiː ', 'foːɹ faɪv '])


@pytest.mark.skipif(
    not EspeakMbrolaBackend.is_available() or
    not EspeakMbrolaBackend.is_supported_language('mb-fr1'),
    reason='mbrola or mb-fr1 voice not installed')
@pytest.mark.parametrize('njobs', [2, 4])
def test_espeak_mbrola(njobs):
    text = ['un deux', 'trois', 'quatre cinq']

    out = phonemize(
        text, language='mb-fr1', backend='espeak-mbrola',
        strip=True, njobs=njobs)
    assert out == ['9~d2', 'tRwa', 'katRse~k']

    out = phonemize(
        text, language='mb-fr1', backend='espeak-mbrola',
        strip=False, njobs=njobs)
    assert out == ['9~d2', 'tRwa', 'katRse~k']


@pytest.mark.parametrize('njobs', [2, 4])
def test_festival(njobs):
    text = ['one two', 'three', 'four five']

    out = phonemize(
        text, language='en-us', backend='festival',
        strip=True, njobs=njobs)
    assert out == ['wahn tuw', 'thriy', 'faor fayv']

    out = phonemize(
        text, language='en-us', backend='festival',
        strip=False, njobs=njobs)
    assert out == ['wahn tuw ', 'thriy ', 'faor fayv ']

    out = phonemize(
        ' '.join(text), language='en-us', backend='festival',
        strip=True, njobs=njobs)
    assert out == ' '.join(['wahn tuw', 'thriy', 'faor fayv'])

    out = phonemize(
        ' '.join(text), language='en-us', backend='festival',
        strip=False, njobs=njobs)
    assert out == ' '.join(['wahn tuw', 'thriy', 'faor fayv '])

    out = phonemize(
        '\n'.join(text), language='en-us', backend='festival',
        strip=True, njobs=njobs)
    assert out == '\n'.join(['wahn tuw', 'thriy', 'faor fayv'])

    out = phonemize(
        '\n'.join(text), language='en-us', backend='festival',
        strip=False, njobs=njobs)
    assert out == '\n'.join(['wahn tuw ', 'thriy ', 'faor fayv '])


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
        strip=True, njobs=njobs)
    assert out == [
        'untṵːlḛ ka̰ːpʼḛːl', 'o̰ːʃpʼḛːl', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo']

    out = phonemize(
        text, language='yucatec', backend='segments',
        strip=False, njobs=njobs)
    assert out == [
        'untṵːlḛ ka̰ːpʼḛːl ', 'o̰ːʃpʼḛːl ', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo ']

    out = phonemize(
        u' '.join(text), language='yucatec', backend='segments',
        strip=True, njobs=njobs)
    assert out == ' '.join(
        ['untṵːlḛ ka̰ːpʼḛːl', 'o̰ːʃpʼḛːl', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo'])

    out = phonemize(
        u' '.join(text), language='yucatec', backend='segments',
        strip=False, njobs=njobs)
    assert out == u' '.join(
        ['untṵːlḛ ka̰ːpʼḛːl', 'o̰ːʃpʼḛːl', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo '])

    out = phonemize(
        u'\n'.join(text), language='yucatec', backend='segments',
        strip=True, njobs=njobs)
    assert out == u'\n'.join(
        ['untṵːlḛ ka̰ːpʼḛːl', 'o̰ːʃpʼḛːl', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo'])

    out = phonemize(
        u'\n'.join(text), language='yucatec', backend='segments',
        strip=False, njobs=njobs)
    assert out == u'\n'.join(
        ['untṵːlḛ ka̰ːpʼḛːl ', 'o̰ːʃpʼḛːl ', 'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo '])
