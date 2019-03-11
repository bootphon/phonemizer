# coding: utf-8

# Copyright 2018 Mathieu Bernard
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
"""Phonemization backends for the phonemizer

This module implements a backend abstract base class and a specialized
class per backend (espeak, festival and segments).

"""

import abc
import codecs
import distutils
import distutils.spawn
import itertools
import logging
import os
import pkg_resources
import re
import shlex
import six
import subprocess
import tempfile

import joblib
import segments
import phonemizer.lispy as lispy
from phonemizer import separator


class BaseBackend(object):
    """Abstract base class of all the phonemization backends

    Provides a common interface to all backends. The central method is
    `phonemize()`

    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, language, logger=logging.getLogger()):
        # ensure the backend is installed on the system
        if not self.is_available():
            raise RuntimeError(
                '{} not installed on your system'.format(self.name))

        self.logger = logger
        self.logger.info(
            'initializing backend %s-%s', self.name(), self.version())

        # ensure the backend support the requested language
        if not self.is_supported_language(language):
            raise RuntimeError(
                'language "{}" is not supported by the {} backend'
                .format(language, self.name))
        self.language = language

    @staticmethod
    def _str2list(s):
        """Returns the string `s` as a list of lines"""
        return s.strip().split('\n') if isinstance(s, six.string_types) else s

    @staticmethod
    def _list2str(s):
        """Returns the list of lines `s` as a single string"""
        return '\n'.join(s) if not isinstance(s, six.string_types) else s

    @classmethod
    def _chunks(cls, text, n):
        """Return `n` equally sized chunks of a `text`

        Only the n-1 first chunks have equal size. The last chunk can
        be longer. The input `text` can be a list or a string. Return
        a list of `n` strings.

        This method is usefull when phonemizing a single text on
        multiple jobs.

        """
        text = cls._str2list(text)
        size = int(max(1, len(text)/n))
        return [cls._list2str(text[i:i+size])
                for i in range(0, len(text), size)]

    @staticmethod
    @abc.abstractmethod
    def name():
        """The name of the backend"""
        pass

    @classmethod
    @abc.abstractmethod
    def is_available(cls):
        """Returns True if the backend is installed, False otherwise"""
        pass

    @staticmethod
    @abc.abstractmethod
    def version():
        """Return the backend version as a string 'major.minor.patch'"""
        pass

    @staticmethod
    @abc.abstractmethod
    def supported_languages():
        """Return a dict of language codes -> name supported by the backend"""
        pass

    def is_supported_language(self, language):
        """Returns True if `language` is supported by the backend"""
        return language in self.supported_languages()

    def phonemize(self, text, separator=separator.default_separator,
                  strip=False, njobs=1):
        """Returns the `text` phonemized for the given language"""
        if njobs == 1:
            # phonemize the text forced as a string
            out = self._phonemize_aux(self._list2str(text), separator, strip)
        else:
            # If using parallel jobs, disable the log as stderr is not
            # picklable.
            self.logger.info('running %s on %s jobs', self.name(), njobs)
            log_storage = self.logger
            self.logger = None

            # we have here a list of phonemized chunks
            out = joblib.Parallel(n_jobs=njobs)(
                joblib.delayed(self._phonemize_aux)(t, separator, strip)
                for t in self._chunks(text, njobs))

            # flatten them in a single list
            out = list(itertools.chain(*out))

            # restore the log as it was before parallel processing
            self.logger = log_storage

        # output the result formatted as a string or a list of strings
        # according to type(text)
        return (self._list2str(out)
                if isinstance(text, six.string_types) else out)

    @abc.abstractmethod
    def _phonemize_aux(self, text, separator, strip):
        pass


class EspeakBackend(BaseBackend):
    """Espeak backend for the phonemizer"""

    espeak_version_re = r'.*: ([0-9]+\.[0-9]+\.[0-9]+)'

    def __init__(self, language, logger=logging.getLogger()):
        super(self.__class__, self).__init__(language, logger=logger)

        # adapt some command line option to the espeak version (for
        # phoneme separation and IPA output)
        version = self.version()
        self.sep = '--sep=_'
        if version == '1.48.03' or int(version.split('.')[1]) <= 47:
            self.sep = ''

        self.ipa = '--ipa=3'
        if self.is_espeak_ng():  # this is espeak-ng
            self.ipa = '-x --ipa'

    @staticmethod
    def name():
        return 'espeak'

    @staticmethod
    def is_available():
        return distutils.spawn.find_executable('espeak')

    @staticmethod
    def long_version():
        return subprocess.check_output(shlex.split(
            'espeak --help', posix=False)).decode('utf8').split('\n')[1]

    @classmethod
    def is_espeak_ng(cls):
        """Returns True if using espeak-ng, False otherwise"""
        return 'eSpeak NG' in cls.long_version()

    @staticmethod
    def version():
        # the full version version string includes extra information
        # we don't need
        long_version = EspeakBackend.long_version()

        # extract the version number with a regular expression
        return re.match(EspeakBackend.espeak_version_re, long_version).group(1)

    @staticmethod
    def supported_languages():
        # retrieve the languages from a call to 'espeak --voices'
        voices = subprocess.check_output(shlex.split(
            'espeak --voices', posix=False)).decode('utf8').split('\n')[1:-1]
        voices = [v.split() for v in voices]

        # u'å' cause a bug in python2
        return {v[1]: v[3].replace(u'_', u' ').replace(u'å', u'a')
                for v in voices}

    def _phonemize_aux(self, text, separator, strip):
        output = []
        for line in text.split('\n'):
            with tempfile.NamedTemporaryFile('w+') as data:
                # save the text as a tempfile
                try:  # python2
                    data.write(line.encode('utf8'))
                except TypeError:  # python3
                    data.write(line)
                data.seek(0)

                # generate the espeak command to run
                command = 'espeak -v{} {} -q -f {} {}'.format(
                    self.language, self.ipa, data.name, self.sep)

                if self.logger:
                    self.logger.debug('running %s', command)

                raw_output = subprocess.check_output(
                    shlex.split(command, posix=False)).decode('utf8')

                for line in (l.strip() for l in raw_output.split('\n') if l):
                    # remove the prefix/suffix in output (if any, this
                    # occurs on russian at least, output lines are
                    # surrounded by "(en)...(ru)")
                    match = re.match(r'^(.*)(.*)(.*)$', line)
                    if match:
                        line = match.group(1)

                    out_line = ''
                    for word in line.split(u' '):
                        # remove the stresses on phonemes
                        w = word.strip().replace(u"ˈ", u'').replace(u'ˌ', u'')
                        if not strip:
                            w += '_'
                        w = w.replace('_', separator.phone)
                        out_line += w + separator.word

                    if strip:
                        out_line = out_line[:-len(separator.word)]
                    output.append(out_line)

        return output


class FestivalBackend(BaseBackend):
    def __init__(self, language, logger=logging.getLogger()):
        super(self.__class__, self).__init__(language, logger=logger)

        self.script = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('phonemizer'),
            'phonemizer/share/phonemize.scm')
        self.logger.info('loaded {}'.format(self.script))

    @staticmethod
    def name():
        return 'festival'

    @staticmethod
    def is_available():
        return distutils.spawn.find_executable('festival')

    @staticmethod
    def version():
        # the full version version string includes extra information
        # we don't need
        long_version = subprocess.check_output(
            ['festival', '--version']).decode('latin1').strip()

        # extract the version number with a regular expression
        festival_version_re = r'.* ([0-9\.]+[0-9]):'
        return re.match(festival_version_re, long_version).group(1)

    @staticmethod
    def supported_languages():
        return {'en-us': 'english-us'}

    def _phonemize_aux(self, text, separator, strip):
        """Return a phonemized version of `text` with festival

        This function is a wrapper on festival, a text to speech
        program, allowing simple phonemization of some English
        text. The US phoneset we use is the default one in festival,
        as described at http://www.festvox.org/bsv/c4711.html

        Any opening and closing parenthesis in `text` are removed, as
        they interfer with the Scheme expression syntax. Moreover
        double quotes are replaced by simple quotes because double
        quotes denotes utterances boundaries in festival.

        Parsing a ill-formed Scheme expression during post-processing
        (typically with unbalanced parenthesis) raises an IndexError.

        """
        a = self._preprocess(text)
        if len(a) == 0:
            return []
        b = self._process(a)
        c = self._postprocess(b, separator, strip)

        return [line for line in c if line.strip() != '']

    @staticmethod
    def _double_quoted(line):
        """Return the string `line` surrounded by double quotes"""
        return '"' + line + '"'

    @staticmethod
    def _cleaned(line):
        """Remove 'forbidden' characters from the line"""
        # special case (very unlikely but causes a crash in festival)
        # where a line is only made of '
        if set(line) == set("'"):
            line = ''

        # remove forbidden characters (reserved for scheme, ie festival
        # scripting language)
        return line.replace('"', '').replace('(', '').replace(')', '').strip()

    @classmethod
    def _preprocess(cls, text):
        """Returns the contents of `text` formatted for festival input

        This function adds double quotes to begining and end of each
        line in text, if not already presents. The returned result is
        a multiline string. Empty lines in inputs are ignored.

        """
        cleaned_text = (
            cls._cleaned(line) for line in text.split('\n') if line != '')

        return '\n'.join(
            cls._double_quoted(line) for line in cleaned_text if line != '')

    def _process(self, text):
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
            scm_script = open(self.script, 'r').read().format(data.name)

            with tempfile.NamedTemporaryFile('w+') as scm:
                scm.write(scm_script)
                scm.seek(0)

                cmd = 'festival -b {}'.format(scm.name)
                if self.logger:
                    self.logger.debug('running %s', cmd)

                # redirect stderr to a tempfile and displaying it only
                # on errors. Messages are something like: "UniSyn: using
                # default diphone ax-ax for y-pau". This is related to
                # wave synthesis (done by festival during phonemization).
                with tempfile.TemporaryFile('w+') as fstderr:
                    try:
                        raw_output = subprocess.check_output(
                            shlex.split(cmd, posix=False), stderr=fstderr)

                        # festival seems to use latin1 and not utf8
                        return re.sub(' +', ' ', raw_output.decode('latin1'))

                    except subprocess.CalledProcessError as err:
                        fstderr.seek(0)
                        raise RuntimeError(
                            'Command "{}" returned exit status {}, '
                            'output is:\n{}'
                            .format(cmd, err.returncode, fstderr.read()))

    @staticmethod
    def _postprocess_syll(syll, separator, strip):
        """Parse a syllable from festival to phonemized output"""
        sep = separator.phone
        out = (phone[0][0].replace('"', '') for phone in syll[1:])
        out = sep.join(o for o in out if o != '')
        return out if strip else out + sep

    @classmethod
    def _postprocess_word(cls, word, separator, strip):
        """Parse a word from festival to phonemized output"""
        sep = separator.syllable
        out = sep.join(
            cls._postprocess_syll(syll, separator, strip)
            for syll in word[1:])
        return out if strip else out + sep

    @classmethod
    def _postprocess_line(cls, line, separator, strip):
        """Parse a line from festival to phonemized output"""
        sep = separator.word
        out = []
        for word in lispy.parse(line):
            word = cls._postprocess_word(word, separator, strip)
            if word != '':
                out.append(word)
        out = sep.join(out)

        return out if strip else out + sep

    @classmethod
    def _postprocess(cls, tree, separator, strip):
        """Conversion from festival syllable tree to desired format"""
        return [cls._postprocess_line(line, separator, strip)
                for line in tree.split('\n')
                if line not in ['', '(nil nil nil)']]


class SegmentsBackend(BaseBackend):
    """Segments backends for the phonemizer

    The phonemize method will raise a ValueError when parsing an
    unknown morpheme.

    """
    def __init__(self, language, logger=logging.getLogger()):
        self.logger = logger
        self.logger.info(
            'initializing backend %s-%s', self.name(), self.version())

        profile = self._load_g2p_profile(language)
        self.tokenizer = segments.Tokenizer(profile=profile)

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
        # directory phonemizer/share
        directory = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('phonemizer'),
            'phonemizer/share')

        # supported languages are files with the 'g2p' extension
        return {f.split('.')[0]: os.path.join(directory, f)
                for f in os.listdir(directory) if f.endswith('g2p')}

    def is_supported_language(self, language):
        if os.path.isfile(language):
            try:
                self._load_g2p_profile(language)
                return True
            except RuntimeError:
                return False
        return language in self.supported_languages().keys()

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

        # load the mapping graphem -> phonem from the file, make sure all
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
