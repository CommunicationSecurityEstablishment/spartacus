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
from CapuaEnvironment.Instruction.OperationDescription import operationDescription
from ToolChain.Assembler.Parser.Parser import Parser

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class TestParser(unittest.TestCase):

    parser = Parser(skipValidation=True)

    def test_init(self):
        """
        Test the method:
        __init__(self, file: str="")
        """
        self.assertRaises(ValueError, Parser)


    def test_readFileContent(self):
        """
        Test the method:
        _readFileContent(self, file: str="")
        """
        pathToTestFile = __file__.replace("test_Parser.py", "testAsm.txt")
        content = self.parser._readFileContent(pathToTestFile)
        self.assertEqual(11, len(content))

    def test_parseCodeFile(self):
        """
        Test the method:
        _parseCodeFile(self)
        """
        pathToTestFile = __file__.replace("test_Parser.py", "testAsm.txt")
        self.parser.fileContent = self.parser._readFileContent(pathToTestFile)
        ins, ref, size = self.parser._parseCodeFile()


    def test_parseCodeLineAdd(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # ADD
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["ADD", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10010010)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "ADD")
        self.assertEqual(buildInstruction.instructionLength, 2)
        self.assertEqual(0b1001001000000001,
                         int.from_bytes(lineInstruction, byteorder="big"))

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["ADD", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100110)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "ADD")
        self.assertEqual(buildInstruction.instructionLength, 6)
        self.assertEqual(0b11001100000000000000000000000001111111100000001,
                         int.from_bytes(lineInstruction, byteorder="big"))

    def test_parseCodeLineAnd(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # AND
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["AND", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10010111)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "AND")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["AND", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "AND")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineCall(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # CALL
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["CALL", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01110010)
        self.assertEqual(buildInstruction.sourceRegister, 1)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "CALL")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["CALL", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b10000010)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "CALL")
        self.assertEqual(buildInstruction.instructionLength, 5)

    def test_parseCodeLineCmp(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # CMP
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["CMP", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01101000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "CMP")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["CMP", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10011010)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "CMP")
        self.assertEqual(buildInstruction.instructionLength, 2)

    def test_parseCodeLineDiv(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # DIV
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["DIV", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10010101)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "DIV")
        self.assertEqual(buildInstruction.instructionLength, 2)

    def test_parseCodeLineJmp(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # JMP
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b000)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<Z>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b100)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<ZL>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b110)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<ZH>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b101)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<L>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b010)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<H>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b001)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b000)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<Z>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b100)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<ZL>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b110)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<ZH>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b101)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<L>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b010)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMP", "<H>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b001)
        self.assertEqual(buildInstruction.operationMnemonic, "JMP")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineJmpr(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        #JMPR
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b000)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<Z>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b100)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<ZL>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b110)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<ZH>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b101)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<L>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b010)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<H>", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b001)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b000)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<Z>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b100)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<ZL>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b110)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<ZH>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b101)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<L>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b010)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["JMPR", "<H>", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b01000000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, 0b001)
        self.assertEqual(buildInstruction.operationMnemonic, "JMPR")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineMemr(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # MEMR
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[4]", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x04)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[3]", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x03)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[2]", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x02)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[1]", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x01)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[4]", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x04)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[3]", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x03)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[2]", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x02)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[1]", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x01)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineMemw(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # MEMW
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMW", "[4]", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00010001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x04)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMW")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMW", "[4]", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00000000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x04)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMW")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMW", "[4]", "$A", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b00100000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, 0xFF)
        self.assertEqual(buildInstruction.width, 0x04)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMW")
        self.assertEqual(buildInstruction.instructionLength, 6)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMW", "[3]", "#0xFE", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b00110000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFE)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, 0xFF)
        self.assertEqual(buildInstruction.width, 0x03)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMW")
        self.assertEqual(buildInstruction.instructionLength, 10)

    def test_parseCodeLineMov(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # MOV
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MOV", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10011011)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MOV")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MOV", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MOV")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineMul(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # MUL
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MUL", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10010100)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MUL")
        self.assertEqual(buildInstruction.instructionLength, 2)

    def test_parseCodeLineNop(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # NOP
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["NOP"])
        self.assertEqual(buildInstruction.instructionCode, 0b11111111)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "NOP")
        self.assertEqual(buildInstruction.instructionLength, 1)

    def test_parseCodeLineNot(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # NOT
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["NOT", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01110000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "NOT")
        self.assertEqual(buildInstruction.instructionLength, 2)

    def test_parseCodeLineOr(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # OR
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["OR", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10011000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "OR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["OR", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100010)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "OR")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLinePop(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # POP
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["POP", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01110100)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "POP")
        self.assertEqual(buildInstruction.instructionLength, 2)

    def test_parseCodeLinePush(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # PUSH
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["PUSH", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01110011)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "PUSH")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["PUSH", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b10000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "PUSH")
        self.assertEqual(buildInstruction.instructionLength, 5)

    def test_parseCodeLineRet(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # RET
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["RET"])
        self.assertEqual(buildInstruction.instructionCode, 0b11110000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "RET")
        self.assertEqual(buildInstruction.instructionLength, 1)

    def test_parseCodeLineShl(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # SHL
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["SHL", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10010110)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "SHL")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["SHL", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100101)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "SHL")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineShr(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # SHR
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["SHR", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10011001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "SHR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["SHR", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100100)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "SHR")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineSnt(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # SNT
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["SNT", "$A"])
        self.assertEqual(buildInstruction.instructionCode, 0b01110001)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "SNT")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["SNT", "#0xFF"])
        self.assertEqual(buildInstruction.instructionCode, 0b10000000)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "SNT")
        self.assertEqual(buildInstruction.instructionLength, 5)

    def test_parseCodeLineSub(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # SUB
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["SUB", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10010011)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "SUB")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["SUB", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100111)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "SUB")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineXor(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """
        # XOR
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["XOR", "$A", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b10010000)
        self.assertEqual(buildInstruction.sourceRegister, 0)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "XOR")
        self.assertEqual(buildInstruction.instructionLength, 2)

        buildInstruction, lineInstruction = self.parser._parseCodeLine(["XOR", "#0xFF", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100011)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "XOR")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_parseCodeLineVarious(self):
        """
        Test the method:
        _parseCodeLine(self, line: list=[])
        """

        # XOR with comment
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["XOR", "#0xFF", "$B", ";test"])
        self.assertEqual(buildInstruction.instructionCode, 0b01100011)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "XOR")
        self.assertEqual(buildInstruction.instructionLength, 6)

        # Comment alone
        buildInstruction, lineInstruction = self.parser._parseCodeLine([";test"])
        self.assertIsNone(buildInstruction)
        self.assertIsNone(lineInstruction)

        # Memory location alone
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["test:"])
        self.assertIsNone(lineInstruction)
        self.assertEqual(buildInstruction.instructionCode, "TEST")
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, None)
        self.assertEqual(buildInstruction.destinationRegister, None)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, None)
        self.assertEqual(buildInstruction.instructionLength, None)

        # MEMR using address indicator
        buildInstruction, lineInstruction = self.parser._parseCodeLine(["MEMR", "[4]", ":test", "$B"])
        self.assertEqual(buildInstruction.instructionCode, 0b00000001)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, ":TEST:")
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, 0x04)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "MEMR")
        self.assertEqual(buildInstruction.instructionLength, 6)

    def test_translateRegisterNameToRegisterCode(self):
        """
        Test the method:
        translateRegisterNameToRegisterCode(self, registerName: str=""):
        """
        self.assertEqual(0b00, self.parser.translateRegisterNameToRegisterCode(registerName="A"))
        self.assertEqual(0b01, self.parser.translateRegisterNameToRegisterCode(registerName="B"))
        self.assertEqual(0b10, self.parser.translateRegisterNameToRegisterCode(registerName="C"))
        self.assertEqual(0b11, self.parser.translateRegisterNameToRegisterCode(registerName="S"))
        self.assertRaises(ValueError, self.parser.translateRegisterNameToRegisterCode, "D")  # Invalid register

    def test_translateTextImmediateToImmediate(self):
        """
        Test the method:
        translateTextImmediateToImmediate(self, textImmediate: str=""):
        """
        self.assertEqual(0x0, self.parser.translateTextImmediateToImmediate(textImmediate="0"))
        self.assertEqual(((0b1 ^ 0xFFFFFFFF) + 1), self.parser.translateTextImmediateToImmediate(textImmediate="-1"))
        self.assertEqual(0b11, self.parser.translateTextImmediateToImmediate(textImmediate="0b11"))
        self.assertEqual(0xFF, self.parser.translateTextImmediateToImmediate(textImmediate="0xFF"))
        self.assertRaises(ValueError, self.parser.translateTextImmediateToImmediate, "0xAAFFFFFFFF")

    def test_translateTextFlagsToCodeFlags(self):
        """
        Test the method:
        translateTextFlagsToCodeFlags(self, textFlags):
        """
        self.assertEqual(0b000, self.parser.translateTextFlagsToCodeFlags(""))
        self.assertEqual(0b100, self.parser.translateTextFlagsToCodeFlags("Z"))  # Flag (Z)ero is set
        self.assertEqual(0b100, self.parser.translateTextFlagsToCodeFlags("E"))  # Flag (Z)ero is set
        self.assertEqual(0b010, self.parser.translateTextFlagsToCodeFlags("L"))  # Flag (L)ower is set
        self.assertEqual(0b110, self.parser.translateTextFlagsToCodeFlags("LE"))  # Flag (L)ower and Z(ero) are set
        self.assertEqual(0b110, self.parser.translateTextFlagsToCodeFlags("LZ"))  # Flag (L)ower and Z(ero) are set
        self.assertEqual(0b001, self.parser.translateTextFlagsToCodeFlags("H"))  # FLAG (H)igher is set
        self.assertEqual(0b101, self.parser.translateTextFlagsToCodeFlags("HE"))  # FLAG (H)igher and Z(ero) are set
        self.assertEqual(0b101, self.parser.translateTextFlagsToCodeFlags("HZ"))  # FLAG (H)igher and Z(ero) are set
        self.assertRaises(ValueError, self.parser.translateTextFlagsToCodeFlags, "F")  # Invalid flag

    def test_evaluateAndExtractInfoFromLine(self):
        """
        Test the method:
        _evaluateAndExtractInfoFromLine(self, line, buildInstruction)
        """
        buildInstruction = Instruction(skipValidation=True)
        self.parser._evaluateAndExtractInfoFromLine(["XOR", "#0xFF", "$B", ";test"], buildInstruction)
        self.assertEqual(buildInstruction.instructionCode, None)
        self.assertEqual(buildInstruction.sourceRegister, None)
        self.assertEqual(buildInstruction.sourceImmediate, 0xFF)
        self.assertEqual(buildInstruction.destinationRegister, 1)
        self.assertEqual(buildInstruction.destinationImmediate, None)
        self.assertEqual(buildInstruction.width, None)
        self.assertEqual(buildInstruction.flags, None)
        self.assertEqual(buildInstruction.operationMnemonic, "XOR")
        self.assertEqual(buildInstruction.instructionLength, None)

        buildInstruction = Instruction(skipValidation=True)
        self.assertRaises(ValueError,
                          self.parser._evaluateAndExtractInfoFromLine,
                          ["MEMW", "[4", "#0xFF", "$A"],
                          buildInstruction)

        buildInstruction = Instruction(skipValidation=True)
        self.assertRaises(ValueError,
                          self.parser._evaluateAndExtractInfoFromLine,
                          ["MEMW", "<4", "#0xFF", "$A"],
                          buildInstruction)

        buildInstruction = Instruction(skipValidation=True)
        self.assertRaises(ValueError,
                          self.parser._evaluateAndExtractInfoFromLine,
                          ["MEMW", "$B", "#0xFF", "$A"],
                          buildInstruction)

        buildInstruction = Instruction(skipValidation=True)
        self.assertRaises(ValueError,
                          self.parser._evaluateAndExtractInfoFromLine,
                          ["MEMW", "4]", "#0xFF", "$A"],
                          buildInstruction)

    def test_findPossibleCodesForInstruction(self):
        """
        Test the method:
        _findPossibleCodesForInstruction(self, partialInstruction: Instruction=None):
        """
        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "ADD"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01100110, 0b10010010])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "AND"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01100001, 0b10010111])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "CALL"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b10000010, 0b01110010])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "CMP"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01101000, 0b10011010])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "DIV"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b10010101])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "JMP"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01000001, 0b01010001])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "JMPR"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01000000, 0b01010000])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "MEMR"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b00000001, 0b00010000])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "MEMW"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b00110000, 0b00000000, 0b00100000, 0b00010001])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "MOV"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01100000, 0b10011011])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "MUL"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b10010100])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "NOP"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b11111111])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "NOT"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01110000])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "OR"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01100010, 0b10011000])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "POP"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01110100])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "PUSH"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b10000001, 0b01110011])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "RET"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b11110000])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "SHL"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01100101, 0b10010110])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "SHR"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01100100, 0b10011001])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "SNT"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b10000000, 0b01110001])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "SUB"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01100111, 0b10010011])

        partialInstruction = Instruction(skipValidation=True)
        partialInstruction.operationMnemonic = "XOR"
        codes = self.parser._findPossibleCodesForInstruction(partialInstruction)
        self.assertEqual(codes, [0b01100011, 0b10010000])

        self.assertEqual(22, len(operationDescription))  # Just validate that nothing was added without changing test case...

    def test_getInstructionCodeAndFormUsingPossibleCodesAdd(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # ADD
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "ADD"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01100110, 0b10010010]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10010010, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesAnd(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # AND
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "AND"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01100001, 0b10010111]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10010111, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesCall(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # CALL
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "CALL"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b10000010, 0b01110010]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b01110010, instructionCode)
        self.assertEqual("InsReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesCmp(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # CMP
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "CMP"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01101000, 0b10011010]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10011010, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesDiv(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # DIV
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "DIV"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b10010101]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10010101, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesJmp(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # Jmp
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "JMP"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = 0b000
        possibleCodes = [0b01000001, 0b01010001]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b01010001, instructionCode)
        self.assertEqual("InsFlagReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesJmpr(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # JMPR
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "JMPR"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = 0b000
        possibleCodes = [0b01000000, 0b01010000]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b01010000, instructionCode)
        self.assertEqual("InsFlagReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesMemr(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # Memr
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "MEMR"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = 4
        buildInstruction.flags = None
        possibleCodes = [0b00000001, 0b00010000]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b00010000, instructionCode)
        self.assertEqual("InsWidthRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesMemw(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # MEMW
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "MEMW"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = 4
        buildInstruction.flags = None
        possibleCodes = [0b00110000, 0b00000000, 0b00100000, 0b00010001]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b00010001, instructionCode)
        self.assertEqual("InsWidthRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesMov(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # MOV
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "MOV"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01100000, 0b10011011]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10011011, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesMul(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # MUL
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "MUL"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b10010100]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10010100, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesNop(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # NOP
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "NOP"
        buildInstruction.sourceRegister = None
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b11111111]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b11111111, instructionCode)
        self.assertEqual("Ins", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesNot(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # NOT
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "NOT"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01110000]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b01110000, instructionCode)
        self.assertEqual("InsReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesOr(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # OR
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "OR"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01100010, 0b10011000]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10011000, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesPop(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # POP
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "POP"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01110100]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b01110100, instructionCode)
        self.assertEqual("InsReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesPush(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # PUSH
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "PUSH"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b10000001, 0b01110011]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b01110011, instructionCode)
        self.assertEqual("InsReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesRet(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # RET
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "RET"
        buildInstruction.sourceRegister = None
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b11110000]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b11110000, instructionCode)
        self.assertEqual("Ins", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesShl(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # SHL
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "SHL"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01100101, 0b10010110]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10010110, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesShr(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # SHR
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "SHR"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01100100, 0b10011001]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10011001, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesSnt(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # SHR
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "SNT"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = None
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b10000000, 0b01110001]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b01110001, instructionCode)
        self.assertEqual("InsReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesSub(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # SUB
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "SUB"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01100111, 0b10010011]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10010011, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesXor(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # XOR
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "XOR"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = None
        buildInstruction.flags = None
        possibleCodes = [0b01100011, 0b10010000]
        instructionCode, instructionForm = self.parser._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                    possibleCodes)
        self.assertEqual(0b10010000, instructionCode)
        self.assertEqual("InsRegReg", instructionForm)

    def test_getInstructionCodeAndFormUsingPossibleCodesXorWithErrors(self):
        """
        Test the method:
        _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        # XOR
        buildInstruction = Instruction(skipValidation=True)
        buildInstruction.operationMnemonic = "XOR"
        buildInstruction.sourceRegister = 0
        buildInstruction.sourceImmediate = None
        buildInstruction.destinationRegister = 1
        buildInstruction.destinationImmediate = None
        buildInstruction.width = 4
        buildInstruction.flags = None
        possibleCodes = [0b01100011, 0b10010000]
        self.assertRaises(ValueError,
                          self.parser._getInstructionCodeAndFormUsingPossibleCodes,
                          buildInstruction,
                          possibleCodes)
