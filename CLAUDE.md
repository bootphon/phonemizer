# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`phonemizer` converts text to phones (G2P) in many languages, exposed as the
Python function `phonemizer.phonemize()` and the `phonemize` CLI
(`phonemizer/main.py`). It wraps four backends: `espeak`, `espeak-mbrola`,
`festival` and `segments`. Most tests need the system tools installed
(`espeak-ng`, `festival`, `mbrola` with voices `mbrola-fr1`/`mbrola-af1`);
tests skip themselves when a backend or a version-specific feature is missing.

## Commands

Plain pip:

```bash
pip install -e .[test,segments]
pytest                                   # coverage enabled via addopts
pytest test/test_punctuation.py::test_name -v
```

With pixi (config in `pyproject.toml`):

```bash
pixi run test                            # default test env
pixi run -e py310 test                   # also py314, py315
pixi run lint                            # ruff on phonemizer and test
```

Docs (Sphinx with myst-parser, in `docs/source`): `pip install .[doc]` then
`make -C docs html`. The changelog page includes the root `CHANGELOG.md`.

CI (`.github/workflows`) runs on Linux, macOS and Windows, on the minimum supported
and latest Pythons, and against espeak 1.48.15 and espeak-ng 1.51.1. Keep code
compatible with the oldest Python in `requires-python` (`pyproject.toml`).

## Architecture

- **Entry point** `phonemize.py`: validates arguments, then builds a backend
  from the `BACKENDS` registry. Backend instances are kept in a small LRU cache
  (`_cached_backend`), **local to each thread** (a backend must never be shared
  between threads). Its key is the full constructor configuration, including
  the logger and the backend's `_installation()` (library, data path or
  executable in use). Add any new constructor option or configuration source
  to the key, or it will return a stale backend. `clear_backends_cache()`
  resets it for all threads. `_phonemize()` normalizes input (str ↔ list of
  lines, empty lines, `prepend_text`).
- **Backend registry** `backend/__init__.py`: `BACKENDS` is a dict subclass
  that imports `segments` lazily, so the optional `segments` dependency is only
  needed when that backend is used. Don't import `segments` eagerly.
- **`BaseBackend`** (`backend/base.py`): the template for every backend.
  `phonemize()` runs `_phonemize_preprocess` (punctuation removed or saved via
  `Punctuation`), then the abstract `_phonemize_aux` (on chunks with `joblib`
  when `njobs > 1`, so backends must pickle), then `_phonemize_postprocess`
  (punctuation restored).
- **espeak** (`backend/espeak/`): no subprocess; it calls libespeak(-ng) via
  ctypes.
  - `api.py` (`EspeakAPI`) holds the low-level bindings. Each instance
    **copies the shared library into a temp dir** before `dlopen`, because
    espeak uses global state and the same `.so` can't be loaded twice.
  - `wrapper.py` (`EspeakWrapper`) is the higher-level API: voices, version,
    `text_to_phonemes`. Custom pickling (`__getstate__`/`__setstate__`)
    re-creates the library for parallel jobs. It carries only the
    `set_library()`/`set_data_path()` values, never resolved paths, and must
    keep loading states pickled by older releases.
  - `base.py` is shared by `espeak.py` (IPA) and `mbrola.py` (SAMPA, which
    runs synthesis and phoneme tracing).
  - `language_switch.py` and `words_mismatch.py` are strategy classes for
    espeak's `language_switch` / `words_mismatch` options.
  - The library and data path can be overridden with
    `EspeakWrapper.set_library()` / `set_data_path()`, or with the env vars
    `PHONEMIZER_ESPEAK_LIBRARY` / `PHONEMIZER_ESPEAK_DATA_PATH`.
- **festival** (`backend/festival/`): runs the `festival` executable as a
  subprocess with the Scheme script `share/festival/phonemize.scm`, then parses
  the Lisp output with `lispy.py`. Override the executable with
  `PHONEMIZER_FESTIVAL_EXECUTABLE`.
- **segments** (`backend/segments.py`): tokenizes with a user-supplied G2P
  file. `share/segments/*.g2p` ships built-in "languages".
- **Cross-cutting**: `separator.py` (phone/syllable/word separators),
  `punctuation.py` (regex-based preserve/restore, with subtle edge cases such
  as decimals; see `test/test_punctuation.py`), `logger.py` and `utils.py`
  (`chunks`, `str2list`/`list2str`).
- **Logging**: by default messages go to the `phonemizer` logger
  (`default_logger()`), which the library never configures; the application
  does. `get_logger()` returns a configured child logger that does not
  propagate. Don't call `get_logger()` as a default.

## Conventions

- PEP 8. `CONTRIBUTING.md` asks for Google-style docstrings, but most existing
  code uses NumPy-style `Parameters`/`Returns` sections. Match the surrounding
  file.
- Every source file starts with the GPLv3 copyright header.
- Record user-visible changes under `unreleased` in
  `CHANGELOG.md` (included in the docs), linking the PR.
- The package version comes from `__version__` in `phonemizer/__init__.py`.
  `phonemizer/version.py` only formats it with the backend versions for
  `--version`.
