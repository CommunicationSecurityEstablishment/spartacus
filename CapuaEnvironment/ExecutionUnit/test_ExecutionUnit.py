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

from CapuaEnvironment.ExecutionUnit.ExecutionUnit import ExecutionUnit
from CapuaEnvironment.IntructionFetchUnit.InstructionFetchUnit import InstructionFetchUnit
from CapuaEnvironment.IOComponent.MemoryIOController import MemoryIOController
from CapuaEnvironment.MemoryArray.MemoryArray import MemoryArray

from Configuration.Configuration import MEMORY_START_AT, \
                                        MEMORY_END_AT

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"


class TestExecutionUnit(unittest.TestCase):

    ma = MemoryArray()
    mioc = MemoryIOController(ma)
    ifu = InstructionFetchUnit(ma)
    eu = ExecutionUnit(mioc, ifu, "System")

    def test_init(self):
        """
        Validates good working of the __init__ method for ExecutionUnit
        def __init__(self, mioc: MemoryIOController=None, ifu: InstructionFetchUnit=None, name: str="System"):
        """
        self.assertRaises(RuntimeError, ExecutionUnit, None, None, None)
        self.assertRaises(RuntimeError, ExecutionUnit, self.mioc, self.ifu, None)
        self.assertRaises(RuntimeError, ExecutionUnit, self.mioc, None, "System")
        self.assertRaises(RuntimeError, ExecutionUnit, None, self.ifu, "System")
        self.assertRaises(RuntimeError, ExecutionUnit, "test", self.ifu, "System")
        self.assertRaises(RuntimeError, ExecutionUnit, self.mioc, "test", "System")
        self.assertRaises(RuntimeError, ExecutionUnit, self.mioc, self.ifu, 0x41414141)

        eu = ExecutionUnit(self.mioc, self.ifu, "System")
        self.assertEqual(self.mioc, eu.mioc)
        self.assertEqual(self.ifu, eu.ifu)
        self.assertEqual("System", eu.name)

    def test_setupCore(self):
        """
        Validates good working of the setupCore method for ExecutionUnit
        def setupCore(self, I: int=MEMORY_START_AT):
        """
        self.assertRaises(RuntimeError, self.eu.setupCore, (MEMORY_START_AT - 1))
        self.assertRaises(RuntimeError, self.eu.setupCore, (MEMORY_END_AT + 1))

        self.eu.setupCore(MEMORY_START_AT)
        self.assertEqual(MEMORY_START_AT, self.eu.I)

    def test_execute(self):
        """
        Validates good working of the execute method for ExecutionUnit
        def execute(self):
        """
        # NOP
        self.eu.setupCore(MEMORY_START_AT)
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 1, self.eu.I)
        self.assertEqual(0, self.eu.A)
        self.assertEqual(0, self.eu.B)
        self.assertEqual(0, self.eu.C)
        self.assertEqual(0, self.eu.S)
        self.assertEqual(0, self.eu.FLAGS)
        self.eu.execute()
        # NOP
        self.assertEqual(MEMORY_START_AT + 2, self.eu.I)
        self.assertEqual(0, self.eu.A)
        self.assertEqual(0, self.eu.B)
        self.assertEqual(0, self.eu.C)
        self.assertEqual(0, self.eu.S)
        self.assertEqual(0, self.eu.FLAGS)
        # MOV
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 2, 1, 0b01100000)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 3, 1, 0b00)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 4, 1, 0b00)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 5, 1, 0b00)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 6, 1, 0b01)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 7, 1, 0b00)
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 8, self.eu.I)
        self.assertEqual(1, self.eu.A)
        self.assertEqual(0, self.eu.B)
        self.assertEqual(0, self.eu.C)
        self.assertEqual(0, self.eu.S)
        self.assertEqual(0, self.eu.FLAGS)
        # JMP
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 8, 1, 0b01000001)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 9, 1, 0b00)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 10, 4, MEMORY_START_AT)
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT, self.eu.I)
        self.assertEqual(1, self.eu.A)
        self.assertEqual(0, self.eu.B)
        self.assertEqual(0, self.eu.C)
        self.assertEqual(0, self.eu.S)
        self.assertEqual(0, self.eu.FLAGS)
        # NOP
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 1, self.eu.I)
        self.assertEqual(1, self.eu.A)
        self.assertEqual(0, self.eu.B)
        self.assertEqual(0, self.eu.C)
        self.assertEqual(0, self.eu.S)
        self.assertEqual(0, self.eu.FLAGS)
        # NOP
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 2, self.eu.I)
        self.assertEqual(1, self.eu.A)
        self.assertEqual(0, self.eu.B)
        self.assertEqual(0, self.eu.C)
        self.assertEqual(0, self.eu.S)
        self.assertEqual(0, self.eu.FLAGS)

        # Beware, ACTI and DACTI tests are dependent one on anoter
        self.eu.setupCore(MEMORY_START_AT)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b11110001)      # ACTI 1
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 1, 0b11110001)  # ACTI 2
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 2, 1, 0b11110010)  # DACTI 1
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 3, 1, 0b11110010)  # DACTI 2
        # ACTI
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 1, self.eu.I)
        self.assertEqual(0b1, self.eu.IS)      # Interrupt State should be = 1 after ACTI
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 2, self.eu.I)
        self.assertEqual(0b1, self.eu.IS)      # Interrupt State should not change if ACTI is run when IS = 1
        # DACTI
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 3, self.eu.I)
        self.assertEqual(0b0, self.eu.IS)      # Interrupt State should be = 0 after DACTI
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 4, self.eu.I)
        self.assertEqual(0b0, self.eu.IS)      # Interrupt State should not change if DACTI is run when IS = 0

        # SFSTOR - Data will be written
        self.eu.setupCore(MEMORY_START_AT)
        self.eu.A = MEMORY_START_AT + 20
        self.eu.B = 0xCCCCCCCC
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b01010010)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 1, 0b00110001)  # Instruction goes: SFSTOR [LH] $B
        self.eu.FLAGS = 0b00
        self.eu.execute()
        dataWritten = self.mioc.memoryReadAtAddressForLength(MEMORY_START_AT + 20, length=4)
        self.assertEqual(MEMORY_START_AT + 2, self.eu.I)
        self.assertEqual(0xCCCCCCCC, dataWritten)
        self.assertEqual(0b10, self.eu.FLAGS)

        # SFSTOR - Data will NOT be written
        self.eu.setupCore(MEMORY_START_AT)
        self.eu.A = MEMORY_START_AT + 20
        self.eu.B = 0xBBBBBBBB
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b01010010)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 1, 0b01000001)  # Instruction goes: SFSTOR [E] $B
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 20, 4, 0xAAAAAAAA)
        self.eu.FLAGS = 0b00
        self.eu.execute()
        dataWritten = self.mioc.memoryReadAtAddressForLength(MEMORY_START_AT + 20, length=4)
        self.assertEqual(MEMORY_START_AT + 2, self.eu.I)
        self.assertNotEqual(0xBBBBBBBB, dataWritten)
        self.assertEqual(0b1, self.eu.FLAGS)

        # SIVR
        self.eu.setupCore(MEMORY_START_AT)
        self.eu.A = 0xAAAAAAAA
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b01110101)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 1, 0b00000000)  # Instruction goes: SIVR $A
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 2, self.eu.I)
        self.assertEqual(0xAAAAAAAA, self.eu.IVR)
        self.assertEqual(0xAAAAAAAA, self.eu.A)

        # HIRET - Deactivated Interrupts
        self.eu.setupCore(MEMORY_START_AT)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b11110011)
        self.mioc.memoryWriteAtAddressForLength(0x40000100, 4, 0x40000200)  # This is the return address
        self.mioc.memoryWriteAtAddressForLength(0x400000FC, 4, 0x1)  # This is the flag to be restored
        self.eu.A = 0xFF
        self.eu.IS = 0b0
        self.eu.S = 0x40000100
        self.eu.FLAGS = 0x0
        sMarker = self.eu.S
        self.eu.execute()
        self.assertEqual(0xFF, self.eu.A, "HIRET broken - bad A register value")
        self.assertEqual(0x01, self.eu.FLAGS, "HIRET broken - bad flag restoration")
        self.assertEqual(0b1, self.eu.IS, "HIRET broken - IS should not be 0")
        self.assertEqual(0x40000200, self.eu.I, "HIRET broken - Bad I address")
        self.assertEqual(sMarker, self.eu.S + 8, "HIRET broken - Bad stack")

        # INT register - Deactivated Interrupts
        self.eu.setupCore(MEMORY_START_AT)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b01110110)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 1, 0b00000000)
        self.eu.A = 0x0     # Holds the interrupt number
        self.eu.IS = 0b0
        self.eu.S = 0x40000100
        self.eu.IVR = 0x40000050
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR, 4, 0xAAAAAAAA)
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR + 4, 4, 0xBBBBBBBB)
        sMarker = self.eu.S
        self.eu.execute()
        self.assertEqual(self.eu.I, MEMORY_START_AT + 2, "INT when IS is 0 broken - Bad I address")
        self.assertEqual(self.eu.S, sMarker, "INT when IS is 0 broken - Bad stack")

        # INT register - Activated Interrupts
        self.eu.setupCore(MEMORY_START_AT)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b01110110)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 1, 0b00000000)
        self.eu.A = 0x0  # Holds the interrupt number
        self.eu.IS = 0b1
        self.eu.S = 0x40000100
        self.eu.IVR = 0x40000050
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR, 4, 0xAAAAAAAA)
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR + 4, 4, 0xBBBBBBBB)
        sMarker = self.eu.S
        iMarker = self.eu.I
        self.eu.execute()
        self.assertEqual(self.eu.I, 0xAAAAAAAA, "INT when IS is 1 broken - Bad I address")
        self.assertEqual(self.eu.S, sMarker + 4, "INT when IS is 1 broken - Bad stack")
        topStack = self.mioc.memoryReadAtAddressForLength(self.eu.S, 4)
        self.assertEqual(iMarker + 2, topStack, "INT when IS is 1 broken - Bad return address")
        # Testing the second vector entry
        self.eu.setupCore(MEMORY_START_AT)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b01110110)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 1, 0b00000000)
        self.eu.A = 0x1  # Holds the interrupt number
        self.eu.IS = 0b1
        self.eu.S = 0x40000100
        self.eu.IVR = 0x40000050
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR, 4, 0xAAAAAAAA)
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR + 4, 4, 0xBBBBBBBB)
        sMarker = self.eu.S
        iMarker = self.eu.I
        self.eu.execute()
        self.assertEqual(self.eu.I, 0xBBBBBBBB, "INT when IS is 1 broken - Bad I address")
        self.assertEqual(self.eu.S, sMarker + 4, "INT when IS is 1 broken - Bad stack")
        topStack = self.mioc.memoryReadAtAddressForLength(self.eu.S, 4)
        self.assertEqual(iMarker + 2, topStack, "INT when IS is 1 broken - Bad return address")

        # INT immediate - Deactivated Interrupts
        self.eu.setupCore(MEMORY_START_AT)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b10000011)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 1, 0b00000000)  # Interrupt number is here
        self.eu.IS = 0b0
        self.eu.S = 0x40000100
        self.eu.IVR = 0x40000050
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR, 4, 0xAAAAAAAA)
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR + 4, 4, 0xBBBBBBBB)
        sMarker = self.eu.S
        self.eu.execute()
        self.assertEqual(self.eu.I, MEMORY_START_AT + 5, "INT when IS is 0 broken - Bad I address")
        self.assertEqual(self.eu.S, sMarker, "INT when IS is 0 broken - Bad stack")

        # INT immediate - Activated Interrupts
        self.eu.setupCore(MEMORY_START_AT)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b10000011)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 4, 0b00000000)  # Interrupt number is here
        self.eu.IS = 0b1
        self.eu.S = 0x40000100
        self.eu.IVR = 0x40000050
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR, 4, 0xAAAAAAAA)
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR + 4, 4, 0xBBBBBBBB)
        sMarker = self.eu.S
        iMarker = self.eu.I
        self.eu.execute()
        self.assertEqual(self.eu.I, 0xAAAAAAAA, "INT when IS is 1 broken - Bad I address")
        self.assertEqual(self.eu.S, sMarker + 4, "INT when IS is 1 broken - Bad stack")
        topStack = self.mioc.memoryReadAtAddressForLength(self.eu.S, 4)
        self.assertEqual(iMarker + 5, topStack, "INT when IS is 1 broken - Bad return address")
        # testing the second vector entry
        self.eu.setupCore(MEMORY_START_AT)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT, 1, 0b10000011)
        self.mioc.memoryWriteAtAddressForLength(MEMORY_START_AT + 1, 4, 0b00000001)  # Interrupt number is here
        self.eu.IS = 0b1
        self.eu.S = 0x40000100
        self.eu.IVR = 0x40000050
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR, 4, 0xAAAAAAAA)
        self.mioc.memoryWriteAtAddressForLength(self.eu.IVR + 4, 4, 0xBBBBBBBB)
        sMarker = self.eu.S
        iMarker = self.eu.I
        self.eu.execute()
        self.assertEqual(self.eu.I, 0xBBBBBBBB, "INT when IS is 1 broken - Bad I address")
        self.assertEqual(self.eu.S, sMarker + 4, "INT when IS is 1 broken - Bad stack")
        topStack = self.mioc.memoryReadAtAddressForLength(self.eu.S, 4)
        self.assertEqual(iMarker + 5, topStack, "INT when IS is 1 broken - Bad return address")

    def test_reset(self):
        self.eu.setupCore(MEMORY_START_AT)
        self.eu.A = 1
        self.eu.B = 1
        self.eu.C = 1
        self.eu.D = 1
        self.eu.E = 1
        self.eu.F = 1
        self.eu.G = 1
        self.eu.H = 1
        self.eu.J = 1
        self.eu.K = 1
        self.eu.L = 1
        self.eu.M = 1
        self.eu.N = 1
        self.eu.O = 1
        self.eu.P = 1
        self.eu.S = 1
        self.eu.IS = 1
        self.eu.IVR = 1
        self.eu.FLAGS = 1
        self.eu.reset(0)  # Making sure we can set I to value requested
        count = self.eu.A + self.eu.B + self.eu.C + self.eu.D + self.eu.E + self.eu.F + self.eu.G + \
                self.eu.H + self.eu.J + self.eu.K + self.eu.L + self.eu.M + self.eu.N + self.eu.O + \
                self.eu.P + self.eu.S + self.eu.IS +self.eu.IVR + self.eu.I + self.eu.FLAGS
        self.assertEqual(count, 0)
        self.eu.setupCore(MEMORY_START_AT)
        self.eu.A = 1
        self.eu.B = 1
        self.eu.C = 1
        self.eu.D = 1
        self.eu.E = 1
        self.eu.F = 1
        self.eu.G = 1
        self.eu.H = 1
        self.eu.J = 1
        self.eu.K = 1
        self.eu.L = 1
        self.eu.M = 1
        self.eu.N = 1
        self.eu.O = 1
        self.eu.P = 1
        self.eu.S = 1
        self.eu.IS = 1
        self.eu.IVR = 1
        self.eu.FLAGS = 1
        self.eu.reset()  # Making sure we can rely on the default value for I after reset
        count = self.eu.A + self.eu.B + self.eu.C + self.eu.D + self.eu.E + self.eu.F + self.eu.G + \
                self.eu.H + self.eu.J + self.eu.K + self.eu.L + self.eu.M + self.eu.N + self.eu.O + \
                self.eu.P + self.eu.S + self.eu.IS + self.eu.IVR + self.eu.I + self.eu.FLAGS
        self.assertEqual(count, MEMORY_START_AT)

