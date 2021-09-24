[![Linux](https://github.com/bootphon/phonemizer/actions/workflows/linux.yaml/badge.svg?branch=master)](
https://github.com/bootphon/phonemizer/actions/workflows/linux.yaml)
[![MacOS](https://github.com/bootphon/phonemizer/actions/workflows/macos.yaml/badge.svg?branch=master)](
https://github.com/bootphon/phonemizer/actions/workflows/macos.yaml)
[![Windows](https://github.com/bootphon/phonemizer/actions/workflows/windows.yaml/badge.svg?branch=master)](
https://github.com/bootphon/phonemizer/actions/workflows/windows.yaml)
[![Codecov](https://img.shields.io/codecov/c/github/bootphon/phonemizer)](
https://codecov.io/gh/bootphon/phonemizer) [![GitHub release (latest
SemVer)](https://img.shields.io/github/v/release/bootphon/phonemizer)](
https://github.com/bootphon/phonemizer/releases/latest)
[![DOI](https://zenodo.org/badge/56728069.svg)](
https://doi.org/10.5281/zenodo.1045825)

# Phonemizer -- *foʊnmaɪzɚ*

* The phonemizer allows simple phonemization of words and texts in many languages.

* Provides both the `phonemize` command-line tool and the Python function
  `phonemizer.phonemize`.

* It is using four backends: espeak, espeak-mbrola, festival and segments.

  * [espeak-ng](https://github.com/espeak-ng/espeak-ng) supports a lot of
    languages and IPA (International Phonetic Alphabet) output.

  * [espeak-ng-mbrola](https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md)
    uses the SAMPA phonetic alphabet instead of IPA but does not preserve word
    boundaries.

  * [festival](http://www.cstr.ed.ac.uk/projects/festival) currently supports
    only American English. It uses a [custom
    phoneset](http://www.festvox.org/bsv/c4711.html), but it allows tokenization
    at the syllable level.

  * [segments](https://github.com/cldf/segments) is a Unicode tokenizer that
    build a phonemization from a grapheme to phoneme mapping provided as a file
    by the user.


## Installation

**You need python>=3.6.** If you really need to use python2, use an [older
version](https://github.com/bootphon/phonemizer/releases/tag/v1.0) of
the phonemizer.


### Dependencies

* You need to install
  [festival](http://www.festvox.org/docs/manual-2.4.0/festival_6.html#Installation),
  [espeak-ng](https://github.com/espeak-ng/espeak-ng#espeak-ng-text-to-speech)
  and [mbrola](https://github.com/numediart/MBROLA) on your system. On
  Debian/Ubuntu simply run:

        $ sudo apt-get install festival espeak-ng mbrola

* When using the **espeak-mbrola** backend, additional mbrola voices must be
  installed (see
  [here](https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md)). On
  Debian/Ubuntu, list the possible voices with `apt search mbrola`.


### Phonemizer

* The simplest way is using pip:

        $ pip install phonemizer

* **OR** install it from sources with:

        $ git clone https://github.com/bootphon/phonemizer
        $ cd phonemizer
        $ [sudo] python setup.py install

  If you experiment an error such as `ImportError: No module named
  setuptools` during installation, refeer to [issue
  11](https://github.com/bootphon/phonemizer/issues/11).


### Docker image

Alternatively you can run the phonemizer within docker, using the
provided `Dockerfile`. To build the docker image, have a:

    $ git clone https://github.com/bootphon/phonemizer
    $ cd phonemizer
    $ sudo docker build -t phonemizer .

Then run an interactive session with:

    $ sudo docker run -it phonemizer /bin/bash


### Testing

When installed from sources or whithin a Docker image, you can run the tests
suite from the root `phonemizer` folder (once you installed `pytest`):

    $ pip install pytest
    $ pytest


## Python usage

In Python import the `phonemize` function with `from phonemizer import
phonemize`. See
[here](https://github.com/bootphon/phonemizer/blob/master/phonemizer/phonemize.py#L32)
for function documentation.


## Command-line examples

**The above examples can be run from Python using the `phonemize` function**


For a complete list of available options, have a:

    $ phonemize --help

See the installed backends with the `--version` option:

    $ phonemize --version
    phonemizer-2.2
    available backends: espeak-ng-1.49.3, espeak-mbrola, festival-2.5.0, segments-2.0.1


### Input/output exemples

* from stdin to stdout:

        $ echo "hello world" | phonemize
        həloʊ wɜːld

* from file to stdout

        $ echo "hello world" > hello.txt
        $ phonemize hello.txt
        həloʊ wɜːld

* from file to file

        $ phonemize hello.txt -o hello.phon --strip
        $ cat hello.phon
        həloʊ wɜːld


### Backends

* The default is to use **espeak** us-english:

        $ echo "hello world" | phonemize
        həloʊ wɜːld
        $ echo "hello world" | phonemize -l en-us -b espeak
        həloʊ wɜːld
        $ echo 'hello world' | phonemize -l en-us -b espeak --tie
        həlo͡ʊ wɜːld

* Use **festival** US English instead

        $ echo "hello world" | phonemize -l en-us -b festival
        hhaxlow werld

* In French, using **espeak** and **espeak-mbrola**, with custom token
  separators (see below). **espeak-mbrola** does not support words separation.

        $ echo "bonjour le monde" | phonemize -b espeak -l fr-fr -p ' ' -w '/w '
        b ɔ̃ ʒ u ʁ /w l ə /w m ɔ̃ d /w
        $ echo "bonjour le monde" | phonemize -b espeak-mbrola -l mb-fr1 -p ' ' -w '/w '
        b o~ Z u R l @ m o~ d

* In Japanese, using **segments**

        $ echo 'konnichiwa' | phonemize -b segments -l japanese
        konnitʃiwa
        $ echo 'konnichiwa' | phonemize -b segments -l ./phonemizer/share/japanese.g2p
        konnitʃiwa


### Supported languages

The exhaustive list of supported languages is available with the command
`phonemize --list-languages [--backend <backend>]`.

* Languages supported by **espeak** are available
  [here](https://github.com/espeak-ng/espeak-ng/blob/master/docs/languages.md).

* Languages supported by **espeak-mbrola** are available
  [here](https://github.com/numediart/MBROLA-voices). Please note that the
  mbrola voices are not bundled with the phonemizer and must be installed
  separately.

* Languages supported by **festival** are:

        en-us -> english-us

* Languages supported by the **segments** backend are:

        chintang  -> ./phonemizer/share/segments/chintang.g2p
	    cree      -> ./phonemizer/share/segments/cree.g2p
	    inuktitut -> ./phonemizer/share/segments/inuktitut.g2p
	    japanese  -> ./phonemizer/share/segments/japanese.g2p
	    sesotho   -> ./phonemizer/share/segments/sesotho.g2p
	    yucatec   -> ./phonemizer/share/segments/yucatec.g2p

  Instead of a language you can also provide a file specifying a
  grapheme to phone mapping (see the files above for examples).


### Token separators

You can specify separators for phones, syllables (**festival** only) and
words (excepted **espeak-mbrola**).

    $ echo "hello world" | phonemize -b festival -w ' ' -p ''
    hhaxlow werld

    $ echo "hello world" | phonemize -b festival -p ' ' -w ''
    hh ax l ow w er l d

    $ echo "hello world" | phonemize -b festival -p '-' -s '|'
    hh-ax-l-|ow-| w-er-l-d-|

    $ echo "hello world" | phonemize -b festival -p '-' -s '|' --strip
    hh-ax-l|ow w-er-l-d

    $ echo "hello world" | phonemize -b festival -p ' ' -s ';esyll ' -w ';eword '
    hh ax l ;esyll ow ;esyll ;eword w er l d ;esyll ;eword

You cannot specify the same separator for several tokens (for instance
a space for both phones and words):

    $ echo "hello world" | phonemize -b festival -p ' ' -w ' '
    fatal error: illegal separator with word=" ", syllable="" and phone=" ",
    must be all differents if not empty


### Punctuation

By default the punctuation is removed in the phonemized output. You can preserve
it using the ``--preserve-punctuation`` option (not supported by the
**espeak-mbrola** backend):

    $ echo "hello, world!" | phonemize --strip
    həloʊ wɜːld

    $ echo "hello, world!" | phonemize --preserve-punctuation --strip
    həloʊ, wɜːld!


### Espeak specific options

* The **espeak** backend can output the stresses on phones:

        $ echo "hello world" | phonemize -l en-us -b espeak --with-stress
        həlˈoʊ wˈɜːld

* The **espeak** backend can switch languages during phonemization (below from
  French to English), use the ``--language-switch`` option to deal with it:

        $ echo "j'aime le football" | phonemize -l fr-fr -b espeak --language-switch keep-flags
        [WARNING] fount 1 utterances containing language switches on lines 1
        [WARNING] extra phones may appear in the "fr-fr" phoneset
        [WARNING] language switch flags have been kept (applying "keep-flags" policy)
        ʒɛm lə- (en)fʊtbɔːl(fr)

        $ echo "j'aime le football" | phonemize -l fr-fr -b espeak --language-switch remove-flags
        [WARNING] fount 1 utterances containing language switches on lines 1
        [WARNING] extra phones may appear in the "fr-fr" phoneset
        [WARNING] language switch flags have been removed (applying "remove-flags" policy)
        ʒɛm lə- fʊtbɔːl

        $ echo "j'aime le football" | phonemize -l fr-fr -b espeak --language-switch remove-utterance
        [WARNING] removed 1 utterances containing language switches (applying "remove-utterance" policy)


## Licence

**Copyright 2015-2021 Mathieu Bernard**

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
