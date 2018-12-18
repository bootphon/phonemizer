# coding: utf-8

# Copyright 2016-2018 Thomas Schatz, Xuan Nga Cao, Mathieu Bernard
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
    assert out == [u'wʌn tuː', u'θɹiː', u'foːɹ faɪv']

    out = phonemize(
        text, language='en-us', backend='espeak',
        strip=False, njobs=njobs)
    assert out == [u'wʌn tuː ', u'θɹiː ', u'foːɹ faɪv ']

    out = phonemize(
        ' '.join(text), language='en-us', backend='espeak',
        strip=True, njobs=njobs)
    assert out == ' '.join([u'wʌn tuː', u'θɹiː', u'foːɹ faɪv'])

    out = phonemize(
        ' '.join(text), language='en-us', backend='espeak',
        strip=False, njobs=njobs)
    assert out == ' '.join([u'wʌn tuː', u'θɹiː', u'foːɹ faɪv '])

    out = phonemize(
        '\n'.join(text), language='en-us', backend='espeak',
        strip=True, njobs=njobs)
    assert out == '\n'.join([u'wʌn tuː', u'θɹiː', u'foːɹ faɪv'])

    out = phonemize(
        '\n'.join(text), language='en-us', backend='espeak',
        strip=False, njobs=njobs)
    assert out == '\n'.join([u'wʌn tuː ', u'θɹiː ', u'foːɹ faɪv '])


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


@pytest.mark.parametrize('njobs', [1, 2, 4])
def test_segments(njobs):
    # one two three four five in Maya Yucatec
    text = [u'untuʼuleʼ kaʼapʼeʼel', u'oʼoxpʼeʼel', u'kantuʼuloʼon chincho']

    out = phonemize(
        text, language='yucatec', backend='segments',
        strip=True, njobs=njobs)
    assert out == [u'untṵːlḛ ka̰ːpʼḛːl', u'o̰ːʃpʼḛːl',
                   u'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo']

    out = phonemize(
        text, language='yucatec', backend='segments',
        strip=False, njobs=njobs)
    assert out == [u'untṵːlḛ ka̰ːpʼḛːl ', u'o̰ːʃpʼḛːl ',
                   u'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo ']

    out = phonemize(
        u' '.join(text), language='yucatec', backend='segments',
        strip=True, njobs=njobs)
    assert out == ' '.join([u'untṵːlḛ ka̰ːpʼḛːl', u'o̰ːʃpʼḛːl',
                            u'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo'])

    out = phonemize(
        u' '.join(text), language='yucatec', backend='segments',
        strip=False, njobs=njobs)
    assert out == u' '.join([u'untṵːlḛ ka̰ːpʼḛːl', u'o̰ːʃpʼḛːl',
                            u'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo '])

    out = phonemize(
        u'\n'.join(text), language='yucatec', backend='segments',
        strip=True, njobs=njobs)
    assert out == u'\n'.join([u'untṵːlḛ ka̰ːpʼḛːl', u'o̰ːʃpʼḛːl',
                             u'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo'])

    out = phonemize(
        u'\n'.join(text), language='yucatec', backend='segments',
        strip=False, njobs=njobs)
    assert out == u'\n'.join([u'untṵːlḛ ka̰ːpʼḛːl ', u'o̰ːʃpʼḛːl ',
                             u'kantṵːlo̰ːn t̠͡ʃint̠͡ʃo '])
