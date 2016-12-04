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
"""Provides the Phonemizer class"""

import collections
import itertools
import joblib
import shlex
import subprocess


def _str2list(s):
    return s.strip().split('\n') if isinstance(s, str) else s


def _list2str(s):
    return '\n'.join(s) if not isinstance(s, str) else s


Separator = collections.namedtuple('Separator', ['word', 'syllable', 'phone'])
"""A named tuple of word, syllable and phone separators"""


DEFAULT_SEPARATOR = Separator(' ', '|', '-')
"""The default separation characters for phones, syllables and words"""


class InterfacePhonemizer(object):
    """Interface that the phonemizer backends must implement

    Arguments
    ---------

    logger (logging.Logger): the logging instance where to send
      messages. If not specified, don't log any messages.

    Methods
    -------

    The central method of the Phonemizer is phonemize(text, njobs),
    which output the input text in a phonemized form. The text can be
    a (multiline) string or a list of strings. If `njobs` > 1,
    parallel runs are done of chunks of the origina text.

    Attributes
    ----------

    separator (Separator): the namedtuple specifying token separation
      strings at 3 levels: word, syllable and phone. Default is
      Phonemizer.default_separator.

    strip_separator (bool): if True, remove the end separator of
      phonemized tokens. Default is False.

    To be implemented in child classes
    ----------------------------------

      * backend: the backend software as called from command-line
        (e.g. 'festival' or 'espeak')

      * _phonemize(self, text): return a version of `text` phonemized
        with the backend software

    Exceptions
    ----------

    Instanciate this class with the backend software not installed
    raises a RuntimeError

    """
    def __init__(self, logger=None):
        # first ensure the backend is installed (espeak or festival)
        if not self.backend_is_here():
            raise RuntimeError(
                '{} not installed on your system'.format(self.backend))

        self.separator = DEFAULT_SEPARATOR
        self.strip_separator = False
        self._log = logger

    @classmethod
    def backend_is_here(cls):
        """Return True is the bakend sofware is in the PATH"""
        try:
            subprocess.check_output(shlex.split(
                'which {}'.format(cls.backend)))
            return True
        except subprocess.CalledProcessError:
            return False

    def __call__(self, text):
        return self._phonemize(text)

    @staticmethod
    def _chunks(text, n):
        """Return `n` equally sized chunks of a `text`

        Only the n-1 first chunks have equal size. The last chunk can
        be longer. The input `text` can be a list or a string. Return
        a list of `n` strings.

        """
        text = _str2list(text)
        size = int(max(1, len(text)/n))
        return [_list2str(text[i:i+size]) for i in range(0, len(text), size)]

    def phonemize(self, text, njobs=1):
        """Return a phonemized version of a text

        `text` is a string (or a list of strings) to be phonologized,
        can be multiline. Any empty line will be ignored.

        `njobs` is an int specifying the number of festival instances
        to launch. The input text is split in `njobs` parts, phonemized
        on parallel instances of festival and the output is collapsed.

        Return a string if `text` is a string, else return a list of
        strings.

        """
        if njobs == 1:
            # phonemize the text forced as a string
            out = self._phonemize(_list2str(text))
        else:
            # If using parallel jobs, disable the log as stderr is not
            # picklable.
            self._log.debug(
                'running {} on {} jobs'.format(self.backend, njobs))
            log_storage = self._log
            self._log = None

            # we have here a list of phonemized chunks
            out = joblib.Parallel(n_jobs=njobs)(
                joblib.delayed(self)(c) for c in self._chunks(text, njobs))

            # flatten them in a single list
            out = itertools.chain(*out)
            self._log = log_storage

        # output the result formatted as a string or a list of strings
        # according to type(text)
        return _list2str(out) if isinstance(text, str) else out

    #
    # To be implemented in child classes
    #

    backend = NotImplemented
    """The backed phonemization software (espeak or festival)"""

    def _phonemize(self, text):
        """Return a phonemized version of a text

        This method is called from self.phonemize, either in a mono or
        parallel context. The input `text` is a string, the returned
        value is a list of strings (the input `text` phonemized and
        split by lines).

        """
        raise NotImplementedError
