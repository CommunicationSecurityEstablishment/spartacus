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

import unittest

from CapuaEnvironment.Instruction.Instruction import Instruction
from CapuaEnvironment.IntructionFetchUnit.FormDescription import formDescription

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class TestInstruction(unittest.TestCase):

    def test_init(self):
        """
        Validates good working of the __init__ method for Instruction
        __init__(self, binaryInstruction=0b000000, form=None)
        """
        ins = Instruction(0b11111111,
                          formDescription["Ins"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 1)
        self.assertEqual(ins.operationMnemonic, "NOP")

        ins = Instruction(0b01110000 << 8 * 1,
                          formDescription["InsReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 2)
        self.assertEqual(ins.operationMnemonic, "NOT")

        ins = Instruction(0b10000000 << 8 * 4,
                          formDescription["InsImm"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 5)
        self.assertEqual(ins.operationMnemonic, "SNT")

        ins = Instruction(0b01100000 << 8 * 5,
                          formDescription["InsImmReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNotNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 6)
        self.assertEqual(ins.operationMnemonic, "MOV")

        ins = Instruction(0b00000000 << 8 * 5,
                          formDescription["InsWidthImmReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNotNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNotNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 6)
        self.assertEqual(ins.operationMnemonic, "MEMW")

        ins = Instruction(0b00010000 << 8 * 1,
                          formDescription["InsWidthRegReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNotNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNotNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 2)
        self.assertEqual(ins.operationMnemonic, "MEMR")

        ins = Instruction(0b00100000 << 8 * 5,
                          formDescription["InsWidthRegImm"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNotNone(ins.destinationImmediate)
        self.assertIsNotNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 6)
        self.assertEqual(ins.operationMnemonic, "MEMW")

        ins = Instruction(0b00110000 << 8 * 9,
                          formDescription["InsWidthImmImm"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNotNone(ins.destinationImmediate)
        self.assertIsNotNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 10)
        self.assertEqual(ins.operationMnemonic, "MEMW")

        ins = Instruction(0b01000000 << 8 * 5,
                          formDescription["InsFlagImm"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNotNone(ins.flags)
        self.assertEqual(ins.instructionLength, 6)
        self.assertEqual(ins.operationMnemonic, "JMPR")

        ins = Instruction(0b01010000 << 8 * 1,
                          formDescription["InsFlagReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNotNone(ins.flags)
        self.assertEqual(ins.instructionLength, 2)
        self.assertEqual(ins.operationMnemonic, "JMPR")

        ins = Instruction(0b10010000 << 8 * 1,
                          formDescription["InsRegReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNotNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)
        self.assertEqual(ins.instructionLength, 2)
        self.assertEqual(ins.operationMnemonic, "XOR")

        self.assertIsNotNone(Instruction(skipValidation=True))

    def test_extractValueFromBinaryField(self):
        """
        Validates good working of the _extractValueFromBinaryField method for Instruction
        _extractValueFromBinaryField(self, mask, field)
        """
        ins = Instruction(0b10010000 << 8 * 1,
                          formDescription["InsRegReg"])
        self.assertEqual(0b10, ins._extractValueFromBinaryField(0b00011000, 0b11110111))
        self.assertEqual(0b10, ins._extractValueFromBinaryField(0b00000011, 0b11111110))
        self.assertEqual(0b00, ins._extractValueFromBinaryField(0b00000000, 0b11111110))
