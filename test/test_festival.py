# Copyright 2015-2021 Thomas Schatz, Xuan Nga Cao, Mathieu Bernard
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
"""Test of the festival backend"""

# pylint: disable=missing-docstring

import os
import pathlib
import shutil

import pytest

from phonemizer import phonemize
from phonemizer.backend import FestivalBackend
from phonemizer.separator import Separator


def _test(text, separator=Separator(word=" ", syllable="|", phone="-")):
    backend = FestivalBackend("en-us")
    # pylint: disable=protected-access
    return backend._phonemize_aux(text, 0, separator, True)


@pytest.mark.skipif(
    not FestivalBackend.is_available() or FestivalBackend.version() <= (2, 1),
    reason="festival not installed or is festival-2.1 (gives different results than further versions "
    "for syllable boundaries)",
)
def test_hello():
    assert _test(["hello world"]) == ["hh-ax|l-ow w-er-l-d"]
    assert _test(["hello", "world"]) == ["hh-ax|l-ow", "w-er-l-d"]


@pytest.mark.skipif(not FestivalBackend.is_available(), reason="festival not installed")
@pytest.mark.parametrize("text", ["", " ", "  ", "(", "()", '"', "'"])
def test_bad_input(text):
    # nothing to give to festival, as before phonemizer-3.5
    # pylint: disable=protected-access
    assert FestivalBackend._preprocess([text]) == ""
    assert _test([]) == []

    # the phonemized string is empty, as before phonemizer-3.5
    assert phonemize(text, backend="festival", language="en-us") == ""

    # changed in phonemizer-3.5: each input line gives an output line, as
    # with espeak. Before, the line was dropped, so the next lines were
    # paired with the wrong input (see test_empty_lines_kept).
    assert _test([text]) == [""]


@pytest.mark.skipif(not FestivalBackend.is_available(), reason="festival not installed")
def test_quote():
    assert _test(["it's"]) == ["ih-t-s"]
    assert _test(["its"]) == ["ih-t-s"]
    assert _test(["it s"]) == ["ih-t eh-s"]
    assert _test(['it "s']) == ["ih-t eh-s"]


@pytest.mark.skipif(not FestivalBackend.is_available(), reason="festival not installed")
def test_im():
    sep = Separator(word=" ", syllable="", phone="")
    assert _test(["I'm looking for an image"], sep) == ["aym luhkaxng faor axn ihmaxjh"]
    assert _test(["Im looking for an image"], sep) == ["ihm luhkaxng faor axn ihmaxjh"]


@pytest.mark.skipif(not shutil.which("festival"), reason="festival not in PATH")
def test_path_good():
    try:
        binary = shutil.which("festival")
        FestivalBackend.set_executable(binary)
        assert FestivalBackend("en-us").executable() == pathlib.Path(binary)
    # restore the festival path to default
    finally:
        FestivalBackend.set_executable(None)


@pytest.mark.skipif(
    not FestivalBackend.is_available()
    or "PHONEMIZER_FESTIVAL_EXECUTABLE" in os.environ,
    reason="festival not installed or environment variable precedence",
)
def test_path_bad():
    try:
        # corrupt the default espeak path, try to use python executable instead
        binary = shutil.which("python")
        FestivalBackend.set_executable(binary)

        with pytest.raises(RuntimeError):
            FestivalBackend("en-us").phonemize(["hello"])
        with pytest.raises(RuntimeError):
            FestivalBackend.version()

        with pytest.raises(RuntimeError):
            FestivalBackend.set_executable(__file__)

    # restore the festival path to default
    finally:
        FestivalBackend.set_executable(None)


@pytest.mark.skipif(
    not FestivalBackend.is_available()
    or "PHONEMIZER_FESTIVAL_EXECUTABLE" in os.environ,
    reason="festival not installed or cannot modify environment",
)
def test_path_venv():
    try:
        os.environ["PHONEMIZER_FESTIVAL_EXECUTABLE"] = shutil.which("python") or ""
        with pytest.raises(RuntimeError):
            FestivalBackend("en-us").phonemize(["hello"])
        with pytest.raises(RuntimeError):
            FestivalBackend.version()

        os.environ["PHONEMIZER_FESTIVAL_EXECUTABLE"] = __file__
        with pytest.raises(RuntimeError):
            FestivalBackend.version()

    finally:
        try:
            del os.environ["PHONEMIZER_FESTIVAL_EXECUTABLE"]
        except KeyError:
            pass


@pytest.mark.skipif(not FestivalBackend.is_available(), reason="festival not installed")
def test_empty_lines_kept():
    # a line emptied by the cleaning must not shift the next lines in output
    hello, world = _test(["hello", "world"])
    assert _test(["hello", "'", '"()"', "world"]) == [hello, "", "", world]
    assert _test(["'", "()"]) == ["", ""]


def test_postprocess_no_word():
    # festival outputs '(nil nil nil)' for an utterance without word
    # pylint: disable=protected-access
    sep = Separator(word=" ", syllable="|", phone="-")
    tree = FestivalBackend._postprocess("(nil nil nil)\n(nil nil nil)\n", sep, True)
    assert tree == ["", ""]


@pytest.mark.skipif(
    not FestivalBackend.is_available() or os.name == "nt",
    reason="festival not installed or not a POSIX shell")
def test_executable_with_spaces(tmp_path):
    # a festival executable in a directory with spaces in its name
    directory = tmp_path / "my festival"
    directory.mkdir()
    executable = directory / "festival"
    executable.write_text(
        f'#!/bin/sh\nexec "{FestivalBackend.executable()}" "$@"\n')
    executable.chmod(0o755)

    expected = _test(["hello"])
    try:
        FestivalBackend.set_executable(str(executable))
        assert FestivalBackend.executable() == executable.resolve()
        assert _test(["hello"]) == expected
    finally:
        FestivalBackend.set_executable(None)
