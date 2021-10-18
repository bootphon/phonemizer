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
"""Abstract base class for phonemization backends"""

import abc
import itertools
import joblib
import six

from phonemizer.separator import default_separator
from phonemizer.logger import get_logger
from phonemizer.punctuation import Punctuation
from phonemizer.utils import list2str, str2list, chunks


class BaseBackend(abc.ABC):
    """Abstract base class of all the phonemization backends

    Provides a common interface to all backends. The central method is
    `phonemize()`

    Parameters
    ----------
    language (str): The language code of the input text, must be supported by
      the backend. If `backend` is 'segments', the language can be a file with
      a grapheme to phoneme mapping.

    preserve_punctuation (bool): When True, will keep the punctuation in the
      phonemized output. Not supported by the 'espeak-mbrola' backend. Default
      to False and remove all the punctuation.

    punctuation_marks (str): The punctuation marks to consider when dealing
      with punctuation, either for removal or preservation. Default to
      Punctuation.default_marks().

    logger (logging.Logger): the logging instance where to send
      messages. If not specified, use the default system logger.

    Raises
    ------
    RuntimeError if the backend is not available of if the `language` cannot be
    initialized.

    """
    def __init__(self, language,
                 punctuation_marks=Punctuation.default_marks(),
                 preserve_punctuation=False,
                 logger=get_logger()):
        # ensure the backend is installed on the system
        if not self.is_available():
            raise RuntimeError(  # pragma: nocover
                '{} not installed on your system'.format(self.name()))

        self._logger = logger
        self._logger.info(
            'initializing backend %s-%s', self.name(), self.version())

        # ensure the backend support the requested language
        self._language = self._init_language(language)

        # setup punctuation processing
        self._preserve_punctuation = preserve_punctuation
        self._punctuator = Punctuation(punctuation_marks)

    @classmethod
    def _init_language(cls, language):
        """Language initialization

        This method may be overloaded in child classes (see Segments backend)

        """
        if not cls.is_supported_language(language):
            raise RuntimeError(
                f'language "{language}" is not supported by the '
                f'{cls.name()} backend')
        return language

    @property
    def logger(self):
        """A logging.Logger instance where to send messages"""
        return self._logger

    @property
    def language(self):
        """The language code configured to be used for phonemization"""
        return self._language

    @staticmethod
    @abc.abstractmethod
    def name():
        """The name of the backend"""

    @classmethod
    @abc.abstractmethod
    def is_available(cls):
        """Returns True if the backend is installed, False otherwise"""

    @classmethod
    @abc.abstractmethod
    def version(cls):
        """Return the backend version as a tuple (major, minor, patch)"""

    @staticmethod
    @abc.abstractmethod
    def supported_languages():
        """Return a dict of language codes -> name supported by the backend"""

    @classmethod
    def is_supported_language(cls, language):
        """Returns True if `language` is supported by the backend"""
        return language in cls.supported_languages()

    def phonemize(self, text, separator=default_separator,
                  strip=False, njobs=1):
        """Returns the `text` phonemized for the given language

        Parameters
        ----------
        text (str or list of str): The text to be phonemized. Any empty line
          will be ignored. If `text` is an str, it can be multiline (lines
          being separated by \n). If `text` is a list, each element is
          considered as a separated line. Each line is considered as a text
          utterance.

        separator (Separator): string separators between phonemes, syllables
          and words, default to separator.default_separator. Syllable separator
          is considered only for the festival backend. Word separator is
          ignored by the 'espeak-mbrola' backend.

        strip (bool): If True, don't output the last word and phone separators
          of a token, default to False.

        njobs (int): The number of parallel jobs to launch. The input text is
          split in `njobs` parts, phonemized on parallel instances of the
          backend and the outputs are finally collapsed.

        Returns
        -------
        phonemized text (str or list of str) : The input `text` phonemized for
          the given `language` and `backend`. The returned value has the same
          type of the input text (either a list or a string).

        Raises
        ------
        RuntimeError if something went wrong during the phonemization

        """
        text, text_type, punctuation_marks = self._phonemize_preprocess(text)

        if njobs == 1:
            # phonemize the text forced as a string
            phonemized = self._phonemize_aux(
                list2str(text), 0, separator, strip)
        else:
            # If using parallel jobs, disable the log as stderr is not
            # picklable.
            self.logger.info('running %s on %s jobs', self.name(), njobs)

            # we have here a list of phonemized chunks
            phonemized = joblib.Parallel(n_jobs=njobs)(
                joblib.delayed(self._phonemize_aux)(
                    # chunk[0] is the text, chunk[1] is the offset
                    chunk[0], chunk[1], separator, strip)
                for chunk in zip(*chunks(text, njobs)))

            # flatten them in a single list
            phonemized = self._flatten(phonemized)

        return self._phonemize_postprocess(
            phonemized, text_type, punctuation_marks)

    @staticmethod
    def _flatten(phonemized):
        """Flatten a list of lists into a single one

        From [[1, 2], [3], [4]] returns [1, 2, 3, 4]. This method is used to
        format the output as obtained using multiple jobs.

        """
        return list(itertools.chain(*phonemized))

    @abc.abstractmethod
    def _phonemize_aux(self, text, offset, separator, strip):
        """The "concrete" phonemization method

        Must be implemented in child classes. `separator` and `strip`
        parameters are as given to the phonemize() method. `text` is as
        returned by _phonemize_preprocess(). `offset` is line number of the
        first line in `text` with respect to the original text (this is only
        usefull with running on chunks in multiple jobs. When using a single
        jobs the offset is 0).

        """

    def _phonemize_preprocess(self, text):
        """Preprocess the text before phonemization

        Converts it to a list of str and removes the punctuation (keep trace of
        punctuation marks for further restoration if required)

        """
        # remember the text type for output (either list or string)
        text_type = type(text)

        # deals with punctuation: remove it and keep track of it for
        # restoration at the end if asked for
        punctuation_marks = []
        if self._preserve_punctuation:
            text, punctuation_marks = self._punctuator.preserve(text)
        else:
            text = self._punctuator.remove(text)

        return text, text_type, punctuation_marks

    def _phonemize_postprocess(self, phonemized, text_type, punctuation_marks):
        """Postprocess the raw phonemized output

        Restores the punctuation as needed and converts back the text to it's
        original type (list or str).

        """
        # restore the punctuation is asked for
        if self._preserve_punctuation:
            phonemized = self._punctuator.restore(
                phonemized, punctuation_marks)

        # remove any empty line in output
        phonemized = [line for line in phonemized if line]

        # output the result formatted as a string or a list of strings
        # according to type(text)
        return (list2str(phonemized) if text_type in six.string_types
                else str2list(phonemized))
