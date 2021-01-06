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
"""Abstract class for phonemization backends"""

import abc
import itertools
import joblib
import six

from phonemizer.separator import default_separator
from phonemizer.logger import get_logger
from phonemizer.punctuation import Punctuation
from phonemizer.utils import list2str, str2list, chunks


class BaseBackend:
    """Abstract base class of all the phonemization backends

    Provides a common interface to all backends. The central method is
    `phonemize()`

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, language,
                 punctuation_marks=Punctuation.default_marks(),
                 preserve_punctuation=False,
                 logger=get_logger()):
        # ensure the backend is installed on the system
        if not self.is_available():
            raise RuntimeError(  # pragma: nocover
                '{} not installed on your system'.format(self.name()))

        self.logger = logger
        self.logger.info(
            'initializing backend %s-%s', self.name(), self.version())

        # ensure the backend support the requested language
        if not self.is_supported_language(language):
            raise RuntimeError(
                'language "{}" is not supported by the {} backend'
                .format(language, self.name()))
        self.language = language

        # setup punctuation processing
        self.preserve_punctuation = preserve_punctuation
        self._punctuator = Punctuation(punctuation_marks)

    @staticmethod
    @abc.abstractmethod
    def name():
        """The name of the backend"""

    @classmethod
    @abc.abstractmethod
    def is_available(cls):
        """Returns True if the backend is installed, False otherwise"""

    @staticmethod
    @abc.abstractmethod
    def version(as_tuple=False):
        """Return the backend version as a string 'major.minor.patch'

        If `as_tuple` is True, returns a tuple (major, minor, patch).

        """

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
        """Returns the `text` phonemized for the given language"""
        text, text_type, punctuation_marks = self._phonemize_preprocess(text)

        if njobs == 1:
            # phonemize the text forced as a string
            text = self._phonemize_aux(list2str(text), separator, strip)
        else:
            # If using parallel jobs, disable the log as stderr is not
            # picklable.
            self.logger.info('running %s on %s jobs', self.name(), njobs)
            log_storage = self.logger
            self.logger = None

            # we have here a list of phonemized chunks
            text = joblib.Parallel(n_jobs=njobs)(
                joblib.delayed(self._phonemize_aux)(t, separator, strip)
                for t in chunks(text, njobs))

            # flatten them in a single list
            text = list(itertools.chain(*text))

            # restore the log as it was before parallel processing
            self.logger = log_storage

        return self._phonemize_postprocess(text, text_type, punctuation_marks)

    @abc.abstractmethod
    def _phonemize_aux(self, text, separator, strip):
        pass

    def _phonemize_preprocess(self, text):
        # remember the text type for output (either list or string)
        text_type = type(text)

        # deals with punctuation: remove it and keep track of it for
        # restoration at the end if asked for
        punctuation_marks = []
        if self.preserve_punctuation:
            text, punctuation_marks = self._punctuator.preserve(text)
        else:
            text = self._punctuator.remove(text)

        return text, text_type, punctuation_marks

    def _phonemize_postprocess(self, text, text_type, punctuation_marks):
        # restore the punctuation is asked for
        if self.preserve_punctuation:
            text = self._punctuator.restore(text, punctuation_marks)

        # remove any empty line in output
        text = [line for line in text if line]

        # output the result formatted as a string or a list of strings
        # according to type(text)
        return (list2str(text) if text_type in six.string_types
                else str2list(text))
