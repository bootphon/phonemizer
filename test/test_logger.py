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
"""Test of the phonemizer.logger module"""

# pylint: disable=missing-docstring

import logging

import pytest

from phonemizer import phonemize
from phonemizer.logger import default_logger, get_logger

# a text yielding warnings: a language switch with espeak-ng, a words count
# mismatch with espeak-1.48
TEXT = ["j'aime le football"]


@pytest.fixture
def phonemizer_level():
    yield
    default_logger().setLevel(logging.NOTSET)


def test_default_propagates(caplog):
    phonemize(TEXT, language='fr-fr')
    assert any(rec.name == 'phonemizer' for rec in caplog.records)


# from https://github.com/bootphon/phonemizer/issues/154
def test_default_level_from_app(caplog, phonemizer_level):
    default_logger().setLevel(logging.ERROR)
    phonemize(TEXT, language='fr-fr')
    phonemize(TEXT, language='fr-fr', preserve_punctuation=True)
    assert not caplog.records
    assert default_logger().level == logging.ERROR


# from https://github.com/bootphon/phonemizer/issues/154
def test_quiet(caplog, capsys):
    phonemize(TEXT, language='fr-fr', logger=get_logger('quiet'))
    assert not caplog.records
    assert not capsys.readouterr().err


def test_normal(caplog, capsys):
    phonemize(TEXT, language='fr-fr', logger=get_logger('normal'))
    assert not caplog.records
    assert capsys.readouterr().err.startswith('[WARNING] ')


def test_get_logger_leaves_default_untouched():
    handlers = list(default_logger().handlers)
    for verbosity in ('quiet', 'normal', 'verbose'):
        get_logger(verbosity)
    assert default_logger().handlers == handlers
    assert default_logger().level == logging.NOTSET
    assert default_logger().propagate


def test_bad_verbosity():
    with pytest.raises(RuntimeError):
        get_logger('foo')
