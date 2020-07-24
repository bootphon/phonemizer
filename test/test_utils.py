"""Test of the phonemizer.utils module"""

import pytest

from phonemizer.utils import chunks, cumsum, str2list, list2str

def test_cumsum():
    assert cumsum([]) == []
    assert cumsum([0]) == [0]
    assert cumsum([1, 2, 3]) == [1, 3, 6]


def test_list2str():
    assert list2str('') == ''
    assert list2str([]) == ''
    assert list2str(['']) == ''
    assert list2str(['abc']) == 'abc'
    assert list2str(['a', 'b', 'c']) == 'a\nb\nc'


def test_str2list():
    assert str2list('') == ['']
    assert str2list('a') == ['a']
    assert str2list('ab') == ['ab']
    assert str2list('a b') == ['a b']
    assert str2list('a\nb') == ['a', 'b']
    assert str2list('a\n\nb\n') == ['a', '', 'b']


def test_chunks():
    for n in range(1, 5):
        c = chunks(['a'], n)
        assert c == ['a']

    assert chunks(['a', 'a'], 1) == ['a\na']
    assert chunks(['a', 'a'], 2) == ['a', 'a']
    assert chunks(['a', 'a'], 10) == ['a', 'a']

    assert chunks(['a', 'a', 'a'], 1) == ['a\na\na']
    assert chunks(['a', 'a', 'a'], 2) == ['a', 'a\na']
    assert chunks(['a', 'a', 'a'], 3) == ['a', 'a', 'a']
    assert chunks(['a', 'a', 'a'], 10) == ['a', 'a', 'a']

    assert chunks(['a', 'a', 'a', 'a'], 1) == ['a\na\na\na']
    assert chunks(['a', 'a', 'a', 'a'], 2) == ['a\na', 'a\na']
    assert chunks(['a', 'a', 'a', 'a'], 3) == ['a', 'a', 'a\na']
    assert chunks(['a', 'a', 'a', 'a'], 10) == ['a', 'a', 'a', 'a']
