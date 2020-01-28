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
"""Provides utility functions for the phonemizer"""

import six


def str2list(s):
    """Returns the string `s` as a list of lines"""
    return s.strip().split('\n') if isinstance(s, six.string_types) else s


def list2str(s):
    """Returns the list of lines `s` as a single string"""
    return '\n'.join(s) if not isinstance(s, six.string_types) else s


def chunks(text, n):
    """Return `n` equally sized chunks of a `text`

    Only the n-1 first chunks have equal size. The last chunk can be longer.
    The input `text` can be a list or a string. Return a list of `n` strings.

    This method is usefull when phonemizing a single text on multiple jobs.

    """
    text = str2list(text)
    size = int(max(1, len(text)/n))
    return [list2str(text[i:i+size])
            for i in range(0, len(text), size)]
