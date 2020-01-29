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
"""Segments backend for the phonemizer"""

import codecs
import os

import segments
from phonemizer.backend.base import BaseBackend
from phonemizer.logger import get_logger
from phonemizer.punctuation import Punctuation
from phonemizer.utils import get_package_resource


class SegmentsBackend(BaseBackend):
    """Segments backends for the phonemizer

    The phonemize method will raise a ValueError when parsing an
    unknown morpheme.

    """
    def __init__(self, language,
                 punctuation_marks=Punctuation.default_marks(),
                 preserve_punctuation=False,
                 logger=get_logger()):
        self.logger = logger
        self.logger.info(
            'initializing backend %s-%s', self.name(), self.version())

        # load the grapheme to phoneme mapping
        profile = self._load_g2p_profile(language)
        self.tokenizer = segments.Tokenizer(profile=profile)

        # setup punctuation processing
        self.preserve_punctuation = preserve_punctuation
        self._punctuator = Punctuation(punctuation_marks)

    @staticmethod
    def name():
        return 'segments'

    @staticmethod
    def version():
        return segments.__version__

    @staticmethod
    def is_available():
        return True

    @staticmethod
    def supported_languages():
        """Returns a dict of language: file supported by the segments backend

        The supported languages have a grapheme to phoneme conversion file
        bundled with phonemizer. Users can also use their own file as
        parameter of the phonemize() function.

        """
        # directory phonemizer/share/segments
        directory = get_package_resource('segments')

        # supported languages are files with the 'g2p' extension
        return {f.split('.')[0]: os.path.join(directory, f)
                for f in os.listdir(directory) if f.endswith('g2p')}

    @classmethod
    def is_supported_language(cls, language):
        if os.path.isfile(language):
            try:
                cls._load_g2p_profile(language)
                return True
            except RuntimeError:
                return False
        return language in cls.supported_languages().keys()

    @classmethod
    def _load_g2p_profile(cls, language):
        """Returns a segments profile from a `language`"""
        # make sure the g2p file exists
        if not os.path.isfile(language):
            try:
                language = cls.supported_languages()[language]
            except KeyError:
                raise RuntimeError(
                    'grapheme to phoneme file not found: {}'.format(language))

        # load the mapping grapheme -> phoneme from the file, make sure all
        # lines are well formatted
        g2p = {}
        for n, line in enumerate(codecs.open(language, 'r', encoding='utf8')):
            elts = line.strip().split()
            if not len(elts) == 2:
                raise RuntimeError(
                    'grapheme to phoneme file, line {} must have 2 rows '
                    'but have {}: {}'.format(n+1, len(elts), language))

            g2p[elts[0]] = elts[1]

        # build the segments profile from the g2p mapping
        return segments.Profile(
            *[{'Grapheme': k, 'mapping': v} for k, v in g2p.items()])

    def _phonemize_aux(self, text, separator, strip):
        # tokenize the input text per utterance
        phonemized = (
            self.tokenizer(line, column='mapping', errors='strict')
            for line in text.split('\n') if line)

        # the output of segments is always strip, so we need to add
        # token separation at the end when strip is False.
        if not strip:
            # add word separator at end of utterance
            phonemized = (p + ' # ' for p in phonemized)
            # add phoneme separator at end of word
            phonemized = (p.replace(' # ', '  # ') for p in phonemized)

        # replace default separators by our custom ones
        phonemized = (p.replace(' # ', '#') for p in phonemized)
        phonemized = (p.replace(' ', separator.phone) for p in phonemized)
        phonemized = (p.replace('#', separator.word) for p in phonemized)

        # return the result as a list of utterances
        return list(phonemized)
