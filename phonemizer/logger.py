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
"""Logging facilities for the phonemizer"""

import logging
import sys
from logging import Logger

# As recommended for libraries, the phonemizer logger has no output on its own:
# the messages are handled by the logging configuration of the application.
logging.getLogger('phonemizer').addHandler(logging.NullHandler())


def default_logger() -> Logger:
    """Returns the logger used when none is given to the phonemizer

    This is the 'phonemizer' logger, it is never configured by the phonemizer
    itself. Its messages propagate to the logging configuration of the
    application, which can set its level or handlers as usual, for instance
    ``logging.getLogger('phonemizer').setLevel(logging.ERROR)``.

    """
    return logging.getLogger('phonemizer')


def get_logger(verbosity: str = 'quiet', name: str = 'phonemizer') -> Logger:
    """Returns a configured logging.Logger instance

    The logger is configured to output messages on the standard error stream
    (stderr). Its messages are not propagated to the logging configuration of
    the application, so that 'quiet' does not display anything. The returned
    logger is a child of `name` dedicated to the given `verbosity`, so that
    calling this function does not alter the configuration of the logger
    `name` itself.

    Parameters
    ----------
    verbosity (str) : The level of verbosity, must be 'verbose' (displays
      debug/info and warning messages), 'normal' (warnings only) or 'quiet' (do
      not display anything).
    name (str) : The logger name, default to 'phonemizer'

    Raises
    ------
    RuntimeError if `verbosity` is not 'normal', 'verbose', or 'quiet'.

    """
    # make sure the verbosity argument is valid
    valid_verbosity = ['normal', 'verbose', 'quiet']
    if verbosity not in valid_verbosity:
        raise RuntimeError(
            f'verbosity is {verbosity} but must be in '
            f'{", ".join(valid_verbosity)}')

    logger = logging.getLogger(f'{name}.{verbosity}')
    logger.propagate = False

    # setup output to stderr
    logger.handlers = []
    handler = logging.StreamHandler(sys.stderr)

    # setup verbosity level
    logger.setLevel(logging.WARNING)
    if verbosity == 'verbose':
        logger.setLevel(logging.DEBUG)
    elif verbosity == 'quiet':
        handler = logging.NullHandler()

    # setup messages format
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(handler)
    return logger
