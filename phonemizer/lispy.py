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
"""Parse a Scheme expression as a nested list

The main function of this module is lispy.parse, other ones should be
considered private. This module is a dependency of the festival
backend.

From http://www.norvig.com/lispy.html

"""


def parse(program):
    """Read a Scheme expression from a string

    Return a nested list

    Raises an IndexError if the expression is not valid scheme
    (unbalanced parenthesis).

    >>> parse('(+ 2 (* 5 2))')
    ['+', '2', ['*', '5', '2']]

    """
    return _read_from_tokens(_tokenize(program))


def _tokenize(chars):
    "Convert a string of characters into a list of tokens."
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def _read_from_tokens(tokens):
    "Read an expression from a sequence of tokens"
    if len(tokens) == 0:  # pragma: nocover
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(_read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return L
    elif ')' == token:  # pragma: nocover
        raise SyntaxError('unexpected )')
    else:
        return token  # was _atom(token)


# def _atom(token):
#     "Numbers become numbers, every other token are not processed"
#     try:
#         return int(token)
#     except ValueError:
#         try:
#             return float(token)
#         except ValueError:
#             return token
