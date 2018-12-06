[![travis](https://travis-ci.org/bootphon/phonemizer.svg?branch=master)](https://travis-ci.org/bootphon/phonemizer) [![DOI](https://zenodo.org/badge/56728069.svg)](https://doi.org/10.5281/zenodo.1045825)

# Phonemizer -- *foʊnmaɪzɚ*

* Simple text to phonemes converter for multiple languages, based
  on [festival](http://www.cstr.ed.ac.uk/projects/festival) and
  [espeak](http://espeak.sourceforge.net/)/[espeak-ng](https://github.com/espeak-ng/espeak-ng/)
  Text-to-Speech systems.

* Provides both the `phonemize` command-line tool and the Python function
  `phonemizer.phonemize`

* Festival provides US English phonemization with syllable
  tokenization, espeak endows multiple languages but without syllable
  boundaries.

* The phoneset used is
  [IPA](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet)
  for the espeak backend whereas festival use its default
  [US phoneset](http://www.festvox.org/bsv/c4711.html)


## Installation

* First you need to install festival and espeak on your system. Visit
  [this festival link](http://www.festvox.org/docs/manual-2.4.0/festival_6.html#Installation)
  and [that espeak one](http://espeak.sourceforge.net/download.html)
  for installation guidelines. On Debian/Ubuntu simply run:

        $ sudo apt-get install festival espeak

  Alternatively you may want to use `espeak-ng` (Next Generation)
  instead of espeak. It supports more languages and significant
  improvements over the original espeak, but requires a manual
  installation. Install it from github
  [here](https://github.com/espeak-ng/espeak-ng/).

* Then download and install the `phonemizer` from
  [github](https://github.com/bootphon/phonemizer) with:

        $ git clone https://github.com/bootphon/phonemizer
        $ cd phonemizer
        $ python setup.py build
        $ [sudo] python setup.py install

  The `phonemize` command should be in your `$PATH`.

* If you experiment an error such as `ImportError: No module named
  setuptools` during installation, refeer to [issue
  11](https://github.com/bootphon/phonemizer/issues/11).

## Docker image

Alternatively you can run the phonemizer within docker, using the
provided `Dockerfile`.

To build the docker image, have a:

    $ git clone https://github.com/bootphon/phonemizer
    $ cd phonemizer
    $ sudo docker build -t phonemizer .

Then run an interactive session with:

    $ sudo docker run -it phonemizer /bin/bash


## Command-line examples

For a complete list of available options, have a:

    phonemize --help


### Input/output exemples

* from stdin to stdout:

        $ echo "hello world" | phonemize
        hhaxlow werld

* from file to stdout

        $ echo "hello world" > hello.txt
        $ phonemize hello.txt
        hhaxlow werld

* from file to file

        $ phonemize hello.txt -o hello.phon --strip
        $ cat hello.phon
        hhaxlow werld


### Token separators

You can specify separators for phonemes, syllables (festival only) and
words.

    $ echo "hello world" | phonemize -p '-' -s '|'
    hh-ax-l-|ow-| w-er-l-d-|

    $ echo "hello world" | phonemize -p '-' -s '|' --strip
    hh-ax-l|ow w-er-l-d

    $ echo "hello world" | phonemize -p ' ' -s ';esyll ' -w ';eword '
    hh ax l ;esyll ow ;esyll ;eword w er l d ;esyll ;eword


### Languages

* Festival US English is the default

        $ echo "hello world" | phonemize -l en-us-festival
        hhaxlow werld

* This uses espeak instead

        $ echo "hello world" | phonemize -l en-us
        həloʊ wɜːld

* In French

        $ echo "bonjour le monde" | phonemize -l fr-fr
        bɔ̃ʒuʁ lə- mɔ̃d

        $ echo "bonjour le monde" | phonemize -l fr-fr -p ' ' -w ';eword '
        b ɔ̃ ʒ u ʁ ;eword l ə- ;eword m ɔ̃ d ;eword

* Languages supported by festival are:

        en-us-festival	->	english-us

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

**Copyright 2015-2018 Mathieu Bernard**

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
