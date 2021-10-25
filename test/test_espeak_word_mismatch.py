"""Tests of the phonemizer.backend.espeak.words_mismatch module"""

# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import pytest

from phonemizer.backend.espeak.words_mismatch import Ignore
from phonemizer import phonemize


@pytest.fixture
def text():
    return ["How are you?", "I have been busy", "I won't have time"]


def test_count_words():
    # pylint: disable=protected-access
    count_words = Ignore._count_words
    assert count_words(['']) == [0]
    assert count_words(['a']) == [1]
    assert count_words(['aaa']) == [1]
    assert count_words([' aaa  ']) == [1]
    assert count_words([' a  a \taa  ']) == [3]


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
