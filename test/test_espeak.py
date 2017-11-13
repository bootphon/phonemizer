# coding: utf-8

# Copyright 2017 Mathieu Bernard
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
"""Test of the phonemizer.espeak module"""

import pytest

import phonemizer.espeak as espeak


def test_espeak():
    text = u'hello world\ngoodbye\nthird line\nyet another'
    out = '\n'.join(espeak.phonemize(text, strip=True))
    assert out == u'həloʊ wɜːld\nɡʊdbaɪ\nθɜːd laɪn\njɛt ɐnʌðɚ'
