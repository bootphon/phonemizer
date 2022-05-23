======================
Command Line Examples
======================


The ``phonemize`` command can be used to replicate most of the features
exposed in :ref:`python-examples`.

For a complete list of available options, have a:

.. code:: shell

   phonemize --help

See the installed backends with the ``--version`` option:

.. code:: shell

   $ phonemize --version
   phonemizer-3.0
   available backends: espeak-ng-1.50, espeak-mbrola, festival-2.5.0, segments-2.1.3

Input/output examples
---------------------

-  from stdin to stdout:

   .. code:: shell

      $ echo "hello world" | phonemize
      həloʊ wɜːld

-  Prepend the input text to output:

   .. code:: shell

      $ echo "hello world" | phonemize --prepend-text
      hello world | həloʊ wɜːld

      $ echo "hello world" | phonemize --prepend-text=';'
      hello world ; həloʊ wɜːld

-  from file to stdout

   .. code:: shell

      $ echo "hello world" > hello.txt
      $ phonemize hello.txt
      həloʊ wɜːld

-  from file to file

   .. code:: shell

      $ phonemize hello.txt -o hello.phon --strip
      $ cat hello.phon
      həloʊ wɜːld

Backends
--------

-  The default is to use **espeak** us-english:

   .. code:: shell

      $ echo "hello world" | phonemize
      həloʊ wɜːld

      $ echo "hello world" | phonemize -l en-us -b espeak
      həloʊ wɜːld

      $ echo 'hello world' | phonemize -l en-us -b espeak --tie
      həlo͡ʊ wɜːld

-  Use **festival** US English instead

   .. code:: shell

      $ echo "hello world" | phonemize -l en-us -b festival
      hhaxlow werld

-  In French, using **espeak** and **espeak-mbrola**, with custom token
   separators (see below). **espeak-mbrola** does not support words
   separation.

   .. code:: shell

      $ echo "bonjour le monde" | phonemize -b espeak -l fr-fr -p ' ' -w '/w '
      b ɔ̃ ʒ u ʁ /w l ə /w m ɔ̃ d /w

      $ echo "bonjour le monde" | phonemize -b espeak-mbrola -l mb-fr1 -p ' ' -w '/w '
      b o~ Z u R l @ m o~ d

-  In Japanese, using **segments**

   .. code:: shell

      $ echo 'konnichiwa' | phonemize -b segments -l japanese
      konnitʃiwa

      $ echo 'konnichiwa' | phonemize -b segments -l ./phonemizer/share/japanese.g2p
      konnitʃiwa

Supported languages
-------------------

The exhaustive list of supported languages is available with the command
``phonemize --list-languages [--backend <backend>]``.

-  Languages supported by **espeak** are available
   `here <https://github.com/espeak-ng/espeak-ng/blob/master/docs/languages.md>`__.

-  Languages supported by **espeak-mbrola** are available
   `here <https://github.com/numediart/MBROLA-voices>`__. Please note
   that the mbrola voices are not bundled with the phonemizer nor the
   mbrola binary and must be installed separately.

-  Languages supported by **festival** are:

   ::

      en-us -> english-us

-  Languages supported by the **segments** backend are:

   ::

      chintang  -> ./phonemizer/share/segments/chintang.g2p
      cree      -> ./phonemizer/share/segments/cree.g2p
      inuktitut -> ./phonemizer/share/segments/inuktitut.g2p
      japanese  -> ./phonemizer/share/segments/japanese.g2p
      sesotho   -> ./phonemizer/share/segments/sesotho.g2p
      yucatec   -> ./phonemizer/share/segments/yucatec.g2p

   Instead of a language you can also provide a file specifying a
   grapheme to phone mapping (see the files above for examples).

Token separators
----------------

You can specify separators for phones, syllables (**festival** only) and
words (excepted **espeak-mbrola**).

.. code:: shell

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

You cannot specify the same separator for several tokens (for instance a
space for both phones and words):

.. code:: shell

   $ echo "hello world" | phonemize -b festival -p ' ' -w ' '
   fatal error: illegal separator with word=" ", syllable="" and phone=" ",
   must be all differents if not empty

Punctuation
-----------

By default the punctuation is removed in the phonemized output. You can
preserve it using the ``--preserve-punctuation`` option (not supported
by the **espeak-mbrola** backend):

.. code:: shell

   $ echo "hello, world!" | phonemize --strip
   həloʊ wɜːld

   $ echo "hello, world!" | phonemize --preserve-punctuation --strip
   həloʊ, wɜːld!

The default punctuation marks are each of the following characters: ``;:,.!?¡¿—…"«»“”``.
These can be overridden by the ``--punctuation-marks`` option.

.. code-block:: shell

    $ echo "hello, world!" | phonemize --preserve-punctuation --strip --punctuation-marks '!?'
    həloʊ wɜːld!

The punctuation marks can be specified as a regular expression by additionally using the
``--punctuation-marks-is-regex`` option. For example, to preserve the default punctuation marks
except for commas and periods in the middle of numbers, the following will work:

.. code-block:: shell

    $ echo "1,000, or so." | phonemize --preserve-punctuation --strip --punctuation-marks '[;:!?¡¿—…"«»“”]|[,.](?!\d)' --punctuation-marks-is-regex
    wʌn θaʊzənd, ɔːɹ soʊ.


Espeak specific options
-----------------------

-  The espeak backend can output the **stresses** on phones:

   .. code:: shell

      $ echo "hello world" | phonemize -l en-us -b espeak --with-stress
      həlˈoʊ wˈɜːld

-  The espeak backend can add **tie** on multi-characters phonemes:

   .. code:: shell

      $ echo "hello world" | phonemize -l en-us -b espeak --tie
      həlo͡ʊ wɜːld

.. warning::

    The espeak backend can **switch languages** during
    phonemization (below from French to English), use the
    ``--language-switch`` option to deal with it:

    .. code:: shell

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

.. warning::
    The espeak backend sometimes **merge words together** in
    the output, use the ``--words-mismatch`` option to deal with it:

    .. code:: shell

      $ echo "that's it, words are merged" | phonemize -l en-us -b espeak
      [WARNING] words count mismatch on 100.0% of the lines (1/1)
      ðætsɪt wɜːdz ɑːɹ mɜːdʒd

