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
"""Test of the phonemizer.backend module"""

# pylint: disable=missing-docstring

import re

import pytest

from phonemizer import backend
from phonemizer.backend import (
    _Backends, EspeakBackend, EspeakMbrolaBackend, FestivalBackend)
from phonemizer.backend.base import BaseBackend


@pytest.fixture
def backends(monkeypatch):
    # a registry with a lazy backend counting its imports, so that the tests
    # do not depend on the optional segments package
    imports = []

    def lazy():
        imports.append('lazy')
        return 'LazyBackend'

    monkeypatch.setattr(_Backends, '_LAZY', {'lazy': lazy})
    return _Backends({'espeak': EspeakBackend}), imports


def test_lazy_mapping(backends):
    registry, imports = backends
    assert len(registry) == 2
    assert 'lazy' in registry
    assert 'foo' not in registry
    assert list(registry) == ['espeak', 'lazy']
    assert registry.keys() == ['espeak', 'lazy']
    assert not imports

    assert registry['lazy'] == 'LazyBackend'
    assert registry.values() == [EspeakBackend, 'LazyBackend']
    assert registry.items() == [
        ('espeak', EspeakBackend), ('lazy', 'LazyBackend')]
    # imported once, then cached
    assert imports == ['lazy']


def test_unknown_backend(backends):
    registry, _ = backends
    with pytest.raises(KeyError):
        registry['foo']  # pylint: disable=pointless-statement


def test_module_getattr():
    assert backend.SegmentsBackend.name() == 'segments'
    with pytest.raises(AttributeError):
        backend.FooBackend  # pylint: disable=pointless-statement,no-member


# from https://github.com/bootphon/phonemizer/issues/189
def test_unavailable_espeak_tells_why(tmp_path):
    library = tmp_path / 'libespeak-ng.so'  # does not exist
    EspeakBackend.set_library(str(library))
    try:
        with pytest.raises(RuntimeError) as err:
            EspeakBackend('en-us')
    finally:
        EspeakBackend.set_library(None)
    assert str(err.value).startswith(
        'espeak not installed on your system: failed to load espeak library')
    # the OS error names the library, its exact form depends on the platform
    assert library.name in str(err.value)


def test_unavailable_festival_tells_why(monkeypatch, tmp_path):
    executable = tmp_path / 'festival'  # does not exist
    monkeypatch.setenv('PHONEMIZER_FESTIVAL_EXECUTABLE', str(executable))
    assert not FestivalBackend.is_available()
    with pytest.raises(RuntimeError, match=re.escape(
            'festival not installed on your system: '
            f'PHONEMIZER_FESTIVAL_EXECUTABLE={executable} '
            'is not an executable file')):
        FestivalBackend('en-us')


def test_unavailable_mbrola_tells_why(monkeypatch):
    from phonemizer.backend.espeak import mbrola  # pylint: disable=import-outside-toplevel
    monkeypatch.setattr(mbrola.shutil, 'which', lambda _: None)
    assert not EspeakMbrolaBackend.is_available()
    with pytest.raises(RuntimeError, match=(
            'espeak-mbrola not installed on your system: '
            'mbrola executable not found')):
        EspeakMbrolaBackend('mb-fr1')


def test_unavailable_without_reason(monkeypatch):
    # a backend telling nothing more than is_available()
    class Backend(FestivalBackend):
        @classmethod
        def is_available(cls):
            return False

    monkeypatch.setattr(Backend, '_unavailable_reason',
                        classmethod(BaseBackend._unavailable_reason.__func__))
    with pytest.raises(RuntimeError, match='^festival not installed on your system$'):
        Backend('en-us')


# from https://github.com/bootphon/phonemizer/issues/200
@pytest.mark.parametrize('language', ['en-us', 'EN-US', 'En-Us'])
def test_language_case_insensitive(language):
    assert EspeakBackend.is_supported_language(language)
    backend = EspeakBackend(language)
    assert backend.language == 'en-us'
    assert backend.phonemize(['hello']) == ['həloʊ ']


def test_language_not_supported():
    assert not EspeakBackend.is_supported_language('xx-YY')
    with pytest.raises(RuntimeError, match='"xx-YY" is not supported'):
        EspeakBackend('xx-YY')


def test_language_ambiguous(monkeypatch):
    # two codes differing only by their case: an exact match is required
    monkeypatch.setattr(
        FestivalBackend, 'supported_languages',
        staticmethod(lambda: {'en-us': 'a', 'EN-US': 'b'}))
    assert FestivalBackend._supported_language('en-us') == 'en-us'  # pylint: disable=protected-access
    assert FestivalBackend._supported_language('En-Us') is None  # pylint: disable=protected-access
