"""Tests to import the phonemize function"""

import pytest


def test_relative():
    from phonemizer import phonemize
    assert phonemize('a') == 'ax '


def test_absolute():
    from phonemizer.phonemize import phonemize
    assert phonemize('a') == 'ax '
