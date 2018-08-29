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
"""Provides the phonemize function"""

import distutils.spawn
import itertools
import joblib

from . import festival, espeak
from .separator import default_separator


def _str2list(s):
    return s.strip().split('\n') if isinstance(s, str) else s


def _list2str(s):
    return '\n'.join(s) if not isinstance(s, str) else s


# def __call__(self, text):
#     return self._phonemize(text)
def chunks(text, n):

    """Return `n` equally sized chunks of a `text`

    Only the n-1 first chunks have equal size. The last chunk can
    be longer. The input `text` can be a list or a string. Return
    a list of `n` strings.

    """
    text = _str2list(text)
    size = int(max(1, len(text)/n))
    return [_list2str(text[i:i+size]) for i in range(0, len(text), size)]


BACKENDS = {'festival': festival,
            'espeak': espeak}
"""The backends supported by the phonemizer"""


def phonemize(text, language='hi', backend='espeak',
              separator=default_separator, strip=True,
              njobs=1, logger=None):
    """Multilingual text to phonemes converter

    Return a phonemized version of an input `text`, given its
    `language` and a phonemization `backend`.

    Arguments
    ---------

    text (str or list of str): The text to be phonemized. Any empty
       line will be ignored. If text is a list, each element is
       considered as a separated line.

    language (str): The language code of the input text, must be
      supported by the backend.

    backend (str): The software backend to use for phonemization, must
      be 'festival' (US English only is supported, coded 'en-us') or
      'espeak'.

    separator (Separator): string separators between phonemes,
      syllables and words, default to separator.default_separator.

    strip (bool): If True, don't output end of word
      separators, default to False.

    njobs (int): The number of parallel jobs to launch. The input text
      is split in `njobs` parts, phonemized on parallel instances of
      the backend and the outputs are fianally collapsed.

    logger (logging.Logger): the logging instance where to send
      messages. If not specified, don't log any messages.

    """
    # ensure the backend is either espeak or festival
    try:
        backend_module = BACKENDS[backend]
    except KeyError:
        raise RuntimeError(
            '{} is not a supported backend, choose in {}.'
            .format(', '.join(BACKENDS.keys())))

    # ensure the backend is installed on the system
    if not distutils.spawn.find_executable(backend):
        raise RuntimeError(
            '{} not installed on your system'.format(backend))

    # ensure the backend support the requested language
    if language not in backend_module.supported_languages():
        raise RuntimeError(
            'language "{}" is not supported by the {} backend'
            .format(language, backend))

    if njobs == 1:
        # phonemize the text forced as a string
        out = backend_module.phonemize(
            _list2str(text), language=language,
            separator=separator, strip=strip, logger=logger)
    else:
        # If using parallel jobs, disable the log as stderr is not
        # picklable.
        if logger:
            logger.debug(
                'running {} on {} jobs'.format(backend, njobs))
        log_storage = logger
        logger = None

        # we have here a list of phonemized chunks
        out = joblib.Parallel(n_jobs=njobs)(
            joblib.delayed(backend_module.phonemize)
            (t, language=language, separator=separator, strip=strip, logger=logger)
            for t in chunks(text, njobs))

        # flatten them in a single list
        out = list(itertools.chain(*out))

        # restore the log as it was before parallel processing
        logger = log_storage

    # output the result formatted as a string or a list of strings
    # according to type(text)
    return _list2str(out) if isinstance(text, str) else out
