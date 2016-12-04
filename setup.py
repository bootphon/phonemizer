#!/usr/bin/env python
#
# Copyright 2015, 2016 Mathieu Bernard
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
"""Setup script for the phonemizer package"""

from setuptools import setup, find_packages

VERSION = '0.3'

setup(
    name='phonemizer',
    version=VERSION,
    packages=find_packages(),
    zip_safe=True,

    # python package dependancies
    install_requires=['joblib'],

    # include any files in phonemizer/share
    package_data={'phonemizer': ['share/phonemize.scm']},

    # define the command-line script to use
    entry_points={'console_scripts': ['phonemize = phonemizer.main:main']},

    # metadata for upload to PyPI
    author='Mathieu Bernard',
    author_email='mmathieubernardd@gmail.com',
    description='Simple phonemization of English text',
    license='GPL3',
    keywords='linguistics phoneme festival TTS',
    url='https://github.com/bootphon/phonemizer',
    long_description=open('README.md').read()
)
