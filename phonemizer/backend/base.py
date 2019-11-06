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
"""Abstract class for phonemization backends"""

import abc
import itertools
import joblib
import six

from phonemizer import separator
from phonemizer.logger import get_logger


class BaseBackend(object):
    """Abstract base class of all the phonemization backends

    Provides a common interface to all backends. The central method is
    `phonemize()`

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, language, logger=get_logger()):
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

    @staticmethod
    def _str2list(s):
        """Returns the string `s` as a list of lines"""
        return s.strip().split('\n') if isinstance(s, six.string_types) else s

    @staticmethod
    def _list2str(s):
        """Returns the list of lines `s` as a single string"""
        return '\n'.join(s) if not isinstance(s, six.string_types) else s

    @classmethod
    def _chunks(cls, text, n):
        """Return `n` equally sized chunks of a `text`

        Only the n-1 first chunks have equal size. The last chunk can
        be longer. The input `text` can be a list or a string. Return
        a list of `n` strings.

        This method is usefull when phonemizing a single text on
        multiple jobs.

        """
        text = cls._str2list(text)
        size = int(max(1, len(text)/n))
        return [cls._list2str(text[i:i+size])
                for i in range(0, len(text), size)]

    @staticmethod
    @abc.abstractmethod
    def name():
        """The name of the backend"""
        pass

    @classmethod
    @abc.abstractmethod
    def is_available(cls):
        """Returns True if the backend is installed, False otherwise"""
        pass

    @staticmethod
    @abc.abstractmethod
    def version():
        """Return the backend version as a string 'major.minor.patch'"""
        pass

    @staticmethod
    @abc.abstractmethod
    def supported_languages():
        """Return a dict of language codes -> name supported by the backend"""
        pass

    def is_supported_language(self, language):
        """Returns True if `language` is supported by the backend"""
        return language in self.supported_languages()

    def phonemize(self, text, separator=separator.default_separator,
                  strip=False, njobs=1):
        """Returns the `text` phonemized for the given language"""
        if njobs == 1:
            # phonemize the text forced as a string
            out = self._phonemize_aux(self._list2str(text), separator, strip)
        else:
            # If using parallel jobs, disable the log as stderr is not
            # picklable.
            self.logger.info('running %s on %s jobs', self.name(), njobs)
            log_storage = self.logger
            self.logger = None

            # we have here a list of phonemized chunks
            out = joblib.Parallel(n_jobs=njobs)(
                joblib.delayed(self._phonemize_aux)(t, separator, strip)
                for t in self._chunks(text, njobs))

            # flatten them in a single list
            out = list(itertools.chain(*out))

            # restore the log as it was before parallel processing
            self.logger = log_storage

        # output the result formatted as a string or a list of strings
        # according to type(text)
        return (self._list2str(out)
                if isinstance(text, six.string_types) else out)

    @abc.abstractmethod
    def _phonemize_aux(self, text, separator, strip):
        pass
