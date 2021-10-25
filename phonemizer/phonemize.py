# Copyright 2015-2021 Mathieu Bernard
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
"""Provides the phonemize function

To use it in your own code, type:

    from phonemizer import phonemize

"""

import os
import sys

from phonemizer.backend import BACKENDS
from phonemizer.logger import get_logger
from phonemizer.punctuation import Punctuation
from phonemizer.separator import default_separator
from phonemizer.utils import list2str, str2list


def _check_arguments(  # pylint: disable=too-many-arguments
        backend, with_stress, tie, separator, language_switch, words_mismatch):
    # ensure the backend is either espeak, festival or segments
    if backend not in ('espeak', 'espeak-mbrola', 'festival', 'segments'):
        raise RuntimeError(
            '{} is not a supported backend, choose in {}.'
            .format(backend, ', '.join(
                ('espeak', 'espeak-mbrola', 'festival', 'segments'))))

    # with_stress option only valid for espeak
    if with_stress and backend != 'espeak':
        raise RuntimeError(
            'the "with_stress" option is available for espeak backend only, '
            'but you are using {} backend'.format(backend))

    # tie option only valid for espeak
    if tie and backend != 'espeak':
        raise RuntimeError(
            'the "tie" option is available for espeak backend only, '
            'but you are using {} backend'.format(backend))

    # tie option incompatible with phone separator
    if tie and separator.phone:
        raise RuntimeError(
            'the "tie" option is incompatible with phone separator '
            f'(which is "{separator.phone}")')

    # language_switch option only valid for espeak
    if language_switch != 'keep-flags' and backend != 'espeak':
        raise RuntimeError(
            'the "language_switch" option is available for espeak backend '
            'only, but you are using {} backend'.format(backend))

    # words_mismatch option only valid for espeak
    if words_mismatch != 'ignore' and backend != 'espeak':
        raise RuntimeError(
            'the "words_mismatch" option is available for espeak backend '
            'only, but you are using {} backend'.format(backend))


def _phonemize(  # pylint: disable=too-many-arguments
        backend, text, separator, strip, njobs, prepend_text):
    """Does the phonemization"""
    # remember the text type for output (either list or string), force the text
    # as a list and ignore empty lines
    text_type = type(text)
    text = (line.strip(os.linesep) for line in str2list(text))
    text = [line for line in text if line.strip()]

    # phonemize the text
    phonemized = backend.phonemize(
        text, separator=separator, strip=strip, njobs=njobs)

    # at that point, the phonemized text is a list of str. Format it as
    # expected by the parameters
    if prepend_text:
        return list(zip(text, phonemized))
    if text_type == str:
        return list2str(phonemized)
    return phonemized


def phonemize(  # pylint: disable=too-many-arguments
        text,
        language='en-us',
        backend='espeak',
        separator=default_separator,
        strip=False,
        prepend_text=False,
        preserve_punctuation=False,
        punctuation_marks=Punctuation.default_marks(),
        with_stress=False,
        tie=False,
        language_switch='keep-flags',
        words_mismatch='ignore',
        njobs=1,
        logger=get_logger()):
    """Multilingual text to phonemes converter

    Return a phonemized version of an input `text`, given its
    `language` and a phonemization `backend`.

    Parameters
    ----------
    text (str or list of str): The text to be phonemized. Any empty line will
      be ignored. If `text` is an str, it can be multiline (lines being
      separated by \n). If `text` is a list, each element is considered as a
      separated line. Each line is considered as a text utterance.

    language (str): The language code of the input text, must be supported by
      the backend. If `backend` is 'segments', the language can be a file with
      a grapheme to phoneme mapping.

    backend (str, optional): The software backend to use for phonemization,
      must be 'festival' (US English only is supported, coded 'en-us'),
      'espeak', 'espeak-mbrola' or 'segments'.

    separator (Separator): string separators between phonemes, syllables and
      words, default to separator.default_separator. Syllable separator is
      considered only for the festival backend. Word separator is ignored by
      the 'espeak-mbrola' backend.

    strip (bool, optional): If True, don't output the last word and phone
      separators of a token, default to False.

    prepend_text (bool, optional): When True, returns a pair (input utterance,
      phonemized utterance) for each line of the input text. When False,
      returns only the phonemized utterances. Default to False

    preserve_punctuation (bool, optional): When True, will keep the punctuation
      in the phonemized output. Not supported by the 'espeak-mbrola' backend.
      Default to False and remove all the punctuation.

    punctuation_marks (str, optional): The punctuation marks to consider when
      dealing with punctuation, either for removal or preservation. Default to
      Punctuation.default_marks().

    with_stress (bool, optional): This option is only valid for the 'espeak'
      backend. When True the stresses on phonemes are present (stresses
      characters are ˈ'ˌ). When False stresses are removed. Default to False.

    tie (bool or char, optional): This option is only valid for the 'espeak'
      backend with espeak>=1.49. It is incompatible with phone separator. When
      not False, use a tie character within multi-letter phoneme names. When
      True, the char 'U+361' is used (as in d͡ʒ), 'z' means ZWJ character,
      default to False.

    language_switch (str, optional): Espeak can output some words in another
      language (typically English) when phonemizing a text. This option setups
      the policy to use when such a language switch occurs. Three values are
      available: 'keep-flags' (the default), 'remove-flags' or
      'remove-utterance'. The 'keep-flags' policy keeps the language switching
      flags, for example "(en) or (jp)", in the output. The 'remove-flags'
      policy removes them and the 'remove-utterance' policy removes the whole
      line of text including a language switch. This option is only valid for
      the 'espeak' backend.

    words_mismatch (str, optional): Espeak can join two consecutive words or
      drop some words, yielding a word count mismatch between orthographic and
      phonemized text. This option setups the policy to use when such a words
      count mismatch occurs. Three values are available: 'ignore' (the default)
      which do nothing, 'warn' which issue a warning for each mismatched line,
      and 'remove' which remove the mismatched lines from the output.

    njobs (int): The number of parallel jobs to launch. The input text is split
      in `njobs` parts, phonemized on parallel instances of the backend and the
      outputs are finally collapsed.

    logger (logging.Logger): the logging instance where to send messages. If
      not specified, use the default system logger.

    Returns
    -------
    phonemized text (str or list of str) : The input `text` phonemized for the
      given `language` and `backend`. The returned value has the same type of
      the input text (either a list or a string), excepted if `prepend_input`
      is True where the output is forced as a list of pairs (input_text,
      phonemized text).

    Raises
    ------
    RuntimeError if the `backend` is not valid or is valid but not installed,
      if the `language` is not supported by the `backend`, if any incompatible
      options are used.

    """
    # ensure we are using a compatible Python version
    if sys.version_info < (3, 6):  # pragma: nocover
        logger.error(
            'Your are using python-%s which is unsupported by the phonemizer, '
            'please update to python>=3.6', ".".join(sys.version_info))

    # ensure the arguments are valid
    _check_arguments(
        backend, with_stress, tie, separator, language_switch, words_mismatch)

    # preserve_punctuation and word separator not valid for espeak-mbrola
    if backend == 'espeak-mbrola' and preserve_punctuation:
        logger.warning('espeak-mbrola backend cannot preserve punctuation')
    if backend == 'espeak-mbrola' and separator.word:
        logger.warning('espeak-mbrola backend cannot preserve word separation')

    # initialize the phonemization backend
    if backend == 'espeak':
        phonemizer = BACKENDS[backend](
            language,
            punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation,
            with_stress=with_stress,
            tie=tie,
            language_switch=language_switch,
            words_mismatch=words_mismatch,
            logger=logger)
    elif backend == 'espeak-mbrola':
        phonemizer = BACKENDS[backend](
            language,
            logger=logger)
    else:  # festival or segments
        phonemizer = BACKENDS[backend](
            language,
            punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation,
            logger=logger)

    # do the phonemization
    return _phonemize(phonemizer, text, separator, strip, njobs, prepend_text)
