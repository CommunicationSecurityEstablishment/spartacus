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

from CapuaEnvironment.IntructionFetchUnit.InstructionFetchUnit import InstructionFetchUnit
from CapuaEnvironment.IntructionFetchUnit.FormDescription import formDescription
from CapuaEnvironment.MemoryArray.MemoryArray import MemoryArray
from Configuration.Configuration import MEMORY_START_AT

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class TestInstructionFetchUnit(unittest.TestCase):

    ma = MemoryArray()
    ifu = InstructionFetchUnit(ma)

    def test_init(self):
        """
        Validates good working of the __init__ method for InstructionFetchUnit
        """
        self.assertRaises(RuntimeError, InstructionFetchUnit)  # IFU needs a memory array to work with
        ma = MemoryArray()
        ifu = InstructionFetchUnit(ma)
        self.assertEqual(ifu._memoryArray, ma)

    def test_fetchInstructionAtAddress(self):
        """
        Validates good working of the fetchInstructionAtAddress method for InstructionFetchUnit
        """
        memoryGroup = self.ifu._memoryArray.extractMemory(MEMORY_START_AT, 1)
        memoryGroup[0].writeValue(0xFF, "System")  # Insert nop instruction in memory
        instruction, nextInstructionAddress = self.ifu.fetchInstructionAtAddress(MEMORY_START_AT)
        self.assertIsNotNone(instruction.instructionCode)
        self.assertIsNone(instruction.sourceRegister)
        self.assertIsNone(instruction.destinationRegister)
        self.assertIsNone(instruction.sourceImmediate)
        self.assertIsNone(instruction.destinationImmediate)
        self.assertIsNone(instruction.width)
        self.assertIsNone(instruction.flags)
        self.assertEqual(nextInstructionAddress, MEMORY_START_AT + 1)

        memoryGroup = self.ifu._memoryArray.extractMemory(MEMORY_START_AT, 1)
        memoryGroup[0].writeValue(0b00010000, "System")  # Insert InsWidthRegReg instruction type in memory
        instruction, nextInstructionAddress = self.ifu.fetchInstructionAtAddress(MEMORY_START_AT)
        self.assertIsNotNone(instruction.instructionCode)
        self.assertIsNotNone(instruction.sourceRegister)
        self.assertIsNotNone(instruction.destinationRegister)
        self.assertIsNone(instruction.sourceImmediate)
        self.assertIsNone(instruction.destinationImmediate)
        self.assertIsNotNone(instruction.width)
        self.assertIsNone(instruction.flags)
        self.assertEqual(nextInstructionAddress, MEMORY_START_AT + 2)


    def test_fetchInstructionFormAtAddress(self):
        """
        Validates good working of the fetchInstructionFormAtAddress method for InstructionFetchUnit
        """
        memoryGroup = self.ifu._memoryArray.extractMemory(MEMORY_START_AT, 1)
        memoryGroup[0].writeValue(0xFF, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["Ins"], form)

        memoryGroup[0].writeValue(0b01110000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsReg"], form)

        memoryGroup[0].writeValue(0b10000000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsImm"], form)

        memoryGroup[0].writeValue(0b01100000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsImmReg"], form)

        memoryGroup[0].writeValue(0b00000000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsWidthImmReg"], form)

        memoryGroup[0].writeValue(0b00010000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsWidthRegReg"], form)

        memoryGroup[0].writeValue(0b00100000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsWidthRegImm"], form)

        memoryGroup[0].writeValue(0b00110000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsWidthImmImm"], form)

        memoryGroup[0].writeValue(0b01000000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsFlagImm"], form)

        memoryGroup[0].writeValue(0b01010000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsFlagReg"], form)

        memoryGroup[0].writeValue(0b10010000, "System")
        form = self.ifu._fetchInstructionFormAtAddress(MEMORY_START_AT)
        self.assertEqual(formDescription["InsRegReg"], form)

    def test_fetchInstructionAtAddressUsingForm(self):
        """
        Validates good working of the fetchInstructionAtAddressUsingForm method for InstructionFetchUnit
        """

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["Ins"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsImm"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsImmReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNotNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsWidthImmReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNotNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNotNone(ins.width)
        self.assertIsNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsWidthRegReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNotNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNotNone(ins.width)
        self.assertIsNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsWidthRegImm"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNotNone(ins.destinationImmediate)
        self.assertIsNotNone(ins.width)
        self.assertIsNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsWidthImmImm"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNotNone(ins.destinationImmediate)
        self.assertIsNotNone(ins.width)
        self.assertIsNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsFlagImm"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNotNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNotNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsFlagReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNotNone(ins.flags)

        ins = self.ifu._fetchInstructionAtAddressUsingForm(MEMORY_START_AT, formDescription["InsRegReg"])
        self.assertIsNotNone(ins.instructionCode)
        self.assertIsNotNone(ins.sourceRegister)
        self.assertIsNotNone(ins.destinationRegister)
        self.assertIsNone(ins.sourceImmediate)
        self.assertIsNone(ins.destinationImmediate)
        self.assertIsNone(ins.width)
        self.assertIsNone(ins.flags)
