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
"""Implementation of punctuation processing"""

import itertools
import re
from typing import List, Optional, Union, Tuple, Pattern

from phonemizer.utils import str2list
from phonemizer.separator import Separator

# The punctuation marks considered by default.
_DEFAULT_MARKS = ';:,.!?¡¿—…"«»“”(){}[]'

# Marks that are also used as a decimal separator, and so must not be treated
# as punctuation when they sit between two digits.
_DECIMAL_SEPARATORS = ',.'

# Marks that do not break an utterance: the words on both sides are
# pronounced together, as without punctuation. The other marks end an
# utterance, see Punctuation.is_inline().
#
# This list comes from the behavior of espeak-ng 1.52, observed by giving it
# texts such as "les X amis" and "from X the house" with each mark X, not
# from its documentation. The marks ;:,.!?¡¿—… end a clause, phonemized
# apart. Quotes and brackets do not: espeak only inserts a short pause, which
# blocks the French liaison (‹› do not even do that). Phonemizer goes further
# and pronounces the words around them as if the marks were not there.
_INLINE_MARKS = '"«»“”‘’„‹›()[]{}'


class Punctuation:
    """Preserve or remove the punctuation during phonemization

    Backends behave differently with punctuation: festival and espeak ignore it
    and remove it silently whereas segments will raise an error. The
    Punctuation class solves that issue by "hiding" the punctuation to the
    phonemization backend and restoring it afterwards.

    Parameters
    ----------
    marks (str or re.Pattern) : The punctuation marks to consider for processing
        (either removal or preservation). If a string, each mark must be made of
        a single character. Default to Punctuation.default_marks().

    """

    def __init__(self, marks: Union[str, Pattern] = _DEFAULT_MARKS):
        self._marks: str = None  # noqa
        self._marks_re: Pattern[str] = None  # noqa
        self.marks = marks

    @staticmethod
    def default_marks():
        """Returns the default punctuation marks as a string"""
        return _DEFAULT_MARKS

    @property
    def marks(self):
        """The punctuation marks as a string"""
        if self._marks is not None:
            return self._marks
        raise ValueError('punctuation initialized from regex, cannot access marks as a string')

    @marks.setter
    def marks(self, value: Union[str, Pattern]):
        if isinstance(value, Pattern):
            # catch the pattern surrounded by zero or more spaces on either
            # side. An empty pattern matches nothing rather than empty strings.
            self._marks_re = re.compile(
                r'((' + value.pattern + r')|\s)+' if value.pattern else r'(?!)')
            self._marks = None
        elif isinstance(value, str):
            self._marks = ''.join(set(value))

            # catching all the marks in one regular expression: zero or more spaces
            # + one or more marks + zero or more spaces.
            #
            # A mark that doubles as a decimal separator is excluded when it sits
            # between two digits, so that a decimal number reaches the backend
            # intact. Splitting "1,5" into "1" and "5" makes espeak read two
            # separate numbers ("one five" instead of "one comma five"), which
            # changes the value being spoken -- "19,99 euro" became "nineteen
            # ninety-nine euro". A separator adjacent to a non-digit, or at the
            # end of a token, is ordinary punctuation and still split as before.
            decimals = ''.join(
                m for m in self._marks if m in _DECIMAL_SEPARATORS)
            others = ''.join(
                m for m in self._marks if m not in _DECIMAL_SEPARATORS)

            alternatives = []
            if others:
                alternatives.append(f'[{re.escape(others)}]')
            if decimals:
                escaped = re.escape(decimals)
                # not preceded by a digit, or not followed by one
                alternatives.append(f'(?<![0-9])[{escaped}]')
                alternatives.append(f'[{escaped}](?![0-9])')

            # with no marks at all, match nothing rather than empty strings
            self._marks_re = re.compile(
                fr'(\s*(?:{"|".join(alternatives)})+\s*)+'
                if alternatives else r'(?!)')
        else:
            raise ValueError('punctuation marks must be defined as a string or re.Pattern')

    def remove(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """Returns the `text` with all punctuation marks replaced by spaces

        The input `text` can be a string or a list and is returned with the
        same type and punctuation removed.

        """

        def aux(text: str) -> str:
            return re.sub(self._marks_re, ' ', text).strip()

        if isinstance(text, str):
            return aux(text)
        return [aux(line) for line in text]

    def is_inline(self, mark: str) -> bool:
        """Returns True if `mark` does not break the utterance

        Quotes and brackets are inline marks: the words on both sides of them
        are pronounced together. The other marks, such as commas or periods,
        end an utterance, as do the marks not known to be inline.

        """
        mark = ''.join(mark.split())
        return bool(mark) and all(char in _INLINE_MARKS for char in mark)

    def preserve(self, text: Union[List[str], str]) \
            -> Tuple[List[str], List[List[Union[int, str]]]]:
        """Removes punctuation from `text`, allowing for further restoration

        Returns the `chunks` of text between the punctuation marks, to be
        phonemized, and, for each line of `text`, its parts in order: the
        index of a chunk in `chunks` or a punctuation mark:

            ['hello, my world!', 'ok'] -> ['hello', 'my world', 'ok'],
                [[0, ', ', 1, '!'], [2]]

        """
        chunks = []
        lines = []
        for line in str2list(text):
            parts = []
            cursor = 0
            # Cut at the matched spans. Searching for the mark text would also
            # cut a decimal point that uses the same character.
            for match in self._marks_re.finditer(line):
                if line[cursor:match.start()]:
                    parts.append(len(chunks))
                    chunks.append(line[cursor:match.start()])
                parts.append(match.group())
                cursor = match.end()
            if line[cursor:]:
                parts.append(len(chunks))
                chunks.append(line[cursor:])
            lines.append(parts)
        return chunks, lines

    def inline_groups(self, lines: List[List[Union[int, str]]]) \
            -> List[List[int]]:
        """Returns the chunks separated by inline marks only

        `lines` is as returned by preserve(). Each group lists the indices of
        consecutive chunks of a line separated by inline marks (quotes or
        brackets, see is_inline()). The backends phonemize such a group as a
        whole as well, so that its words are pronounced in context, see
        restore().

        """
        groups = []
        for parts in lines:
            group = []
            for num, part in enumerate(parts):
                if not isinstance(part, int):
                    continue
                if (group and num >= 2 and parts[num - 2] == group[-1]
                        and self.is_inline(parts[num - 1])):
                    group.append(part)
                else:
                    if len(group) > 1:
                        groups.append(group)
                    group = [part]
            if len(group) > 1:
                groups.append(group)
        return groups

    @staticmethod
    def _words(text: str, sep: Separator) -> List[str]:
        """The words of a phonemized `text`, split on the word separator"""
        return [word for word in text.split(sep.word) if word]

    @classmethod
    def _context(cls, text: List[str], group: List[int], phonemized: str,
                 sep: Separator) -> Optional[List[str]]:
        """Splits a group phonemized as a whole at its inline marks

        Returns the phonemized `group`, cut at the inline marks into one part
        per chunk, or None if the marks cannot be placed for sure.

        A backend can join words, or split a word in several ones, and so the
        number of words is not the same in input and output. Here the words
        phonemized in context must be as many as the words of each chunk
        phonemized alone, which are then known to be the same words: a mark
        is placed after the words of the chunks before it.

        """
        # the words cannot be counted when the word separator is empty or
        # found in the other separators
        if not sep.word or any(
                sep.word in other for other in (sep.phone, sep.syllable)):
            return None

        counts = [len(cls._words(text[chunk], sep)) for chunk in group]
        if not all(counts) or len(cls._words(phonemized, sep)) != sum(counts):
            return None

        # cut before the first word of each chunk but the first one
        starts = set(itertools.accumulate(counts[:-1]))
        pieces = phonemized.split(sep.word)
        cuts = [0]
        nwords = 0
        for num, piece in enumerate(pieces):
            if piece:
                if nwords in starts:
                    cuts.append(num)
                nwords += 1
        cuts.append(len(pieces))
        return [sep.word.join(pieces[start:end])
                for start, end in zip(cuts, cuts[1:])]

    @classmethod
    def restore(cls, text: Union[str, List[str]],
                lines: List[List[Union[int, str]]],
                sep: Separator,
                strip: bool,
                context: Optional[List[Tuple[List[int], str]]] = None) \
            -> List[str]:
        """Restore punctuation in a text.

        This is the reverse operation of Punctuation.preserve(). It takes the
        phonemized chunks and the parts of each line, as well as the separator
        and strip parameters used by phonemize. It returns the punctuated text
        as a list:

            ['hello', 'my world', 'ok'], [[0, ', ', 1, '!'], [2]]
                -> ['hello, my world!', 'ok']

        The internal spaces of the marks are replaced by the word separator.
        `context` optionally gives, for groups of chunks as returned by
        inline_groups(), the group phonemized as a whole. It is used in place
        of the chunks phonemized alone when the inline marks can be placed in
        it for sure.

        """
        text = str2list(text)

        # the parts of each group phonemized in context, by first chunk
        groups = {}
        for group, phonemized in context or []:
            parts = cls._context(text, group, phonemized, sep)
            if parts is not None:
                groups[group[0]] = parts

        punctuated_text = []
        for line in lines:
            punctuated = ''
            mark = None
            num = 0
            while num < len(line):
                part = line[num]
                if isinstance(part, str):
                    # remove the last word separator before the mark, and
                    # replace its internal spaces with the word separator
                    if sep.word and punctuated.endswith(sep.word):
                        punctuated = punctuated[:-len(sep.word)]
                    mark = part.replace(' ', sep.word)
                    punctuated += mark
                    num += 1
                elif part in groups:
                    # the chunks of the group, separated by its inline marks
                    for pos, chunk in enumerate(groups[part]):
                        if pos:
                            if sep.word and punctuated.endswith(sep.word):
                                punctuated = punctuated[:-len(sep.word)]
                            punctuated += line[num + 2 * pos - 1].replace(
                                ' ', sep.word)
                        punctuated += chunk
                    num += 2 * len(groups[part]) - 1
                    mark = None
                else:
                    # a chunk phonemized as nothing does not follow the mark
                    if text[part]:
                        punctuated += text[part]
                        mark = None
                    num += 1

            # a final mark is followed by a word separator, if not stripped
            if mark is not None and not strip and not mark.endswith(sep.word):
                punctuated += sep.word
            punctuated_text.append(punctuated)

        return punctuated_text
