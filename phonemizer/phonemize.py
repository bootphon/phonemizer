# Copyright 2015-2018 Mathieu Bernard
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

import logging

from phonemizer.separator import default_separator
from phonemizer.backend import (
    EspeakBackend, FestivalBackend, SegmentsBackend)


def phonemize(text, language='en-us', backend='festival',
              separator=default_separator, strip=False,
              njobs=1, logger=logging.getLogger()):
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
      If the `backend` is not valid or is valid but not installed, if
      the `language` is not supported by the `backend`.

    """
    # ensure the backend is either espeak, festival or segments
    if backend not in ('espeak', 'festival', 'segments'):
        raise RuntimeError(
            '{} is not a supported backend, choose in {}.'
            .format(backend, ', '.join(('espeak', 'festival', 'segments'))))

    # instanciate the requested backend for the given language (raises
    # a RuntimeError if the language is not supported).
    backends = {b.name(): b for b in (
        EspeakBackend, FestivalBackend, SegmentsBackend)}
    backend = backends[backend](language, logger=logger)

    # phonemize the input text with the backend
    return backend.phonemize(
        text, separator=separator, strip=strip, njobs=njobs)
