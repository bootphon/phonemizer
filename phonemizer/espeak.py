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

import shlex
import subprocess


class EspeakPhonemizer():
    """Multilingual test to IPA phonemes with espeak

    This class is a wrapper on the espeak text to speech software.

    """
    def __init__(self, language, logger=None):
        # first ensure espeak is installed
        if not self.espeak_is_here():
            raise RuntimeError('espeak not installed on your system')

        self.separator = self.default_separator
        self.strip_separator = False

        self._log = logger

    @staticmethod
    def espeak_is_here():
        """Return True is the espeak binary is in the PATH"""
        try:
            subprocess.check_output(shlex.split('which espeak'))
            return True
        except subprocess.CalledProcessError:
            return False
