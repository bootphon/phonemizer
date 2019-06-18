# ChangeLog

Version numbers follow [semantic versioning](https://semver.org)


## phonemizer-1.0.1

* bugfix when calling *festival* or *espeak* subprocesses on Windows,
  see [#17](https://github.com/bootphon/phonemizer/issues/17).

* bugfix in detecting recent versions of *espeak-ng*, see
  [#18](https://github.com/bootphon/phonemizer/issues/18).

* bugfix when using utf8 input on *espeak* backend (python2), see
  [#19](https://github.com/bootphon/phonemizer/issues/19).


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
