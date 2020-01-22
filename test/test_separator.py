# Copyright 2015-2020 Thomas Schatz, Xuan Nga Cao, Mathieu Bernard
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
"""Test of the Separator class"""

import pytest

from phonemizer.separator import Separator, default_separator


def test_prop():
    # read only attributes
    with pytest.raises(AttributeError):
        default_separator.phone = 'a'

    with pytest.raises(AttributeError):
        default_separator.syllable = 'a'

    with pytest.raises(AttributeError):
        default_separator.word = 'a'


@pytest.mark.parametrize('val', [None, '', False])
def test_empty(val):
    s = Separator(val, val, val)
    assert s.phone == ''
    assert s.syllable == ''
    assert s.word == ''


def test_same():
    with pytest.raises(ValueError):
        Separator(word=' ', phone=' ')


def test_str():
    separator = Separator(word='w', syllable='s', phone='p')
    assert str(separator) == '(phone: "p", syllable: "s", word: "w")'
    assert str(default_separator) == '(phone: "", syllable: "", word: " ")'


def test_equal():
    assert Separator() == Separator()
    assert default_separator == Separator(phone='', syllable='', word=' ')
    assert Separator(word='  ') != default_separator
