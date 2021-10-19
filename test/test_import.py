"""Tests to import the phonemize function"""

# pylint: disable=missing-docstring
# pylint: disable=import-outside-toplevel


def test_relative():
    from phonemizer import phonemize
    assert phonemize('a') == 'eɪ '


def test_absolute():
    from phonemizer.phonemize import phonemize
    assert phonemize('a') == 'eɪ '
