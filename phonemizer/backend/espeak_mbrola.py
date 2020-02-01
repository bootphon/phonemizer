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
"""Espeak backend for the phonemizer"""

import distutils.spawn
import os
import re
import shlex
import subprocess
import tempfile

from phonemizer.backend.base import BaseBackend
from phonemizer.logger import get_logger
from phonemizer.punctuation import Punctuation

# a regular expression to find language switching flags in espeak output,
# Switches have the following form (here a switch from English to French):
# "something (fr) quelque chose (en) another thing".
_ESPEAK_FLAGS_RE = re.compile(r'\(.+?\)')

# a global variable being used to overload the default espeak installed on the
# system. The user can choose an alternative espeak with the method
# EspeakBackend.set_espeak_path().
_ESPEAK_DEFAULT_PATH = None


class EspeakMbrolaBackend(BaseBackend):
    """Espeak-mbrola backend for the phonemizer"""

    espeak_version_re = r'.*: ([0-9]+(\.[0-9]+)+(\-dev)?)'

    def __init__(self, language,
                 punctuation_marks=Punctuation.default_marks(),
                 preserve_punctuation=False,
                 language_switch='keep-flags',
                 logger=get_logger()):
        super().__init__(
            language, punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation, logger=logger)
        self.logger.debug(f'espeak is {self.espeak_path()}')

        # adapt some command line option to the espeak version (for
        # phoneme separation and IPA output)
        version = self.version()

        # TODO : check this
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
        return 'espeak-mbrola'

    @staticmethod
    def set_espeak_path(fpath):
        """"""
        global _ESPEAK_DEFAULT_PATH
        if not fpath:
            _ESPEAK_DEFAULT_PATH = None
            return

        if not (os.path.isfile(fpath) and os.access(fpath, os.X_OK)):
            raise ValueError(
                f'{fpath} is not an executable file')

        _ESPEAK_DEFAULT_PATH = os.path.abspath(fpath)

    @staticmethod
    def espeak_path():
        if 'PHONEMIZER_ESPEAK_PATH' in os.environ:
            espeak = os.environ['PHONEMIZER_ESPEAK_PATH']
            if not (os.path.isfile(espeak) and os.access(espeak, os.X_OK)):
                raise ValueError(
                    f'PHONEMIZER_ESPEAK_PATH={espeak} '
                    f'is not an executable file')
            return os.path.abspath(espeak)

        if _ESPEAK_DEFAULT_PATH:
            return _ESPEAK_DEFAULT_PATH

        espeak = distutils.spawn.find_executable('espeak-ng')
        if not espeak:  # pragma: nocover
            espeak = distutils.spawn.find_executable('espeak')
        return espeak

    @classmethod
    def is_available(cls):
        return True if cls.espeak_path() else False

    @classmethod
    def long_version(cls):
        return subprocess.check_output(shlex.split(
            '{} --help'.format(cls.espeak_path()), posix=False)).decode(
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
        try:
            return re.match(cls.espeak_version_re, long_version).group(1)
        except AttributeError:
            raise RuntimeError(f'cannot extract espeak version from {cls.espeak_path()}')

    @classmethod
    def supported_languages(cls):
        # retrieve the voices from a call to 'espeak --voices=mb"
        voices = subprocess.check_output(shlex.split(
            f'{cls.espeak_path()} --voices=mb', posix=False)).decode(
            'utf8').split('\n')[1:-1]
        voices = [voice.split() for voice in voices]

        return {voice[4]: voice[3] for voice in voices}

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
                    command = '{} -v {} -q -f {}'.format(
                        self.espeak_path(), self.language, data.name)

                    if self.logger:
                        self.logger.debug('running %s', command)

                    pho_output = subprocess.check_output(
                        shlex.split(command, posix=False)).decode('utf8')
                finally:
                    os.remove(data.name)

                # splitting lines, then throwing away the pronunciation params
                # (duration and pitch variations)
                lines = pho_output.split("\n")
                phonemes = [line.split("\t")[0] for line in lines]

                if not phonemes:
                    continue
                # sticking all phonemes together to be compliant with the
                # expected output
                output.append("_".join(phonemes))

        return output
