"""Tests of the phonemizer.backend.espeak.words_mismatch module"""

# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import re

import pytest

from phonemizer import phonemize
from phonemizer.backend.espeak.words_mismatch import Ignore
from phonemizer.separator import Separator, default_separator


@pytest.fixture
def text():
    return ["How are you?", "I have been busy", "I won't have time"]


def test_count_words():
    def count_words(phn):
        # pylint: disable=protected-access
        return Ignore._count_words(phn, wordsep=default_separator.word)

    assert count_words(['']) == [0]
    assert count_words(['a']) == [1]
    assert count_words(['aaa']) == [1]
    assert count_words([' aaa  ']) == [1]
    assert count_words([' a  a \taa  ']) == [3]


def test_count_words_whitespaces():
    # pylint: disable=protected-access
    text = ['', ' a ', 'a　b\tc', ' a b  c ']
    assert Ignore._count_words(text) == [0, 1, 3, 3]


@pytest.mark.parametrize('wordsep, expected', [
    (' | ', [0, 1, 1, 2]),
    ('|', [0, 1, 3, 3]),
    # an empty separator splits between each character
    ('', [0, 1, 8, 9]),
    (re.compile(r'\s*\|\s*'), [0, 1, 3, 3]),
])
def test_count_words_separators(wordsep, expected):
    # pylint: disable=protected-access
    text = ['', ' a ', ' a　| b |c\t', 'a | b|c | ']
    assert Ignore._count_words(text, wordsep) == expected


def test_bad():
    with pytest.raises(RuntimeError):
        phonemize('', words_mismatch='foo')

    with pytest.raises(RuntimeError):
        phonemize('', backend='festival', words_mismatch='remove')


@pytest.mark.parametrize('mode', ['ignore', 'warn', 'remove'])
def test_mismatch(caplog, text, mode):
    phn = phonemize(
        text, backend='espeak', language='en-us', words_mismatch=mode)

    if mode == 'ignore':
        assert phn == ['haʊ ɑːɹ juː ', 'aɪ hɐvbɪn bɪzi ', 'aɪ woʊntɐv taɪm ']
        messages = [msg[2] for msg in caplog.record_tuples]
        assert len(messages) == 1
        assert 'words count mismatch on 67.0% of the lines (2/3)' in messages
    elif mode == 'remove':
        assert phn == ['haʊ ɑːɹ juː ', '', '']
        messages = [msg[2] for msg in caplog.record_tuples]
        assert len(messages) == 2
        assert 'words count mismatch on 67.0% of the lines (2/3)' in messages
        assert 'removing the mismatched lines' in messages
    elif mode == 'warn':
        assert phn == ['haʊ ɑːɹ juː ', 'aɪ hɐvbɪn bɪzi ', 'aɪ woʊntɐv taɪm ']
        messages = [msg[2] for msg in caplog.record_tuples]
        assert len(messages) == 3
        assert (
            'words count mismatch on line 2 (expected 4 words but get 3)'
            in messages)
        assert (
            'words count mismatch on line 3 (expected 4 words but get 3)'
            in messages)
        assert 'words count mismatch on 67.0% of the lines (2/3)' in messages


# from https://github.com/bootphon/phonemizer/issues/169
def test_custom_separator(caplog):
    phn = phonemize(
        'try',
        backend='espeak',
        language='en-us',
        separator=Separator(word='|', phone=' '),
        words_mismatch='warn')

    assert phn == 't ɹ aɪ |'
    messages = [msg[2] for msg in caplog.record_tuples]
    assert len(messages) == 0


# from https://github.com/bootphon/phonemizer/issues/181
@pytest.mark.parametrize('text, expected', [
    (['Fine, I have been busy', 'Hello', 'Good morning'],
     ['', 'həloʊ ', 'ɡʊd mɔːɹnɪŋ ']),
    (['Hello, how are you?', 'I have been busy'],
     ['həloʊ, haʊ ɑːɹ juː? ', '']),
    (['Hello, how are you?', '!!', 'Good morning.'],
     ['həloʊ, haʊ ɑːɹ juː? ', '!! ', 'ɡʊd mɔːɹnɪŋ. '])])
def test_remove_preserve_punctuation(text, expected):
    phn = phonemize(
        text, backend='espeak', language='en-us', words_mismatch='remove',
        preserve_punctuation=True)
    assert phn == expected
