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
"""Espeak backend for the phonemizer"""

import distutils.spawn
import logging
import os
import re
import shlex
import subprocess
import tempfile

from phonemizer.backend.base import BaseBackend


class EspeakBackend(BaseBackend):
    """Espeak backend for the phonemizer"""

    espeak_version_re = r'.*: ([0-9]+\.[0-9]+\.[0-9]+)'

    def __init__(self, language, use_sampa=False, lang_switch='ignore',
                 logger=logging.getLogger()):
        super(self.__class__, self).__init__(language, logger=logger)

        # adapt some command line option to the espeak version (for
        # phoneme separation and IPA output)
        version = self.version()

        self.sep = '--sep=_'
        if version == '1.48.03' or int(version.split('.')[1]) <= 47:
            self.sep = ''

        self.ipa = '--ipa=3'
        if self.is_espeak_ng():  # this is espeak-ng
            self.ipa = '-x --ipa'

        if use_sampa is True:
            if not self.is_espeak_ng():
                raise RuntimeError(
                    'sampa alphabet is only supported by espeak-ng backend, '
                    'please install it instead of espeak')
            self.ipa = '-x --pho'

        # ensure the lang_switch argument is valid
        valid_lang_switch = [
            'ignore', 'drop_utterance', 'drop_expression', 'unflag']
        if lang_switch not in valid_lang_switch:
            raise RuntimeError(
                f'lang_switch argument "{lang_switch}" invalid, '
                f'must be in {", ".join(valid_lang_switch)}')
        self._lang_swith = lang_switch

    @staticmethod
    def name():
        return 'espeak'

    @staticmethod
    def espeak_exe():
        espeak = distutils.spawn.find_executable('espeak-ng')
        if not espeak:
            espeak = distutils.spawn.find_executable('espeak')
        return espeak

    @classmethod
    def is_available(cls):
        return True if cls.espeak_exe() else False

    @classmethod
    def long_version(cls):
        return subprocess.check_output(shlex.split(
            '{} --help'.format(cls.espeak_exe()), posix=False)).decode(
                'utf8').split('\n')[1]

    @classmethod
    def is_espeak_ng(cls):
        """Returns True if using espeak-ng, False otherwise"""
        return 'eSpeak NG' in cls.long_version()

    @classmethod
    def version(cls):
        # the full version version string includes extra information
        # we don't need
        long_version = cls.long_version()

        # extract the version number with a regular expression
        return re.match(cls.espeak_version_re, long_version).group(1)

    @classmethod
    def supported_languages(cls):
        # retrieve the languages from a call to 'espeak --voices'
        voices = subprocess.check_output(shlex.split(
            '{} --voices'.format(cls.espeak_exe()), posix=False)).decode(
                'utf8').split('\n')[1:-1]
        voices = [v.split() for v in voices]

        # u'å' cause a bug in python2
        return {v[1]: v[3].replace(u'_', u' ').replace(u'å', u'a')
                for v in voices}

    def _process_lang_switch(self, line):
        if self._lang_swith == 'ignore':
            # ignore the language switch but warn if one is found
            # TODO register the {expression : lang} TODO at the end log warning
            return line

        elif self._lang_swith == 'unflag':
            # remove all the (lang) flags in the line
            # TODO register and log warning at the end
            flags = set(re.findall(r'\(.+?\)', line))
            for flag in flags:
                line = line.replace(flag, '')

        elif self._lang_swith == 'drop_utterance':
            # TODO register and log warning at the end
            return None

        else:  # drop_expression
            pass

    def _phonemize_aux(self, text, separator, strip):
        output = []
        for line in text.split('\n'):
            with tempfile.NamedTemporaryFile('w+', delete=False) as data:
                try:
                    # save the text as a tempfile
                    try:  # python2
                        data.write(line.encode('utf8'))
                    except TypeError:  # python3
                        data.write(line)
                    data.close()

                    # generate the espeak command to run
                    command = '{} -v{} {} -q -f {} {}'.format(
                        self.espeak_exe(), self.language, self.ipa,
                        data.name, self.sep)

                    if self.logger:
                        self.logger.debug('running %s', command)

                    raw_output = subprocess.check_output(
                        shlex.split(command, posix=False)).decode('utf8')
                finally:
                    os.remove(data.name)

                for line in (l.strip() for l in raw_output.split('\n') if l):
                    line = self._process_lang_switch(line)

                    out_line = ''
                    for word in line.split(u' '):
                        # remove the stresses on phonemes
                        w = word.strip().replace(u"ˈ", u'').replace(
                            u'ˌ', u'').replace(u"'", u'')
                        if not strip:
                            w += '_'
                        w = w.replace('_', separator.phone)
                        out_line += w + separator.word

                    if strip:
                        out_line = out_line[:-len(separator.word)]
                    output.append(out_line)

        return output
