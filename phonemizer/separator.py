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
"""Provides the Separator tuple and its default value"""


class Separator(object):
    """Defines phone, syllable and word boundary tokens"""
    def __init__(self, word=' ', syllable=None, phone=None):
        # check we have different separators, None excluded
        g1 = list(sep for sep in (phone, syllable, word) if sep)
        g2 = set(sep for sep in (phone, syllable, word) if sep)
        if len(g1) != len(g2):
            raise ValueError(
                'illegal separator with word="{}", syllable="{}" and '
                'phone="{}", must be all differents if not empty'
                .format(phone, syllable, word))

        self._phone = str(phone) if phone else ''
        self._syllable = str(syllable) if syllable else ''
        self._word = str(word) if word else ''

    def __eq__(self, other):
        return (
            self.phone == other.phone
            and self.syllable == other.syllable
            and self.word == other.word)

    def __str__(self):
        def format(s):
            return '"{}"'.format(s)

        return '(phone: {}, syllable: {}, word: {})'.format(
            format(self.phone), format(self.syllable), format(self.word))

    @property
    def phone(self):
        return self._phone

    @property
    def syllable(self):
        return self._syllable

    @property
    def word(self):
        return self._word


default_separator = Separator(phone='', syllable='', word=' ')
"""The default separation characters for phonemes, syllables and words"""
