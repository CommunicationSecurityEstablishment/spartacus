#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

"""
This file is part of Spartacus project
Copyright (C) 2018  CSE

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

__author__ = "CSE"
__copyright__ = "Copyright 2018, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "3.0"
__maintainer__ = "CSE"
__status__ = "Dev"

import re

ACCEPTED_TYPES = ["int", "char"]
OPERATORS = ['+', '-', '*', '/']
BINARY_OPERATORS = ["|", "&"]
BOOLEAN_OPERATORS = ["<", ">", "="]
IGNORE_CHARS = [" ", "\n"]
REGISTER_NAMES = ["A", "B", "C", "D", "E", "F", "G"]
SINGLE_QUOTE = "\'"
DOUBLE_QUOTE = "\""


L_PARENTHESES = '('
R_PARENTHESES = ')'
PLUS = '+'
MINUS = '-'
MULTIPLICATION = '*'
DIVISION = '/'

UNDEFINED = "&&undefined&&"
DEFAULT_OUTPUT_EXTENSION = ".casm"

REGISTERS = {
    0: "A",
    1: "B",
    2: "C",
    3: "D",
    4: "E",
    5: "F",
    6: "G"
}

ALLOWED_CHARS = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
    "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
    "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g",
    "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r",
    "s", "t", "u", "v", "w", "x", "y", "z", "$", "_", "#"
]

OPERATIONS = {
              PLUS: {'priority': 1, 'function': lambda a, b: a + b},
              MINUS: {'priority': 1, 'function': lambda a, b: a - b},
              MULTIPLICATION: {'priority': 2, 'function': lambda a, b: a * b},
              DIVISION: {'priority': 2, 'function': lambda a, b: a / b},
}

INSTRUCTIONS = {
                PLUS: "ADD",
                MINUS: "SUB",
                MULTIPLICATION: "MUL",
                DIVISION: "DIV"
}

TOKEN_SEPARATOR = re.compile(r'\s*(%s|%s|%s|%s|%s|%s)\s*' % (
                  re.escape(L_PARENTHESES),
                  re.escape(R_PARENTHESES),
                  re.escape(PLUS),
                  re.escape(MINUS),
                  re.escape(MULTIPLICATION),
                  re.escape(DIVISION))
)

ARRAY_PATTERN = "\w*\[[0-9]\]"



