"""Test of the phonemizer.utils module"""

# pylint: disable=missing-docstring
import os

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
    assert list2str(['a', 'b', 'c']) == os.linesep.join('abc')


def test_str2list():
    assert str2list('') == ['']
    assert str2list('a') == ['a']
    assert str2list('ab') == ['ab']
    assert str2list('a b') == ['a b']
    assert str2list(f'a{os.linesep}b') == ['a', 'b']
    assert str2list(
        f'a{os.linesep}{os.linesep}b{os.linesep}') == ['a', '', 'b']


def test_chunks():
    for i in range(1, 5):
        assert chunks(['a'], i) == ([['a']], [0])

    assert chunks(['a', 'a'], 1) == ([['a', 'a']], [0])
    assert chunks(['a', 'a'], 2) == ([['a'], ['a']], [0, 1])
    assert chunks(['a', 'a'], 10) == ([['a'], ['a']], [0, 1])

    assert chunks(['a', 'a', 'a'], 1) == ([['a', 'a', 'a']], [0])
    assert chunks(['a', 'a', 'a'], 2) == ([['a'], ['a', 'a']], [0, 1])
    assert chunks(['a', 'a', 'a'], 3) == ([['a'], ['a'], ['a']], [0, 1, 2])
    assert chunks(['a', 'a', 'a'], 10) == ([['a'], ['a'], ['a']], [0, 1, 2])

    assert chunks(['a', 'a', 'a', 'a'], 1) == ([['a', 'a', 'a', 'a']], [0])
    assert chunks(['a', 'a', 'a', 'a'], 2) == (
        [['a', 'a'], ['a', 'a']], [0, 2])
    assert chunks(['a', 'a', 'a', 'a'], 3) == (
        [['a'], ['a'], ['a', 'a']], [0, 1, 2])
    assert chunks(['a', 'a', 'a', 'a'], 10) == (
        [['a'], ['a'], ['a'], ['a']], [0, 1, 2, 3])
