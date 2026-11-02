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
from pathlib import Path

import pytest
import re

from phonemizer.backend import EspeakBackend, FestivalBackend, SegmentsBackend
from phonemizer.punctuation import Punctuation
from phonemizer.phonemize import phonemize
from phonemizer.separator import Separator, default_separator

# True if we are using espeak>=1.50
ESPEAK_150 = (EspeakBackend.version() >= (1, 50))

# True if we are using espeak>=1.49.3
ESPEAK_149 = (EspeakBackend.version() >= (1, 49, 3))

# True if we are using festival>=2.5
FESTIVAL_25 = False if not FestivalBackend.is_available() else (FestivalBackend.version() >= (2, 5))


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
        ["!'"],
        ["It is ! (I think so)"],
        ["This {is} right"],
        ["[He] is right"],
    ])
def test_preserve(inp):
    punct = Punctuation()
    text, marks = punct.preserve(inp)
    assert inp == punct.restore(text, marks, sep=default_separator, strip=True)


@pytest.mark.parametrize(
    'text, expected_restore, expected_output', [
        # a final chunk is restored as is: phonemized, it ends with a word
        # separator, or is empty and the mark before is followed by one
        (['hi; hi,"'], ['hi; hi,"'], ['haɪ; haɪ, ']),
        (['hi; "hi,'], ['hi; "hi, '], ['haɪ; haɪ, '] if ESPEAK_149 else ['haɪ;  haɪ, ']),
        (['"hi; hi,'], ['"hi; hi, '], ['haɪ; haɪ, '] if ESPEAK_149 else [' haɪ; haɪ, '])])
def test_preserve_2(text, expected_restore, expected_output):
    marks = ".!;:,?"
    punct = Punctuation(marks=marks)
    assert expected_restore == punct.restore(
        *punct.preserve(text), sep=default_separator, strip=False)

    output = phonemize(
        text, backend="espeak",
        preserve_punctuation=True, punctuation_marks=marks)
    assert output == expected_output


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
    expected4 = 'həloʊ, wɜːld! '

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


@pytest.mark.skipif(
    not FestivalBackend.is_available(), reason="festival not installed")
def test_festival():
    text = 'hello, world!'
    expected1 = 'hhaxlow werld'
    expected2 = 'hhaxlow, werld!'
    expected3 = 'hhaxlow werld '
    expected4 = 'hhaxlow, werld! '

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
    expected4 = 'ʌtʃɪ, ʌtʃʊ! '

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
    'text, expected', [("!'", "! "), ("'!", "! "), ("!'!", "!! "), ("'!'", "! ")])
def test_issue_54(text, expected):
    output = phonemize(
        [text], language='en-us', backend='espeak',
        preserve_punctuation=True)[0]
    assert expected == output


# see https://github.com/bootphon/phonemizer/issues/55
@pytest.mark.parametrize(
    'backend, marks, text, expected', [
        ('espeak', 'default', ['"Hey! "', '"hey,"'], ['"heɪ! " ', '"heɪ," ']),
        ('espeak', '.!;:,?', ['"Hey! " ', '"hey," '],
         ['heɪ! ', 'heɪ, '] if ESPEAK_150 else [' heɪ! ', ' heɪ, ']),
        ('espeak', 'default', ['! ?', 'hey!'], ['! ? ', 'heɪ! ']),
        ('espeak', '!', ['! ?', 'hey!'], ['! ', 'heɪ! ']),
        ('segments', 'default', ['! ?', 'hey!'], ['! ? ', 'heːj! ']),
        ('segments', '!', ['! ?', 'hey!'], ValueError),
        ('festival', 'default', ['! ?', 'hey!'], ['! ? ', 'hhey! ']),
        ('festival', '!', ['! ?', 'hey!'], ['! ', 'hhey! '])])
def test_issue55(backend, marks, text, expected):
    if backend == "festival" and not FestivalBackend.is_available():
        return

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


@pytest.mark.parametrize(
    'punctuation_marks, text, expected', [
        (';:,.!?¡—…"«»“”',
         'hello, ,world? ‡ 3,000, or 2.50. ¿hello?',
         'həloʊ, ,wɜːld? θɹiː θaʊzənd, ɔːɹ tuː pɔɪnt faɪv ziəɹoʊ. həloʊ? '),
        (re.compile(r"[^a-zA-ZÀ-ÖØ-öø-ÿ0-9'$@&+%\-=/\\]"),
         'hello, ,world? ‡ 3,000, or 2.50. ¿hello?',
         'həloʊ, ,wɜːld? ‡ θɹiː,ziəɹoʊziəɹoʊ ziəɹoʊ, ɔːɹ tuː.fɪfti. ¿həloʊ? '),
        (re.compile(r"[^a-zA-ZÀ-ÖØ-öø-ÿ0-9',.$@&+%\-=/\\]|[,.](?!\d)"),
         'hello, ,world? ‡ 3,000, or 2.50. ¿hello?',
         'həloʊ, ,wɜːld? ‡ θɹiː θaʊzənd, ɔːɹ tuː pɔɪnt faɪv ziəɹoʊ. ¿həloʊ? ')
    ])
def test_punctuation_marks_regex(punctuation_marks, text, expected):
    assert expected == phonemize(
        text, preserve_punctuation=True, punctuation_marks=punctuation_marks)


def test_marks_getter_with_regex():
    marks_re = re.compile(r"[^a-zA-Z0-9]")
    punct = Punctuation(marks_re)
    with pytest.raises(ValueError):
        punct.marks == marks_re


def test_long_document():
    # testing issue raised by #108
    DATA_FOLDER = Path(__file__).parent / "data"
    with open(DATA_FOLDER / "pg67147.txt") as txt_file:
        phonemize(txt_file.read().split("\n"), backend="espeak", preserve_punctuation=True)


@pytest.mark.parametrize(
    'text', [
        ([
            'worked david ford i started in deloitte and i was immediately',
         ]
        ),
        ([
            'worked david ford i started in deloitte, and i was immediately',
         ]
        ),
        ([
            'worked david ford i started in deloitte and i was immediately',
            'an offer of price waterhouse cooper and here i take may',
            'we are now as maximum plan for a customer time and',
            "they're going to meet all the xvin so great it"
         ]
        ),
        ([
            'worked david ford i started in deloitte, and i was immediately',
            'an offer of price waterhouse cooper and here i take may',
            'we are now as maximum plan for a customer time and',
            "they're going to meet all the xvin so great it."
         ]
        ),
    ])
def test_multiline_punctuation(text):
    phonemized = phonemize(text, preserve_punctuation=True)
    assert len(text) == len(phonemized)


# A mark that doubles as a decimal separator must not split a number: espeak
# then reads two separate numbers and the spoken value changes ("19,99 euro"
# became "nineteen ninety-nine euro"). A separator next to a non-digit is
# ordinary punctuation and is still split.
@pytest.mark.parametrize('text,expected', [
    ('1,5', '1,5'),
    ('3.14', '3.14'),
    ('19,99 euro', '19,99 euro'),
    ('version 2.5', 'version 2.5'),
    # first comma is a decimal separator, second is punctuation
    ('1,5, and more', '1,5 and more'),
    # a separator at the end of a number is punctuation
    ('I have 42.', 'I have 42'),
    ('42, 43', '42 43'),
    ('line 42, column 7', 'line 42 column 7'),
])
def test_decimal_separator_not_split(text, expected):
    assert Punctuation().remove(text) == expected


@pytest.mark.parametrize('text', [
    '1,5 and more',
    '19,99 euro',
    'hello, world',
    '3.14 is pi.',
    '1.5.',
])
def test_decimal_separator_preserve_restore(text):
    punctuation = Punctuation()
    preserved, marks = punctuation.preserve([text])
    restored = punctuation.restore(preserved, marks, default_separator, True)
    assert restored == [text]


def test_empty_marks():
    # no marks means no punctuation processing, not a match on every char
    punct = Punctuation('')
    assert punct.marks == ''
    assert punct.remove('hello, world') == 'hello, world'
    assert punct.preserve(['hello, world']) == (['hello, world'], [[0]])
    assert phonemize('hello world', punctuation_marks='') == 'həloʊ wɜːld '
    assert phonemize(
        'hello world', punctuation_marks=re.compile('')) == 'həloʊ wɜːld '


def test_preserve_parts():
    text = ['hello, my world!', '...', 'ok', '"a (b) c", d']
    chunks, lines = Punctuation().preserve(text)
    assert chunks == ['hello', 'my world', 'ok', 'a', 'b', 'c', 'd']
    assert lines == [
        [0, ', ', 1, '!'], ['...'], [2], ['"', 3, ' (', 4, ') ', 5, '", ', 6]]

    # the chunks separated by quotes or brackets only
    assert Punctuation().inline_groups(lines) == [[3, 4, 5]]


@pytest.mark.parametrize('mark, inline', [
    ('(', True), (' « ', True), ('") ', True), (', ', False), ('", ', False),
    ('-', False), (' ', False), ('', False)])
def test_is_inline(mark, inline):
    assert Punctuation().is_inline(mark) is inline


@pytest.mark.parametrize('context, expected', [
    # no context, or the words cannot be aligned with the chunks
    (None, ['a (b c) ']),
    ('x y ', ['a (b c) ']),
    ('x y z w ', ['a (b c) ']),
    ('', ['a (b c) ']),
    # aligned: the mark goes after the words of the first chunk
    ('x y z ', ['x (y z) ']),
    ('x  y z ', ['x (y z) ']),
])
def test_restore_context(context, expected):
    chunks, lines = Punctuation().preserve(['a (b c)'])
    phonemized = ['a ', 'b c ']
    context = [([0, 1], context)] if context else None
    assert Punctuation.restore(
        phonemized, lines, default_separator, False, context) == expected

    # the words cannot be counted without a word separator
    assert Punctuation.restore(
        ['a', 'bc'], lines, Separator(word='', phone='-'), False,
        [([0, 1], 'xyz')]) == ['a(bc)']
    assert Punctuation.restore(
        ['a|', 'b|c|'], lines, Separator(word='|', phone=' | '), False,
        [([0, 1], 'x|y|z|')]) == ['a|(b|c)|']


@pytest.mark.parametrize('lang, text, expected', [
    # pronounced as without punctuation, in context
    ('fr-fr', 'les (amis)', 'lez (ami) '),
    ('fr-fr', 'les « amis » de « mes amis »', 'lez « ami » də « mez ami » '),
    ('en-us', 'an (apple)', 'ɐn (æpəl) '),
    ('en-us', '"hello" world, (an) apple.', '"həloʊ" wɜːld, (ɐn) æpəl. '),
    # espeak joins "do not" in a single word, the marks are placed as when
    # phonemizing each chunk alone
    ('en-us', 'I do (not) know', 'aɪ duː (nɑːt) noʊ '),
    ('en-us', 'not (a) dog', 'nɑːt (eɪ) dɑːɡ '),
])
def test_espeak_context(lang, text, expected):
    assert phonemize(text, language=lang, preserve_punctuation=True) == expected


@pytest.mark.parametrize('lang, text', [
    ('en-us', ['to "the" house', '(a) [b] {c}', 'he said "it is (a lot)"']),
    ('fr-fr', ['les (amis) de « mes amis »', "c'est (un) [ami]"]),
])
def test_espeak_context_as_without_punctuation(lang, text):
    # with quotes and brackets only, the phonemes are the same as without
    # punctuation, when no words are joined across a mark
    marks = re.compile('[' + re.escape('"«»()[]{}') + ']')
    preserved = phonemize(text, language=lang, preserve_punctuation=True)
    removed = phonemize(text, language=lang)
    assert [' '.join(marks.sub(' ', line).split()) for line in preserved] \
        == [' '.join(line.split()) for line in removed]


@pytest.mark.parametrize('njobs', [1, 2])
def test_marks_alone_on_lines(njobs):
    # a line made of marks only used to merge with the next ones, or to remove
    # the word separator ending the next line
    assert phonemize(
        ['a', '!', '?'], preserve_punctuation=True, njobs=njobs) == \
        ['eɪ ', '! ', '? ']
    assert phonemize(
        ['!', 'hello', 'a.'], preserve_punctuation=True, njobs=njobs) == \
        ['! ', 'həloʊ ', 'eɪ. ']


def test_restore_many_lines():
    # restore() used to slice its lists at each mark, taking minutes on a few
    # tens of thousands of lines
    text = [f'hello, my world {i}!' for i in range(50000)]
    punct = Punctuation()
    chunks, marks = punct.preserve(text)
    assert punct.restore(chunks, marks, default_separator, True) == text


def test_restore_keeps_input():
    chunks, marks = Punctuation().preserve(['a, b!'])
    phonemized = [c + ' ' for c in chunks]
    Punctuation.restore(phonemized, marks, default_separator, False)
    assert phonemized == ['a ', 'b ']


@pytest.mark.parametrize('word', ['\\', '\\1', '\\n', ' \\g<0> '])
def test_restore_backslash_separator(word):
    # the word separator was used as a regex replacement template, so that
    # backslashes raised an error or were read as escapes
    text = ['hello, world', 'ok!', 'a ,b']
    expected = [
        line.replace('|', word) for line in phonemize(
            text, preserve_punctuation=True, separator=Separator(word='|'))]
    assert phonemize(
        text, preserve_punctuation=True,
        separator=Separator(word=word)) == expected

    # a line made of marks only
    assert Punctuation.restore(
        [], [['! ?']], Separator(word=word), True) == [f'!{word}?']


def test_restore_context_not_a_group():
    # the chunks of a group must be separated by a single inline mark in a
    # line, else the group is ignored
    chunks, lines = Punctuation().preserve(['a (b), c'])
    phonemized = ['a ', 'b ', 'c ']
    expected = ['a (b), c ']
    for group in ([0, 2], [1, 2], [0, 5]):
        assert Punctuation.restore(
            phonemized, lines, default_separator, False,
            [(group, 'x y ')]) == expected


@pytest.mark.parametrize('njobs', [1, 2])
def test_espeak_context_njobs(njobs):
    text = ['les (amis)', 'hello, world', 'an (apple) and "the" tree'] * 3
    assert EspeakBackend('en-us', preserve_punctuation=True).phonemize(
        text[1:2] + text[2:3], njobs=njobs) == [
            'həloʊ, wɜːld ', 'ɐn (æpəl) ænd "ðə" tɹiː ']
    assert phonemize(
        text, language='fr-fr', preserve_punctuation=True, njobs=njobs,
        language_switch='remove-flags')[:2] == [
            'lez (ami) ', 'ɛlo, wɜːld ']


@pytest.mark.skipif(
    not FestivalBackend.is_available(), reason="festival not installed")
def test_festival_context():
    # weak form of "an" before a vowel, in context
    assert FestivalBackend('en-us', preserve_punctuation=True).phonemize(
        ['an (apple) a day']) == ['axn (aepaxl) ax dey ']


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
def test_espeak_context_language_switch(caplog):
    # the switches of the groups phonemized in context are not reported, they
    # are on the chunks phonemized alone as well
    out = EspeakBackend('fr-fr', preserve_punctuation=True).phonemize(
        ['le (football) et le weekend', 'le football'])
    assert out == [
        'lə ((en)fʊtbɔːl(fr)) e lə (en)wiːkɛnd(fr) ',
        'lə (en)fʊtbɔːl(fr) ']
    messages = [msg[2] for msg in caplog.record_tuples]
    assert (
        '3 utterances containing language switches on lines 2, 3, 4'
        in messages)


def test_context_with_old_postprocess():
    # a backend overloading _phonemize_postprocess() with its signature of
    # previous releases still works
    class Backend(EspeakBackend):
        def _phonemize_postprocess(self, phonemized, punctuation_marks,
                                   separator, strip):
            return super()._phonemize_postprocess(
                phonemized, punctuation_marks, separator, strip)

    assert Backend('en-us', preserve_punctuation=True).phonemize(
        ['an (apple)']) == ['ɐn (æpəl) ']


@pytest.mark.parametrize('separator, context', [
    (Separator(word=' ', phone='-'), True),
    (Separator(word='', phone='-'), False),
    (Separator(word='|', phone='|-'), False),
])
def test_context_separator(separator, context):
    # the groups are not phonemized in context when their marks cannot be
    # placed with this separator
    backend = EspeakBackend('en-us', preserve_punctuation=True)
    phonemized = []
    phonemize_aux = backend._phonemize_aux

    def spy(text, *args):
        phonemized.extend(text)
        return phonemize_aux(text, *args)

    backend._phonemize_aux = spy
    backend.phonemize(['an (apple)'], separator=separator)
    assert phonemized == ['an', 'apple'] + (['an apple'] if context else [])
