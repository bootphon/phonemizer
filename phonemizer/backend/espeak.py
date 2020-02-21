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

import abc
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


class BaseEspeakBackend(BaseBackend):
    """Espeak backend for the phonemizer"""

    espeak_version_re = r'.*: ([0-9]+(\.[0-9]+)+(\-dev)?)'

    @staticmethod
    def set_espeak_path(fpath):
        """Sets the espeak executable as `fpath`"""
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
        """Returns the absolute path to the espeak executable"""
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
        """Returns full version line

        Includes data path and detailed name (espeak or espeak-ng).

        """
        return subprocess.check_output(shlex.split(
            '{} --help'.format(cls.espeak_path()), posix=False)).decode(
                'utf8').split('\n')[1]

    @classmethod
    def is_espeak_ng(cls):
        """Returns True if using espeak-ng, False otherwise"""
        return 'eSpeak NG' in cls.long_version()

    @classmethod
    def version(cls, as_tuple=False):
        # the full version version string includes extra information
        # we don't need
        long_version = cls.long_version()

        # extract the version number with a regular expression
        try:
            version = re.match(cls.espeak_version_re, long_version).group(1)
        except AttributeError:
            raise RuntimeError(
                f'cannot extract espeak version from {cls.espeak_path()}')

        if as_tuple:
            # ignore the '-dev' at the end
            version = version.replace('-dev', '')
            version = tuple(int(v) for v in version.split('.'))
        return version

    @abc.abstractmethod
    def _command(self, fname):
        pass

    @abc.abstractmethod
    def _postprocess_line(self, line, num, separator, strip):
        pass

    def _phonemize_aux(self, text, separator, strip):
        output = []
        for num, line in enumerate(text.split('\n'), start=1):
            with tempfile.NamedTemporaryFile('w+', delete=False) as data:
                try:
                    # save the text as a tempfile
                    data.write(line)
                    data.close()

                    # generate the espeak command to run
                    command = self._command(data.name)
                    if self.logger:
                        self.logger.debug('running %s', command)

                    # run the command
                    completed = subprocess.run(
                        shlex.split(command, posix=False),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)

                    # retrieve the output line (raw phonemization)
                    line = completed.stdout.decode('utf8')

                    # ensure all was OK
                    error = completed.stderr.decode('utf8')
                    for err_line in error.split('\n'):  # pragma: nocover
                        err_line = err_line.strip()
                        if err_line:
                            self.logger.error(err_line)
                    if error or completed.returncode:  # pragma: nocover
                        raise RuntimeError(
                            f'espeak failed with return code '
                            f'{completed.returncode}')
                finally:
                    os.remove(data.name)

                line = self._postprocess_line(line, num, separator, strip)
                if line:
                    output.append(line)

        self._warn_on_lang_switch()
        return output

    def _process_lang_switch(self, num, utt):
        # look for language swith in the current utterance
        flags = re.findall(_ESPEAK_FLAGS_RE, utt)

        # no language switch, nothing to do
        if not flags:
            return utt

        # language switch detected, register the line number
        self._lang_switch_list.append(num)

        # ignore the language switch but warn if one is found
        if self._lang_switch == 'keep-flags':
            return utt

        if self._lang_switch == 'remove-flags':
            # remove all the (lang) flags in the current utterance
            for flag in set(flags):
                utt = utt.replace(flag, '')

        else:  # self._lang_switch == 'remove-utterances':
            # drop the entire utterance
            return None

        return utt

    def _warn_on_lang_switch(self):
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


class EspeakBackend(BaseEspeakBackend):
    """Espeak backend for the phonemizer"""
    def __init__(self, language,
                 punctuation_marks=Punctuation.default_marks(),
                 preserve_punctuation=False,
                 language_switch='keep-flags',
                 with_stress=False,
                 logger=get_logger()):
        super().__init__(
            language, punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation, logger=logger)
        self.logger.debug('espeak is %s', self.espeak_path())

        # adapt some command line option to the espeak version (for
        # phoneme separation and IPA output)
        version = self.version()

        self.sep = '--sep=_'
        if version == '1.48.03' or version.split('.')[1] <= '47':
            self.sep = ''  # pragma: nocover

        self.ipa = '--ipa=3'
        if self.is_espeak_ng():  # this is espeak-ng
            self.ipa = '-x --ipa'

        # ensure the lang_switch argument is valid
        valid_lang_switch = [
            'keep-flags', 'remove-flags', 'remove-utterance']
        if language_switch not in valid_lang_switch:
            raise RuntimeError(
                'lang_switch argument "{}" invalid, must be in {}'
                .format(language_switch, ", ".join(valid_lang_switch)))
        self._lang_switch = language_switch
        self._lang_switch_list = []

        self._with_stress = with_stress

    @staticmethod
    def name():
        return 'espeak'

    @classmethod
    def supported_languages(cls):
        # retrieve the languages from a call to 'espeak --voices'
        voices = subprocess.check_output(shlex.split(
            '{} --voices'.format(cls.espeak_path()), posix=False)).decode(
                'utf8').split('\n')[1:-1]
        voices = [v.split() for v in voices]

        return {v[1]: v[3].replace('_', ' ') for v in voices}

    def _command(self, fname):
        return (
            f'{self.espeak_path()} -v{self.language} {self.ipa} '
            f'-q -f {fname} {self.sep}')

    def _postprocess_line(self, line, num, separator, strip):
        # espeak can split an utterance into several lines because
        # of punctuation, here we merge the lines into a single one
        line = line.strip().replace('\n', ' ').replace('  ', ' ')

        # due to a bug in espeak-ng, some additional separators can be
        # added at the end of a word. Here a quick fix to solve that
        # issue. See https://github.com/espeak-ng/espeak-ng/issues/694
        line = re.sub(r'_+', '_', line)
        line = re.sub(r'_ ', ' ', line)

        line = self._process_lang_switch(num, line)
        if not line:
            return ''

        out_line = ''
        for word in line.split(u' '):
            word = word.strip()

            # remove the stresses on phonemes
            if not self._with_stress:
                word = word.replace("ˈ", '')
                word = word.replace('ˌ', '')
                word = word.replace("'", '')
                word = word.replace("-", '')

            if not strip:
                word += '_'
            word = word.replace('_', separator.phone)
            out_line += word + separator.word

        if strip and separator.word:
            out_line = out_line[:-len(separator.word)]

        return out_line


class EspeakMbrolaBackend(BaseEspeakBackend):
    """Espeak-mbrola backend for the phonemizer"""
    # this will be initialized once, at the first call to supported_languages()
    _supported_languages = None

    _lang_switch_list = []

    def __init__(self, language, logger=get_logger()):
        super().__init__(language, logger=logger)
        self.logger.debug('espeak is %s', self.espeak_path())

    @staticmethod
    def name():
        return 'espeak-mbrola'

    @staticmethod
    def is_available():
        return (
            BaseEspeakBackend.is_available() and
            distutils.spawn.find_executable('mbrola') is not None)

    @classmethod
    def _all_supported_languages(cls):
        # retrieve the voices from a call to 'espeak --voices=mb'. This voices
        # must be installed separately.
        voices = subprocess.check_output(shlex.split(
            f'{cls.espeak_path()} --voices=mb', posix=False)).decode(
                'utf8').split('\n')[1:-1]
        voices = [voice.split() for voice in voices]
        return {voice[4][3:]: voice[3] for voice in voices}

    @classmethod
    def _is_language_installed(cls, language):
        """Returns True if the required mbrola voice is installed"""
        command = f'{cls.espeak_path()} --stdin -v {language} -q --pho'
        completed = subprocess.run(
            shlex.split(command, posix=False),
            input=b'',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        if completed.stderr.decode('utf8'):
            return False
        return True

    @classmethod
    def supported_languages(cls):  # pragma: nocover
        """Returns the list of installed mbrola voices"""
        if cls._supported_languages is None:
            cls._supported_languages = {
                k: v for k, v in cls._all_supported_languages().items()
                if cls._is_language_installed(k)}
        return cls._supported_languages

    def _command(self, fname):
        return f'{self.espeak_path()} -v {self.language} -q -f {fname} --pho'

    def _postprocess_line(self, line, num, separator, strip):
        # retrieve the phonemes with the correct SAMPA alphabet (but
        # without word separation)
        phonemes = (
            l.split('\t')[0] for l in line.split('\n') if l.strip())
        phonemes = separator.phone.join(pho for pho in phonemes if pho != '_')

        if not strip:
            phonemes += separator.phone

        return phonemes
