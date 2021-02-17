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
"""Provides utility functions for the phonemizer"""

import os
import pkg_resources
import six


def cumsum(iterable):
    """Returns the cumulative sum of the `iterable` as a list"""
    res = []
    cumulative = 0
    for value in iterable:
        cumulative += value
        res.append(cumulative)
    return res


def str2list(s):
    """Returns the string `s` as a list of lines, split by \n"""
    return s.strip().split('\n') if isinstance(s, six.string_types) else s


def list2str(s):
    """Returns the list of lines `s` as a single string separated by \n"""
    return '\n'.join(s) if not isinstance(s, six.string_types) else s


def chunks(text, num):
    """Return a maximum of `num` equally sized chunks of a `text`

    This method is usefull when phonemizing a single text on multiple jobs.

    The exact number of chunks returned is `m = min(num, len(str2list(text)))`.
    Only the m-1 first chunks have equal size. The last chunk can be longer.
    The input `text` can be a list or a string. Return a list of `m` strings.

    Parameters
    ----------
    text (str or list) : The text to divide in chunks

    num (int) : The number of chunks to build, must be a strictly positive
    integer.

    Returns
    -------
    The chunked text as a list of str.

    """
    text = str2list(text)
    size = int(max(1, len(text) / num))
    nchunks = min(num, len(text))

    result = [list2str(text[i*size:(i+1)*size]) for i in range(nchunks - 1)]

    last = list2str(text[(nchunks - 1)*size:])
    if last:
        result.append(last)

    return result


def get_package_resource(path):
    """Returns the absolute path to a phonemizer resource file or directory

    The packages resource are stored within the source tree in the
    'phonemizer/share' directory and, once the package is installed, are moved
    to another system directory (e.g. /share/phonemizer).

    Parameters
    ----------
    path (str) : the file or directory to get, must be relative to
        'phonemizer/share'.

    Raises
    ------
    ValueError if the required `path` is not found

    Returns
    -------
    The absolute path to the required resource

    """
    path = pkg_resources.resource_filename(
        pkg_resources.Requirement.parse('phonemizer'),
        'phonemizer/share/{}'.format(path))

    if not os.path.exists(path):  # pragma: nocover
        raise ValueError(
            'the requested resource does not exist: {}'.format(path))

    return os.path.abspath(path)
