#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

"""
This file is part of Spartacus project
Copyright (C) 2016  CSE

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
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"

REGISTER_PREFIX = "$"
IMMEDIATE_PREFIX = "#"
FLAGS_INDICATORS = "<>"
WIDTH_INDICATORS = "[]"
MEMORY_REFERENCE_INDICATORS = ":"
EXPORTED_REFERENCE_INDICATOR = ".GLOBAL"
DATA_NUMERIC_INDICATOR = ".DATANUMERIC"
DATA_ALPHA_INDICATOR = ".DATAALPHA"
DATA_MEMORY_REFERENCE = ".DATAMEMREF"
COMMENT_INDICATORS = ";"
MAX_OPERAND_COUNT = 3

INSTRUCTION_FLAG = 0
LOCAL_REFERENCE_FLAG = 1
GLOBAL_REFERENCE_FLAG = 2
COMMENT_FLAG = 3

NUMERIC_DATA_INDICATOR = "int"
ALPHA_DATA_INDICATOR = "alpha"

UNDEFINED = "&&undefined&&"
DEFAULT_OUTPUT_EXTENSION = ".o"

REGISTERS = {
    "A": 0b0000, "B": 0b0001, "C": 0b0010, "D": 0b0011,
    "E": 0b0100, "F": 0b0101, "G": 0b0110, "S": 0b0111,

    "A2": 0b1000, "B2": 0b1001, "C2": 0b1010, "D2": 0b1011,
    "E2": 0b1100, "F2": 0b1101, "G2": 0b1110, "S2": 0b1111
}

INSTRUCTION_LIST = [
    "ACTI", "ADD", "AND", "CALL", "CMP", "DACTI", "DIV",
    "HIRET", "INT", "JMP", "JMPR", "MEMR", "MEMW", "MOV",
    "MUL", "NOP", "NOT", "NOP", "OR", "POP", "PUSH",
    "RET", "SFSTOR", "SIVR", "SHL", "SHR", "SUB", "XOR"
]

IDENTIFIER_LIST = [
    ":", ".GLOBAL", ".DATAALPHA", ".DATANUMERIC", ".DATAMEMREF", ";"
]

STATE_LIST = {
    "Ins": "STATE0",
    "InsReg": "STATE1",
    "InsRegReg": "STATE2",
    "InsImm": "STATE3",
    "InsImmReg": "STATE4",
    "InsWidthImmImm": "STATE5",
    "InsWidthImmReg": "STATE6",
    "InsWidthRegImm": "STATE7",
    "InsWidthRegReg": "STATE8",
    "InsFlagImm": "STATE9",
    "InsFlagReg": "STATE10",
}