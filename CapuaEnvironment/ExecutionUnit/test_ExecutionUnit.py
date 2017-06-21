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
__version__ = "1.3"
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
        # MOV
        self.eu.execute()
        self.assertEqual(MEMORY_START_AT + 8, self.eu.I)
        self.assertEqual(1, self.eu.A)
        self.assertEqual(0, self.eu.B)
        self.assertEqual(0, self.eu.C)
        self.assertEqual(0, self.eu.S)
        self.assertEqual(0, self.eu.FLAGS)
