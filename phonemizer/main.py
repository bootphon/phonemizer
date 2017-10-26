#!/usr/bin/env python
# coding: utf-8

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
"""Command-line phonemizer tool, have a 'phonemizer --help' to get in"""

import argparse
import codecs
import logging
import pkg_resources
import sys

from . import phonemize, espeak, festival, separator


def parse_args(argv):
    """Argument parser for the phonemization script"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Multilingual text to phonemes converter

The 'phonemize' program allows simple phonemisation of words and texts
in many language. It is a wrapper on the text to speech softwares
'festival' and 'espeak'. The 'espeak' backend support the
International Phonetic Alphabet, whereas the 'festival' backend uses a
custom phoneset (http://www.festvox.org/bsv/c4711.html).
''',
        epilog='''
   Languages supported by festival are:
   {}

   Languages supported by espeak are:
   {}


Exemples:

* Phonemize a US English text with espeak

   $ echo 'hello world' | phonemize -l en-us
   həloʊ wɜːld

* Phonemize a US English text with festival

   $ echo 'hello world' | phonemize -l en-us-festival
   hhaxlow werld

* Add a separator between phones

  $ echo 'hello world' | phonemize -l en-us-festival -p '-' --strip
  hh-ax-l-ow w-er-l-d

* Phonemize some French text file

  $ phonemize -l fr-fr text.txt -o phones.txt
        '''.format(
            '\n'.join('\t{}-festival\t->\t{}'.format(k, v) for k, v in
                      sorted(festival.supported_languages().items())),
            '\n'.join('\t{}\t->\t{}'.format(k, v.encode('utf8')) for k, v in
                      sorted(espeak.supported_languages().items()))))

    # general arguments
    parser.add_argument(
        '--version', action='store_true',
        help='show version information and exit')

    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='write some log messages to stderr')

    parser.add_argument(
        '-j', '--njobs', type=int, metavar='<int>', default=1,
        help='number of parallel jobs, default is %(default)s')

    # input/output arguments
    group = parser.add_argument_group('input/output')
    group.add_argument(
        'input', default=sys.stdin, nargs='?', metavar='<file>',
        help='input text file to phonemize, if not specified read from stdin')

    group.add_argument(
        '-o', '--output', default=sys.stdout, metavar='<file>',
        help='output text file to write, if not specified write to stdout')

    group = parser.add_argument_group('separators')

    group.add_argument(
        '-p', '--phone-separator', metavar='<str>',
        default=separator.default_separator.phone,
        help='phone separator, default is "%(default)s"')

    group.add_argument(
        '-w', '--word-separator', metavar='<str>',
        default=separator.default_separator.word,
        help='word separator, default is "%(default)s"')

    group.add_argument(
        '-s', '--syllable-separator', metavar='<str>',
        default=separator.default_separator.syllable,
        help='''syllable separator is available only for the festival backend,
        this option has no effect if espeak is used.
        Default is "%(default)s"''')

    group.add_argument(
        '--strip', action='store_true',
        help='removes the end separators in phonemized tokens')

    group = parser.add_argument_group('language')

    group.add_argument(
        '-l', '--language', metavar='<str>', default='en-us-festival',
        help='''the language code of the input text, see below for a list of
        supported languages. According to the language code you
        specify, the appropriate backend (espeak or festival) will be
        called in background. Default is %(default)s''')

    return parser.parse_args(argv)


def version():
    """Return version information for front and backends"""
    # phonemize
    version = ('phonemizer: '
               + pkg_resources.get_distribution('phonemizer').version)

    return '\n'.join(
        (version, festival.festival_version(), espeak.espeak_version()))


def main(argv=sys.argv[1:]):
    """Phonemize a text from command-line arguments"""
    args = parse_args(argv)

    if args.version:
        print(version())
        return

    # configure logging according to --verbose option. If verbose,
    # init a logger to output on stderr. Else init a logger going to
    # the void.
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    if args.verbose:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter('%(message)s'))
    else:
        handler = logging.NullHandler()
    logger.addHandler(handler)

    # configure input as a readable stream
    streamin = args.input
    if isinstance(streamin, str):
        streamin = open(streamin, 'r')
    logger.debug('reading from %s', streamin.name)

    # configure output as a writable stream
    streamout = args.output
    if isinstance(streamout, str):
        streamout = codecs.open(streamout, 'w', 'utf8')
    logger.debug('writing to %s', streamout.name)

    # configure the separator for phonemes, syllables and words.
    sep = separator.Separator(
        args.word_separator,
        args.syllable_separator,
        args.phone_separator)

    # setup backend and language code
    if 'festival' in args.language:
        backend = 'festival'
        language = args.language.replace('-festival', '')
    else:
        backend = 'espeak'
        language = args.language

    # phonemize the input text
    out = phonemize(
        streamin.read(), language=language, backend=backend,
        separator=sep, strip=args.strip, njobs=args.njobs, logger=logger)

    if len(out):
        streamout.write(out + '\n')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, IndexError, pkg_resources.DistributionNotFound) as e:
        print('fatal error: {}'.format(e))
        sys.exit(-1)
    except KeyboardInterrupt:
        print('keybord interruption, exiting')
        sys.exit(-1)
