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

import pytest
import tempfile
import shlex

from phonemizer.main import main


class TestPhonemizerMain(object):
    def setup(self):
        pass

    def _test(self, input, output, args=''):
        with tempfile.NamedTemporaryFile('w') as finput:
            finput.write(input)
            finput.seek(0)

            with tempfile.NamedTemporaryFile('rw') as foutput:
                main(shlex.split('{} -o {} {}'.format(
                    finput.name, foutput.name, args)))
                assert foutput.read() == output + '\n'

    def test_help(self):
        with pytest.raises(SystemExit):
            main('-h'.split())

    def test_readme1(self):
        input = ('Simple phonemization of English text, '
                 'based on the festival TTS system')
        output = ('s-ih-m-p|ax-l f-ax-n|ih-m|ih-z|ey-sh|ax-n ax-v '
                  'ih-ng-g|l-ax-sh t-eh-k-s-t b-ey-s-t aa-n dh-ax '
                  'f-eh-s|t-ax-v|ax-l t-iy t-iy eh-s s-ih-s|t-ax-m')
        self._test(input, output, '--strip')

    def test_readme2(self):
        self._test('hello world', 'hh-ax-l-|ow-| w-er-l-d-| ')
        self._test('hello world', 'hh-ax-l|ow w-er-l-d', '--strip')
        self._test(
            'hello world',
            'hh ax l ;esyll ow ;esyll ;eword w er l d ;esyll ;eword ',
            "-p ' ' -s ';esyll ' -w ';eword '")
