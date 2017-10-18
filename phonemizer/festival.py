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
"""Festival phonemizer backend

This module is called from the phonemizer.phonemize function, it
should not be used directly.

"""

import os
import pkg_resources
import re
import shlex
import subprocess
import tempfile

from . import lispy
from .separator import default_separator


def supported_languages():
    """Return a dict of language codes -> names supported by festival"""
    return {'en-us': 'english-us'}


def default_script():
    """Return the default festival script from package share directory"""
    return pkg_resources.resource_filename(
        pkg_resources.Requirement.parse('phonemizer'),
        'phonemizer/share/phonemize.scm')


def festival_version():
    """Return a string describing the festival version"""
    return subprocess.check_output(
        ['festival', '--version']).decode('latin1').split(':')[2].strip()


def phonemize(text, language='en-us', separator=default_separator,
              strip=False, logger=None):
    """Return a phonemized version of `text` with festival

    This function is a wrapper on festival, a text to speech program,
    allowing simple phonemization of some English text. The US
    phoneset we use is the default one in festival, as described at
    http://www.festvox.org/bsv/c4711.html

    Any opening and closing parenthesis in `text` are removed, as they
    interfer with the Scheme expression syntax. Moreover double quotes
    are replaced by simple quotes because double quotes denotes
    utterances boundaries in festival.

    Parsing a ill-formed Scheme expression during post-processing
    (typically with unbalanced parenthesis) raises an IndexError.

    """
    assert language in supported_languages()

    script = default_script()
    if logger:
        logger.debug('loading {}'.format(script))

    a = _preprocess(text)
    b = _process(a, script, logger)
    c = _postprocess(b, separator, strip)

    return [line for line in c if line.strip() != '']


def _double_quoted(line):
    """Return the string `line` surrounded by double quotes"""
    return '"' + line + '"'


def _cleaned(line):
    """Remove 'forbidden' characters from the line"""
    return line.replace('"', "'").replace('(', '').replace(')', '')


def _preprocess(text):
    """Returns the contents of `text` formatted for festival input

    This function adds double quotes to begining and end of each
    line in text, if not already presents. The returned result is
    a multiline string. Empty lines in inputs are ignored.

    """
    return '\n'.join(
        [_double_quoted(_cleaned(line))
         for line in text.split('\n') if line != ''])


def _process(text, script, logger):
    """Return the raw phonemization of `text`

    This function delegates to festival the text analysis and
    syllabic structure extraction.

    Return a string containing the "SylStructure" relation tree of
    the text, as a scheme expression.

    """
    with tempfile.NamedTemporaryFile('w+') as data:
        # save the text as a tempfile
        data.write(text)
        data.seek(0)

        # the Scheme script to be send to festival
        scm_script = open(script, 'r').read().format(data.name)

        with tempfile.NamedTemporaryFile('w+') as scm:
            scm.write(scm_script)
            scm.seek(0)

            cmd = 'festival -b {}'.format(scm.name)
            if logger:
                logger.debug('running %s', cmd)

            # festival seems to use latin1 and not utf8, moreover it
            # may print on stderr that are redirected to
            # /dev/null. Messages are something like: "UniSyn: using
            # default diphone ax-ax for y-pau". This is related to
            # wave synthesis (done by festival during phonemization).
            return re.sub(' +', ' ', subprocess.check_output(
                shlex.split(cmd),
                stderr=open(os.devnull, 'w')).decode('latin1'))


def _postprocess_syll(syll, separator, strip):
    """Parse a syllable from festival to phonemized output"""
    sep = separator.phone
    out = (phone[0][0].replace('"', '') for phone in syll[1:])
    out = sep.join(o for o in out if o != '')
    return out if strip else out + sep


def _postprocess_word(word, separator, strip):
    """Parse a word from festival to phonemized output"""
    sep = separator.syllable
    out = sep.join(_postprocess_syll(syll, separator, strip)
                   for syll in word[1:])
    return out if strip else out + sep


def _postprocess_line(line, separator, strip):
    """Parse a line from festival to phonemized output"""
    sep = separator.word
    out = []
    for word in lispy.parse(line):
        word = _postprocess_word(word, separator, strip)
        if word != '':
            out.append(word)
    out = sep.join(out)

    return out if strip else out + sep


def _postprocess(tree, separator, strip):
    """Conversion from festival syllable tree to desired format"""
    return [_postprocess_line(line, separator, strip)
            for line in tree.split('\n')
            if line not in ['', '(nil nil nil)']]
