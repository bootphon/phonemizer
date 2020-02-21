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
"""Festival backend for the phonemizer"""


import distutils
import os
import re
import shlex
import subprocess
import tempfile

import phonemizer.lispy as lispy
from phonemizer.backend.base import BaseBackend
from phonemizer.logger import get_logger
from phonemizer.punctuation import Punctuation
from phonemizer.utils import get_package_resource


# a global variable being used to overload the default festival installed on
# the system. The user can choose an alternative espeak with the method
# FestivalBackend.set_festival_path().
_FESTIVAL_DEFAULT_PATH = None


class FestivalBackend(BaseBackend):
    def __init__(self, language,
                 punctuation_marks=Punctuation.default_marks(),
                 preserve_punctuation=False,
                 logger=get_logger()):
        super(self.__class__, self).__init__(
            language, punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation, logger=logger)

        self.script = get_package_resource('festival/phonemize.scm')
        self.logger.info('loaded {}'.format(self.script))

    @staticmethod
    def name():
        return 'festival'

    @staticmethod
    def set_festival_path(fpath):
        """"""
        global _FESTIVAL_DEFAULT_PATH
        if not fpath:
            _FESTIVAL_DEFAULT_PATH = None
            return

        if not (os.path.isfile(fpath) and os.access(fpath, os.X_OK)):
            raise ValueError(
                f'{fpath} is not an executable file')

        _FESTIVAL_DEFAULT_PATH = os.path.abspath(fpath)

    @staticmethod
    def festival_path():
        if 'PHONEMIZER_FESTIVAL_PATH' in os.environ:
            festival = os.environ['PHONEMIZER_FESTIVAL_PATH']
            if not (os.path.isfile(festival) and os.access(festival, os.X_OK)):
                raise ValueError(
                    f'PHONEMIZER_FESTIVAL_PATH={festival} '
                    f'is not an executable file')
            return os.path.abspath(festival)

        if _FESTIVAL_DEFAULT_PATH:
            return _FESTIVAL_DEFAULT_PATH

        return distutils.spawn.find_executable('festival')

    @classmethod
    def is_available(cls):
        return True if cls.festival_path() else False

    @classmethod
    def version(cls):
        # the full version version string includes extra information
        # we don't need
        long_version = subprocess.check_output(
            [cls.festival_path(), '--version']).decode('latin1').strip()

        # extract the version number with a regular expression
        festival_version_re = r'.* ([0-9\.]+[0-9]):'
        try:
            return re.match(festival_version_re, long_version).group(1)
        except AttributeError:
            raise RuntimeError(
                f'cannot extract festival version from {cls.festival_path()}')

    @staticmethod
    def supported_languages():
        return {'en-us': 'english-us'}

    def _phonemize_aux(self, text, separator, strip):
        """Return a phonemized version of `text` with festival

        This function is a wrapper on festival, a text to speech
        program, allowing simple phonemization of some English
        text. The US phoneset we use is the default one in festival,
        as described at http://www.festvox.org/bsv/c4711.html

        Any opening and closing parenthesis in `text` are removed, as
        they interfer with the Scheme expression syntax. Moreover
        double quotes are replaced by simple quotes because double
        quotes denotes utterances boundaries in festival.

        Parsing a ill-formed Scheme expression during post-processing
        (typically with unbalanced parenthesis) raises an IndexError.

        """
        a = self._preprocess(text)
        if len(a) == 0:
            return []
        b = self._process(a)
        c = self._postprocess(b, separator, strip)

        return [line for line in c if line.strip() != '']

    @staticmethod
    def _double_quoted(line):
        """Return the string `line` surrounded by double quotes"""
        return '"' + line + '"'

    @staticmethod
    def _cleaned(line):
        """Remove 'forbidden' characters from the line"""
        # special case (very unlikely but causes a crash in festival)
        # where a line is only made of '
        if set(line) == set("'"):
            line = ''

        # remove forbidden characters (reserved for scheme, ie festival
        # scripting language)
        return line.replace('"', '').replace('(', '').replace(')', '').strip()

    @classmethod
    def _preprocess(cls, text):
        """Returns the contents of `text` formatted for festival input

        This function adds double quotes to begining and end of each
        line in text, if not already presents. The returned result is
        a multiline string. Empty lines in inputs are ignored.

        """
        cleaned_text = (
            cls._cleaned(line) for line in text.split('\n') if line != '')

        return '\n'.join(
            cls._double_quoted(line) for line in cleaned_text if line != '')

    def _process(self, text):
        """Return the raw phonemization of `text`

        This function delegates to festival the text analysis and
        syllabic structure extraction.

        Return a string containing the "SylStructure" relation tree of
        the text, as a scheme expression.

        """
        with tempfile.NamedTemporaryFile('w+', delete=False) as data:
            try:
                # save the text as a tempfile
                data.write(text)
                data.close()

                # the Scheme script to be send to festival
                scm_script = open(self.script, 'r').read().format(data.name)

                with tempfile.NamedTemporaryFile('w+', delete=False) as scm:
                    try:
                        scm.write(scm_script)
                        scm.close()

                        cmd = '{} -b {}'.format(self.festival_path(), scm.name)
                        if self.logger:
                            self.logger.debug('running %s', cmd)

                        # redirect stderr to a tempfile and displaying it only
                        # on errors. Messages are something like: "UniSyn:
                        # using default diphone ax-ax for y-pau". This is
                        # related to wave synthesis (done by festival during
                        # phonemization).
                        with tempfile.TemporaryFile('w+') as fstderr:
                            return self._run_festival(cmd, fstderr)
                    finally:
                        os.remove(scm.name)
            finally:
                os.remove(data.name)

    @staticmethod
    def _run_festival(cmd, fstderr):
        """Runs the festival command for phonemization

        Returns the raw phonemized output (need to be postprocesses). Raises a
        RuntimeError if festival fails.

        """
        try:
            output = subprocess.check_output(
                shlex.split(cmd, posix=False), stderr=fstderr)

            # festival seems to use latin1 and not utf8
            return re.sub(' +', ' ', output.decode('latin1'))

        except subprocess.CalledProcessError as err:  # pragma: nocover
            fstderr.seek(0)
            raise RuntimeError(
                'Command "{}" returned exit status {}, output is:\n{}'
                .format(cmd, err.returncode, fstderr.read()))

    @staticmethod
    def _postprocess_syll(syll, separator, strip):
        """Parse a syllable from festival to phonemized output"""
        sep = separator.phone
        out = (phone[0][0].replace('"', '') for phone in syll[1:])
        out = sep.join(o for o in out if o != '')
        return out if strip else out + sep

    @classmethod
    def _postprocess_word(cls, word, separator, strip):
        """Parse a word from festival to phonemized output"""
        sep = separator.syllable
        out = sep.join(
            cls._postprocess_syll(syll, separator, strip)
            for syll in word[1:])
        return out if strip else out + sep

    @classmethod
    def _postprocess_line(cls, line, separator, strip):
        """Parse a line from festival to phonemized output"""
        sep = separator.word
        out = []
        for word in lispy.parse(line):
            word = cls._postprocess_word(word, separator, strip)
            if word != '':
                out.append(word)
        out = sep.join(out)

        return out if strip else out + sep

    @classmethod
    def _postprocess(cls, tree, separator, strip):
        """Conversion from festival syllable tree to desired format"""
        return [cls._postprocess_line(line, separator, strip)
                for line in tree.split('\n')
                if line not in ['', '(nil nil nil)']]
