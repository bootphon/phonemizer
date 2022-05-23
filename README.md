|         **Tests** | [![Linux][badge-test-linux]](https://github.com/bootphon/phonemizer/actions/workflows/linux.yaml) [![MacOS][badge-test-macos]](https://github.com/bootphon/phonemizer/actions/workflows/macos.yaml) [![Windows][badge-test-windows]](https://github.com/bootphon/phonemizer/actions/workflows/windows.yaml) [![Codecov][badge-codecov]](https://codecov.io/gh/bootphon/phonemizer) |
|------------------:| --- |
| **Documentation** | [![Doc](https://github.com/bootphon/phonemizer/actions/workflows/doc.yaml/badge.svg)](https://bootphon.github.io/phonemizer/) |
|       **Release** | [![GitHub release (latest SemVer)][badge-github-version]](https://github.com/bootphon/phonemizer/releases/latest) [![PyPI][badge-pypi-version]](https://pypi.python.org/pypi/phonemizer) [![downloads][badge-pypi-downloads]](https://pypi.python.org/pypi/phonemizer) |
|      **Citation** | [![status][badge-joss]](https://joss.theoj.org/papers/08d1ffc14f233f56942f78f3742b266e) [![DOI][badge-zenodo]](https://doi.org/10.5281/zenodo.1045825) |

---

# Phonemizer -- *foʊnmaɪzɚ*

* The phonemizer allows simple phonemization of words and texts in many languages.

* Provides both the `phonemize` command-line tool and the Python function
  `phonemizer.phonemize`. See [the package's documentation](https://bootphon.github.io/phonemizer/).

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
