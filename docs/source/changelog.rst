===============
Changelog
===============

Version numbers follow `semantic versioning <https://semver.org>`__.


phonemizer-3.3.0
----------------

**This version depends on python>=3.8 (was 3.6 in previous versions). Tests now
 requires pytest>=6.0**

* **improvements**

  * Replaced dependency to deprecated ``pkg_resources`` by ``importlib``
    (requires python>=3.8).

  * Replaced deprecated ``setup.py`` by ``pyproject.toml``.

* **bug fix**

  * ``espeak`` backend: words mismatch now works when using custom word
    separators. See `issue #169
    <https://github.com/bootphon/phonemizer/issues/169>`__.


phonemizer-3.2.1
----------------

* **bug fixes**

  * Fixed a bug when trying to restore punctuation on a multiline text.
    See `issue #129 <https://github.com/bootphon/phonemizer/issues/129>`__.


phonemizer-3.2.0
----------------

* **bug fixes**

  * Fixed a bug when trying to restore punctuation on very long text.
    See `issue #108 <https://github.com/bootphon/phonemizer/issues/108>`__.

* **improvements**

  * Improved consistency with the handling of word separators when
    preserving punctuation, and when using a word separator that is
    not a literal space character. See
    `issue #106 <https://github.com/bootphon/phonemizer/issues/106>`__.

* **new features**

  * Added the option to define punctuation with a regular expression.
    Previously only strings were accepted. See
    `PR #120 <https://github.com/bootphon/phonemizer/pull/120>`__

    * In the python API, the ``punctuation_marks`` parameter can now be
      passed to ``phonemize`` (or a backend constructor) as a ``re.Pattern``
      that defines which characters will be matched as punctuation.
      Passing ``punctuation_marks`` as a str will continue to function as
      before, treating each character in the string as a punctuation mark.

    * Added the optional parameter ``--punctuation_marks_is_regex`` to the CLI
      interface. When used, the CLI will attempt to compile a ``re.Pattern``
      from the value passed to ``--punctuation-marks``.

phonemizer-3.1.1
----------------

-  **improvements**

   -  Preserve empty lines in texts when using
      ``--preserve-empty-lines``. Without this option, empty lines used
      to be automatically dropped. See `PR
      #103 <https://github.com/bootphon/phonemizer/pull/103>`__

-  **new features**

   -  Type hinted most of ``phonemizer``\ ’s API. This makes the usage
      of our API a bit clearer, and can be easily leveraged by IDE’s and
      type checkers to prevent typing issues.

phonemizer-3.0.1
----------------

-  **bug fixes**

   -  The method ``BaseBackend.phonemize`` now raises a ``RuntimeError``
      if the input text is a str instead of a list of of str (was only
      logging an error message).

   -  Preserve punctuation alignement when using
      ``--preserve-punctuation``, was inserting a space before each
      punctuation token, see `issue
      #97 <https://github.com/bootphon/phonemizer/issues/97>`__.

phonemizer-3.0
--------------

-  **breaking change**

   -  Do not remove empty lines from output. For example:

   .. code:: python

      # this is now
      phonemize(["hello", "!??"]) == ['həloʊ ', '']
      # this was
      phonemize(["hello", "!??"]) == ['həloʊ ']

   -  Default backend in the ``phonemize`` function is now ``espeak``
      (was ``festival``).

   -  ``espeak-mbrola`` backend now requires ``espeak>=1.49``.

   -  ``--espeak-path`` option renamed as ``--espeak-library``\ and
      ``PHONEMIZER_ESPEAK_PATH`` environment variable renamed as
      ``PHONEMIZER_ESPEAK_LIBRARY``.

   -  ``--festival-path`` option renamed as ``--festival-executable``
      and ``PHONEMIZER_FESTIVAL_PATH`` environment variable renamed as
      ``PHONEMIZER_FESTIVAL_EXECUTABLE``.

   -  The methods ``backend.phonemize()`` from the backend classes take
      only a list of str a input text (was either a str or a list of
      str).

   -  The methods ``backend.version()`` from the backend classes returns
      a tuple of int instead of a str.

-  **improvements**

   -  ``espeak`` and ``mbrola`` backends now rely on the ``espeak``
      shared library using the ``ctypes`` Python module, instead of
      reliying on the ``espeak`` executable through subprocesses. This
      implies **drastic speed improvments, up to 40 times faster**.

-  **new features**

   -  New option ``--prepend-text`` to prepend the input text to
      phonemized utterances, so as to have both orthographic and
      phonemized available at output.

   -  New option ``--tie`` for the ``espeak`` backend to display a tie
      character within multi-letter phonemes. (see issue
      `#74 <https://github.com/bootphon/phonemizer/issues/74>`__).

   -  New option ``--words-mismatch`` for the ``espeak`` backend. This
      allows to detect when espeak merge consecutive words or drop a
      word from the orthographic text. Possible actions are to ignore
      those misatches, to issue a warning for each line where a mismatch
      is detectd, or to remove those lines from the output.

-  **bugfixes**

   -  phonemizer’s logger no more conflicts with other loggers when
      imported from Python (see PR
      `#61 <https://github.com/bootphon/phonemizer/pull/61>`__).

phonemizer-2.2.2
----------------

-  **bugfixes**

   -  fixed installation from source (bug introduced in 2.2.1, see issue
      `#52 <https://github.com/bootphon/phonemizer/issues/52>`__).

   -  Fixed a bug when trying to restore punctuation on an empty text
      (see issue
      `#54 <https://github.com/bootphon/phonemizer/issues/54>`__).

   -  Fixed an edge case bug when using custom punctuation marks (see
      issue `#55 <https://github.com/bootphon/phonemizer/issues/55>`__).

   -  Fixed regex issue that causes digits to be considered punctuation
      (see issue
      `#60 <https://github.com/bootphon/phonemizer/pull/60>`__).

phonemizer-2.2.1
----------------

-  **improvements**

   From Python import the phonemize function using
   ``from phonemizer import phonemize`` instead of
   ``from phonemizer.phonemize import phonemize``. The second import is
   still available for compatibility.

-  **bugfixes**

   -  Fixed a minor bug in ``utils.chunks``.

   -  Fixed warnings on language switching for espeak backend when using
      parallel jobs (see issue
      `#50 <https://github.com/bootphon/phonemizer/issues/50>`__).

   -  Save file in utf-8 explicitly for Windows compat (see issue
      `#43 <https://github.com/bootphon/phonemizer/issues/43>`__).

   -  Fixed build and tests in Dockerfile (see issue
      `#45 <https://github.com/bootphon/phonemizer/issues/45>`__).

phonemizer-2.2
--------------

-  **new features**

   -  New option ``--list-languages`` to list the available languages
      for a given backend from the command line.

   -  The ``--sampa`` option of the ``espeak`` backend has been replaced
      by a new backend ``espeak-mbrola``.

      -  The former ``--sampa`` option (introduced in phonemizer-2.0)
         outputs phones that are not standard SAMPA but are adapted to
         the espeak TTS front-end.

      -  On the other hand the ``espeak-mbrola`` backend allows espeak
         to output phones in standard SAMPA (adapted to the mbrola TTS
         front-end). This backend requires mbrola to be installed, as
         well as additional mbrola voices to support needed languages.
         **This backend does not support word separation nor punctuation
         preservation**.

-  **bugfixes**

   -  Fixed issues with punctuation processing on some corner cases, see
      issues `#39 <https://github.com/bootphon/phonemizer/issues/39>`__
      and `#40 <https://github.com/bootphon/phonemizer/issues/40>`__.

   -  Improvments and updates in the documentation (Readme,
      ``phonemize --help`` and Python code).

   -  Fixed a test when using ``espeak>=1.50``.

   -  Empty lines are correctly ignored when reading text from a file.

phonemizer-2.1
--------------

-  **new features**

   -  Possibility to preserve the punctuation (ignored and silently
      removed by default) in the phonemized output with the new option
      ``--preserve-punctuation`` from command line (or the equivalent
      ``preserve-punctuation`` from Python API). With the
      ``punctuation-marks`` option, one can overload the default marls
      considered as punctuation.

   -  It is now possible to specify the path to a custom ``espeak`` or
      ``festival`` executable (for instance to use a local installation
      or to test different versions). Either specify the
      ``PHONEMIZER_ESPEAK_PATH`` environment variable, the
      ``--espeak-path`` option from command line or use the
      ``EspeakBackend.set_espeak_path`` method from the Python API.
      Similarly for festival use ``PHONEMIZER_FESTIVAL_PATH``,
      ``--festival-path`` or ``FestivalBackend.set_festival_path``.

   -  The ``--sampa`` option is now available for espeak (was available
      only for espeak-ng).

   -  When using ``espeak`` with SAMPA output, some SAMPA phones are
      corrected to correspond to the normalized SAMPA alphabet (espeak
      seems not to respect it). The corrections are language specific. A
      correction file must be placed in ``phonemizer/share/espeak``.
      This have been implemented only for French by now.

-  **bugfixes**

   -  parses correctly the version of ``espeak-ng`` even for dev
      versions (e.g. ``1.51-dev``).

   -  fixed an issue with ``espeak`` backend, where multiple phone
      separators can be present at the end of a word, see
      `#31 <https://github.com/bootphon/phonemizer/issues/31>`__.

   -  added an additional stress symbol ``-`` for ``espeak``.

phonemizer-2.0.1
----------------

-  **bugfixes**

   -  ``keep-flags`` was not the default argument for
      ``language_switch`` in the class ``EspeakBackend``.

   -  fixed an issue with punctuation processing in the espeak backend,
      see `#26 <https://github.com/bootphon/phonemizer/issues/26>`__

-  **improvements**

   -  log a warning if using ``python2``.

phonemizer-2.0
--------------

-  **incompatible change**

   Starting with ``phonemizer-2.0`` only python3 is supported.
   **Compatibility with python2 is no more ensured nor tested.**
   https://pythonclock.org.

-  **bugfixes**

   -  new ``--language-switch`` option to use with ``espeak`` backend to
      deals with language switching on phonemized output. In previous
      version there was a bug in detection of the language switching
      flags (sometimes removed, sometimes not). Now you can choose to
      keep the flags, to remove them, or to delete the whole utterance.

   -  bugfix in a test with ``espeak>=1.49.3``.

   -  bugfix using ``NamedTemporaryFile`` on windows, see
      `#21 <https://github.com/bootphon/phonemizer/issues/21>`__.

   -  bugfix when calling *festival* or *espeak* subprocesses on
      Windows, see
      `#17 <https://github.com/bootphon/phonemizer/issues/17>`__.

   -  bugfix in detecting recent versions of *espeak-ng*, see
      `#18 <https://github.com/bootphon/phonemizer/issues/18>`__.

   -  bugfix when using utf8 input on *espeak* backend (python2), see
      `#19 <https://github.com/bootphon/phonemizer/issues/19>`__.

-  **new features and improvements**

   -  new ``--sampa`` option to output phonemes in SAMPA alphabet
      instead of IPA, available for espeak-ng only.

   -  new ``--with-stress`` option to use with ``espeak`` backend to not
      remove the stresses on phonemized output. For instance:

      ::

         $ echo "hello world" | phonemize
         həloʊ wɜːld
         $ echo "hello world" | phonemize --with-stress
         həlˈoʊ wˈɜːld

   -  improved logging: by default only warnings are displayed, use the
      new ``--quiet`` option to inhibate all log messages or
      ``--verbose`` to see all of them. Log messages now display level
      name (debug/info/warning).

   -  improved code organization:

      -  backends are now implemented in the ``backend`` submodule as
         separated source files.

      -  improved version string (displays uninstalled backends, moved
         outside of main for use from Python).

      -  improved logger implemented in its own module so as a call to
         phonemizer from CLI or API yields the same log messages.

phonemizer-1.0
--------------

-  **incompabile changes**

   The following changes break the compatibility with previous versions
   of phonemizer (0.X.Y):

   -  command-line ``phonemize`` program: new
      ``--backend   <espeak|festival|segments>`` option, default
      language is now *espeak en-us* (was *festival en-us*),

   -  it is now illegal to have the same separator at different levels
      (for instance a space for both word and phone),

   -  from Python, must import the phonemize function as
      ``from   phonemizer.phonemize import phonemize``, was
      ``from phonemizer   import phonemize``.

-  New backend `segments <https://github.com/cldf/segments>`__ for
   phonemization based on grapheme-to-phoneme mappings.

-  Major refactoring of the backends implementation and separators (as
   Python classes).

-  Input to phonemizer now supports utf8.

-  Better handling of errors (display of a meaningful message).

-  Fixed a bug in fetching espeak version on macos, see
   `#14 <https://github.com/bootphon/phonemizer/issues/14>`__.

phonemizer-0.3.3
----------------

-  Fix a bug introduced in phonemizer-0.3.2 (apostrophes in festival
   backend). See
   `#12 <https://github.com/bootphon/phonemizer/issues/12>`__.

phonemizer-0.3.2
----------------

-  Continuous integration with tracis-ci.

-  Support for docker.

-  Better support for different versions of espeak/festival.

-  Minor bugfixes and improved tests.

phonemizer-0.3.1
----------------

-  New espeak or espeak-ng backend with more than 100 languages.

-  Support for Python 2.7 and 3.5.

-  Integration with zenodo for citation.

-  Various bugfixes and minor improvments.

phonemizer-0.2
--------------

-  First public release.

-  Support for festival backend, American English only.
