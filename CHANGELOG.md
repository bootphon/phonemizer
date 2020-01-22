# ChangeLog

Version numbers follow [semantic versioning](https://semver.org)

## not yet released (will be phonemizer-2.1)

* **improvements**

  * it is now possible to specify the path to a custom ``espeak`` executable
    (for instance to use a local installation or to test different versions).
    Either specify the ``ESPEAK_PATH`` environment variable, the
    ``--espeak-path`` option from command line or use the
    ``EspeakBackend.set_espeak_path`` method from the Python API.

* **bugfixes**

  * parses correctly the version of ``espeak-ng`` even for dev versions (e.g.
    ``1.51-dev``).

  * fix an issue with ``espeak`` backend, where multiple phone separators can be
    present at the end of a word, see
    [#31](https://github.com/bootphon/phonemizer/issues/31).

## phonemizer-2.0.1

* **bugfixes**

  * ``keep-flags`` was not the default argument for ``language_switch`` in the
    class ``EspeakBackend``.

  * fixed an issue with punctuation processing in the espeak backend, see
    [#26](https://github.com/bootphon/phonemizer/issues/26)

* **improvements**

  * log a warning if using ``python2``.


## phonemizer-2.0

* **incompatible change**

  Starting with ``phonemizer-2.0`` only python3 is supported. **Compatibility
  with python2 is no more ensured nor tested.** https://pythonclock.org.

* **bugfixes**

  * new ``--language-switch`` option to use with ``espeak`` backend to deals
    with language switching on phonemized output. In previous version there was
    a bug in detection of the language switching flags (sometimes removed,
    sometimes not). Now you can choose to keep the flags, to remove them, or to
    delete the whole utterance.

  * bugfix in a test with `espeak>=1.49.3`.

  * bugfix using `NamedTemporaryFile` on windows, see
    [#21](https://github.com/bootphon/phonemizer/issues/21).

  * bugfix when calling *festival* or *espeak* subprocesses on Windows, see
    [#17](https://github.com/bootphon/phonemizer/issues/17).

  * bugfix in detecting recent versions of *espeak-ng*, see
    [#18](https://github.com/bootphon/phonemizer/issues/18).

  * bugfix when using utf8 input on *espeak* backend (python2), see
    [#19](https://github.com/bootphon/phonemizer/issues/19).


* **new features and improvements**

  * new `--sampa` option to output phonemes in SAMPA alphabet instead of IPA,
    available for espeak-ng only.

  * new ``--with-stress`` option to use with ``espeak`` backend to not remove the
    stresses on phonemized output. For instance:

        $ echo "hello world" | phonemize
        həloʊ wɜːld
        $ echo "hello world" | phonemize --with-stress
        həlˈoʊ wˈɜːld

  * improved logging: by default only warnings are displayed, use the new
    ``--quiet`` option to inhibate all log messages or ``--verbose`` to see all of
    them. Log messages now display level name (debug/info/warning).

  * improved code organization:

    * backends are now implemented in the ``backend`` submodule
      as separated source files.

    * improved version string (displays uninstalled backends, moved outside of
      main for use from Python).

    * improved logger implemented in its own module so as a call to phonemizer
      from CLI or API yields the same log messages.


## phonemizer-1.0

* **incompabile changes**

  The following changes break the compatibility with previous versions
  of phonemizer (0.X.Y):

  * command-line `phonemize` program: new `--backend
    <espeak|festival|segments>` option, default language is now
    *espeak en-us* (was *festival en-us*),

  * it is now illegal to have the same separator at different levels
    (for instance a space for both word and phone),

  * from Python, must import the phonemize function as `from
    phonemizer.phonemize import phonemize`, was `from phonemizer
    import phonemize`.

* New backend [segments](https://github.com/cldf/segments) for
  phonemization based on grapheme-to-phoneme mappings.

* Major refactoring of the backends implementation and separators (as
  Python classes).

* Input to phonemizer now supports utf8.

* Better handling of errors (display of a meaningful message).

* Fixed a bug in fetching espeak version on macos, see
  [#14](https://github.com/bootphon/phonemizer/issues/14).

## phonemizer-0.3.3

* Fix a bug introduced in phonemizer-0.3.2 (apostrophes in festival
  backend). See [#12](https://github.com/bootphon/phonemizer/issues/12).


## phonemizer-0.3.2

* Continuous integration with tracis-ci.

* Support for docker.

* Better support for different versions of espeak/festival.

* Minor bugfixes and improved tests.


## phonemizer-0.3.1

* New espeak or espeak-ng backend with more than 100 languages.

* Support for Python 2.7 and 3.5.

* Integration with zenodo for citation.

* Various bugfixes and minor improvments.


## phonemizer-0.2

* First public release.

* Support for festival backend, American English only.
