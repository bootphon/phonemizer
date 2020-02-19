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
import os
import re
import shlex
import subprocess
import tempfile

from phonemizer.backend.base import BaseBackend
from phonemizer.logger import get_logger


# a regular expression to find language switching flags in espeak output,
# Switches have the following form (here a switch from English to French):
# "something (fr) quelque chose (en) another thing".
_ESPEAK_FLAGS_RE = re.compile(r'\(.+?\)')


class EspeakBackend(BaseBackend):
    """Espeak backend for the phonemizer"""

    espeak_version_re = r'.*: ([0-9]+\.[0-9]+\.[0-9]+)'

    def __init__(self, language, use_sampa=False,
                 language_switch='keep-flags', with_stress=False,
                 logger=get_logger()):
        super(self.__class__, self).__init__(language, logger=logger)

        # adapt some command line option to the espeak version (for
        # phoneme separation and IPA output)
        version = self.version()

        self.sep = '--sep=_'
        if version == '1.48.03' or int(version.split('.')[1]) <= 47:
            self.sep = ''  # pragma: nocover

        self.ipa = '--ipa=3'
        if self.is_espeak_ng():  # this is espeak-ng
            self.ipa = '-x --ipa'

        self._with_stress = with_stress
        if use_sampa is True:
            if not self.is_espeak_ng():
                raise RuntimeError(  # pragma: nocover
                    'sampa alphabet is only supported by espeak-ng backend, '
                    'please install it instead of espeak')
            self.ipa = '-x --pho'

        # ensure the lang_switch argument is valid
        valid_lang_switch = [
            'keep-flags', 'remove-flags', 'remove-utterance']
        if language_switch not in valid_lang_switch:
            raise RuntimeError(
                'lang_switch argument "{}" invalid, must be in {}'
                .format(language_switch, ", ".join(valid_lang_switch)))
        self._lang_switch = language_switch
        self._lang_switch_list = []

    @staticmethod
    def name():
        return 'espeak'

    @staticmethod
    def espeak_exe():
        espeak = distutils.spawn.find_executable('espeak-ng')
        if not espeak:  # pragma: nocover
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

    def _process_lang_switch(self, n, utt):
        # look for language swith in the current utterance
        flags = re.findall(_ESPEAK_FLAGS_RE, utt)

        # no language switch, nothing to do
        if not flags:
            return utt

        # language switch detected, register the line number
        self._lang_switch_list.append(n)

        # ignore the language switch but warn if one is found
        if self._lang_switch == 'keep-flags':
            return utt

        elif self._lang_switch == 'remove-flags':
            # remove all the (lang) flags in the current utterance
            for flag in set(flags):
                utt = utt.replace(flag, '')

        else:  # self._lang_switch == 'remove-utterances':
            # drop the entire utterance
            return None

        return utt

    def _phonemize_aux(self, text, separator, strip):
        output = []
        for n, line in enumerate(text.split('\n'), start=1):
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
                    line = self._process_lang_switch(n, line)
                    if not line:
                        continue

                    out_line = ''
                    for word in line.split(u' '):
                        w = word.strip()

                        # remove the stresses on phonemes
                        if not self._with_stress:
                            w = w.replace(u"ˈ", u'')
                            w = w.replace(u'ˌ', u'')
                            w = w.replace(u"'", u'')

                        if not strip:
                            w += '_'
                        w = w.replace('_', separator.phone)
                        out_line += w + separator.word

                    if strip:
                        out_line = out_line[:-len(separator.word)]
                    output.append(out_line)

        # warn the user on language switches fount during phonemization
        if self._lang_switch_list:
            nswitches = len(self._lang_switch_list)
            if self._lang_switch == 'remove-utterance':
                self.logger.warning(
                    'removed %s utterances containing language switches '
                    '(applying "remove-utterance" policy)', nswitches)
            else:
                self.logger.warning(
                    'fount %s utterances containing language switches '
                    'on lines %s', nswitches,
                    ', '.join(str(l) for l in self._lang_switch_list))
                self.logger.warning(
                    'extra phones may appear in the "%s" phoneset',
                    self.language)
                if self._lang_switch == "remove-flags":
                    self.logger.warning(
                        'language switch flags have been removed '
                        '(applying "remove-flags" policy)')
                else:
                    self.logger.warning(
                        'language switch flags have been kept '
                        '(applying "keep-flags" policy)')

        return output
