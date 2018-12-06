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
"""Test of the phonemizer.Phonemizer class"""

import pytest
from phonemizer import festival, separator


def _test(text, separator=separator.Separator(' ', '|', '-')):
    return festival.phonemize(
        text, language='en-us', strip=True,
        separator=separator)


@pytest.mark.skipif(
    '2.1' in festival.festival_version(),
    reason='festival-2.1 gives different results than further versions '
    'for syllable boundaries')
def test_hello():
    assert _test('hello world') == ['hh-ax|l-ow w-er-l-d']
    assert _test('hello\nworld') == ['hh-ax|l-ow', 'w-er-l-d']
    assert _test('hello\nworld\n') == ['hh-ax|l-ow', 'w-er-l-d']


@pytest.mark.parametrize('text', ['', ' ', '  ', '(', '()', '"', "'"])
def test_bad_input(text):
    assert _test(text) == []


def test_quote():
    assert _test("here a 'quote") == ['hh-ih-r ax k-w-ow-t']
    assert _test('here a "quote') == ['hh-ih-r ax k-w-ow-t']


def test_its():
    assert _test("it's") == ['ih-t-s']
    assert _test("its") == ['ih-t-s']
    assert _test("it s") == ['ih-t eh-s']
    assert _test('it "s') == ['ih-t eh-s']


def test_im():
    sep = separator.Separator(' ', '', '')
    assert _test("I'm looking for an image", sep) \
        == ['aym luhkaxng faor axn ihmaxjh']
    assert _test("Im looking for an image", sep) \
        == ['ihm luhkaxng faor axn ihmaxjh']
