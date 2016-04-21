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
import os
import pkg_resources
import shlex
import subprocess
import tempfile

import lispy


Separator = collections.namedtuple('Separator', ['word', 'syllable', 'phone'])
"""A named tuple of word, syllable and phone separators"""


class Phonemizer(object):
    """Phonemization of English text with festival

    This class is a wrapper on festival, a text to speech program,
    allowing simple phonemization of some English text.

    The US phoneset we use is the default one in festival, as
    described at http://www.festvox.org/bsv/c4711.html

    Arguments
    ---------

    script (str): the festival script to be executed on input text. By
      default use Phonemizer.default_script().

    logger (logging.Logger): the logging instance where to send
      messages. If not specified, don't log any messages.

    Attributes
    ----------

    separator (Separator): the namedtuple specifying token separation
      strings at 3 levels: word, syllable and phone. Default is
      Phonemizer.default_separator.

    strip_separator (bool): if True, remove the end separator of
      phonemized tokens. Default is False.

    Methods
    -------

    The central method of the Phonemizer is phonemize(text), which
    output that input text in a US English phonologized form.

    Exceptions
    ----------

    Instanciate this class with no 'festival' in your PATH raises a
    RuntimeError

    Parsing a ill-formed Scheme expression during post-processing
    (typically with unbalanced parenthesis) raises an IndexError

    """

    default_separator = Separator(' ', '|', '-')

    def __init__(self, script=None, logger=None):
        # first ensure festival is installed
        if not self.festival_is_here():
            raise RuntimeError('festival not installed on your system')

        self.separator = self.default_separator
        self.strip_separator = False

        self._log = logger
        self._script = self.default_script() if script is None else script

        if self._log:
            self._log.debug('loading {}'.format(self._script))

    @staticmethod
    def _double_quoted(line):
        """Return the string `line` surrounded by double quotes"""
        return '"' + line + '"'

    @staticmethod
    def _cleaned(line):
        """Remove 'forbidden' characters from the line"""
        return line.replace('"', "'").replace('(', '').replace(')', '')

    def _preprocess(self, text):
        """Returns the contents of `text` formatted for festival input

        This function adds double quotes to begining and end of each
        line in text, if not already presents. The returned result is
        a multiline string. Empty lines in inputs are ignored.

        """
        return '\n'.join(
            [self._double_quoted(self._cleaned(line))
             for line in text.split('\n') if line != ''])

    def _process(self, text):
        """Return the raw phonemization of `text`

        This function delegates to festival the text analysis and
        syllabic structure extraction.

        Return a string containing the "SylStructure" relation tree of
        the text, as a scheme expression.

        """
        try:
            with tempfile.NamedTemporaryFile('w+', delete=False) as data:
                # save the text as a tempfile
                data.write(text)
                data.close()

                # the Scheme script to be send to festival
                scm_script = open(self._script, 'r').read().format(data.name)

            with tempfile.NamedTemporaryFile('w+', delete=False) as scm:
                scm.write(scm_script)
                scm.close()

            cmd = 'festival -b {}'.format(scm.name)
            if self._log:
                self._log.debug('running %s', cmd)

            # festival seems to use latin1 and not utf8, moreover it
            # may print on stderr that are redirected to
            # /dev/null. Messages are something like: "UniSyn: using
            # default diphone ax-ax for y-pau". This is related to
            # wave synthesis (done by festival during phonemization).
            return subprocess.check_output(
                shlex.split(cmd),
                stderr=open(os.devnull, 'w')).decode('latin1')
        finally:
            for tmp in (data, scm):
                os.remove(tmp.name)

    def _postprocess_syll(self, syll):
        """Parse a syllable from festival to phonemized output"""
        sep = self.separator.phone
        out = (phone[0][0].replace('"', '') for phone in syll[1:])
        out = sep.join(o for o in out if o != '')
        return out if self.strip_separator else out + sep

    def _postprocess_word(self, word):
        """Parse a word from festival to phonemized output"""
        sep = self.separator.syllable
        out = sep.join(self._postprocess_syll(syll) for syll in word[1:])
        return out if self.strip_separator else out + sep

    def _postprocess_line(self, line):
        """Parse a line from festival to phonemized output"""
        sep = self.separator.word
        out = []
        for word in lispy.parse(line):
            word = self._postprocess_word(word)
            if word != '':
                out.append(word)
        out = sep.join(out)

        return out if self.strip_separator else out + sep

    def _postprocess(self, tree):
        """Conversion from festival syllable tree to desired format"""
        return [self._postprocess_line(line)
                for line in tree.split('\n')
                if line not in ['', '(nil nil nil)']]

    @staticmethod
    def festival_is_here():
        """Return True is the festival binary is in the PATH"""
        try:
            subprocess.check_output(shlex.split('which festival'))
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def default_script():
        """Return the default festival script from abkhazia share directory"""
        return pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('phonemizer'),
            'phonemizer/share/phonemize.scm')

    def phonemize(self, text):
        """Return a phonemized version of a text

        `text` is a string to be phonologized, can be multiline. Any
        empty line will be ignored. Any opening and closing
        parenthesis are removed, as they interfer with the Scheme
        expression syntax. Moreover double quotes are replaced by
        simple quotes because double quotes denotes utterances
        boundaries in festival.

        The returned result is a multiline string as well.

        """
        a = self._preprocess(text)
        b = self._process(a)
        c = self._postprocess(b)
        return '\n'.join(line for line in c if line.strip() != '')
