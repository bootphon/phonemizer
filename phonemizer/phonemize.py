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
"""Provides the phonemize function

To use it in your own code, type:

    from phonemizer.phonemize import phonemize

"""

import sys

from phonemizer.logger import get_logger
from phonemizer.separator import default_separator
from phonemizer.backend import (
    EspeakBackend, EspeakMbrolaBackend, FestivalBackend, SegmentsBackend)
from phonemizer.punctuation import Punctuation


def phonemize(
        text,
        language='en-us',
        backend='festival',
        separator=default_separator,
        strip=False,
        preserve_punctuation=False,
        punctuation_marks=Punctuation.default_marks(),
        with_stress=False,
        language_switch='keep-flags',
        njobs=1,
        logger=get_logger()):
    """Multilingual text to phonemes converter

    Return a phonemized version of an input `text`, given its
    `language` and a phonemization `backend`.

    Parameters
    ----------
    text (str or list of str): The text to be phonemized. Any empty
       line will be ignored. If `text` is an str, it can be multiline
       (lines being separated by \n). If `text` is a list, each
       element is considered as a separated line. Each line is
       considered as a text utterance.

    language (str): The language code of the input text, must be
      supported by the backend. If `backend` is 'segments', the
      language can be a file with a grapheme to phoneme mapping.

    backend (str): The software backend to use for phonemization, must
      be 'festival' (US English only is supported, coded 'en-us'),
      'espeak', 'espeak-mbrola' or 'segments'.

    separator (Separator): string separators between phonemes, syllables and
      words, default to separator.default_separator. Syllable separator is
      considered only for the festival backend. Word separator is ignored by
      the 'espeak-mbrola' backend.

    strip (bool): If True, don't output the last word and phone
      separators of a token, default to False.

    preserve_punctuation (bool): When True, will keep the punctuation in the
        phonemized output. Not supportyed by the 'espeak-mbrola' backend.
        Default to False and remove all the punctuation.

    punctuation_marks (str): The punctuation marks to consider when dealing
        with punctuation. Default to Punctuation.default_marks().

    with_stress (bool): This option is only valid for the 'espeak' backend.
      When True the stresses on phonemes are present (stresses characters are
      ˈ'ˌ). When False stresses are removed. Default to False.

    language_switch (str): Espeak can output some words in another language
      (typically English) when phonemizing a text. This option setups the
      policy to use when such a language switch occurs. Three values are
      available: 'keep-flags' (the default), 'remove-flags' or
      'remove-utterance'. The 'keep-flags' policy keeps the language switching
      flags, for example (en) or (jp), in the output. The 'remove-flags' policy
      removes them and the 'remove-utterance' policy removes the whole line of
      text including a language switch. This option is only valid for the
      'espeak' backend.

    njobs (int): The number of parallel jobs to launch. The input text
      is split in `njobs` parts, phonemized on parallel instances of
      the backend and the outputs are finally collapsed.

    logger (logging.Logger): the logging instance where to send
      messages. If not specified, use the default system logger.

    Returns
    -------
    phonemized text (str or list of str) : The input `text` phonemized
      for the given `language` and `backend`. The returned value has
      the same type of the input text (either a list or a string).

    Raises
    ------
    RuntimeError if the `backend` is not valid or is valid but not installed,
      if the `language` is not supported by the `backend`, if with_stress` or
      `language_switch` are used but the backend is not 'espeak'.

    """
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

    # language_switch option only valid for espeak
    if (
            language_switch != 'keep-flags'
            and backend not in ('espeak', 'espeak-mbrola')
    ):
        raise RuntimeError(
            'the "language_switch" option is available for espeak backend '
            'only, but you are using {} backend'.format(backend))

    # preserve_punctuation and word separator not valid for espeak-mbrola
    if backend == 'espeak-mbrola' and preserve_punctuation:
        logger.warning('espeak-mbrola backend cannot preserve punctuation')
    if backend == 'espeak-mbrola' and separator.word:
        logger.warning('espeak-mbrola backend cannot preserve word separation')

    # python2 needs additional utf8 encoding
    if sys.version_info[0] == 2:  # pragma: nocover
        logger.warning(
            'Your are using python2 but unsupported by the phonemizer, '
            'please update to python>=3.6')

    # instanciate the requested backend for the given language (raises
    # a RuntimeError if the language is not supported).
    backends = {b.name(): b for b in (
        EspeakBackend, FestivalBackend, SegmentsBackend, EspeakMbrolaBackend)}

    if backend == 'espeak':
        phonemizer = backends[backend](
            language,
            punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation,
            with_stress=with_stress,
            language_switch=language_switch,
            logger=logger)
    elif backend == 'espeak-mbrola':
        phonemizer = backends[backend](
            language,
            logger=logger)
    else:  # festival or segments
        phonemizer = backends[backend](
            language,
            punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation,
            logger=logger)

    # phonemize the input text
    return phonemizer.phonemize(
        text, separator=separator, strip=strip, njobs=njobs)
