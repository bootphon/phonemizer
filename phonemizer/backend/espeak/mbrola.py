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
"""Mbrola backend for the phonemizer"""
import pathlib
import re
import shutil
import sys
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import Union, Optional, List, Dict, Pattern, Tuple

from phonemizer.backend.espeak.base import BaseEspeakBackend
from phonemizer.backend.espeak.language_switch import get_language_switch_processor, BaseLanguageSwitch, LanguageSwitch
from phonemizer.backend.espeak.words_mismatch import BaseWordsMismatch, get_words_mismatch_processor, WordMismatch
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.separator import Separator


class EspeakMbrolaBackend(BaseEspeakBackend):
    """Espeak-mbrola backend for the phonemizer"""
    # this will be initialized once, at the first call to supported_languages()
    _supported_languages = None

    def __init__(self, language: str, logger: Optional[Logger] = None):
        super().__init__(language, logger=logger)
        self._espeak.set_voice(language)

    @staticmethod
    def name():
        return 'espeak-mbrola'

    @classmethod
    def is_available(cls) -> bool:
        """Mbrola backend is available for espeak>=1.49"""
        return (
                BaseEspeakBackend.is_available() and
                shutil.which('mbrola') and
                BaseEspeakBackend.is_espeak_ng())

    @classmethod
    def _all_supported_languages(cls):
        # retrieve the mbrola voices. This voices must be installed separately.
        voices = EspeakWrapper().available_voices('mbrola')
        return {voice.identifier[3:]: voice.name for voice in voices}

    @classmethod
    def _is_language_installed(cls, language: str, data_path: Union[str, Path]) \
            -> bool:
        """Returns True if the required mbrola voice is installed"""
        # this is a reimplementation of LoadMbrolaTable from espeak
        # synth_mbrola.h sources
        voice = language[3:]  # remove mb- prefix

        if pathlib.Path(data_path / 'mbrola' / voice).is_file():
            return True  # pragma: nocover

        if sys.platform != 'win32':
            candidates = [
                f'/usr/share/mbrola/{voice}',
                f'/usr/share/mbrola/{voice}/{voice}',
                f'/usr/share/mbrola/voices/{voice}']
            for candidate in candidates:
                if pathlib.Path(candidate).is_file():
                    return True

        return False

    @classmethod
    def supported_languages(cls) -> Dict[str, str]:  # pragma: nocover
        """Returns the list of installed mbrola voices"""
        if cls._supported_languages is None:
            data_path = EspeakWrapper().data_path
            cls._supported_languages = {
                k: v for k, v in cls._all_supported_languages().items()
                if cls._is_language_installed(k, data_path)}
        return cls._supported_languages

    def _phonemize_aux(self, text: List[str], offset: int,
                       separator: Separator, strip: bool) -> List[str]:
        output = []
        for num, line in enumerate(text, start=1):
            line = self._espeak.synthetize(line)
            line = self._postprocess_line(line, offset + num, separator, strip)
            output.append(line)
        return output

    def _postprocess_line(self, line: str, num: int,
                          separator: Separator, strip: bool) -> str:
        # retrieve the phonemes with the correct SAMPA alphabet (but
        # without word separation)
        phonemes = (
            phn.split('\t')[0] for phn in line.split('\n') if phn.strip())
        phonemes = separator.phone.join(pho for pho in phonemes if pho != '_')

        if not strip:
            phonemes += separator.phone

        return phonemes


@dataclass
class Phoneme:
    pho: str
    stressed: bool


class FoldingState:

    def __init__(self, words: List[List[str]]):
        pass

    @property
    def current_phoneme(self) -> Phoneme:
        pass

    @property
    def substitute_current(self, phonemes: Tuple[str]):
        pass

    @property
    def is_word_start(self) -> bool:
        pass

    @property
    def is_word_end(self) -> bool:
        pass


@dataclass
class FoldingRule:
    mode: int
    espeak_ph1: str
    espeak_ph2: Optional[Union[int, str]]
    mbrola_ph1: str
    mbrola_ph2: Optional[str] = None

    def matches(self) -> int:  # returns a matching score
        pass


class MbrolaFolding:
    COMMENTS_RE = re.compile("//.*")

    def __init__(self, path: Path, lang: str):
        self.path = path
        self.lang = lang
        self.rules = []

        with open(self.path) as mbrola_folding:
            for line in mbrola_folding:

                if line == "volume":
                    continue
                # removing comments
                line = re.sub(self.COMMENTS_RE, "", line)

                # full-comment line or empty line
                if not line:
                    continue

                row = line.split(" ")
                control_mode = int(row[0])
                espeak_ph1 = row[1]
                espeak_ph2 = None if row[2] == "NULL" else row[2]
                mbrola_ph1 = row[3]
                if len(row) == 4:
                    rule = FoldingRule(control_mode, espeak_ph1, espeak_ph2, mbrola_ph1)
                elif len(row) == 5:
                    mbrola_ph2 = row[4]
                    rule = FoldingRule(control_mode, espeak_ph1, espeak_ph2, mbrola_ph1, mbrola_ph2)

                self.rules.append(rule)

    def fold(self, phonemes: List[str]) -> List[str]:
        # TODO: use list of words instead of list of phonemes
        # TODO: investigate stressed phonemes
        # TODO: iterate over phonemes then rules to find best matching one, then use rule to fold
        pass


@dataclass
class VoiceConfig:
    name: str
    languages: List[str]
    mbrola_voice: str


class EspeakMbrolaNoSynthBackend(BaseEspeakBackend):
    MBROLA_FOLDINGS_FOLDER = Path(__file__).parent / "mbrola-foldings"
    MBROLA_VOICES_FOLDER = Path(__file__).parent / "mbrola-voices"
    voice_config_re = re.compile("([a-z]+) (.*)")

    # pylint: disable=too-many-arguments
    def __init__(self, language: str,
                 punctuation_marks: Optional[Union[str, Pattern]] = None,
                 preserve_punctuation: bool = False,
                 with_stress: bool = False,
                 language_switch: LanguageSwitch = 'keep-flags',
                 words_mismatch: WordMismatch = 'ignore',
                 logger: Optional[Logger] = None):
        super().__init__(
            language, punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation, logger=logger)

        self._espeak.set_voice(language)
        self._with_stress = with_stress
        self._lang_switch: BaseLanguageSwitch = get_language_switch_processor(
            language_switch, self.logger, self.language)
        self._words_mismatch: BaseWordsMismatch = get_words_mismatch_processor(
            words_mismatch, self.logger)

    # TODO : figure out system for voices
    #  - load voices from mbrola-voices/
    #  - get espeak voice from config file
    #  - get phoneme translation rules from config file

    @staticmethod
    def name():
        return 'espeak-mbrola'

    @classmethod
    def _parse_voice_config(cls, path: Path) -> VoiceConfig:
        config_dict = dict()
        languages = []
        with open(path) as config_file:
            for line in config_file:
                line = line.strip()
                if not line:
                    continue

                key, value = re.match(cls.voice_config_re, line).group(1, 2)
                if key == "language":
                    languages.append(value.split(" ")[0])
                else:
                    config_dict[key] = value.strip()
        languages.sort(key=lambda el: len(el), reverse=True)

        assert set(config_dict).issuperset({"mbrola", "name"})
        assert languages

        return VoiceConfig(
            name=config_dict["name"],
            languages=languages,
            mbrola_voice=config_dict["mbrola"].split(" ")[0]
        )

    @classmethod
    def list_voice_configs(cls) -> List[VoiceConfig]:
        configs = []
        for config_filepath in cls.MBROLA_VOICES_FOLDER.iterdir():
            if not config_filepath.is_file():
                continue
            configs.append(cls._parse_voice_config(config_filepath))
        return configs

    @classmethod
    def supported_languages(cls):
        espeak = {
            voice.language: voice.name
            for voice in EspeakWrapper().available_voices()}

    def _phonemize_aux(self, text, offset, separator, strip):
        output = []
        lang_switches = []
        for num, line in enumerate(text, start=1):
            line = self._espeak.text_to_phonemes(line, tie=False, ipa=False)
            line, has_switch = self._postprocess_line(
                line, num, separator, strip)
            output.append(line)
            if has_switch:
                lang_switches.append(num + offset)

        return output, lang_switches

    def _process_stress(self, word):
        # remove the stresses on phonemes
        return re.sub(self._ESPEAK_STRESS_RE, '', word)

    def _postprocess_line(self, line: str, num: int,
                          separator: Separator, strip: bool) -> Tuple[str, bool]:
        # espeak can split an utterance into several lines because
        # of punctuation, here we merge the lines into a single one
        line = line.strip().replace('\n', ' ').replace('  ', ' ')

        # due to a bug in espeak-ng, some additional separators can be
        # added at the end of a word. Here a quick fix to solve that
        # issue. See https://github.com/espeak-ng/espeak-ng/issues/694
        line = re.sub(r'_+', '_', line)
        line = re.sub(r'_ ', ' ', line)

        line, has_switch = self._lang_switch.process(line)
        if not line:
            return '', has_switch

        out_line = ''
        for word in line.split(' '):
            word = self._process_stress(word.strip())
            if not strip and self._tie is None:
                word += '_'
            word = self._process_tie(word, separator)
            out_line += word + separator.word

        if strip and separator.word:
            # erase the last word separator from the line
            out_line = out_line[:-len(separator.word)]

        return out_line, has_switch

    def _phonemize_preprocess(self, text: List[str]) -> Tuple[Union[str, List[str]], List]:
        text, punctuation_marks = super()._phonemize_preprocess(text)
        self._words_mismatch.count_text(text)
        return text, punctuation_marks

    def _phonemize_postprocess(self, phonemized, punctuation_marks, separator: Separator, strip: bool):
        text = phonemized[0]
        switches = phonemized[1]

        self._words_mismatch.count_phonemized(text)
        self._lang_switch.warning(switches)

        phonemized = super()._phonemize_postprocess(text, punctuation_marks, separator, strip)
        return self._words_mismatch.process(phonemized)

    @staticmethod
    def _flatten(phonemized) -> List:
        """Specialization of BaseBackend._flatten for the espeak backend

        From [([1, 2], ['a', 'b']), ([3],), ([4], ['c'])] to [[1, 2, 3, 4],
        ['a', 'b', 'c']].

        """
        flattened = []
        for i in range(len(phonemized[0])):
            flattened.append(
                list(itertools.chain(
                    c for chunk in phonemized for c in chunk[i])))
        return flattened
