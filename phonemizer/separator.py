# Copyright 2015, 2016 Mathieu Bernard
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
"""Provides the Separator tuple and its default value"""

import collections


Separator = collections.namedtuple('Separator', ['word', 'syllable', 'phone'])
"""A tuple of word, syllable and phone separators"""


default_separator = Separator(' ', '', '_')
"""The default separation characters for phonemes, syllables and words"""
