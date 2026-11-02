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
"""Low-level bindings to the espeak API"""

import ctypes
import os
import pathlib
import shutil
import sys
import tempfile
import weakref
from ctypes import CDLL
from pathlib import Path
from typing import Union

from phonemizer.backend.espeak.voice import EspeakVoice

if sys.platform != 'win32':
    # cause a crash on Windows
    import dlinfo


# Where to look for the espeak library when its path cannot be retrieved from
# the loaded library
_LIBRARY_DIRECTORIES = ('/usr/local/lib', '/usr/lib', '/lib')

# Size of the buffer storing the path to the espeak data directory, from
# speech.h in the espeak and espeak-ng sources
_N_PATH_HOME = 230 if sys.platform == 'win32' else 160


class EspeakAPI:
    """Exposes the espeak API to the EspeakWrapper

    This class exposes only low-level bindings to the API and should not be
    used directly.

    """

    def __init__(self, library: Union[str, Path], data_path: Union[str, Path, None]):
        # set to None to avoid an AttributeError in _delete if the __init__
        # method raises, will be properly initialized below
        self._library = None

        # Because the library is not designed to be wrapped nor to be used in
        # multithreaded/multiprocess contexts (massive use of global variables)
        # we need a copy of the original library for each instance of the
        # wrapper... (see "man dlopen" on Linux/MacOS: we cannot load two times
        # the same library because a reference is then returned by dlopen). The
        # tweak is therefore to make a copy of the original library in a
        # different (temporary) directory.
        try:
            # load the original library in order to retrieve its full path?
            # Forced as str as it is required on Windows.
            espeak: CDLL = ctypes.cdll.LoadLibrary(str(library))
            library_path = self._shared_library_path(espeak)
            del espeak
        except OSError as error:
            raise RuntimeError(
                f'failed to load espeak library: {str(error)}') from None

        # will be automatically destroyed after use
        self._tempdir = tempfile.mkdtemp()
        try:
            espeak_copy = pathlib.Path(self._tempdir) / library_path.name
            shutil.copy(library_path, espeak_copy, follow_symlinks=False)

            # finally load the library copy and initialize it. 0x02 is
            # AUDIO_OUTPUT_SYNCHRONOUS in the espeak API
            self._library = ctypes.cdll.LoadLibrary(str(espeak_copy))
            try:
                # older versions are not supported, they crash on
                # phonemization (see issue #180)
                version = self._version()
                if version < (1, 48):
                    raise RuntimeError(
                        f'espeak-{".".join(str(v) for v in version)} is not '
                        f'supported, phonemizer requires espeak>=1.48')

                if data_path is not None:
                    data_path = self._data_path_argument(
                        data_path, version, self._tempdir)
                if self._library.espeak_Initialize(0x02, 0, data_path, 0) <= 0:
                    raise RuntimeError(  # pragma: nocover
                        'failed to initialize espeak shared library')
            except AttributeError:  # pragma: nocover
                raise RuntimeError(
                    'failed to load espeak library') from None
        except BaseException:
            # do not leave the library copy behind
            if self._library is not None:
                self._unload(self._library)
            shutil.rmtree(self._tempdir, ignore_errors=True)
            raise

        # properly exit when the wrapper object is destroyed (see
        # https://docs.python.org/3/library/weakref.html#comparing-finalizers-with-del-methods).
        # This is registered once the library is loaded, so that the finalizer
        # gets it.
        weakref.finalize(self, self._delete, self._library, self._tempdir)

        # the path to the original one (the copy is considered an
        # implementation detail and is not exposed)
        self._library_path = library_path

    def _version(self):
        """The espeak version as a tuple (major, minor)

        Available before espeak_Initialize() is called.

        """
        f_info = self._library.espeak_Info
        f_info.restype = ctypes.c_char_p
        version = f_info(ctypes.byref(ctypes.c_char_p()))
        # espeak-1.48 appends the release date to the version number
        version = version.decode().strip().split(' ')[0].replace('-dev', '')
        return tuple(int(v) for v in version.split('.')[:2])

    @staticmethod
    def _data_path_argument(data_path, version, tempdir=None) -> bytes:
        """Returns the data path to give to espeak_Initialize()

        `data_path` is the espeak data directory, containing the phontab file.
        espeak-ng accepts it as is, or its parent directory. espeak<1.49
        expects the directory containing it, which must be named espeak-data.

        espeak stores the path of its data directory in a buffer of
        _N_PATH_HOME bytes and silently uses its default data when the path
        is longer. In that case a link to the data is made in `tempdir` and
        its shorter path is given to espeak instead.

        Raises a RuntimeError if espeak cannot read its data from `data_path`:
        espeak would exit the whole process instead.

        """
        data_path = pathlib.Path(data_path)
        if version < (1, 49):
            if data_path.name == 'espeak-data':
                data_path = data_path.parent
            data = data_path / 'espeak-data'
        elif (data_path / 'phontab').is_file():
            data = data_path
        else:
            data = data_path / 'espeak-ng-data'

        if not (data / 'phontab').is_file():
            raise RuntimeError(f'no espeak data found in {data_path}')

        if len(str(data).encode('utf-8')) >= _N_PATH_HOME:
            # the link name is the one espeak looks for in the given directory
            link = pathlib.Path(tempdir or '') / (
                'espeak-data' if version < (1, 49) else 'espeak-ng-data')
            try:
                if tempdir is None:
                    raise OSError('no directory for the link')
                os.symlink(data, link, target_is_directory=True)
            except OSError as error:
                raise RuntimeError(
                    f'the path to the espeak data is too long for espeak '
                    f'({_N_PATH_HOME - 1} bytes at most) and a shorter link to '
                    f'it cannot be made: {error}') from None
            data_path = link.parent

        return str(data_path).encode('utf-8')

    @staticmethod
    def _delete(library, tempdir):
        # The library is always loaded here: the finalizer is registered once
        # it is. An error is reported by the finalizer, it must not prevent
        # the removal of the tempdir.
        try:
            # clean up the espeak library allocated memory
            library.espeak_Terminate()

            # Unload the library copy, or it stays mapped in memory along with
            # the espeak data it allocated (several MB for each instance). On
            # Windows this is also required or the .dll file cannot be erased
            # from the temporary directory.
            EspeakAPI._unload(library)
        finally:
            # clean up the tempdir containing the copy of the library
            shutil.rmtree(tempdir, ignore_errors=True)

    @staticmethod
    def _unload(library):
        """Unloads the shared `library` from memory"""
        # pylint: disable=import-outside-toplevel
        # pylint: disable=protected-access
        # pylint: disable=no-member
        import _ctypes
        if sys.platform == 'win32':  # pragma: nocover
            _ctypes.FreeLibrary(library._handle)
        else:
            _ctypes.dlclose(library._handle)

    @property
    def library_path(self):
        """Absolute path to the espeak library being in use"""
        return self._library_path

    @staticmethod
    def _shared_library_path(library) -> Path:
        """Returns the absolute path to `library`

        This function is cross-platform and works for Linux, MacOS and Windows.
        Raises a RuntimeError if the library path cannot be retrieved

        """
        # pylint: disable=protected-access
        path = pathlib.Path(library._name).resolve()
        if path.is_file():
            return path

        try:
            # Linux or MacOS only, ImportError on Windows
            return pathlib.Path(dlinfo.DLInfo(library).path).resolve()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        # dlinfo is not supported everywhere (e.g. on FreeBSD, see issue
        # #209), where the library name given by ctypes.util.find_library()
        # is not a path. Look for it in the standard directories.
        for directory in _LIBRARY_DIRECTORIES:
            path = pathlib.Path(directory) / library._name
            if path.is_file():
                return path.resolve()

        raise RuntimeError(
            f'failed to retrieve the path to {library} library')

    def info(self):
        """Bindings to espeak_Info

        Returns
        -------
        version, data_path: encoded strings containing the espeak version
            number and data path respectively

        """
        f_info = self._library.espeak_Info
        f_info.restype = ctypes.c_char_p
        data_path = ctypes.c_char_p()
        version = f_info(ctypes.byref(data_path))
        return version, data_path.value

    def list_voices(self, name):
        """Bindings to espeak_ListVoices

        Parameters
        ----------
        name (str or None): if specified, a filter on voices to be listed

        Returns
        -------
        voices: a pointer to EspeakVoice.Struct instances

        """
        f_list_voices = self._library.espeak_ListVoices
        f_list_voices.argtypes = [ctypes.POINTER(EspeakVoice.VoiceStruct)]
        f_list_voices.restype = ctypes.POINTER(
            ctypes.POINTER(EspeakVoice.VoiceStruct))
        return f_list_voices(name)

    def set_voice_by_name(self, name) -> int:
        """Bindings to espeak_SetVoiceByName

        Parameters
        ----------
        name (str) : the voice name to setup

        Returns
        -------
        0 on success, non-zero integer on failure

        """
        f_set_voice_by_name = self._library.espeak_SetVoiceByName
        f_set_voice_by_name.argtypes = [ctypes.c_char_p]
        return f_set_voice_by_name(name)

    def get_current_voice(self):
        """Bindings to espeak_GetCurrentVoice

        Returns
        -------
        a EspeakVoice.Struct instance or None if no voice has been setup

        """
        f_get_current_voice = self._library.espeak_GetCurrentVoice
        f_get_current_voice.restype = ctypes.POINTER(EspeakVoice.VoiceStruct)
        return f_get_current_voice().contents

    def text_to_phonemes(self, text_ptr, text_mode, phonemes_mode):
        """Bindings to espeak_TextToPhonemes

        Parameters
        ----------
        text_ptr (pointer): the text to be phonemized, as a pointer to a
            pointer of chars
        text_mode (bits field): see espeak sources for details
        phonemes_mode (bits field): see espeak sources for details

        Returns
        -------
        an encoded string containing the computed phonemes

        """
        f_text_to_phonemes = self._library.espeak_TextToPhonemes
        f_text_to_phonemes.restype = ctypes.c_char_p
        f_text_to_phonemes.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.c_int,
            ctypes.c_int]
        return f_text_to_phonemes(text_ptr, text_mode, phonemes_mode)

    def set_phoneme_trace(self, mode, file_pointer):
        """"Bindings on espeak_SetPhonemeTrace

        This method must be called before any call to synthetize()

        Parameters
        ----------
        mode (bits field): see espeak sources for details
        file_pointer (FILE*): a pointer to an opened file in which to output
            the phoneme trace

        """
        f_set_phoneme_trace = self._library.espeak_SetPhonemeTrace
        f_set_phoneme_trace.argtypes = [
            ctypes.c_int,
            ctypes.c_void_p]
        f_set_phoneme_trace(mode, file_pointer)

    def synthetize(self, text_ptr, size, mode):
        """Bindings on espeak_Synth

        The output phonemes are sent to the file specified by a call to
        set_phoneme_trace().

        Parameters
        ----------
        text (pointer) : a pointer to chars
        size (int) : number of chars in `text`
        mode (bits field) : see espeak sources for details

        Returns
        -------
        0 on success, non-zero integer on failure

        """
        f_synthetize = self._library.espeak_Synth
        f_synthetize.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_uint,
            ctypes.c_int,  # position_type
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.c_void_p]
        return f_synthetize(text_ptr, size, 0, 1, 0, mode, None, None)
