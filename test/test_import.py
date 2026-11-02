"""Tests to import the phonemize function"""

# pylint: disable=missing-docstring
# pylint: disable=import-outside-toplevel


def test_relative():
    from phonemizer import phonemize
    assert phonemize('a') == 'eɪ '


def test_absolute():
    from phonemizer.phonemize import phonemize
    assert phonemize('a') == 'eɪ '


def test_package_resource_without_pytest():
    # pytest imports importlib.resources itself, so a missing import in
    # phonemizer only shows up in a fresh interpreter
    import subprocess
    import sys
    subprocess.run(
        [sys.executable, '-c',
         'from phonemizer.utils import get_package_resource; '
         'get_package_resource("festival/phonemize.scm")'],
        check=True)
