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
"""Implementation of punctuation processing"""


import re


_DEFAULT_MARKS = ';:,.!?¡¿—"'


def _apply_str_or_list(function, text):
    if isinstance(text, list):
        return [function(line) for line in text]
    return function(text)


class Punctuation:
    def __init__(self, marks=_DEFAULT_MARKS):
        self.marks = marks

    @staticmethod
    def default_marks():
        return _DEFAULT_MARKS

    @property
    def marks(self):
        return self._marks

    @marks.setter
    def marks(self, value):
        if not isinstance(value, str):
            raise ValueError('punctuation marks must be defined as a string')
        self._marks = ''.join(set(value))

        # catching all the marks in one regular expression: zero or more spaces
        # + one or more marks + zero or more spaces.
        self.marks_re = re.compile(fr'\s*[{self._marks}]+\s*')

    def remove(self, text):
        """Returns the `text` with all punctuation marks replaced by spaces"""
        return _apply_str_or_list(self._remove_str, text)

    def _remove_str(self, text):
        return re.sub(self._match_re, ' ', text)

    def preserve(self, text):
        return _apply_str_or_list(self._preserve_str, text)

    def _preserve_str(self, text):
        return text, []

    def restore(text, marks):
        return _apply_str_or_list(self._restore_str, text)

    def _restore_str(self, text):
        return text
