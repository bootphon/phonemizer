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
"""Provides the phonemize function

To use it in your own code, type:

    from phonemizer.phonemize import phonemize

"""

import sys

from phonemizer.logger import get_logger
from phonemizer.separator import default_separator
from phonemizer.backend import (
    EspeakBackend, FestivalBackend, SegmentsBackend)


def phonemize(text, language='en-us', backend='festival',
              separator=default_separator, strip=False,
              with_stress=False, use_sampa=False,
              language_switch='keep-flags',
              njobs=1, logger=get_logger()):
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
      'espeak' or 'segments'.

    separator (Separator): string separators between phonemes,
      syllables and words, default to separator.default_separator.

    strip (bool): If True, don't output the last word and phone
      separators of a token, default to False.

    with_stress (bool): This option is only valid for the espeak/espeak-ng
      backend. When True the stresses on phonemes are present (stresses
      characters are ˈ'ˌ). When False stresses are removed. Default to False.

    use_sampa (bool): Use the 'sampa' phonetic alphabet (Speech Assessment
      Methods Phonetic Alphabet) instead of 'ipa' (International Phonetic
      Alphabet). This option is only valid for the 'espeak-ng' backend. Default
      to False.

    language_switch (str) : espeak can pronounce some words in another language
      (typically English) when phonemizing a text. This option setups the
      policy to use when such a language switch occurs. Three values are
      available: 'keep-flags' (the default), 'remove-flags' or
      'remove-utterance'. The 'keep-flags' policy keeps the language switching
      flags, for example (en) or (jp), in the output. The 'remove-flags' policy
      removes them and the 'remove-utterance' policy removes the whole line of
      text including a language switch.

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
    RuntimeError

      If the `backend` is not valid or is valid but not installed, if the
      `language` is not supported by the `backend`, if `use_sampa`,
      `with_stress` or `language_switch` are used but the backend is not
      'espeak-ng'.

    """
    # ensure the backend is either espeak, festival or segments
    if backend not in ('espeak', 'festival', 'segments'):
        raise RuntimeError(
            '{} is not a supported backend, choose in {}.'
            .format(backend, ', '.join(('espeak', 'festival', 'segments'))))

    # ensure the phonetic alphabet is valid
    if use_sampa is True:
        if backend == 'espeak' and not EspeakBackend.is_espeak_ng():
            raise RuntimeError(  # pragma: nocover
                'sampa alphabet is not supported by espeak, '
                'please install espeak-ng')
        if backend != 'espeak':
            raise RuntimeError(
                'sampa alphabet is only supported by espeak backend')

    # with_stress option only valid for espeak
    if with_stress and backend != 'espeak':
        raise RuntimeError(
            'the "with_stress" option is available for espeak backend only, '
            'but you are using {} backend'.format(backend))

    # language_switch option only valid for espeak
    if language_switch != 'keep-flags' and backend != 'espeak':
        raise RuntimeError(
            'the "language_switch" option is available for espeak backend '
            'only, but you are using {} backend'.format(backend))

    # python2 needs additional utf8 encoding
    if sys.version_info[0] == 2:  # pragma: nocover
        logger.warning(
            'Your are using python2 but unsupported by the phonemizer, '
            'please update to python3')

    # instanciate the requested backend for the given language (raises
    # a RuntimeError if the language is not supported).
    backends = {b.name(): b for b in (
        EspeakBackend, FestivalBackend, SegmentsBackend)}

    if backend == 'espeak':
        phonemizer = backends[backend](
            language,
            with_stress=with_stress,
            use_sampa=use_sampa,
            language_switch=language_switch,
            logger=logger)
    else:
        phonemizer = backends[backend](language, logger=logger)

    # phonemize the input text with the backend
    return phonemizer.phonemize(
        text, separator=separator, strip=strip, njobs=njobs)
