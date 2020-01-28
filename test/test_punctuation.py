# Copyright 2015-2020 Mathieu Bernard
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

import pytest

from phonemizer.punctuation import Punctuation


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
        ['a, a?', 'aaa bb', '.bb, b', 'c', '!d.d. dd??  d!']])
def test_preserve(inp):
    p = Punctuation()
    t, m = p.preserve(inp)
    assert inp == p.restore(t, m)


def test_custom():
    p = Punctuation()
    m = p.marks
    assert set(m) == set(p.default_marks())
    assert p.remove('a,b.c') == 'a b c'

    with pytest.raises(ValueError):
        p.marks = ['?', '.']
    p.marks = '?.'
    assert len(p.marks) == 2
    assert p.remove('a,b.c') == 'a,b c'
