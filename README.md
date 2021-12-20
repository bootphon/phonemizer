| **Tests** | [![Linux][badge-test-linux]](https://github.com/bootphon/phonemizer/actions/workflows/linux.yaml) [![MacOS][badge-test-macos]](https://github.com/bootphon/phonemizer/actions/workflows/macos.yaml) [![Windows][badge-test-windows]](https://github.com/bootphon/phonemizer/actions/workflows/windows.yaml) [![Codecov][badge-codecov]](https://codecov.io/gh/bootphon/phonemizer) |
| ---: | --- |
| **Release** | [![GitHub release (latest SemVer)][badge-github-version]](https://github.com/bootphon/phonemizer/releases/latest) [![PyPI][badge-pypi-version]](https://pypi.python.org/pypi/phonemizer) [![downloads][badge-pypi-downloads]](https://pypi.python.org/pypi/phonemizer) |
| **Citation** | [![status][badge-joss]](https://joss.theoj.org/papers/08d1ffc14f233f56942f78f3742b266e) [![DOI][badge-zenodo]](https://doi.org/10.5281/zenodo.1045825) |

---

# Phonemizer -- *foʊnmaɪzɚ*

* The phonemizer allows simple phonemization of words and texts in many languages.

* Provides both the `phonemize` command-line tool and the Python function
  `phonemizer.phonemize`. See [function documentation][phonemize-function].

* It is based on four backends: **espeak**, **espeak-mbrola**, **festival** and
  **segments**. The backends have different properties and capabilities resumed
  in table below. The backend choice is let to the user.

  * [espeak-ng](https://github.com/espeak-ng/espeak-ng) is a Text-to-Speech
    software supporting a lot of languages and IPA (International Phonetic
    Alphabet) output.

  * [espeak-ng-mbrola](https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md)
    uses the SAMPA phonetic alphabet instead of IPA but does not preserve word
    boundaries.

  * [festival](http://www.cstr.ed.ac.uk/projects/festival) is another
    Tex-to-Speech engine. Its phonemizer backend currently supports only
    American English. It uses a [custom phoneset][festival-phoneset], but it
    allows tokenization at the syllable level.

  * [segments](https://github.com/cldf/segments) is a Unicode tokenizer that
    build a phonemization from a grapheme to phoneme mapping provided as a file
    by the user.

  |                              | espeak                   | espeak-mbrola           | festival                    | segments           |
  | ---:                         | ---                      | ---                     | ---                         | ---                |
  | **phone set**                | [IPA]                    | [SAMPA]                 | [custom][festival-phoneset] | user defined       |
  | **supported languages**      | [100+][espeak-languages] | [35][mbrola-languages] | US English                  | user defined       |
  | **processing speed**         | fast                     | slow                    | very slow                   | fast               |
  | **phone tokens**             | :heavy_check_mark:       | :heavy_check_mark:      | :heavy_check_mark:          | :heavy_check_mark: |
  | **syllable tokens**          | :x:                      | :x:                     | :heavy_check_mark:          | :x:                |
  | **word tokens**              | :heavy_check_mark:       | :x:                     | :heavy_check_mark:          | :heavy_check_mark: |
  | **punctuation preservation** | :heavy_check_mark:       | :x:                     | :heavy_check_mark:          | :heavy_check_mark: |
  | **stressed phones**          | :heavy_check_mark:       | :x:                     | :x:                         | :x:                |
  | [**tie**][tie-IPA]           | :heavy_check_mark:       | :x:                     | :x:                         | :x:                |


## Installation

### Dependencies

**You need python>=3.6.** If you really need to use python2, use the
[phonemizer-1.0] release.

You need to install
[festival](http://www.festvox.org/docs/manual-2.4.0/festival_6.html#Installation),
[espeak-ng](https://github.com/espeak-ng/espeak-ng#espeak-ng-text-to-speech)
and/or [mbrola](https://github.com/numediart/MBROLA) in order to use the
corresponding `phonemizer` backends. Follow instructions for your system below.

<details><summary>on Debian/Unbuntu</summary>
<p>

To install dependencies, simply run `sudo apt-get install festival espeak-ng mbrola`.

When using the **espeak-mbrola** backend, additional mbrola voices must be
installed (see
[here](https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md)). List
the installable voices with `apt search mbrola`.

</p>
</details>

<details><summary>on CentOS/Fedora</summary>
<p>

To install dependencies, simply run `sudo yum install festival espeak-ng`.

When using the **espeak-mbrola** backend, the mbrola binary and additional
mbrola voices must be installed (see
[here](https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md)).

</p>
</details>

<details><summary>on MacOS</summary>
<p>

**espeak** is available on brew at version 1.48: `brew install espeak`. If you
want a more recent version you have to [compile it from
sources](https://github.com/espeak-ng/espeak-ng/blob/master/docs/building.md#linux-mac-bsd).
To install **festival**, **mbrola** and additional mbrola voices, use the
script provided [here](https://github.com/pettarin/setup-festival-mbrola).

</p>
</details>

<details><summary>on Windows</summary>
<p>

Install **espeak-ng** with the `.msi` Windows installer provided with [espeak
releases](https://github.com/espeak-ng/espeak-ng/releases). **festival** must be
compiled from sources (see
[here](https://github.com/festvox/festival/blob/master/INSTALL) and
[here](https://www.eguidedog.net/doc/doc_build_win_festival.php)). **mbrola** is
not available for Windows.

</p>
</details>


### Phonemizer

* The simplest way is using pip:

        pip install phonemizer

* **OR** install it from sources with:

  ```shell
  git clone https://github.com/bootphon/phonemizer
  cd phonemizer
  python setup.py install
  ```

  If you experiment an error such as `ImportError: No module named setuptools`
  during installation, refeer to [issue
  #11](https://github.com/bootphon/phonemizer/issues/11).


### Docker image

Alternatively you can run the phonemizer within docker, using the
provided `Dockerfile`. To build the docker image, have a:

```shell
git clone https://github.com/bootphon/phonemizer
cd phonemizer
sudo docker build -t phonemizer .
```

Then run an interactive session with:

```shell
sudo docker run -it phonemizer /bin/bash
```


### Testing

When installed from sources or whithin a Docker image, you can run the tests
suite from the root `phonemizer` folder (once you installed `pytest`):

```shell
pip install pytest
pytest
```

### Developers

The `phonemizer` project is open-source and is welcoming contributions from
everyone. Please look at the [contributors guidelines](CONTRIBUTING.md) if you
wish to contribute.


## Citation

To refenrece the `phonemizer` in your own work, please cite the following [JOSS
paper](https://joss.theoj.org/papers/10.21105/joss.03958).

```bibtex
@article{Bernard2021,
  doi = {10.21105/joss.03958},
  url = {https://doi.org/10.21105/joss.03958},
  year = {2021},
  publisher = {The Open Journal},
  volume = {6},
  number = {68},
  pages = {3958},
  author = {Mathieu Bernard and Hadrien Titeux},
  title = {Phonemizer: Text to Phones Transcription for Multiple Languages in Python},
  journal = {Journal of Open Source Software}
}
```

## Python usage

In Python import the `phonemize` function with `from phonemizer import
phonemize`. See the [function documentation][phonemize-function].


### Advice for best performances

It is much more efficient to minimize the number of calls to the `phonemize`
function. Indeed the initialization of the phonemization backend can be
expensive, especially for espeak. In one exemple:

```python
from phonemizer import phonemize

text = [line1, line2, ...]

# Do this:
phonemized = phonemize(text, ...)

# Not this:
phonemized = [phonemize(line, ...) for line in text]

# An alternative is to directly instanciate the backend and to call the
# phonemize function from it:
from phonemizer.backend import EspeakBackend
backend = EspeakBackend('en-us', ...)
phonemized = [backend.phonemize(line, ...) for line in text]
```

### Exemple 1: phonemize a text with festival

The following exemple downloads a text and phonemizes it using the festival
backend, preserving punctuation and using 4 jobs in parallel. The phones are not
separated, words are separated by a space and syllables by `|`.

```python
# need to pip install requests
import requests
from phonemizer import phonemize
from phonemizer.separator import Separator

# text is a list of 190 English sentences downloaded from github
url = (
    'https://gist.githubusercontent.com/CorentinJ/'
    '0bc27814d93510ae8b6fe4516dc6981d/raw/'
    'bb6e852b05f5bc918a9a3cb439afe7e2de570312/small_corpus.txt')
text = requests.get(url).content.decode()
text = [line.strip() for line in text.split('\n') if line]

# phn is a list of 190 phonemized sentences
phn = phonemize(
    text,
    language='en-us',
    backend='festival',
    separator=Separator(phone=None, word=' ', syllable='|'),
    strip=True,
    preserve_punctuation=True,
    njobs=4)
```

### Exemple 2: build a lexicon with espeak

The following exemple extracts a list of words present in a text, ignoring
punctuation, and builds a dictionary `word: [phones]`, e.g. `{'students': 's t
uː d ə n t s', 'cobb': 'k ɑː b', 'its': 'ɪ t s', 'put': 'p ʊ t', ...}`. We
consider here the same text as in the previous exemple.

```python
from phonemizer.backend import EspeakBackend
from phonemizer.punctuation import Punctuation
from phonemizer.separator import Separator

# remove all the punctuation from the text, condidering only the specified
# punctuation marks
text = Punctuation(';:,.!"?()-').remove(text)

# build the set of all the words in the text
words = {w.lower() for line in text for w in line.strip().split(' ') if w}

# initialize the espeak backend for English
backend = EspeakBackend('en-us')

# separate phones by a space and ignoring words boundaries
separator = Separator(phone=' ', word=None)

# build the lexicon by phonemizing each word one by one. The backend.phonemize
# function expect a list as input and outputs a list.
lexicon = {
    word: backend.phonemize([word], separator=separator, strip=True)[0]
    for word in words}
```

## Command-line examples

**The above examples can be run from Python using the `phonemize` function**


For a complete list of available options, have a:

```shell
phonemize --help
```

See the installed backends with the `--version` option:

```shell
$ phonemize --version
phonemizer-3.0
available backends: espeak-ng-1.50, espeak-mbrola, festival-2.5.0, segments-2.1.3
```


### Input/output exemples

* from stdin to stdout:

  ```shell
  $ echo "hello world" | phonemize
  həloʊ wɜːld
  ```

* Prepend the input text to output:

  ```shell
  $ echo "hello world" | phonemize --prepend-text
  hello world | həloʊ wɜːld

  $ echo "hello world" | phonemize --prepend-text=';'
  hello world ; həloʊ wɜːld
  ```

* from file to stdout

  ```shell
  $ echo "hello world" > hello.txt
  $ phonemize hello.txt
  həloʊ wɜːld
  ```

* from file to file

  ```shell
  $ phonemize hello.txt -o hello.phon --strip
  $ cat hello.phon
  həloʊ wɜːld
  ```


### Backends

* The default is to use **espeak** us-english:

  ```shell
  $ echo "hello world" | phonemize
  həloʊ wɜːld

  $ echo "hello world" | phonemize -l en-us -b espeak
  həloʊ wɜːld

  $ echo 'hello world' | phonemize -l en-us -b espeak --tie
  həlo͡ʊ wɜːld
  ```

* Use **festival** US English instead

  ```shell
  $ echo "hello world" | phonemize -l en-us -b festival
  hhaxlow werld
  ```

* In French, using **espeak** and **espeak-mbrola**, with custom token
  separators (see below). **espeak-mbrola** does not support words separation.

  ```shell
  $ echo "bonjour le monde" | phonemize -b espeak -l fr-fr -p ' ' -w '/w '
  b ɔ̃ ʒ u ʁ /w l ə /w m ɔ̃ d /w

  $ echo "bonjour le monde" | phonemize -b espeak-mbrola -l mb-fr1 -p ' ' -w '/w '
  b o~ Z u R l @ m o~ d
  ```

* In Japanese, using **segments**

  ```shell
  $ echo 'konnichiwa' | phonemize -b segments -l japanese
  konnitʃiwa

  $ echo 'konnichiwa' | phonemize -b segments -l ./phonemizer/share/japanese.g2p
  konnitʃiwa
  ```

### Supported languages

The exhaustive list of supported languages is available with the command
`phonemize --list-languages [--backend <backend>]`.

* Languages supported by **espeak** are available [here][espeak-languages].

* Languages supported by **espeak-mbrola** are available
  [here][mbrola-languages]. Please note that the mbrola voices are not bundled
  with the phonemizer nor the mbrola binary and must be installed separately.

* Languages supported by **festival** are:

  ```
  en-us -> english-us
  ```

* Languages supported by the **segments** backend are:

  ```
  chintang  -> ./phonemizer/share/segments/chintang.g2p
  cree      -> ./phonemizer/share/segments/cree.g2p
  inuktitut -> ./phonemizer/share/segments/inuktitut.g2p
  japanese  -> ./phonemizer/share/segments/japanese.g2p
  sesotho   -> ./phonemizer/share/segments/sesotho.g2p
  yucatec   -> ./phonemizer/share/segments/yucatec.g2p
  ```

  Instead of a language you can also provide a file specifying a
  grapheme to phone mapping (see the files above for examples).


### Token separators

You can specify separators for phones, syllables (**festival** only) and
words (excepted **espeak-mbrola**).

```shell
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
```

You cannot specify the same separator for several tokens (for instance
a space for both phones and words):

```shell
$ echo "hello world" | phonemize -b festival -p ' ' -w ' '
fatal error: illegal separator with word=" ", syllable="" and phone=" ",
must be all differents if not empty
```


### Punctuation

By default the punctuation is removed in the phonemized output. You can preserve
it using the ``--preserve-punctuation`` option (not supported by the
**espeak-mbrola** backend):

```shell
$ echo "hello, world!" | phonemize --strip
həloʊ wɜːld

$ echo "hello, world!" | phonemize --preserve-punctuation --strip
həloʊ, wɜːld!
```


### Espeak specific options

* The espeak backend can output the **stresses** on phones:

  ```shell
  $ echo "hello world" | phonemize -l en-us -b espeak --with-stress
  həlˈoʊ wˈɜːld
  ```

* The espeak backend can add **tie** on multi-characters phonemes:

  ```shell
  $ echo "hello world" | phonemize -l en-us -b espeak --tie
  həlo͡ʊ wɜːld
  ```

* :warning: The espeak backend can **switch languages** during phonemization (below from
  French to English), use the ``--language-switch`` option to deal with it:

  ```shell
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
  ```

* :warning: The espeak backend sometimes **merge words together** in the output, use the
  `--words-mismatch` option to deal with it:

  ```shell
  $ echo "that's it, words are merged" | phonemize -l en-us -b espeak
  [WARNING] words count mismatch on 100.0% of the lines (1/1)
  ðætsɪt wɜːdz ɑːɹ mɜːdʒd
  ```


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


[badge-test-linux]: https://github.com/bootphon/phonemizer/actions/workflows/linux.yaml/badge.svg?branch=master
[badge-test-macos]: https://github.com/bootphon/phonemizer/actions/workflows/macos.yaml/badge.svg?branch=master
[badge-test-windows]: https://github.com/bootphon/phonemizer/actions/workflows/windows.yaml/badge.svg?branch=master
[badge-codecov]: https://img.shields.io/codecov/c/github/bootphon/phonemizer
[badge-github-version]: https://img.shields.io/github/v/release/bootphon/phonemizer
[badge-pypi-version]: https://img.shields.io/pypi/v/phonemizer
[badge-pypi-downloads]: https://img.shields.io/pypi/dm/phonemizer
[badge-joss]: https://joss.theoj.org/papers/08d1ffc14f233f56942f78f3742b266e/status.svg
[badge-zenodo]: https://zenodo.org/badge/56728069.svg
[phonemizer-1.0]: https://github.com/bootphon/phonemizer/releases/tag/v1.0
[festival-phoneset]: http://www.festvox.org/bsv/c4711.html
[IPA]: https://en.wikipedia.org/wiki/International_Phonetic_Alphabet
[SAMPA]: https://en.wikipedia.org/wiki/SAMPA
[phonemize-function]: https://github.com/bootphon/phonemizer/blob/c5e2f3878d6db391ec7253173f44e4a85cfe41e3/phonemizer/phonemize.py#L33-L156
[tie-IPA]: https://en.wikipedia.org/wiki/Tie_(typography)#International_Phonetic_Alphabet
[espeak-languages]: https://github.com/espeak-ng/espeak-ng/blob/master/docs/languages.md
[mbrola-languages]: https://github.com/numediart/MBROLA-voices
