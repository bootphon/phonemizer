# Copyright 2016 Thomas Schatz, Xuan Nga Cao, Mathieu Bernard
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

import phonemizer


class TestPhonemizer(object):
    def setup(self):
        self.p = phonemizer.Phonemizer()
        self.p.strip_separator = True

    def test_hello(self):
        assert self.p.phonemize('hello world') == 'hh-ax-l|ow w-er-l-d'
        assert self.p.phonemize('hello\nworld') == 'hh-ax-l|ow\nw-er-l-d'

    def test_empty(self):
        assert self.p.phonemize('') == ''
        assert self.p.phonemize(' ') == ''
        assert self.p.phonemize('  ') == ''
        assert self.p.phonemize('(') == ''
        assert self.p.phonemize('()') == ''
        assert self.p.phonemize('"') == ''
        assert self.p.phonemize("'") == ''

    def test_quote(self):
        assert self.p.phonemize("here a 'quote") == 'hh-ih-r ax k-w-ow-t'
        assert self.p.phonemize('here a "quote') == 'hh-ih-r ax k-w-ow-t'
