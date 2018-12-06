# coding: utf-8

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
import tempfile
import shlex

from phonemizer import main, festival


def _test(input, expected_output, args=''):
    with tempfile.NamedTemporaryFile('w', delete=False) as finput:
        finput.write(input)
        finput.seek(0)

        with tempfile.NamedTemporaryFile('w+', delete=False) as foutput:
            opts = '{} -o {} {}'.format(finput.name, foutput.name, args)
            main.main(shlex.split(opts))
            output = foutput.read()
            try:  # python2 needs additional utf8 decoding
                output = output.decode('utf8')
            except AttributeError:  # python3 is OK
                pass
            assert output == expected_output + '\n'


def test_help():
    with pytest.raises(SystemExit):
        main.main('-h'.split())


def test_readme():
    _test(u'hello world', u'hhaxlow werld ')
    _test(u'hello world', u'hhaxlow werld', '--strip')
    _test(u'hello world', u'həloʊ wɜːld ', '-l en-us')
    _test(u'bonjour le monde', u'bɔ̃ʒuʁ lə- mɔ̃d ', '-l fr-fr')
    _test(u'bonjour le monde', u'b ɔ̃ ʒ u ʁ ;eword l ə- ;eword m ɔ̃ d ;eword ',
          '-l fr-fr -p " " -w ";eword "')


@pytest.mark.skipif(
    '2.1' in festival.festival_version(),
    reason='festival-2.1 gives different results than further versions '
    'for syllable boundaries')
def test_readme_festival_syll():
    _test(u'hello world',
          u'hh ax ;esyll l ow ;esyll ;eword w er l d ;esyll ;eword ',
          u"-p ' ' -s ';esyll ' -w ';eword '")


def test_njobs():
    for njobs in range(1, 4):
        _test(
            u'hello world\ngoodbye\nthird line\nyet another',
            u'h-ə-l-oʊ w-ɜː-l-d\nɡ-ʊ-d-b-aɪ\nθ-ɜː-d l-aɪ-n\nj-ɛ-t ɐ-n-ʌ-ð-ɚ',
            u'--strip -j {} -l en-us -p "-" -s "|" -w " "'.format(njobs))
