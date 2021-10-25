# Copyright 2015-2021 Mathieu Bernard
#
# This file is part of phonologizer: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Phonologizer is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with phonologizer. If not, see <http://www.gnu.org/licenses/>.
"""Multilingual text to phones converter"""


__version__ = '3.0'
"""Phonemizer version"""


try:  # pragma: nocover
    # This variable is injected in the __builtins__ by the build process. In
    # that case we don't want to import phonemize as there are missing
    # dependencies.
    __PHONEMIZER_SETUP__
except NameError:
    __PHONEMIZER_SETUP__ = False


if __PHONEMIZER_SETUP__:  # pragma: nocover
    import sys
    sys.stderr.write(
        'Partial import of phonemizer during the build process.\n')
else:
    # pylint: disable=unused-import
    from .phonemize import phonemize
