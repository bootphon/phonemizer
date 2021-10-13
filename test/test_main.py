# Copyright 2015-2021 Thomas Schatz, Xuan Nga Cao, Mathieu Bernard
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

# pylint: disable=missing-docstring

import os
import pathlib
import tempfile
import shlex
import sys

import pytest

from phonemizer.backend import EspeakBackend, EspeakMbrolaBackend
from phonemizer import main, backend, logger


def _test(text, expected_output, args=''):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = pathlib.Path(tmpdir) / 'input.txt'
        output_file = pathlib.Path(tmpdir) / 'output.txt'
        with open(input_file, 'wb') as finput:
            finput.write(text.encode('utf8'))

        sys.argv = ['unused', f'{input_file}', '-o', f'{output_file}']
        if args:
            sys.argv += shlex.split(args)
        main.main()

        with open(output_file, 'rb') as foutput:
            output = foutput.read().decode()

        if expected_output == '':
            assert output == ''
        else:
            # linesep is \n on Linux/MacOS and \r\n on Windows
            assert output == expected_output + os.linesep


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


@pytest.mark.parametrize('njobs', range(1, 6))
def test_njobs(njobs):
    _test(
        os.linsep.join(
            u'hello world',
            u'goodbye',
            u'third line',
            u'yet another',
        os.linesep.join(
            u'h-ə-l-oʊ w-ɜː-l-d',
            u'ɡ-ʊ-d-b-aɪ',
            u'θ-ɜː-d l-aɪ-n',
            u'j-ɛ-t ɐ-n-ʌ-ð-ɚ',
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
          '-b espeak-mbrola -l mb-fr1 -p" " --preserve-punctuation')


def test_espeak_path():
    espeak = pathlib.Path(backend.EspeakBackend.library())
    if sys.platform == 'win32':
        espeak = str(espeak).replace('\\', '\\\\').replace(' ', '\\ ')
    _test(u'hello world', u'həloʊ wɜːld ', f'--espeak-library={espeak}')


def test_festival_path():
    festival = pathlib.Path(backend.FestivalBackend.executable())
    if sys.platform == 'win32':
        festival = str(festival).replace('\\', '\\\\').replace(' ', '\\ ')

    _test(u'hello world', u'hhaxlow werld ',
          f'--festival-executable={festival} -b festival')
