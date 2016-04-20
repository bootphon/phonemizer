# Phonemizer

Simple phonemization of English text utterances, based on
[festival](http://www.cstr.ed.ac.uk/projects/festival) TTS system.

## Installation

### Festival

First you need to install
[festival](http://www.cstr.ed.ac.uk/projects/festival) on your
system. On Debian/Ubuntu simply run::

    sudo apt-get install festival

Visit
[this link](http://www.festvox.org/docs/manual-2.4.0/festival_6.html#Installation)
for detailed installation guidelines.

### Phonemizer

After have cloned this repository, install it from the `phonemizer`
directory with

    $ python setup.py build
    $ python setup.py install


## Examples

* First, have a

        $ phonemize --help

* Here are few basic examples

        $ echo "hello world" | ./phonemize
        hh ax l ;esyll ow ;esyll ;eword w er l d ;esyll ;eword

        $ echo "hello world" > hello.txt
        $ ./phonemize hello.txt
        hh ax l ;esyll ow ;esyll ;eword w er l d ;esyll ;eword

        $ ./phonemize hello.txt -o hello.phon
        $ cat hello.phon
        hh ax l ;esyll ow ;esyll ;eword w er l d ;esyll ;eword


## Potential issues

The program may print on stderr something like:

    UniSyn: using default diphone ax-ax for y-pau

This is related to wave synthesis (done by festival during
phonologization). It should be useful to overload this configuration
if the phonologization takes too long (I began this but it seems a bit
tricky and time consuming).


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
