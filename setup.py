#!/usr/bin/env python
#
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
"""Setup script for the phonemizer package"""

import builtins
import codecs
import setuptools


# This is a bit hackish: we are setting a global variable so that the main
# phonemizer __init__ can detect if it is being loaded by the setup routine, to
# avoid attempting to load components that aren't built yet.
builtins.__PHONEMIZER_SETUP__ = True


import phonemizer


setuptools.setup(
    # general description
    name='phonemizer',
    description=' Simple text to phones converter for multiple languages',
    version=phonemizer.__version__,

    # python package dependancies
    install_requires=['joblib', 'segments', 'attrs>=18.1', 'dlinfo'],

    # include Python code and any files in phonemizer/share
    packages=setuptools.find_packages(),
    package_data={
        'phonemizer': [
            'share/espeak/*', 'share/festival/*', 'share/segments/*']},

    # define the command-line script to use
    entry_points={'console_scripts': ['phonemize = phonemizer.main:main']},

    # metadata for upload to PyPI
    author='Mathieu Bernard',
    author_email='mathieu.a.bernard@inria.fr',
    license='GPL3',
    keywords='linguistics G2P phone festival espeak TTS',
    url='https://github.com/bootphon/phonemizer',
    long_description=codecs.open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    zip_safe=True,
)
