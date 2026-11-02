# Copyright 2015-2021 Mathieu Bernard
#
# This file is part of phonemizer: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Phonemizer is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with phonemizer. If not, see <http://www.gnu.org/licenses/>.
"""Test of the EspeakWrapper class"""

# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import os
import pathlib
import pickle
import shutil
import sys

import pytest

from phonemizer.backend import EspeakBackend, EspeakMbrolaBackend
from phonemizer.backend.espeak.voice import EspeakVoice
from phonemizer.backend.espeak.wrapper import EspeakWrapper


@pytest.fixture
def wrapper():
    return EspeakWrapper()


def test_basic(wrapper):
    assert wrapper.version >= (1, 48)
    assert "espeak" in str(wrapper.library_path)
    assert os.path.isabs(wrapper.library_path)
    assert os.path.isabs(wrapper.data_path)  # not None, no raise


def test_available_voices(wrapper):
    espeak = set(wrapper.available_voices())
    assert espeak

    # mbrola voices are not available on Windows by default (at least on the
    # github CI pipeline)
    if sys.platform != "win32":
        mbrola = set(wrapper.available_voices("mbrola"))
        if mbrola:
            assert not espeak.intersection(mbrola)


def test_set_get_voice(wrapper):
    assert wrapper.voice is None
    with pytest.raises(RuntimeError) as err:
        wrapper.set_voice("")
    assert 'invalid voice code ""' in str(err)

    wrapper.set_voice("fr-fr")
    assert wrapper.voice.language == "fr-fr"
    assert wrapper.voice.name in (
        "French (France)",  # >1.48.3
        "french",
    )  # older espeak

    wrapper.set_voice("en-us")
    assert wrapper.voice.language == "en-us"
    assert wrapper.voice.name in (
        "English (America)",  # >1.48.3
        "english-us",
    )  # older espeak

    # no mbrola voices available on Windows and macos by default (at least on
    # the github CI pipeline)
    try:
        wrapper.set_voice("mb-af1")
        assert wrapper.voice.language == "af"
        assert wrapper.voice.name == "afrikaans-mbrola-1"
    except RuntimeError:
        pass

    with pytest.raises(RuntimeError) as err:
        wrapper.set_voice("some non existant voice code")
    assert "invalid voice code" in str(err)


def _test_pickle(voice):
    # the wrapper is pickled when using espeak backend on multiple jobs
    wrapper = EspeakWrapper()
    wrapper.set_voice(voice)

    dump = pickle.dumps(wrapper)
    wrapper2 = pickle.loads(dump)

    assert wrapper.version == wrapper2.version
    assert wrapper.library_path == wrapper2.library_path
    assert wrapper.data_path == wrapper2.data_path
    assert wrapper.voice == wrapper2.voice


def test_pickle_en_us():
    _test_pickle("en-us")


@pytest.mark.skipif(
    not EspeakMbrolaBackend.is_available()
    or not EspeakMbrolaBackend.is_supported_language("mb-fr1"),
    reason="mbrola or mb-fr1 voice not installed",
)
def test_pickle_mb_fr1():
    _test_pickle("mb-fr1")


def test_twice():
    wrapper1 = EspeakWrapper()
    wrapper2 = EspeakWrapper()

    assert wrapper1.data_path == wrapper2.data_path
    assert wrapper1.version == wrapper2.version
    assert wrapper1.library_path == wrapper2.library_path

    wrapper1.set_voice("fr-fr")
    assert wrapper1.voice.language == "fr-fr"
    wrapper2.set_voice("en-us")
    assert wrapper2.voice.language == "en-us"
    assert wrapper1.voice.language == "fr-fr"

    # pylint: disable=protected-access
    assert wrapper1._espeak._tempdir != wrapper2._espeak._tempdir


def test_deletion():
    # pylint: disable=protected-access
    wrapper = EspeakWrapper()
    path = pathlib.Path(wrapper._espeak._tempdir)
    del wrapper
    assert not path.exists()


# from https://github.com/bootphon/phonemizer/issues/153
@pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="requires /proc/self/maps")
def test_deletion_unloads_library():
    # pylint: disable=protected-access
    wrapper = EspeakWrapper()
    path = wrapper._espeak._tempdir
    assert path in pathlib.Path("/proc/self/maps").read_text()
    del wrapper
    assert path not in pathlib.Path("/proc/self/maps").read_text()


@pytest.mark.parametrize("language", ["ar", "cs", "el", "hi", "ja", "ms"])
def test_mbrola_does_not_shadow_plain_voice(wrapper, language):
    """A language with mbrola variants must still resolve to a usable voice.

    These languages list their mbrola variants under the same language code as
    the plain espeak voice, and the mbrola ones can sort first (on Windows "ar"
    lists mb/mb-ar1, mb/mb-ar2, sem/ar in that order). Selecting the first
    entry then picks a voice needing the mbrola binary, making the language
    unusable even though a working voice exists further down the list.
    """
    if not EspeakBackend.is_supported_language(language):
        pytest.skip(f"{language} is not supported by this espeak version")

    wrapper.set_voice(language)
    assert wrapper.voice is not None

    identifier = str(wrapper.voice.identifier).replace(os.sep, "/")
    assert not identifier.startswith("mb/")
    assert wrapper.text_to_phonemes("test").strip()
    
    
@pytest.mark.skipif(
    "PHONEMIZER_ESPEAK_LIBRARY" in os.environ,
    reason="PHONEMIZER_ESPEAK_LIBRARY takes precedence over the lookup",
)
def test_library_found_without_configuration():
    """The library must be found on a stock installation.

    On Windows the official espeak-ng installer names the DLL
    "libespeak-ng.dll". ctypes.util.find_library does not add a "lib" prefix
    there (unlike Linux, where "espeak-ng" resolves to "libespeak-ng.so"), so
    looking up only "espeak-ng"/"espeak" missed an installation that was
    already on PATH.
    """
    library = EspeakWrapper.library()
    assert library
    assert pathlib.Path(str(library)).name.lower().startswith(("espeak", "libespeak"))


def test_pickle_library_and_data_path(tmp_path):
    # set_library() and set_data_path() are not called in the processes of
    # parallel jobs, the pickled wrapper must carry the library and data path
    default = EspeakWrapper()
    library = tmp_path / default.library_path.name
    shutil.copy(default.library_path, library)
    try:
        EspeakWrapper.set_library(str(library))
        EspeakWrapper.set_data_path(str(default.data_path))
        dump = pickle.dumps(EspeakWrapper())
    finally:
        EspeakWrapper.set_library(None)
        EspeakWrapper.set_data_path(None)

    # pylint: disable=protected-access
    wrapper = pickle.loads(dump)
    assert wrapper.library_path == library.resolve()
    assert wrapper._data_path_override == str(default.data_path)


def test_pickle_from_older_version():
    # wrappers pickled by phonemizer<3.5 have no library and data path
    # overrides, they must load with the default espeak
    wrapper = EspeakWrapper()
    wrapper.set_voice("en-us")
    state = wrapper.__getstate__()
    del state["library_override"], state["data_path_override"]

    wrapper2 = EspeakWrapper.__new__(EspeakWrapper)
    wrapper2.__setstate__(state)
    assert wrapper2.library_path == wrapper.library_path
    assert wrapper2.voice == wrapper.voice


def test_failed_load_removes_tempdir(monkeypatch, tmp_path):
    # the copy of the library is made in a temporary directory, which must be
    # removed if the copy cannot be made or loaded (e.g. on a noexec /tmp)
    from phonemizer.backend.espeak import api  # pylint: disable=import-outside-toplevel
    monkeypatch.setattr(api.tempfile, "mkdtemp", lambda: str(tmp_path / "copy"))
    (tmp_path / "copy").mkdir()

    def failing_copy(*args, **kwargs):
        raise OSError("cannot copy")

    monkeypatch.setattr(api.shutil, "copy", failing_copy)
    with pytest.raises(OSError):
        api.EspeakAPI(EspeakWrapper.library(), None)
    assert not (tmp_path / "copy").exists()


def test_deletion_error_removes_tempdir(monkeypatch, tmp_path):
    # an error while freeing the library must not leave the tempdir behind
    from phonemizer.backend.espeak import api  # pylint: disable=import-outside-toplevel

    class Library:  # pylint: disable=too-few-public-methods
        def espeak_Terminate(self):  # pylint: disable=invalid-name
            pass

    def failing_unload(_):
        raise OSError("cannot unload")

    monkeypatch.setattr(api.EspeakAPI, "_unload", staticmethod(failing_unload))
    with pytest.raises(OSError):
        api.EspeakAPI._delete(Library(), str(tmp_path))
    assert not tmp_path.exists()


def test_failed_init_unloads_library(monkeypatch, tmp_path):
    # a library that loads but cannot be initialized must be unloaded and its
    # tempdir removed
    from phonemizer.backend.espeak import api  # pylint: disable=import-outside-toplevel

    class NotEspeak:  # pylint: disable=too-few-public-methods
        """A shared library without the espeak_Initialize function"""

    loaded = []
    load_library = api.ctypes.cdll.LoadLibrary

    def fake_load_library(path):
        # the first call loads the original library to find its path, the
        # second one loads the copy
        loaded.append(path)
        return load_library(path) if len(loaded) == 1 else NotEspeak()

    unloaded = []
    monkeypatch.setattr(api.ctypes.cdll, "LoadLibrary", fake_load_library)
    monkeypatch.setattr(
        api.EspeakAPI, "_unload", staticmethod(unloaded.append))
    monkeypatch.setattr(api.tempfile, "mkdtemp", lambda: str(tmp_path / "copy"))
    (tmp_path / "copy").mkdir()

    with pytest.raises(RuntimeError, match="failed to load espeak library"):
        api.EspeakAPI(EspeakWrapper.library(), None)
    assert len(unloaded) == 1 and isinstance(unloaded[0], NotEspeak)
    assert not (tmp_path / "copy").exists()


def test_data_path_not_a_directory(tmp_path):
    EspeakWrapper.set_data_path(str(tmp_path / "missing"))
    try:
        with pytest.raises(RuntimeError, match="not a readable directory"):
            EspeakWrapper()
    finally:
        EspeakWrapper.set_data_path(None)


def test_data_path_from_environment(monkeypatch, tmp_path):
    data_path = EspeakWrapper().data_path
    monkeypatch.setenv("PHONEMIZER_ESPEAK_DATA_PATH", str(data_path))
    assert EspeakWrapper().data_path == data_path

    monkeypatch.setenv("PHONEMIZER_ESPEAK_DATA_PATH", str(tmp_path / "missing"))
    with pytest.raises(RuntimeError, match="not a readable directory"):
        EspeakWrapper()


def test_mbrola_voice_listed_first(wrapper, monkeypatch):
    # on Windows, mbrola voices can be listed before the plain espeak voice of
    # the same language: they must be skipped
    voices = wrapper.available_voices()
    mbrola = EspeakVoice(name="mbrola", language="en-us", identifier="mb/mb-us1")
    monkeypatch.setattr(wrapper, "available_voices", lambda: [mbrola] + voices)
    wrapper.set_voice("en-us")
    assert not wrapper.voice.identifier.startswith("mb/")


def _data_dir(path):
    path.mkdir(parents=True)
    (path / "phontab").touch()
    return path


@pytest.mark.parametrize("version", [(1, 48), (1, 51)])
def test_data_path_argument(tmp_path, version):
    # espeak<1.49 expects the parent of the data directory, named espeak-data;
    # espeak-ng accepts the data directory or its parent (if the data
    # directory is named espeak-ng-data). Otherwise espeak exits the process.
    from phonemizer.backend.espeak.api import EspeakAPI  # pylint: disable=import-outside-toplevel
    # pylint: disable=protected-access
    argument = EspeakAPI._data_path_argument

    name = "espeak-data" if version < (1, 49) else "espeak-ng-data"
    data = _data_dir(tmp_path / name)
    expected = tmp_path if version < (1, 49) else data
    assert argument(data, version) == str(expected).encode()
    assert argument(tmp_path, version) == str(tmp_path).encode()

    other = _data_dir(tmp_path / "other")
    if version < (1, 49):
        with pytest.raises(RuntimeError, match="no espeak data found"):
            argument(other, version)
    else:
        assert argument(other, version) == str(other).encode()

    with pytest.raises(RuntimeError, match="no espeak data found"):
        argument(tmp_path / "missing", version)


def test_data_path_without_data(tmp_path):
    # a directory without espeak data raises an error instead of exiting
    EspeakWrapper.set_data_path(str(tmp_path))
    try:
        with pytest.raises(RuntimeError, match="no espeak data found"):
            EspeakWrapper()
    finally:
        EspeakWrapper.set_data_path(None)


# from https://github.com/bootphon/phonemizer/issues/196
@pytest.mark.skipif(sys.platform == "win32", reason="symlinks need privileges")
def test_data_path_too_long(tmp_path):
    # espeak silently ignores a data path longer than its 160 bytes buffer and
    # uses its default data instead
    data_path = EspeakWrapper().data_path
    # a real directory (the path is resolved by EspeakWrapper), with links to
    # the files of the espeak data to save copying them
    long_path = tmp_path / ("d" * 170) / "espeak-data"
    long_path.mkdir(parents=True)
    for child in data_path.iterdir():
        (long_path / child.name).symlink_to(child)
    assert len(str(long_path)) > 160

    EspeakWrapper.set_data_path(str(long_path))
    try:
        wrapper = EspeakWrapper()
    finally:
        EspeakWrapper.set_data_path(None)

    # pylint: disable=protected-access
    # espeak uses a short link to the data, in the tempdir of the library
    _, path_home = wrapper._espeak.info()
    assert path_home.decode().startswith(wrapper._espeak._tempdir)
    assert pathlib.Path(path_home.decode()).resolve() == long_path.resolve()
    wrapper.set_voice("en-us")
    assert wrapper.text_to_phonemes("hello").strip()


def test_data_path_too_long_without_link(tmp_path, monkeypatch):
    from phonemizer.backend.espeak.api import EspeakAPI  # pylint: disable=import-outside-toplevel
    # pylint: disable=protected-access
    data = _data_dir(tmp_path / ("d" * 170) / "espeak-ng-data")
    with pytest.raises(RuntimeError, match="too long for espeak"):
        EspeakAPI._data_path_argument(data, (1, 52))

    def failing_symlink(*args, **kwargs):
        raise OSError("symbolic link privilege not held")

    monkeypatch.setattr(os, "symlink", failing_symlink)
    with pytest.raises(RuntimeError, match="privilege not held"):
        EspeakAPI._data_path_argument(data, (1, 52), tmp_path)


# from https://github.com/bootphon/phonemizer/issues/180
def test_espeak_too_old(monkeypatch):
    from phonemizer.backend.espeak import api  # pylint: disable=import-outside-toplevel
    monkeypatch.setattr(api.EspeakAPI, "_version", lambda self: (1, 47))
    with pytest.raises(RuntimeError, match=r"espeak-1\.47 is not supported"):
        EspeakWrapper()
    assert not EspeakBackend.is_available()
    with pytest.raises(RuntimeError, match="espeak not installed on your system"):
        EspeakBackend("en-us")
