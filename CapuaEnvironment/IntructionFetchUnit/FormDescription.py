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
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"

formDescription = {
    "Ins": {
        'typeCode': 0b1111,
        'listing': [0b0000,  # RET
                    0b1111], # NOP
        'description': {
            "instructionCode": 0b11111111
        },
        "length": 1
    },
    "InsReg": {
        'typeCode': 0b0111,
        'listing': [0b0000,  # NOT
                    0b0001,  # SNT - This is not implemented, DO NOT USE
                    0b0010,  # CALL
                    0b0011,  # PUSH
                    0b0100], # POP
        'description': {
            "instructionCode": 0b1111111100000000,
            "sourceRegister": 0b0000000011111111
        },
        "length": 2
    },
    "InsImm": {
        'typeCode': 0b1000,
        'listing': [0b0000,  # SNT - This is not implemented, DO NOT USE
                    0b0001,  # PUSH
                    0b0010], # CALL
        'description': {
            "instructionCode": 0b1111111100000000000000000000000000000000,
            "sourceImmediate": 0b0000000011111111111111111111111111111111
        },
        "length": 5
    },
    "InsImmReg": {
        'typeCode': 0b0110,
        'listing': [0b0000,  # MOV
                    0b0001,  # AND
                    0b0010,  # OR
                    0b0011,  # XOR
                    0b0100,  # SHR
                    0b0101,  # SHL
                    0b0110,  # ADD
                    0b0111,  # SUB
                    0b1000], # CMP
        'description': {
            "instructionCode": 0b111111110000000000000000000000000000000000000000,
            "sourceImmediate": 0b000000001111111111111111111111111111111100000000,
            "destinationRegister": 0b000000000000000000000000000000000000000011111111
        },
        "length": 6
    },
    "InsWidthImmReg": {
        'typeCode': 0b0000,
        'listing': [0b0000,  # MEMW
                    0b0001], # MEMR
        'description': {
            "instructionCode": 0b111111110000000000000000000000000000000000000000,
            "width": 0b000000001111000000000000000000000000000000000000,
            "sourceImmediate": 0b000000000000000011111111111111111111111111111111,
            "destinationRegister": 0b000000000000111100000000000000000000000000000000
        },
        "length": 6
    },
    "InsWidthRegReg": {
        'typeCode': 0b0001,
        'listing': [0b0000,  # MEMR
                    0b0001], # MEMW
        'description': {
            "instructionCode": 0b1111111100000000,
            "width": 0b0000000011110000,
            "sourceRegister": 0b0000000000001100,
            "destinationRegister": 0b0000000000000011
        },
        "length": 2
    },
    "InsWidthRegImm": {
        'typeCode': 0b0010,
        'listing': [0b0000],  # MEMW
        'description': {
            "instructionCode": 0b111111110000000000000000000000000000000000000000,
            "width": 0b000000001111000000000000000000000000000000000000,
            "sourceRegister": 0b000000000000111100000000000000000000000000000000,
            "destinationImmediate": 0b000000000000000011111111111111111111111111111111
        },
        "length": 6
    },
    "InsWidthImmImm": {
        'typeCode': 0b0011,
        'listing': [0b0000], # MEMW
        'description': {
            "instructionCode": 0b11111111000000000000000000000000000000000000000000000000000000000000000000000000,
            "width": 0b00000000111111110000000000000000000000000000000000000000000000000000000000000000,
            "sourceImmediate": 0b00000000000000001111111111111111111111111111111100000000000000000000000000000000,
            "destinationImmediate": 0b00000000000000000000000000000000000000000000000011111111111111111111111111111111
        },
        "length": 10
    },
    "InsFlagImm": {
        'typeCode': 0b0100,
        'listing': [0b0000,  # JMPR
                    0b0001], # JMP
        'description': {
            "instructionCode": 0b111111110000000000000000000000000000000000000000,
            "flags": 0b000000001111111100000000000000000000000000000000,
            "sourceImmediate": 0b000000000000000011111111111111111111111111111111,
        },
        "length": 6
    },
    "InsFlagReg": {
        'typeCode': 0b0101,
        'listing': [0b0000,  # JMPR
                    0b0001], # JMP
        'description': {
            "instructionCode": 0b1111111100000000,
            "flags": 0b0000000011110000,
            "sourceRegister": 0b0000000000001111,
        },
        "length": 2
    },
    "InsRegReg": {
        'typeCode': 0b1001,
        'listing': [0b0000,  # XOR
                    0b0010,  # ADD
                    0b0011,  # SUB
                    0b0100,  # MUL
                    0b0101,  # DIV
                    0b0110,  # SHL
                    0b0111,  # AND
                    0b1000,  # OR
                    0b1001,  # SHR
                    0b1010,  # CMP
                    0b1011], # MOV
        'description': {
            "instructionCode": 0b1111111100000000,
            "sourceRegister": 0b0000000011110000,
            "destinationRegister": 0b0000000000001111
        },
        "length": 2
    }
}
