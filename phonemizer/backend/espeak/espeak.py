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
"""Espeak backend for the phonemizer"""

import itertools
import re
from logging import Logger
from typing import Optional, Tuple, List, Union, Pattern

from phonemizer.backend.espeak.base import BaseEspeakBackend
from phonemizer.backend.espeak.language_switch import (
    get_language_switch_processor, LanguageSwitch, BaseLanguageSwitch)
from phonemizer.backend.espeak.words_mismatch import (
    get_words_mismatch_processor, WordMismatch, BaseWordsMismatch)
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from phonemizer.separator import Separator


class EspeakBackend(BaseEspeakBackend):
    """Espeak backend for the phonemizer"""
    # the phonemes stresses in espeak output, removed with str.translate()
    _ESPEAK_STRESS = str.maketrans('', '', "ˈˌ'-")

    # repeated phone separators in espeak output
    _ESPEAK_UNDERSCORES_RE = re.compile(r'_+')

    # pylint: disable=too-many-arguments
    def __init__(self, language: str,
                 punctuation_marks: Optional[Union[str, Pattern]] = None,
                 preserve_punctuation: bool = False,
                 with_stress: bool = False,
                 tie: Union[bool, str] = False,
                 language_switch: LanguageSwitch = 'keep-flags',
                 words_mismatch: WordMismatch = 'ignore',
                 logger: Optional[Logger] = None):
        super().__init__(
            language, punctuation_marks=punctuation_marks,
            preserve_punctuation=preserve_punctuation, logger=logger)

        self._espeak.set_voice(self.language)
        self._with_stress = with_stress
        self._tie = self._init_tie(tie)
        self._lang_switch: BaseLanguageSwitch = get_language_switch_processor(
            language_switch, self.logger, self.language)
        self._words_mismatch: BaseWordsMismatch = get_words_mismatch_processor(
            words_mismatch, self.logger)

    @staticmethod
    def _init_tie(tie) -> Optional[str]:
        if not tie:
            return None

        if tie is True:  # default U+361 tie character
            return '͡'

        # non default tie charcacter
        tie = str(tie)
        if len(tie) != 1:
            raise RuntimeError(
                f'explicit tie must be a single charcacter but is {tie}')
        return tie

    @staticmethod
    def name():
        return 'espeak'

    @classmethod
    def supported_languages(cls):
        return {
            voice.language: voice.name
            for voice in EspeakWrapper().available_voices()}

    def _phonemize_aux(self, text, offset, separator, strip):
        if self._tie is not None and separator.phone:
            self.logger.warning(
                'cannot use ties AND phone separation, '
                'ignoring phone separator')

        output = []
        lang_switches = []
        for num, line in enumerate(text, start=1):
            line = self._espeak.text_to_phonemes(line, self._tie)
            line, has_switch = self._postprocess_line(
                line, num, separator, strip)
            output.append(line)
            if has_switch:
                lang_switches.append(num + offset)

        return output, lang_switches

    def _postprocess_line(self, line: str, num: int,
                          separator: Separator, strip: bool) -> Tuple[str, bool]:
        # espeak can split an utterance into several lines because
        # of punctuation, here we merge the lines into a single one
        line = line.strip().replace('\n', ' ').replace('  ', ' ')

        # due to a bug in espeak-ng, some additional separators can be
        # added at the end of a word. Here a quick fix to solve that
        # issue. See https://github.com/espeak-ng/espeak-ng/issues/694
        if '__' in line:
            line = self._ESPEAK_UNDERSCORES_RE.sub('_', line)
        line = line.replace('_ ', ' ')

        line, has_switch = self._lang_switch.process(line)
        if not line:
            return '', has_switch

        # Each step runs on all the words at once, with str methods rather
        # than regular expressions, as this is called on every line.
        words = [word.strip() for word in line.split(' ')]
        if not self._with_stress:
            # remove the stresses on phonemes
            words = [word.translate(self._ESPEAK_STRESS) for word in words]
        if not strip and self._tie is None:
            words = [word + '_' for word in words]

        # NOTE a bug in espeak append ties to (en) flags so as (͡e͡n).
        # We do not correct it here.
        if self._tie is not None and self._tie != '͡':
            # replace default '͡' by the requested one
            words = [word.replace('͡', self._tie) for word in words]
        else:
            words = [word.replace('_', separator.phone) for word in words]

        out_line = separator.word.join(words)
        if not strip:
            # the last word is followed by a word separator as well
            out_line += separator.word

        return out_line, has_switch

    def _phonemize_preprocess(self, text: List[str]) -> Tuple[Union[str, List[str]], List]:
        # When preserving the punctuation, the lines are split in chunks at
        # each punctuation mark. Words are counted on the input lines, not on
        # the chunks, so that the mismatched lines are the ones processed.
        if self._preserve_punctuation:
            chunks, punctuation_marks, lines = self._punctuator.preserve_lines(
                text)
        else:
            chunks, punctuation_marks, lines = (
                self._punctuator.remove(text), [], None)

        self._words_mismatch.count_text(chunks, lines, len(text))
        return chunks, punctuation_marks

    def _phonemize_postprocess(self, phonemized, punctuation_marks, separator: Separator, strip: bool):
        text = phonemized[0]
        switches = phonemized[1]

        self._words_mismatch.count_phonemized(text, separator)
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
