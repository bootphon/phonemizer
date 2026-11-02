# Changelog

Version numbers follow [semantic versioning](https://semver.org).

## phonemizer-3.6.0

This release makes the espeak backend faster and, with
`preserve_punctuation=True`, pronounces the words around quotes and brackets
in context, which changes the output of such lines.

- **behaviour changes**
  - With `preserve_punctuation=True`, the words on both sides of quotes and
    brackets (`"«»“”‘’„‹›()[]{}`) are pronounced together, as without
    punctuation. They used to be phonemized apart, as at the end of a
    sentence: `les (amis)` gave `le (ami)` in French, and is now `lez (ami)`;
    `an (apple)` gave `æn (æpəl)` in English, and is now `ɐn (æpəl)`. The
    other marks, such as commas or periods, still end an utterance. The
    output changes only on lines with quotes or brackets between words.
    These words are phonemized twice, alone and together, which costs time on
    such lines. When the backend joins words across a mark (espeak joins *do
    not* in English) or splits a word, the mark cannot be placed for sure in
    the words phonemized together, and the words are phonemized apart as
    before. The `segments` backend, which phonemizes each word alone, is not
    concerned. See [PR #233](https://github.com/bootphon/phonemizer/pull/233).
  - `Punctuation.preserve()` returns the chunks to phonemize and, for each
    line, its parts: chunk indices and punctuation marks. It replaces the
    list of `_MarkIndex` it returned before, and `Punctuation.restore()`
    takes these parts. `Punctuation.preserve_lines()` is removed. The new
    `Punctuation.is_inline()` and `Punctuation.inline_groups()` tell which
    chunks are pronounced together, and `Punctuation.can_align()` whether
    the marks can be placed in context with a given separator (not with an
    empty word separator, for instance). See [PR #233](https://github.com/bootphon/phonemizer/pull/233).
- **improvements**
  - Creating an espeak backend is about 3 times faster (from 28 to 8 ms on
    Linux): the espeak library found on the system is now looked up once per
    process instead of at each creation. `set_library()` and
    `PHONEMIZER_ESPEAK_LIBRARY` still apply at any time, but an espeak
    library installed or removed after the first lookup is not seen until the
    process restarts. See [PR #232](https://github.com/bootphon/phonemizer/pull/232).
  - The espeak backend is about 12% faster: the post-processing of espeak
    output is 2.5 times faster, and the words are counted with `str.split()`
    rather than regular expressions. The outputs are unchanged. See [PR
    #232](https://github.com/bootphon/phonemizer/pull/232).
- **bug fixes**
  - Restoring the punctuation (`preserve_punctuation=True`) took a time
    quadratic in the number of lines: about 11 seconds for 20,000 lines, now
    40 milliseconds. `Punctuation.restore()` no longer modifies the list it
    is given. See [PR #232](https://github.com/bootphon/phonemizer/pull/232).
  - With `preserve_punctuation=True`, a line made only of punctuation marks
    was merged with the next ones made only of marks, so that the output had
    fewer lines than the input. It also removed the word separator ending the
    next line, as did a line starting with a mark when the punctuation of
    later lines was restored. A line removed by
    `language_switch='remove-utterance'` is now empty, as without
    punctuation, where it was sometimes a word separator. See [PR #233](https://github.com/bootphon/phonemizer/pull/233).
  - With `preserve_punctuation=True`, a word separator containing a backslash
    raised an error (`\`) or was read as an escape sequence (`\n` gave a new
    line). It is now inserted as is. See [PR
    #232](https://github.com/bootphon/phonemizer/pull/232).

## phonemizer-3.5.0

This release requires Python 3.10 or later, leaves the `phonemizer` logger to the
application, and fixes many bugs, among them a memory leak of the espeak
backend and installation issues on Windows, macOS and FreeBSD.

- **breaking changes**
  - Python 3.8 and 3.9, which have reached their end of life, are no longer
    supported. The phonemizer now requires `python>=3.10`. Users of older
    Python versions are served the phonemizer-3.4 release by pip.
  - The phonemizer no longer configures the `phonemizer` logger. By default
    its messages are handled by the logging configuration of the application,
    which can tune it as usual, for instance with
    `logging.getLogger('phonemizer').setLevel(logging.ERROR)`. The level was
    previously forced to `WARNING`, so an application logging at the
    `INFO` or `DEBUG` level now gets the phonemizer messages of that
    level. The loggers returned by `get_logger()` no longer propagate to the
    application, so `get_logger('quiet')` is actually quiet. See [issue #154](https://github.com/bootphon/phonemizer/issues/154).
  - Lines are separated by `\n` on every platform. On Windows, a string
    given to `phonemize()` is now split on `\n` (it was split on `\r\n`
    only), and a string output is joined with `\n` (it was `\r\n`). The
    `phonemize` command writes its output in text mode, so its files still
    use the native line ending (they had `\r\r\n` on Windows).
- **improvements**
  - When a backend cannot be loaded, the error tells why after the usual
    `espeak not installed on your system` message, for instance the library
    path or a missing dependency of the espeak library. See [issue
    #189](https://github.com/bootphon/phonemizer/issues/189).
  - Language codes are case insensitive: `en-US` is accepted as `en-us`. See
    [issue #200](https://github.com/bootphon/phonemizer/issues/200).
- **bug fixes**
  - `words_mismatch='remove'` with `preserve_punctuation=True` removed
    the wrong lines or raised an `IndexError`. See [issue #181](https://github.com/bootphon/phonemizer/issues/181).
  - Each espeak backend leaked about 5 MB of memory: the espeak library was
    never terminated nor unloaded when the backend was deleted. See [issue
    #153](https://github.com/bootphon/phonemizer/issues/153).
  - On Windows, the temporary copies of the espeak library are now removed
    when the backend is deleted, instead of at the end of the Python
    process. They are also removed when the library fails to load. See
    [issue #147](https://github.com/bootphon/phonemizer/issues/147).
  - With `njobs > 1`, the espeak library and data path set with
    `set_library()` and `set_data_path()` were ignored by the parallel
    jobs, which used the default espeak installation.
  - The backends cached by `phonemize()` were reused after a call to
    `set_library()`, `set_data_path()` or `set_executable()`.
  - `punctuation_marks=''` made espeak spell out every letter, it now
    disables the punctuation processing.
  - `phonemize --list-languages` printed `None` at the end.
  - With espeak<1.49, a data path set with `set_data_path()` or
    `PHONEMIZER_ESPEAK_DATA_PATH` made espeak exit the Python process, as it
    expects the parent of the data directory. The data directory is now
    accepted by all espeak versions, and a path without espeak data raises a
    `RuntimeError`.
  - The festival backend dropped the lines it could not phonemize (empty
    once cleaned, or without words), shifting the next lines with respect to
    the input, for instance with `prepend_text`. It now outputs an empty line
    for them, as the espeak backend does: `phonemize(['hello', '()'],
    backend='festival')` gives `['hhaxlow ', '']` instead of `['hhaxlow ']`.
  - The festival executable can be in a directory whose name has spaces.
  - An espeak data directory with a path longer than 159 bytes (229 on
    Windows) was silently ignored by espeak, which then looked for its data
    elsewhere. Such a path is now given to espeak through a shorter link. See
    [issue #196](https://github.com/bootphon/phonemizer/issues/196).
  - espeak versions older than 1.48, which crash on phonemization, are
    refused with a clear error. See [issue
    #180](https://github.com/bootphon/phonemizer/issues/180).
  - The espeak library is looked for in the standard directories when its
    path cannot be retrieved from the loaded library (e.g. on FreeBSD), and
    `phonemize --version` works for a renamed distribution of phonemizer or
    when running from sources. See [issue
    #209](https://github.com/bootphon/phonemizer/issues/209).
- **documentation**
  - The installation of festival and mbrola on MacOS is documented, the
    setup script formerly suggested no longer works. See [issue
    #203](https://github.com/bootphon/phonemizer/issues/203).
- **tests**
  - The festival tests expect the syllables of the installed festival
    version, they no longer fail on festival-2.4. The tests no longer depend
    on a `python` executable nor on the transcription of a given espeak
    build. See [issue #221](https://github.com/bootphon/phonemizer/issues/221)
    and [issue #209](https://github.com/bootphon/phonemizer/issues/209).

## phonemizer-3.4.1

This release fixes two regressions of 3.4.0: `phonemize()` is thread-safe
again and the festival backend works outside of the tests.

- **bug fixes**
  - A sentence-final period no longer splits a decimal point that the
    punctuation matcher already kept, so `3.14 is pi.` and `1.5.` stay
    one chunk. `see 3.14!` is still one chunk. See [PR #222](https://github.com/bootphon/phonemizer/pull/222).
  - Lifetime of EspeakWrapper cannot be dropped because of the usage of lru cache,
    which cause lots of EspeakWrapper being created when using multi threads,
    that makes a bunch of folder created under /tmp, finally cause the fd run out
    and program panics. See [PR #224](https://github.com/bootphon/phonemizer/pull/224).
  - The festival backend failed with `AttributeError: module 'importlib' has no attribute 'resources'` outside of pytest, including from the
    `phonemize` command (regression in 3.4.0).
  - `phonemize()` is thread-safe again: the backend cache introduced in
    3.4.0 shared a single espeak instance between threads, yielding wrong
    outputs or errors. Backends are now cached per thread.

## phonemizer-3.4.0

This release makes `phonemize()` reuse its backends across calls, lets you
choose the espeak data directory, and keeps decimal numbers such as `19,99`
whole when processing the punctuation.

- **improvements**
  - The espeak data directory can now be chosen with
    `EspeakWrapper.set_data_path()` or the environment variable
    `PHONEMIZER_ESPEAK_DATA_PATH`. See [PR #213](https://github.com/bootphon/phonemizer/pull/213).
  - `phonemize()` now reuses backend instances across calls instead of
    building a new one every time. See [PR #212](https://github.com/bootphon/phonemizer/pull/212).
- **bug fixes**
  - **Behaviour change:** a comma or period between two digits is no longer
    treated as punctuation, so numbers such as `19,99` and `3.14` are kept
    whole instead of being split into two numbers. Splitting them changed the
    spoken output. The previous behaviour can still be obtained by passing an
    explicit regex as `punctuation_marks`. See [PR #216](https://github.com/bootphon/phonemizer/pull/216).
  - Selecting a language by its code no longer resolves to an mbrola variant
    that shadows the plain espeak voice, which made such languages unusable
    when the mbrola binary is absent. See [PR #215](https://github.com/bootphon/phonemizer/pull/215).
  - The espeak library is now also looked up under its `lib`-prefixed names,
    so a stock espeak-ng installation on Windows is found. See [PR #214](https://github.com/bootphon/phonemizer/pull/214).
  - Tests related to <span class="title-ref">festival</span> backend are now skipped when <span class="title-ref">festival</span> is not installed on the system.
  - Improved espeak library lookup on macos.
  - Unusable mbrola voices are filtered out on Windows.
  - Make the segments backend an optional dependency. See [PR #211](https://github.com/bootphon/phonemizer/pull/211).

## phonemizer-3.3.0

**This version depends on python>=3.8 (was 3.6 in previous versions). Tests now
requires pytest>=6.0**

- **improvements**
  - Replaced dependency to deprecated `pkg_resources` by `importlib`
    (requires python>=3.8).
  - Replaced deprecated `setup.py` by `pyproject.toml`.
- **bug fix**
  - `espeak` backend: words mismatch now works when using custom word
    separators. See [issue #169](https://github.com/bootphon/phonemizer/issues/169).

## phonemizer-3.2.1

- **bug fixes**
  - Fixed a bug when trying to restore punctuation on a multiline text.
    See [issue #129](https://github.com/bootphon/phonemizer/issues/129).

## phonemizer-3.2.0

- **bug fixes**
  - Fixed a bug when trying to restore punctuation on very long text.
    See [issue #108](https://github.com/bootphon/phonemizer/issues/108).
- **improvements**
  - Improved consistency with the handling of word separators when
    preserving punctuation, and when using a word separator that is
    not a literal space character. See
    [issue #106](https://github.com/bootphon/phonemizer/issues/106).
- **new features**
  - Added the option to define punctuation with a regular expression.
    Previously only strings were accepted. See
    [PR #120](https://github.com/bootphon/phonemizer/pull/120)
    - In the python API, the `punctuation_marks` parameter can now be
      passed to `phonemize` (or a backend constructor) as a `re.Pattern`
      that defines which characters will be matched as punctuation.
      Passing `punctuation_marks` as a str will continue to function as
      before, treating each character in the string as a punctuation mark.
    - Added the optional parameter `--punctuation_marks_is_regex` to the CLI
      interface. When used, the CLI will attempt to compile a `re.Pattern`
      from the value passed to `--punctuation-marks`.

## phonemizer-3.1.1

- **improvements**
  - Preserve empty lines in texts when using
    `--preserve-empty-lines`. Without this option, empty lines used
    to be automatically dropped. See [PR
    #103](https://github.com/bootphon/phonemizer/pull/103)
- **new features**
  - Type hinted most of `phonemizer`’s API. This makes the usage
    of our API a bit clearer, and can be easily leveraged by IDE’s and
    type checkers to prevent typing issues.

## phonemizer-3.0.1

- **bug fixes**
  - The method `BaseBackend.phonemize` now raises a `RuntimeError`
    if the input text is a str instead of a list of of str (was only
    logging an error message).
  - Preserve punctuation alignement when using
    `--preserve-punctuation`, was inserting a space before each
    punctuation token, see [issue
    #97](https://github.com/bootphon/phonemizer/issues/97).

## phonemizer-3.0

- **breaking change**

  - Do not remove empty lines from output. For example:

  ``` python
  # this is now
  phonemize(["hello", "!??"]) == ['həloʊ ', '']
  # this was
  phonemize(["hello", "!??"]) == ['həloʊ ']
  ```

  - Default backend in the `phonemize` function is now `espeak`
    (was `festival`).
  - `espeak-mbrola` backend now requires `espeak>=1.49`.
  - `--espeak-path` option renamed as `--espeak-library`and
    `PHONEMIZER_ESPEAK_PATH` environment variable renamed as
    `PHONEMIZER_ESPEAK_LIBRARY`.
  - `--festival-path` option renamed as `--festival-executable`
    and `PHONEMIZER_FESTIVAL_PATH` environment variable renamed as
    `PHONEMIZER_FESTIVAL_EXECUTABLE`.
  - The methods `backend.phonemize()` from the backend classes take
    only a list of str a input text (was either a str or a list of
    str).
  - The methods `backend.version()` from the backend classes returns
    a tuple of int instead of a str.

- **improvements**

  - `espeak` and `mbrola` backends now rely on the `espeak`
    shared library using the `ctypes` Python module, instead of
    reliying on the `espeak` executable through subprocesses. This
    implies **drastic speed improvments, up to 40 times faster**.

- **new features**

  - New option `--prepend-text` to prepend the input text to
    phonemized utterances, so as to have both orthographic and
    phonemized available at output.
  - New option `--tie` for the `espeak` backend to display a tie
    character within multi-letter phonemes. (see issue
    [#74](https://github.com/bootphon/phonemizer/issues/74)).
  - New option `--words-mismatch` for the `espeak` backend. This
    allows to detect when espeak merge consecutive words or drop a
    word from the orthographic text. Possible actions are to ignore
    those misatches, to issue a warning for each line where a mismatch
    is detectd, or to remove those lines from the output.

- **bugfixes**

  - phonemizer’s logger no more conflicts with other loggers when
    imported from Python (see PR
    [#61](https://github.com/bootphon/phonemizer/pull/61)).

## phonemizer-2.2.2

- **bugfixes**
  - fixed installation from source (bug introduced in 2.2.1, see issue
    [#52](https://github.com/bootphon/phonemizer/issues/52)).
  - Fixed a bug when trying to restore punctuation on an empty text
    (see issue
    [#54](https://github.com/bootphon/phonemizer/issues/54)).
  - Fixed an edge case bug when using custom punctuation marks (see
    issue [#55](https://github.com/bootphon/phonemizer/issues/55)).
  - Fixed regex issue that causes digits to be considered punctuation
    (see issue
    [#60](https://github.com/bootphon/phonemizer/pull/60)).

## phonemizer-2.2.1

- **improvements**

  From Python import the phonemize function using
  `from phonemizer import phonemize` instead of
  `from phonemizer.phonemize import phonemize`. The second import is
  still available for compatibility.

- **bugfixes**

  - Fixed a minor bug in `utils.chunks`.
  - Fixed warnings on language switching for espeak backend when using
    parallel jobs (see issue
    [#50](https://github.com/bootphon/phonemizer/issues/50)).
  - Save file in utf-8 explicitly for Windows compat (see issue
    [#43](https://github.com/bootphon/phonemizer/issues/43)).
  - Fixed build and tests in Dockerfile (see issue
    [#45](https://github.com/bootphon/phonemizer/issues/45)).

## phonemizer-2.2

- **new features**
  - New option `--list-languages` to list the available languages
    for a given backend from the command line.
  - The `--sampa` option of the `espeak` backend has been replaced
    by a new backend `espeak-mbrola`.
    - The former `--sampa` option (introduced in phonemizer-2.0)
      outputs phones that are not standard SAMPA but are adapted to
      the espeak TTS front-end.
    - On the other hand the `espeak-mbrola` backend allows espeak
      to output phones in standard SAMPA (adapted to the mbrola TTS
      front-end). This backend requires mbrola to be installed, as
      well as additional mbrola voices to support needed languages.
      **This backend does not support word separation nor punctuation
      preservation**.
- **bugfixes**
  - Fixed issues with punctuation processing on some corner cases, see
    issues [#39](https://github.com/bootphon/phonemizer/issues/39)
    and [#40](https://github.com/bootphon/phonemizer/issues/40).
  - Improvments and updates in the documentation (Readme,
    `phonemize --help` and Python code).
  - Fixed a test when using `espeak>=1.50`.
  - Empty lines are correctly ignored when reading text from a file.

## phonemizer-2.1

- **new features**
  - Possibility to preserve the punctuation (ignored and silently
    removed by default) in the phonemized output with the new option
    `--preserve-punctuation` from command line (or the equivalent
    `preserve-punctuation` from Python API). With the
    `punctuation-marks` option, one can overload the default marls
    considered as punctuation.
  - It is now possible to specify the path to a custom `espeak` or
    `festival` executable (for instance to use a local installation
    or to test different versions). Either specify the
    `PHONEMIZER_ESPEAK_PATH` environment variable, the
    `--espeak-path` option from command line or use the
    `EspeakBackend.set_espeak_path` method from the Python API.
    Similarly for festival use `PHONEMIZER_FESTIVAL_PATH`,
    `--festival-path` or `FestivalBackend.set_festival_path`.
  - The `--sampa` option is now available for espeak (was available
    only for espeak-ng).
  - When using `espeak` with SAMPA output, some SAMPA phones are
    corrected to correspond to the normalized SAMPA alphabet (espeak
    seems not to respect it). The corrections are language specific. A
    correction file must be placed in `phonemizer/share/espeak`.
    This have been implemented only for French by now.
- **bugfixes**
  - parses correctly the version of `espeak-ng` even for dev
    versions (e.g. `1.51-dev`).
  - fixed an issue with `espeak` backend, where multiple phone
    separators can be present at the end of a word, see
    [#31](https://github.com/bootphon/phonemizer/issues/31).
  - added an additional stress symbol `-` for `espeak`.

## phonemizer-2.0.1

- **bugfixes**
  - `keep-flags` was not the default argument for
    `language_switch` in the class `EspeakBackend`.
  - fixed an issue with punctuation processing in the espeak backend,
    see [#26](https://github.com/bootphon/phonemizer/issues/26)
- **improvements**
  - log a warning if using `python2`.

## phonemizer-2.0

- **incompatible change**

  Starting with `phonemizer-2.0` only python3 is supported.
  **Compatibility with python2 is no more ensured nor tested.**
  <https://pythonclock.org>.

- **bugfixes**

  - new `--language-switch` option to use with `espeak` backend to
    deals with language switching on phonemized output. In previous
    version there was a bug in detection of the language switching
    flags (sometimes removed, sometimes not). Now you can choose to
    keep the flags, to remove them, or to delete the whole utterance.
  - bugfix in a test with `espeak>=1.49.3`.
  - bugfix using `NamedTemporaryFile` on windows, see
    [#21](https://github.com/bootphon/phonemizer/issues/21).
  - bugfix when calling *festival* or *espeak* subprocesses on
    Windows, see
    [#17](https://github.com/bootphon/phonemizer/issues/17).
  - bugfix in detecting recent versions of *espeak-ng*, see
    [#18](https://github.com/bootphon/phonemizer/issues/18).
  - bugfix when using utf8 input on *espeak* backend (python2), see
    [#19](https://github.com/bootphon/phonemizer/issues/19).

- **new features and improvements**

  - new `--sampa` option to output phonemes in SAMPA alphabet
    instead of IPA, available for espeak-ng only.

  - new `--with-stress` option to use with `espeak` backend to not
    remove the stresses on phonemized output. For instance:

        $ echo "hello world" | phonemize
        həloʊ wɜːld
        $ echo "hello world" | phonemize --with-stress
        həlˈoʊ wˈɜːld

  - improved logging: by default only warnings are displayed, use the
    new `--quiet` option to inhibate all log messages or
    `--verbose` to see all of them. Log messages now display level
    name (debug/info/warning).

  - improved code organization:

    - backends are now implemented in the `backend` submodule as
      separated source files.
    - improved version string (displays uninstalled backends, moved
      outside of main for use from Python).
    - improved logger implemented in its own module so as a call to
      phonemizer from CLI or API yields the same log messages.

## phonemizer-1.0

- **incompabile changes**

  The following changes break the compatibility with previous versions
  of phonemizer (0.X.Y):

  - command-line `phonemize` program: new
    `--backend   <espeak|festival|segments>` option, default
    language is now *espeak en-us* (was *festival en-us*),
  - it is now illegal to have the same separator at different levels
    (for instance a space for both word and phone),
  - from Python, must import the phonemize function as
    `from   phonemizer.phonemize import phonemize`, was
    `from phonemizer   import phonemize`.

- New backend [segments](https://github.com/cldf/segments) for
  phonemization based on grapheme-to-phoneme mappings.

- Major refactoring of the backends implementation and separators (as
  Python classes).

- Input to phonemizer now supports utf8.

- Better handling of errors (display of a meaningful message).

- Fixed a bug in fetching espeak version on macos, see
  [#14](https://github.com/bootphon/phonemizer/issues/14).

## phonemizer-0.3.3

- Fix a bug introduced in phonemizer-0.3.2 (apostrophes in festival
  backend). See
  [#12](https://github.com/bootphon/phonemizer/issues/12).

## phonemizer-0.3.2

- Continuous integration with tracis-ci.
- Support for docker.
- Better support for different versions of espeak/festival.
- Minor bugfixes and improved tests.

## phonemizer-0.3.1

- New espeak or espeak-ng backend with more than 100 languages.
- Support for Python 2.7 and 3.5.
- Integration with zenodo for citation.
- Various bugfixes and minor improvments.

## phonemizer-0.2

- First public release.
- Support for festival backend, American English only.
