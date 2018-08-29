# coding: utf-8

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
"""ESpeak phonemizer backend

This module is called from the phonemizer.phonemize function, it
should not be used directly.

"""

import re
import shlex
import subprocess
import tempfile

from .separator import default_separator


def espeak_version():
    """Return the version of espeak as a string"""
    return subprocess.check_output(
        shlex.split('espeak --help')).decode('utf8').split('\n')[1]


def espeak_version_short():
    """Return the short version (numbers only) of espeak as a string"""
    return re.search(r'([0-9]+\.[0-9]+\.[0-9]+)', espeak_version()).group()


def supported_languages():
    """Return a dict of language codes -> name supported by espeak"""
    # retrieve the languages from a call to 'espeak --voices'
    voices = subprocess.check_output(
        shlex.split('espeak --voices')).decode('utf8').split('\n')[1:-1]
    voices = [v.split() for v in voices]
    return {v[1]: v[3] for v in voices}


def phonemize(text, language='en-us', separator=default_separator,
              strip=False, logger=None):
    """Return a phonemized version of `text` with espeak

    As espeak don't support multiline input, we must run a separate
    espeak for each line of the `text`

    """
    assert language in supported_languages()

    # old espeak versions don't support --sep
    version = espeak_version_short()
    if logger:
        logger.debug('espeak version is: {}'.format(version))

    sep = '--sep=_'
    if version == '1.48.03' or int(version.split('.')[1]) <= 47:
        sep = ''

    ipa = '--ipa=3'
    if version == '1.49.2':  # espeak-ng
        ipa = '-x --ipa'

    output = []
    for line in text.split('\n'):
        with tempfile.NamedTemporaryFile('w+') as data:
            # save the text as a tempfile
            data.write(line)
            data.seek(0)

            # generate the espeak command to run
            command = 'espeak -v{} {} -q -f {} {}'.format(
                language, ipa, data.name, sep)

            if logger:
                logger.debug('running %s', command)

            raw_output = subprocess.check_output(
                shlex.split(command)).decode('utf8')

            for line in (l.strip() for l in raw_output.split('\n') if l):
                # remove the prefix/suffix in output (if any, this
                # occurs on russian at least, output lines are
                # surrounded by "(en)...(ru)")
                match = re.match('^\(.*\)(.*)\(.*\)$', line)
                if match:
                    line = match.group(1)

                l = ''
                for word in line.split(u' '):
                    # remove the stresses on phonemes
                    w = word.strip().strip('_').replace(u"ˈ", u'').replace(u'ˌ', u'')
                    if not strip:
                        w += '_'
                    w = w.replace('_', separator.phone)
                    l += w + separator.word

                if strip:
                    l = l[:-len(separator.word)]
                output.append(l)

    return output
