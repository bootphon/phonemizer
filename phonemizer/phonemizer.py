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


class Phonemizer(object):
    """Phonologization of English text with festival

    This class is a wrapper on festival, a text to speech program,
    allowing simple phonemization of some English text.

    The US phoneset we use is described at
    http://www.festvox.org/bsv/c4711.html

    Exceptions
    ----------

    Instanciate this class with no 'festival' in your PATH raises a
    RuntimeError

    """

    default_separator = Separator(' ', '|', '-')

    def __init__(self, script=None, logger=None):
        # first ensure festival is installed
        if not self.festival_is_here():
            raise RuntimeError('festival not installed on your system')

        self.separator = self.default_separator

        self._script = self.default_script() if script is None else script
        self._log = logger

        self._log.debug(
            'loading festival script from {}'.format(self._script))

    @staticmethod
    def _double_quoted(line):
        """Return `line` surrounded by double quotes"""
        return '"' + line + '"'

    def _preprocess(self, text):
        """Returns the contents of `text` formatted for festival input

        This function adds double quotes to begining and end of each line
        in text, if not already presents. The returned result is a
        multiline string.

        """
        return '\n'.join(
            [self._double_quoted(line)
             for line in text.split('\n') if line != ''])

    def _process(self, text):
        """Return the raw phonemization of `text`

        This function delegates to festival the text analysis and
        syllabic structure extraction.

        Return a string containing the "SylStructure" relation tree of
        the text.

        """
        with tempfile.NamedTemporaryFile('w+', delete=False) as tmpdata:
            # save the text as a tempfile
            tmpdata.write(text)
            tmpdata.close()

            # the Scheme script to be send to festival
            scm_script = open(self._script, 'r').read().format(tmpdata.name)

            with tempfile.NamedTemporaryFile('w+', delete=False) as tmpscm:
                tmpscm.write(scm_script)
                tmpscm.close()
                cmd = 'festival -b ' + tmpscm.name
                self._log.debug('running %s', cmd)
                res = subprocess.check_output(shlex.split(cmd))

        os.remove(tmpdata.name)
        os.remove(tmpscm.name)

        # festival seems to use latin1 and not utf8
        return res.decode('latin1')

    def _postprocess_syll(self, syll):
        out = (phone[0][0].replace('"', '') for phone in syll[1:])
        return self.separator.phone.join(
            (o for o in out if o != ''))

    def _postprocess_word(self, word):
        return (self.separator.syllable.join(
            (self._postprocess_syll(syll) for syll in word[1:])))

    def _postprocess_line(self, line):
        return (self.separator.word.join(
            (self._postprocess_word(word) for word in lispy.parse(line))))

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
            'share/phonemize.scm')

    def phonemize(self, text):
        """Return a phonemized version of a text

        `text` is a string to be phonologized, can be multiline.

        """
        a = self._preprocess(text)
        b = self._process(a)
        return self._postprocess(b)
