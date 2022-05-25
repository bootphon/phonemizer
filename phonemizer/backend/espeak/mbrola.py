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
from typing import Union, Optional, List, Dict

from phonemizer.backend.espeak.base import BaseEspeakBackend
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
class FoldingRule:
    mode: int
    espeak_ph1: str
    espeak_ph2: Optional[Union[int, str]]
    mbrola_ph1: str
    mbrola_ph2: Optional[str] = None

    def matches(self) -> int: # returns a matching score
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


class EspeakMbrolaNoSynthBackend(BaseEspeakBackend):
    MBROLA_FOLDINGS_FOLDER = Path(__file__).parent / "mbrola-foldings"
