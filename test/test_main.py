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
"""Test of the command line interface"""

import pytest
import tempfile
import shlex
import sys

from phonemizer.backend import EspeakBackend, EspeakMbrolaBackend
from phonemizer import main, backend, logger


def _test(input, expected_output, args=''):
    with tempfile.NamedTemporaryFile('w') as finput:
        # python2 needs additional utf8 encoding
        if sys.version_info[0] == 2:
            input = input.encode('utf8')
        finput.write(input)
        finput.seek(0)

        with tempfile.NamedTemporaryFile('w+') as foutput:
            opts = '{} -o {} {}'.format(finput.name, foutput.name, args)
            sys.argv = ['foo'] + shlex.split(opts)
            main.main()

            output = foutput.read()
            if expected_output == '':
                assert output == ''
            else:
                assert output == expected_output + '\n'


def test_help():
    sys.argv = ['foo', '-h']
    with pytest.raises(SystemExit):
        main.main()


def test_version():
    sys.argv = ['foo', '--version']
    main.main()


def test_list_languages():
    sys.argv = ['foo', '--list-languages']
    main.main()


def test_readme():
    _test(u'hello world', u'həloʊ wɜːld ')
    _test(u'hello world', u'həloʊ wɜːld ', '--verbose')
    _test(u'hello world', u'həloʊ wɜːld ', '--quiet')
    _test(u'hello world', u'hhaxlow werld', '-b festival --strip')
    _test(u'hello world', u'həloʊ wɜːld ', '-l en-us')
    _test(u'bonjour le monde', u'bɔ̃ʒuʁ lə mɔ̃d ', '-l fr-fr')
    _test(u'bonjour le monde', u'b ɔ̃ ʒ u ʁ ;eword l ə ;eword m ɔ̃ d ;eword ',
          '-l fr-fr -p " " -w ";eword "')


@pytest.mark.skipif(
    '2.1' in backend.FestivalBackend.version(),
    reason='festival-2.1 gives different results than further versions '
    'for syllable boundaries')
def test_readme_festival_syll():
    _test(u'hello world',
          u'hh ax ;esyll l ow ;esyll ;eword w er l d ;esyll ;eword ',
          u"-p ' ' -s ';esyll ' -w ';eword ' -b festival -l en-us")


def test_njobs():
    for njobs in range(1, 6):
        _test(
            u'hello world\ngoodbye\nthird line\nyet another',
            u'h-ə-l-oʊ w-ɜː-l-d\nɡ-ʊ-d-b-aɪ\nθ-ɜː-d l-aɪ-n\nj-ɛ-t ɐ-n-ʌ-ð-ɚ',
            u'--strip -j {} -l en-us -b espeak -p "-" -s "|" -w " "'
            .format(njobs))


def test_unicode():
    _test(u'untuʼule', u'untṵːle', '-l yucatec -b segments --strip')
    _test(u'untuʼule', u'untṵːle ', '-l yucatec -b segments')


@pytest.mark.skipif(
    not EspeakBackend.is_espeak_ng(),
    reason='language switch only exists for espeak-ng')
def test_language_switch():
    _test("j'aime le football", "ʒɛm lə (en)fʊtbɔːl(fr) ",
          '-l fr-fr -b espeak')

    _test("j'aime le football", "ʒɛm lə (en)fʊtbɔːl(fr) ",
          '-l fr-fr -b espeak --language-switch keep-flags')

    _test("j'aime le football", "ʒɛm lə fʊtbɔːl ",
          '-l fr-fr -b espeak --language-switch remove-flags')

    _test("j'aime le football", "",
          '-l fr-fr -b espeak --language-switch remove-utterance')


def test_logger():
    with pytest.raises(RuntimeError):
        logger.get_logger(verbosity=1)


@pytest.mark.skipif(
    not EspeakMbrolaBackend.is_available() or
    not EspeakMbrolaBackend.is_supported_language('mb-fr1'),
    reason='mbrola or mb-fr1 voice not installed')
def test_espeak_mbrola():
    _test(u'coucou toi!', u'k u k u t w a ',
          f'-b espeak-mbrola -l mb-fr1 -p" " --preserve-punctuation')


def test_espeak_path():
    espeak = backend.EspeakBackend.espeak_path()
    _test(u'hello world', u'həloʊ wɜːld ', f'--espeak-path={espeak}')


def test_festival_path():
    festival = backend.FestivalBackend.festival_path()
    _test(u'hello world', u'hhaxlow werld ',
          f'--festival-path={festival} -b festival')
