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
"""Test of the punctuation processing"""

# pylint: disable=missing-docstring

import pytest

from phonemizer.backend import EspeakBackend, FestivalBackend, SegmentsBackend
from phonemizer.punctuation import Punctuation
from phonemizer.phonemize import phonemize

# True if we are using espeak>=1.50
ESPEAK_150 = (EspeakBackend.version() >= (1, 50))

# True if we are using espeak>=1.49.3
ESPEAK_143 = (EspeakBackend.version() >= (1, 49, 3))

# True if we are using festival>=2.5
FESTIVAL_25 = (FestivalBackend.version() >= (2, 5))


@pytest.mark.parametrize(
    'inp, out', [
        ('a, b,c.', 'a b c'),
        ('abc de', 'abc de'),
        ('!d.d. dd??  d!', 'd d dd d')])
def test_remove(inp, out):
    assert Punctuation().remove(inp) == out


@pytest.mark.parametrize(
    'inp', [
        ['.a.b.c.'],
        ['a, a?', 'b, b'],
        ['a, a?', 'b, b', '!'],
        ['a, a?', '!?', 'b, b'],
        ['!?', 'a, a?', 'b, b'],
        ['a, a, a'],
        ['a, a?', 'aaa bb', '.bb, b', 'c', '!d.d. dd??  d!'],
        ['Truly replied, "Yes".'],
        ['hi; ho,"'],
        ["!?"],
        ["!'"]])
def test_preserve(inp):
    punct = Punctuation()
    text, marks = punct.preserve(inp)
    assert inp == punct.restore(text, marks)


@pytest.mark.parametrize(
    'text, expected', [
        (['hi; ho,"'], ['haɪ ; hoʊ ,']),
        (['hi; "ho,'], ['haɪ ; hoʊ ,'] if ESPEAK_143 else ['haɪ ;  hoʊ ,']),
        (['"hi; ho,'], ['haɪ ; hoʊ ,'] if ESPEAK_143 else [' haɪ ; hoʊ ,'])])
def test_preserve_2(text, expected):
    marks = ".!;:,?"
    punct = Punctuation(marks=marks)
    assert text == punct.restore(*punct.preserve(text))

    output = phonemize(
        text, backend="espeak",
        preserve_punctuation=True, punctuation_marks=marks)
    assert output == expected


def test_custom():
    punct = Punctuation()
    assert set(punct.marks) == set(punct.default_marks())
    assert punct.remove('a,b.c') == 'a b c'

    with pytest.raises(ValueError):
        punct.marks = ['?', '.']
    punct.marks = '?.'
    assert len(punct.marks) == 2
    assert punct.remove('a,b.c') == 'a,b c'


def test_espeak():
    text = 'hello, world!'
    expected1 = 'həloʊ wɜːld'
    expected2 = 'həloʊ, wɜːld!'
    expected3 = 'həloʊ wɜːld '
    expected4 = 'həloʊ , wɜːld !'

    out1 = EspeakBackend('en-us', preserve_punctuation=False).phonemize(
        [text], strip=True)[0]
    assert out1 == expected1

    out2 = EspeakBackend('en-us', preserve_punctuation=True).phonemize(
        [text], strip=True)[0]
    assert out2 == expected2

    out3 = EspeakBackend('en-us', preserve_punctuation=False).phonemize(
        [text], strip=False)[0]
    assert out3 == expected3

    out4 = EspeakBackend('en-us', preserve_punctuation=True).phonemize(
        [text], strip=False)[0]
    assert out4 == expected4


def test_festival():
    text = 'hello, world!'
    expected1 = 'hhaxlow werld'
    expected2 = 'hhaxlow, werld!'
    expected3 = 'hhaxlow werld '
    expected4 = 'hhaxlow , werld !'

    out1 = FestivalBackend('en-us', preserve_punctuation=False).phonemize(
        [text], strip=True)[0]
    assert out1 == expected1

    out2 = FestivalBackend('en-us', preserve_punctuation=True).phonemize(
        [text], strip=True)[0]
    assert out2 == expected2

    out3 = FestivalBackend('en-us', preserve_punctuation=False).phonemize(
        [text], strip=False)[0]
    assert out3 == expected3

    out4 = FestivalBackend('en-us', preserve_punctuation=True).phonemize(
        [text], strip=False)[0]
    assert out4 == expected4


def test_segments():
    text = 'achi, acho!'
    expected1 = 'ʌtʃɪ ʌtʃʊ'
    expected2 = 'ʌtʃɪ, ʌtʃʊ!'
    expected3 = 'ʌtʃɪ ʌtʃʊ '
    expected4 = 'ʌtʃɪ , ʌtʃʊ !'

    out1 = SegmentsBackend('cree', preserve_punctuation=False).phonemize(
        [text], strip=True)[0]
    assert out1 == expected1

    out2 = SegmentsBackend('cree', preserve_punctuation=True).phonemize(
        [text], strip=True)[0]
    assert out2 == expected2

    out3 = SegmentsBackend('cree', preserve_punctuation=False).phonemize(
        [text], strip=False)[0]
    assert out3 == expected3

    out4 = SegmentsBackend('cree', preserve_punctuation=True).phonemize(
        [text], strip=False)[0]
    assert out4 == expected4


# see https://github.com/bootphon/phonemizer/issues/54
@pytest.mark.parametrize(
    'text', ["!'", "'!", "!'!", "'!'"])
def test_issue_54(text):
    output = phonemize(
        [text], language='en-us', backend='espeak',
        preserve_punctuation=True)[0]
    assert text.replace("'", '') == output


# see https://github.com/bootphon/phonemizer/issues/55
@pytest.mark.parametrize(
    'backend, marks, text, expected', [
        ('espeak', 'default', ['"Hey! "', '"hey,"'], ['"heɪ ! "', '"heɪ ,"']),
        ('espeak', '.!;:,?', ['"Hey! "', '"hey,"'],
         ['heɪ ! ', 'heɪ ,'] if ESPEAK_150 else [' heɪ ! ', ' heɪ ,']),
        ('espeak', 'default', ['! ?', 'hey!'], ['! ?', 'heɪ !']),
        ('espeak', '!', ['! ?', 'hey!'], ['! ', 'heɪ !']),
        ('segments', 'default', ['! ?', 'hey!'], ['! ?', 'heːj !']),
        ('segments', '!', ['! ?', 'hey!'], ValueError),
        ('festival', 'default', ['! ?', 'hey!'], ['! ?', 'hhey !']),
        ('festival', '!', ['! ?', 'hey!'], ['!  ', 'hhey !'])])
def test_issue55(backend, marks, text, expected):
    if marks == 'default':
        marks = Punctuation.default_marks()
    language = 'cree' if backend == 'segments' else 'en-us'

    try:
        with pytest.raises(expected):
            phonemize(
                text, language=language, backend=backend,
                preserve_punctuation=True, punctuation_marks=marks)
    except TypeError:
        try:
            assert expected == phonemize(
                text, language=language, backend=backend,
                preserve_punctuation=True, punctuation_marks=marks)
        except RuntimeError:
            if backend == 'festival':
                # TODO on some installations festival fails to phonemize "?".
                # It ends with a segmentation fault. This seems to only appear
                # with festival-2.5 (but is working on travis and docker image)
                pass
