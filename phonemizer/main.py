#!/usr/bin/env python
# Copyright 2015-2019 Mathieu Bernard
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
import pkg_resources
import sys

from phonemizer import phonemize, separator, version, logger
from phonemizer.backend import (
    EspeakBackend, FestivalBackend, SegmentsBackend)


class CatchExceptions(object):  # pragma: nocover
    """Decorator wrapping a function in a try/except block

    When an exception occurs, display a user friendly message on
    standard output before exiting with error code 1.

    The detected exceptions are ValueError, OSError, RuntimeError,
    AssertionError, KeyboardInterrupt and
    pkg_resources.DistributionNotFound.

    Parameters
    ----------
    function :
        The function to wrap in a try/except block

    """
    def __init__(self, function):
        self.function = function

    def __call__(self):
        """Executes the wrapped function and catch common exceptions"""
        try:
            self.function()

        except (IOError, ValueError, OSError,
                RuntimeError, AssertionError) as err:
            self.exit('fatal error: {}'.format(err))

        except pkg_resources.DistributionNotFound:
            self.exit(
                'fatal error: phonemizer package not found\n'
                'please install phonemizer on your system')

        except KeyboardInterrupt:
            self.exit('keyboard interruption, exiting')

    @staticmethod
    def exit(msg):
        """Write `msg` on stderr and exit with error code 1"""
        sys.stderr.write(msg.strip() + '\n')
        sys.exit(1)


def parse_args():
    """Argument parser for the phonemization script"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Multilingual text to phonemes converter

The 'phonemize' program allows simple phonemization of words and texts
in many language using three backends: espeak, festival and segments.

- espeak is a text-to-speech software supporting multiple languages
  and IPA (Internatinal Phonetic Alphabet) output. See
  http://espeak.sourceforge.net or
  https://github.com/espeak-ng/espeak-ng

- festival is also a text-to-speech software. Currently only American
  English is supported and festival uses a custom phoneset
  (http://www.festvox.org/bsv/c4711.html), but festival is the only
  backend supporting tokenization at the syllable
  level. See http://www.cstr.ed.ac.uk/projects/festival

- segments is a Unicode tokenizer that build a phonemization from a
  grapheme to phoneme mapping provided as a file by the user. See
  https://github.com/cldf/segments.

See the '--language' option below for details on the languages
supported by each backend.

''',
        epilog='''
   Languages supported by the festival backend are:
   {festival}

   Languages supported by the segments backend are:
   {segments}
   Instead of a language you can also provide a file specifying a
   grapheme to phoneme mapping (see the files above for exemples).

   Languages supported by the espeak backend are:
   {espeak}


Exemples:

* Phonemize a US English text with espeak

   $ echo 'hello world' | phonemize -l en-us -b espeak
   həloʊ wɜːld

* Phonemize a US English text with festival

   $ echo 'hello world' | phonemize -l en-us -b festival
   hhaxlow werld

* Phonemize a Japanese text with segments

  $ echo 'konnichiwa tsekai' | phonemize -l japanese -b segments
  konnitʃiwa t͡sekai

* Add a separator between phones

  $ echo 'hello world' | phonemize -l en-us -b festival -p '-' --strip
  hh-ax-l-ow w-er-l-d

* Phonemize some French text file using espeak

  $ phonemize -l fr-fr -b espeak text.txt -o phones.txt
        '''.format(
            festival='\n'.join(
                '\t{}\t->\t{}'.format(k, v) for k, v in
                sorted(FestivalBackend.supported_languages().items())),
            segments='\n'.join(
                '\t{}\t->\t{}'.format(k, v) for k, v in
                sorted(SegmentsBackend.supported_languages().items())),
            espeak='\n'.join(
                '\t{}\t->\t{}'.format(k, v) for k, v in
                sorted(EspeakBackend.supported_languages().items()))))

    # general arguments
    parser.add_argument(
        '--version', action='store_true',
        help='show version information and exit.')

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-v', '--verbose', action='store_true',
        help='write all log messages to stderr '
        '(displays only warnings by default).')
    group.add_argument(
        '-q', '--quiet', action='store_true',
        help='do not display any log message, even warnings.')

    parser.add_argument(
        '-j', '--njobs', type=int, metavar='<int>', default=1,
        help='number of parallel jobs, default is %(default)s.')

    # input/output arguments
    group = parser.add_argument_group('input/output')
    group.add_argument(
        'input', default=sys.stdin, nargs='?', metavar='<file>',
        help='input text file to phonemize, if not specified read from stdin.')

    group.add_argument(
        '-o', '--output', default=sys.stdout, metavar='<file>',
        help='output text file to write, if not specified write to stdout.')

    group = parser.add_argument_group('separators')
    group.add_argument(
        '-p', '--phone-separator', metavar='<str>',
        default=separator.default_separator.phone,
        help='phone separator, default is "%(default)s".')

    group.add_argument(
        '-w', '--word-separator', metavar='<str>',
        default=separator.default_separator.word,
        help='word separator, default is "%(default)s".')

    group.add_argument(
        '-s', '--syllable-separator', metavar='<str>',
        default=separator.default_separator.syllable,
        help='''syllable separator, only valid for festival backend,
        this option has no effect if espeak or segments is used.
        Default is "%(default)s".''')

    group.add_argument(
        '--strip', action='store_true',
        help='removes the end separators in phonemized tokens.')

    group = parser.add_argument_group('backends')
    group.add_argument(
        '-b', '--backend', metavar='<str>', default='espeak',
        choices=['espeak', 'festival', 'segments'],
        help="""the phonemization backend, must be 'espeak', 'festival' or
        'segments'. Default is %(default)s.""")

    group = parser.add_argument_group('specific to espeak backend')
    group.add_argument(
        '--with-stress', action='store_true',
        help='''when the option is set, the stresses on phonemes are present
        (stresses characters are ˈ'ˌ). By default stresses are removed.''')
    group.add_argument(
        '--sampa', action='store_true',
        help='''only valid for espeak-ng and NOT supported for espeak, use the
        "sampa" (Speech Assessment Methods Phonetic Alphabet) alphabet instead
        of "ipa" (International Phonetic Alphabet).''')
    group.add_argument(
        '--language-switch', default='keep-flags',
        choices=['keep-flags', 'remove-flags', 'remove-utterance'],
        help="""espeak can pronounce some words in another language (typically
        English) when phonemizing a text. This option setups the policy to use
        when such a language switch occurs. Three values are available:
        'keep-flags' (the default), 'remove-flags' or 'remove-utterance'. The
        'keep-flags' policy keeps the language switching flags, for example
        (en) or (jp), in the output. The 'remove-flags' policy removes them and
        the 'remove-utterance' policy removes the whole line of text including
        a language switch.""")

    group = parser.add_argument_group('language')
    group.add_argument(
        '-l', '--language', metavar='<str|file>', default='en-us',
        help='''the language code of the input text, see below for a list of
        supported languages. According to the language code you
        specify, the appropriate backend (segments, espeak or
        festival) will be called in background. Default is
        %(default)s.''')

    return parser.parse_args()


@CatchExceptions
def main():
    """Phonemize a text from command-line arguments"""
    args = parse_args()

    if args.version:
        print(version.version())
        return

    # configure logging according to --verbose/--quiet options
    verbosity = 'normal'
    if args.verbose:
        verbosity = 'verbose'
    elif args.quiet:
        verbosity = 'quiet'
    log = logger.get_logger(verbosity=verbosity)

    # configure input as a readable stream
    streamin = args.input
    if isinstance(streamin, str):
        streamin = codecs.open(streamin, 'r', encoding='utf8')
    log.debug('reading from %s', streamin.name)

    # configure output as a writable stream
    streamout = args.output
    if isinstance(streamout, str):
        streamout = codecs.open(streamout, 'w', 'utf8')
    log.debug('writing to %s', streamout.name)

    # configure the separator for phonemes, syllables and words.
    sep = separator.Separator(
        phone=args.phone_separator,
        syllable=args.syllable_separator,
        word=args.word_separator)
    log.debug('separator is %s', sep)

    # load the input text (python2 optionnally needs an extra decode)
    text = streamin.read()
    try:
        text = text.decode('utf8')
    except (AttributeError, UnicodeEncodeError):
        pass

    # phonemize the input text
    out = phonemize.phonemize(
        text,
        language=args.language,
        backend=args.backend,
        separator=sep,
        strip=args.strip,
        with_stress=args.with_stress,
        use_sampa=args.sampa,
        language_switch=args.language_switch,
        njobs=args.njobs,
        logger=log)

    if len(out):
        streamout.write(out + '\n')


if __name__ == '__main__':  # pragma: nocover
    main()
