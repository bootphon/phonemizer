# Copyright 2015-2020 Mathieu Bernard
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
"""Phonemizer version description"""


import pkg_resources

from phonemizer.backend import (
    EspeakBackend, EspeakMbrolaBackend, FestivalBackend, SegmentsBackend)


def version():
    """Return version information for front and backends"""
    # version of the phonemizer
    version = (
        'phonemizer-' + pkg_resources.get_distribution('phonemizer').version)

    # for each backend, check if it is available or not. If so get its version
    available = []
    unavailable = []

    if EspeakBackend.is_available():
        available.append(
            'espeak-' + ('ng-' if EspeakBackend.is_espeak_ng() else '')
            + EspeakBackend.version())
    else:  # pragma: nocover
        unavailable.append('espeak')

    if EspeakMbrolaBackend.is_available():
        available.append('espeak-mbrola')
    else:  # pragma: nocover
        unavailable.append('espeak-mbrola')

    if FestivalBackend.is_available():
        available.append('festival-' + FestivalBackend.version())
    else:  # pragma: nocover
        unavailable.append('festival')

    if SegmentsBackend.is_available():
        available.append('segments-' + SegmentsBackend.version())
    else:  # pragma: nocover
        unavailable.append('segments')

    # resumes the backends status in the final version string
    if available:
        version += '\navailable backends: ' + ', '.join(available)
    if unavailable:  # pragma: nocover
        version += '\nuninstalled backends: ' + ', '.join(unavailable)

    return version
