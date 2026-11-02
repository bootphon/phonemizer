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

import pytest

from phonemizer import backend
from phonemizer.backend import _Backends, EspeakBackend


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
