# Copyright 2016-2019 Thomas Schatz, Xuan Nga Cao, Mathieu Bernard
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
from phonemizer.backend import EspeakBackend


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


@pytest.mark.parametrize('njobs', [1, 2, 4])
def test_espeak(njobs):
    text = ['one two', 'three', 'four five']

    out = phonemize(
        text, language='en-us', backend='espeak',
        strip=True, njobs=njobs)
    assert out == ['wʌn tuː', 'θɹiː', 'foːɹ faɪv']

    if EspeakBackend.is_espeak_ng():
        out = phonemize(
            text, language='en-us', backend='espeak', use_sampa=True,
            strip=True, njobs=njobs)
        assert out == ['wVn tu:', 'Tri:', 'fo@ faIv']

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


@pytest.mark.parametrize('njobs', [1, 2, 4])
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
            text, language='en-us', backend='festival', use_sampa=True)

    with pytest.raises(RuntimeError):
        phonemize(
            text, language='en-us', backend='festival', with_stress=True)

    with pytest.raises(RuntimeError):
        phonemize(
            text, language='en-us', backend='festival',
            language_switch='remove-flags')


@pytest.mark.parametrize('njobs', [1, 2, 4])
def test_segments(njobs):
    # one two three four five in Maya Yucatec
    text = ['untuʼuleʼ kaʼapʼeʼel', 'oʼoxpʼeʼel', 'kantuʼuloʼon chincho']

    with pytest.raises(RuntimeError):
        phonemize(
            text, language='yucatec', backend='segments',
            use_sampa=True, strip=True, njobs=njobs)

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
