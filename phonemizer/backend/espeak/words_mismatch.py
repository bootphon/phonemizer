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
"""Manages words count mismatches for the espeak backend"""


import abc
import re


def get_words_mismatch_processor(mode, logger):
    """Returns a word count mismatch processor according to `mode`

    The `mode` can be one of the following:
    - `ignore` to ignore words mismatches
    - `warn` to display a warning on each mismatched utterance
    - `remove` to remove any utterance containing a words mismatch

    Raises a RuntimeError if the `mode` is unknown.

    """
    processors = {
        'ignore': Ignore,
        'warn': Warn,
        'remove': Remove}

    try:
        return processors[mode](logger)
    except KeyError:
        raise RuntimeError(
            f'mode {mode} invalid, must be in {", ".join(processors.keys())}'
        ) from None


class BaseWordsMismatch(abc.ABC):
    """The base class of all word count mismatch processors"""
    _RE_SPACES = re.compile(r'\s+')

    def __init__(self, logger):
        self._logger = logger
        self._count_txt = []
        self._count_phn = []

    @classmethod
    def _count_words(cls, text):
        """Return the number of words contained in each line of `text`"""
        return [
            len([w for w in cls._RE_SPACES.split(line.strip()) if w])
            for line in text]

    def _mismatched_lines(self):
        """Returns a list of (num_line, nwords_input, nwords_output)

        Consider only the lines where nwords_input != nwords_output. Raises a
        RuntimeError if input and output do not have the same number of lines.

        """
        if len(self._count_txt) != len(self._count_phn):
            raise RuntimeError(  # pragma: nocover
                f'number of lines in input and output must be equal, '
                f'we have: input={len(self._count_txt)}, '
                f'output={len(self._count_phn)}')

        return [
            (n, t, p) for n, (t, p) in
            enumerate(zip(self._count_txt, self._count_phn))
            if t != p]

    def _resume(self, nmismatch, nlines):
        """Logs a high level undetailed warning"""
        if nmismatch:
            self._logger.warning(
                'words count mismatch on %s%% of the lines (%s/%s)',
                round(nmismatch / nlines, 2) * 100, nmismatch, nlines)

    def count_text(self, text):
        """Stores the number of words in each input line"""
        self._count_txt = self._count_words(text)

    def count_phonemized(self, text):
        """Stores the number of words in each output line"""
        self._count_phn = self._count_words(text)

    @abc.abstractmethod
    def process(self, text):
        """Detects and process word count misatches according to the mode

        This method is called at the very end of phonemization, during
        post-processing.

        """


class Ignore(BaseWordsMismatch):
    """Ignores word count mismatches"""
    def process(self, text):
        self._resume(len(self._mismatched_lines()), len(text))
        return text


class Warn(BaseWordsMismatch):
    """Warns on every mismatch detected"""
    def process(self, text):
        mismatch = self._mismatched_lines()
        for num, ntxt, nphn in mismatch:
            self._logger.warning(
                'words count mismatch on line %s '
                '(expected %s words but get %s)',
                num+1, ntxt, nphn)

        self._resume(len(mismatch), len(text))
        return text


class Remove(BaseWordsMismatch):
    """Removes any utterance containing a word count mismatch"""
    def process(self, text):
        mismatch = [line[0] for line in self._mismatched_lines()]
        self._resume(len(mismatch), len(text))
        self._logger.warning('removing the mismatched lines')

        for index in mismatch:
            text[index] = ''
        return text
