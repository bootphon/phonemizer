# Phonemizer -- *f-ax-n|ih-m|ay-z|er*

* Simple phonemization of English text, based on the
  [festival](http://www.cstr.ed.ac.uk/projects/festival) TTS system

* The phoneset used is is the default
  [US phoneset](http://www.festvox.org/bsv/c4711.html) used by
  festival

* Provides both the `phonemize` command-line tool and the Python class
  `phonemizer.Phonemizer`

## Installation

* First you need to install
  [festival](http://www.cstr.ed.ac.uk/projects/festival) on your
  system. Visit
  [this link](http://www.festvox.org/docs/manual-2.4.0/festival_6.html#Installation)
  for installation guidelines. On Debian/Ubuntu simply run:

        $ sudo apt-get install festival

* Then download and install the `phonemizer` from
[github](https://github.com/bootphon/phonemizer) with:

        $ git clone git@github.com:bootphon/phonemizer.git
        $ cd phonemizer
        $ python setup.py build
        $ [sudo] python setup.py install

  The `phonemizer` command should be in your `$PATH`.

## Command-line examples

* First, have a

        $ phonemize --help

* Here are few basic examples

    * from stdin to stdout:

            $ echo "hello world" | phonemize
            hh-ax-l-|ow-| w-er-l-d-|

            $ echo "hello world" | phonemize --strip
            hh-ax-l|ow w-er-l-d

            $ echo "hello world" | phonemize -p ' ' -s ';esyll ' -w ';eword '
            hh ax l ;esyll ow ;esyll ;eword w er l d ;esyll ;eword

    * from file to stdout

            $ echo "hello world" > hello.txt
            $ phonemize hello.txt --strip
            hh-ax-l|ow w-er-l-d

    * from file to file

            $ phonemize hello.txt -o hello.phon --strip
            $ cat hello.phon
            hh-ax-l|ow w-er-l-d

## Licence

**Copyright 2015, 2016 Mathieu Bernard**

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
