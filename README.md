[![Travis (.org)](https://img.shields.io/travis/bootphon/phonemizer)](
https://travis-ci.org/bootphon/phonemizer)
[![Codecov](https://img.shields.io/codecov/c/github/bootphon/phonemizer)](
https://codecov.io/gh/bootphon/phonemizer)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/bootphon/phonemizer)](
https://github.com/bootphon/phonemizer/releases/latest)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/phonemizer)](
https://pypi.org/project/phonemizer)
[![DOI](https://zenodo.org/badge/56728069.svg)](
https://doi.org/10.5281/zenodo.1045825)

# Phonemizer -- *foʊnmaɪzɚ*

* Simple text to phonemes converter for multiple languages, based on
  [festival](http://www.cstr.ed.ac.uk/projects/festival),
  [espeak-ng](https://github.com/espeak-ng/espeak-ng/)
  and [segments](https://github.com/cldf/segments).

* Provides both the `phonemize` command-line tool and the Python function
  `phonemizer.phonemize`

* **espeak-ng** is a text-to-speech software supporting multiple
  languages and IPA (Internatinal Phonetic Alphabet) output. See
  https://github.com/espeak-ng/espeak-ng. Alternatively you can use
  the orginal [espeak](http://espeak.sourceforge.net/) program
  (*espeak-ng* is a fork of *espeak* supporting much more languages
  and significant improvements).

* **festival** is also a text-to-speech software. Currently only
  American English is supported and festival uses a custom phoneset
  (http://www.festvox.org/bsv/c4711.html), but festival is the only
  backend supporting tokenization at the syllable level. See
  http://www.cstr.ed.ac.uk/projects/festival.

* **segments** is a Unicode tokenizer that build a phonemization from
  a grapheme to phoneme mapping provided as a file by the user. See
  https://github.com/cldf/segments.


## Installation

**You need python>=3.6.** If you really need to use python2, use an [older
version](https://github.com/bootphon/phonemizer/releases/tag/v1.0) of
phonemizer.

### Dependencies

* You need to install festival and espeak-ng on your system. Visit
  [this festival link](http://www.festvox.org/docs/manual-2.4.0/festival_6.html#Installation)
  and [that espeak-ng one](https://github.com/espeak-ng/espeak-ng#espeak-ng-text-to-speech)
  for installation guidelines. On Debian/Ubuntu simply run:

        $ sudo apt-get install festival espeak-ng

* Alternatively you may want to use `espeak` instead of `espeak-ng`,
  see [here](http://espeak.sourceforge.net/download.html) for
  instalaltion instructions.

### Phonemizer

* The simplest way is using pip:

        $ pip install phonemizer

* **OR** install it from sources with:

        $ git clone https://github.com/bootphon/phonemizer
        $ cd phonemizer
        $ python setup.py build
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


## Command-line examples

For a complete list of available options, have a:

    $ phonemize --help

See the installed backends with the `--version` option:

    $ phonemize --version
    phonemizer-2.0
    available backends: festival-2.5.0, espeak-ng-1.49.3, segments-2.0.1


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


### Token separators

You can specify separators for phonemes, syllables (festival only) and
words.

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


### Options

* **Espeak** us-english is the default

        $ echo "hello world" | phonemize
        həloʊ wɜːld
        $ echo "hello world" | phonemize -l en-us -b espeak
        həloʊ wɜːld

* use **Festival** US English instead

        $ echo "hello world" | phonemize -l en-us -b festival
        hhaxlow werld

* In French, using **espeak**

        $ echo "bonjour le monde" | phonemize -b espeak -l fr-fr
        bɔ̃ʒuʁ lə- mɔ̃d

        $ echo "bonjour le monde" | phonemize -b espeak -l fr-fr -p ' ' -w ';eword '
        b ɔ̃ ʒ u ʁ ;eword l ə- ;eword m ɔ̃ d ;eword

* In Japanese, using **segments**

        $ echo 'konnichiwa' | phonemize -b segments -l japanese
        konnitʃiwa

        $ echo 'konnichiwa' | phonemize -b segments -l ./phonemizer/share/japanese.g2p
        konnitʃiwa

* **Espeak** can output SAMPA phonemes instead of IPA ones (this is only supported
  by espeak-ng, not by the original espeak)

        $ echo "hello world" | phonemize -l en-us -b espeak --sampa
        h@loU w3:ld

* **Espeak** can output the stresses on phonemes (this is not supported by festival
  or segments backends)

        $ echo "hello world" | phonemize -l en-us -b espeak --with-stress
        həlˈoʊ wˈɜːld

* **Espeak** can switch languages during phonemization (below from French to
  English), use the ``--language-switch`` option to deal with it

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


### Supported languages

* Languages supported by festival are:

        en-us	->	english-us

* Languages supported by the segments backend are:

        chintang  -> ./phonemizer/share/chintang.g2p
	    cree	  -> ./phonemizer/share/cree.g2p
	    inuktitut -> ./phonemizer/share/inuktitut.g2p
	    japanese  -> ./phonemizer/share/japanese.g2p
	    sesotho	  -> ./phonemizer/share/sesotho.g2p
	    yucatec	  -> ./phonemizer/share/yucatec.g2p

  Instead of a language you can also provide a file specifying a
  grapheme to phoneme mapping (see the files above for exemples).

* Languages supported by espeak are (espeak-ng supports even more of
  them), type `phonemize --help` for an exhaustive list:

        af	->	afrikaans
        an	->	aragonese
        bg	->	bulgarian
        bs	->	bosnian
        ca	->	catalan
        cs	->	czech
        cy	->	welsh
        da	->	danish
        de	->	german
        el	->	greek
        en	->	default
        en-gb	->	english
        en-sc	->	en-scottish
        en-uk-north	->	english-north
        en-uk-rp	->	english_rp
        en-uk-wmids	->	english_wmids
        en-us	->	english-us
        en-wi	->	en-westindies
        eo	->	esperanto
        es	->	spanish
        es-la	->	spanish-latin-am
        et	->	estonian
        fa	->	persian
        fa-pin	->	persian-pinglish
        fi	->	finnish
        fr-be	->	french-Belgium
        fr-fr	->	french
        ga	->	irish-gaeilge
        grc	->	greek-ancient
        hi	->	hindi
        hr	->	croatian
        hu	->	hungarian
        hy	->	armenian
        hy-west	->	armenian-west
        id	->	indonesian
        is	->	icelandic
        it	->	italian
        jbo	->	lojban
        ka	->	georgian
        kn	->	kannada
        ku	->	kurdish
        la	->	latin
        lfn	->	lingua_franca_nova
        lt	->	lithuanian
        lv	->	latvian
        mk	->	macedonian
        ml	->	malayalam
        ms	->	malay
        ne	->	nepali
        nl	->	dutch
        no	->	norwegian
        pa	->	punjabi
        pl	->	polish
        pt-br	->	brazil
        pt-pt	->	portugal
        ro	->	romanian
        ru	->	russian
        sk	->	slovak
        sq	->	albanian
        sr	->	serbian
        sv	->	swedish
        sw	->	swahili-test
        ta	->	tamil
        tr	->	turkish
        vi	->	vietnam
        vi-hue	->	vietnam_hue
        vi-sgn	->	vietnam_sgn
        zh	->	Mandarin
        zh-yue	->	cantonese


## Licence

**Copyright 2015-2019 Mathieu Bernard**

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
