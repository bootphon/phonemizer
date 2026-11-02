.. Phonemizer documentation master file, created by
   sphinx-quickstart on Tue Mar 29 17:37:07 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Phonemizer's documentation!
======================================


* ``phonemizer`` allows simple phonemization of words and texts in many languages.

* Provides both the ``phonemize`` command-line tool and the Python function
  :py:meth:`phonemizer.phonemize`.

* It is based on four backends: **espeak**, **espeak-mbrola**, **festival** and
  **segments**. The backends have different properties and capabilities resumed
  in table below. The backend choice is let to the user.

  * `espeak-ng <https://github.com/espeak-ng/espeak-ng>`_ is a Text-to-Speech
    software supporting a lot of languages and IPA (International Phonetic
    Alphabet) output.

  * `espeak-ng-mbrola <https://github.com/espeak-ng/espeak-ng/blob/master/docs/mbrola.md>`_
    uses the SAMPA phonetic alphabet instead of IPA but does not preserve word
    boundaries.

  * `festival <http://www.cstr.ed.ac.uk/projects/festival>`_ is another
    Text-to-Speech engine. Its phonemizer backend currently supports only
    American English. It uses a `custom phoneset
    <http://www.festvox.org/bsv/c4711.html>`_, but it allows tokenization at
    the syllable level.

  * `segments <https://github.com/cldf/segments>`_ is a Unicode tokenizer that
    build a phonemization from a grapheme to phoneme mapping provided as a file
    by the user.

.. list-table::
   :header-rows: 1
   :stub-columns: 1

   * -
     - espeak
     - espeak-mbrola
     - festival
     - segments
   * - phone set
     - `IPA <https://en.wikipedia.org/wiki/International_Phonetic_Alphabet>`_
     - `SAMPA <https://en.wikipedia.org/wiki/SAMPA>`_
     - custom
     - user defined
   * - supported languages
     - `100+ <https://github.com/espeak-ng/espeak-ng/blob/master/docs/languages.md>`_
     - `35 <https://github.com/numediart/MBROLA-voices>`_
     - US English
     - user defined
   * - processing speed
     - fast
     - slow
     - very slow
     - fast
   * - phone tokens
     - yes
     - yes
     - yes
     - yes
   * - syllable tokens
     - no
     - no
     - yes
     - no
   * - word tokens
     - yes
     - no
     - yes
     - yes
   * - punctuation preservation
     - yes
     - no
     - yes
     - yes
   * - stressed phones
     - yes
     - no
     - no
     - no
   * - `tie <https://en.wikipedia.org/wiki/Tie_(typography)#International_Phonetic_Alphabet>`_
     - yes
     - no
     - no
     - no

To reference ``phonemizer`` in your own work, please cite the following
`JOSS paper <https://joss.theoj.org/papers/10.21105/joss.03958>`_.

.. code:: bibtex

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


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   install
   cli
   python_examples
   common_issues
   api_reference
   changelog




