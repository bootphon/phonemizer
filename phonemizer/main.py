#!/usr/bin/env python
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
"""Phonemization of English text utterances using festival and a US phoneset"""

import argparse
import logging
import pkg_resources
import sys

from phonemizer import Phonemizer, Separator


def parse_args(argv):
    """Argument parser for the phonemization script"""
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        'input', default=sys.stdin, nargs='?', metavar='<file>',
        help='input text file to phonemize, if not specified read from stdin')

    parser.add_argument(
        '-o', '--output', default=sys.stdout, metavar='<file>',
        help='output text file to write, if not specified write to stdout')

    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='write some log messages to stderr')

    group = parser.add_argument_group('separators')

    group.add_argument(
        '-w', '--word-separator', metavar='<str>',
        default=Phonemizer.default_separator.word,
        help='word separator, default is "%(default)s"')

    group.add_argument(
        '-s', '--syllable-separator', metavar='<str>',
        default=Phonemizer.default_separator.syllable,
        help='syllable separator, default is "%(default)s"')

    group.add_argument(
        '-p', '--phone-separator', metavar='<str>',
        default=Phonemizer.default_separator.phone,
        help='phone separator, default is "%(default)s"')

    group.add_argument(
        '--strip', action='store_true',
        help='removes the end separators in phonemized tokens')

    return parser.parse_args(argv)


def main(argv=sys.argv[1:]):
    """Compute the phonologization of an input text through festival"""
    args = parse_args(argv)

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
        streamout = open(streamout, 'w')
    logger.debug('writing to %s', streamout.name)

    # configure the phonemizer
    p = Phonemizer(logger=logger)
    p.separator = Separator(
        args.word_separator,
        args.syllable_separator,
        args.phone_separator)
    p.strip_separator = args.strip

    # do the phonemization and output it
    out = p.phonemize(streamin.read())
    if len(out):
        streamout.write(out + '\n')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, pkg_resources.DistributionNotFound) as err:
        print('fatal error: {}'.format(err))
        sys.exit(1)
