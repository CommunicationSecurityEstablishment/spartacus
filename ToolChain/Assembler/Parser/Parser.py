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

from ToolChain.Assembler.Constants import REGISTERS, \
                                          INSTRUCTION_LIST, \
                                          MEMORY_REFERENCE_INDICATORS, \
                                          EXPORTED_REFERENCE_INDICATOR, \
                                          DATA_NUMERIC_INDICATOR, \
                                          DATA_ALPHA_INDICATOR, \
                                          DATA_MEMORY_REFERENCE, \
                                          COMMENT_INDICATORS, \
                                          IMMEDIATE_PREFIX, \
                                          REGISTER_PREFIX, \
                                          FLAGS_INDICATORS, \
                                          WIDTH_INDICATORS, \
                                          MAX_OPERAND_COUNT, \
                                          INSTRUCTION_FLAG, \
                                          LOCAL_REFERENCE_FLAG, \
                                          GLOBAL_REFERENCE_FLAG, \
                                          EMPTY_LINE_FLAG, \
                                          STATE0, \
                                          STATE1, \
                                          STATE2, \
                                          STATE3, \
                                          STATE4, \
                                          STATE5, \
                                          STATE6, \
                                          STATE7, \
                                          STATE8, \
                                          STATE9, \
                                          STATE10

from CapuaEnvironment.IntructionFetchUnit.FormDescription import formDescription
from CapuaEnvironment.Instruction.OperationDescription import operationDescription

import struct
import re


class Parser:
    """
    This class is used to parse the text format code and build a list of instruction from it.
    To do so, it has a direct link into CapuaEnvironment instruction information. Those class
    and description files are directly used in order to help build the binary code required
    to run code inside of the Capua environment. The steps are as follows:
    1. Verify if the file name is valid, and that it is not empty.
    2. Read the file and parse each line into a list to be evaluated one at a time.
    3. Evaluate each line and, if not an empty line, store instructions and memory references in lists.
        - Parse each line and determine whether we're dealing with an instruction, memory reference, data, etc.
        - If an instruction is found, determine all possible forms for this instruction (eg. InsRegReg)
        - Using possible forms for an instruction, determine the correct instruction code based on given operands.
    4. Once all info has been evaluated, if correct, we generate the binary code for each instruction
    """

    relativeAddress = 0                       # Used to determine memory address of a label at a given point in the file

    def parse(self, text):
        """
        This takes in an individual line of code, parses the info and returns the fully built binary code, or returns a
        memory reference with the appropriate offset.
        :param text: Str, Individual line of code.
        :return: tuple: Represents the binary instruction, the current offset, and the appropriate flag
        """

        self.relativeAddress = 0                              # Reset offset (instruction size) for every line parsed
        line = text.split(COMMENT_INDICATORS, maxsplit=1)[0]  # This removes the comments from the line
        line = line.split()                                   # Our line split into individual tokens

        # This ensures we don't evaluate an empty line. This also handles a line full of spaces
        if len(line) == 0:
            return "", self.relativeAddress, EMPTY_LINE_FLAG

        # First off, we need to determine if this line has a label, alpha value, numeric value, or mem ref to evaluate
        # If so, we can simply return the label, the offset, and the appropriate flag

        mnemonic = line[0].upper()                # First token of the line, either a label identifier or instruction
        operands = line[1:]                       # The remainder of the line, our list of operands
        labelFlag = INSTRUCTION_FLAG              # Determines what type of data we're returning

        if re.search(r'(\.(\w*))|(\w*:)', mnemonic):
            # We had a match for identifier patterns, so we assume there's no instruction.
            instruction, labelFlag = self._evaluateIndicatorData(text, mnemonic)
            return instruction, self.relativeAddress, labelFlag

        elif mnemonic in INSTRUCTION_LIST:
            # Next we check if the first item on the line is an instruction
            # If we make it to this line, there were no data indicators (.dataAlpha, comments, labels etc.)
            # We build our instruction's form by verifying each operand after the instruction
            # This will allow us to determine which "state" the instruction belongs to.
            operands = [op.upper() for op in operands]
            form = self._evaluateFormBasedOnOperands(operands)
            instruction = self._findInstructionCode(form, mnemonic)

            # Finally we evaluate how we will build our binary code. Each state has a distinct pattern we must follow
            instruction += self._buildBinaryCode(form, operands)

        else:
            # The instruction was not in the list, and no identifier mnemonics were found.
            raise ValueError("Invalid assembly instruction format")

        return instruction, self.relativeAddress, labelFlag

    def _findInstructionCode(self, form, mnemonic):
        """
        Finds the instruction's binary code based on the instruction's form, which relies on the operands after the
        instruction. Since each instruction + form pair has one distinct instruction length, we also add it here to the
        relativeAddressCounter.
        :param form: str, the assembled form of the particular instruction (ex: InsRegReg)
        :param mnemonic: str list, our line read from input split into individual tokens
        :return: bytestring, our instruction's correct binary code
        """

        instruction = b''

        try:
            # We make sure the form is described in the formDescription Class
            insform = formDescription[form]
            ins = operationDescription[mnemonic]

        except KeyError as e:
            raise ValueError("Invalid instruction format")

        for possibleCodes in ins:
            # We shift the binary code by 4 bits to see if we have a match with typeCode for this form
            # ex: typeCode = 0010, possiblecodes = 00101011 would be true since the first 4 bits match.
            # Once we have our instruction match, we know the size of the instruction and we add to the counter
            if insform["typeCode"] is (possibleCodes >> 4):
                self.relativeAddress += insform["length"]
                instruction += bytes((possibleCodes,))
                return instruction
        else:
            # We shouldn't get to this part since the instruction was in the instruction list. Code error.
            raise ValueError("Invalid instruction format")

    def _evaluateIndicatorData(self, text, mnemonic):
        """
        In this method, we are dealing with identifiers, meaning either .dataAlpha, .dataNumeric, .global, a label, or
        a comment.
        :param text: str, The raw line of text as read from the file directly
        :return: bytestring, Instruction containing relevant data, and the appropriate flag to be used by the assembler
        """

        operands = text.split()
        labelFlag = INSTRUCTION_FLAG
        instruction = b''

        if mnemonic[-1] == MEMORY_REFERENCE_INDICATORS:
            # Local (internal) label that can only be used within the file
            if mnemonic.count(MEMORY_REFERENCE_INDICATORS) > 1:
                # Forcing coding standard: labels can't contain colons ":"
                raise ValueError("Syntax error, memory reference has too many \":\"")
            instruction = mnemonic[:-1].upper()
            labelFlag = LOCAL_REFERENCE_FLAG

        elif mnemonic == EXPORTED_REFERENCE_INDICATOR:
            # Global (external) label that can be used by other files
            instruction = operands[1].upper()
            labelFlag = GLOBAL_REFERENCE_FLAG

        elif mnemonic == DATA_ALPHA_INDICATOR:
            # DataAlpha text, which must be converted into bytestring
            operands = text.split(maxsplit=1)
            instruction += operands[1][:-1].encode("utf-8")
            self.relativeAddress += len(instruction) + 1
            instruction += b'\x00'

        elif mnemonic == DATA_NUMERIC_INDICATOR:
            # DataNumeric number which must be converted to binary
            numeric = self.translateTextImmediate(operands[1])
            instruction += struct.pack(">I", numeric)
            self.relativeAddress += 4

        elif mnemonic == DATA_MEMORY_REFERENCE:
            # Memory reference, label will be returned as the instruction
            instruction += b':' + operands[1].encode("utf-8").upper() + b':'
            self.relativeAddress += 4

        else:
            # Identifier not in accepted list
            raise ValueError("Invalid instruction format")

        return instruction, labelFlag

    def _evaluateFormBasedOnOperands(self, operands):
        """
        Method looks at the whole line after the initial instruction and determines its form based on the operands.
        Registers are concatenated as "REG", immediates and lables as "IMM", etc.
        :param operands: str list, Line split into individual operands
        :return: str, Fully constructed form
        """

        form = "Ins"

        if len(operands) > MAX_OPERAND_COUNT:
            raise ValueError("Invalid instruction format: Too many operands")

        for element in operands:
            if element[0] == REGISTER_PREFIX:
                form += "Reg"
            elif element[0] == IMMEDIATE_PREFIX:
                form += "Imm"
            elif element[0] + element[-1] == FLAGS_INDICATORS:
                form += "Flag"
            elif element[0] + element[-1] == WIDTH_INDICATORS:
                form += "Width"
            else:
                form += "Imm"

        return form

    def _buildBinaryCode(self, form, operandList):
        """
        This is the last step in parsing a line of code: assembling the actual binary code. Each state has a particular
        structure that is needed to be read correctly by the Capua VM. This method takes care of every form and gets
        the binary values for each register and immediate value. Labels are converted to bytestring as they are.
        :param state: str, State of the instruction based on evaluated form (ex: InsReg = STATE1)
        :param operandList: str list, List of operands to be converted to binary code and assembled
        :return: bytestring, The newly built binary code for the instruction and operands
        """

        instruction = b''

        if form == STATE0:
            # Instruction is already complete, there is only one operand (the instruction itself, Ins)
            pass

        elif form == STATE1:
            # Form = Instruction - Register
            register = self.translateRegisterName(operandList[0][1:])
            instruction += bytes(0b0000) + bytes((register,))

        elif form == STATE2:
            # Form = Instruction - Register - Register
            register = self.translateRegisterName(operandList[0][1:])
            register2 = self.translateRegisterName(operandList[1][1:])
            register = (register << 4) + register2
            instruction += bytes((register,))

        elif form == STATE3:
            # Form = Instruction - Immediate
            if operandList[0][0] == "#":
                immediate = self.translateTextImmediate(operandList[0][1:])
                instruction += immediate.to_bytes(4, byteorder='big')
            else:
                instruction += self.verifyLabel(operandList[0])

        elif form == STATE4:
            # Form = Instruction - Immediate - Register
            register = self.translateRegisterName(operandList[1][1:])
            if operandList[0][0] == "#":
                immediate = self.translateTextImmediate(operandList[0][1:])
                instruction += immediate.to_bytes(4, byteorder='big') + bytes(0b0000) + bytes((register,))
            else:
                instruction += self.verifyLabel(operandList[0]) + bytes(0b0000) + bytes((register,))

        elif form == STATE5:
            # Form = Instruction - Width - Immediate - Immediate
            width = operandList[0][1:-1]
            if operandList[1][0] == IMMEDIATE_PREFIX:
                immediate = self.translateTextImmediate(operandList[1][1:])
                immediate = immediate.to_bytes(4, byteorder='big')
            else:
                immediate = self.verifyLabel(operandList[1])

            if operandList[2][0] == IMMEDIATE_PREFIX:
                immediate2 = self.translateTextImmediate(operandList[2][1:])
                immediate2 = immediate2.to_bytes(4, byteorder='big')
            else:
                immediate2 = self.verifyLabel(operandList[2])

            width = self.translateTextImmediate(width)
            instruction += bytes(0b0000) + bytes((width,)) + immediate + immediate2

        elif form == STATE6:
            # Form = Instruction - Width - Immediate - Register
            width = operandList[0][1:-1]
            if operandList[1][0] == IMMEDIATE_PREFIX:
                immediate = self.translateTextImmediate(operandList[1][1:])
                immediate = immediate.to_bytes(4, byteorder='big')
            else:
                immediate = self.verifyLabel(operandList[1])

            register = self.translateRegisterName(operandList[2][1:])
            width = self.translateTextImmediate(width)
            width = (width << 4) + register
            instruction += bytes((width,)) + immediate

        elif form == STATE7:
            # Form = Instruction - Width - Register - Immediate
            width = operandList[0][1:-1]
            register = self.translateRegisterName(operandList[1][1:])
            if operandList[2][0] == IMMEDIATE_PREFIX:
                immediate = self.translateTextImmediate(operandList[2][1:])
                immediate = immediate.to_bytes(4, byteorder='big')
            else:
                immediate = self.verifyLabel(operandList[2])

            width = self.translateTextImmediate(width)
            width = (width << 4) + register
            instruction += bytes((width,)) + immediate

        elif form == STATE8:
            # Form = Instruction - Width - Register - Register
            width = operandList[0][1:-1]
            register = self.translateRegisterName(operandList[1][1:])
            register2 = self.translateRegisterName(operandList[2][1:])
            width = self.translateTextImmediate(width)
            width = (width << 4) + register
            instruction += bytes((width,)) + bytes((register2,))

        elif form == STATE9:
            # Form = Instruction - Flag - Immediate
            flag = self.translateTextFlags(operandList[0][1:-1])
            if operandList[1][0] == "#":
                immediate = self.translateTextImmediate(operandList[1][1:])
                instruction += bytes((flag,)) + bytes(0b0000) + immediate.to_bytes(4, byteorder='big')
            else:
                instruction += bytes((flag,)) + bytes(0b0000) + self.verifyLabel(operandList[1])

        elif form == STATE10:
            # Form = Instruction - Flag - Register
            flag = self.translateTextFlags(operandList[0][1:-1])
            register = self.translateRegisterName(operandList[1][1:])
            flag = (flag << 4) + register
            instruction += bytes((flag,))

        else:
            # Instruction is invalid
            raise ValueError("Invalid instruction format")

        return instruction

    def verifyLabel(self, label):
        """
        Function takes a given label and validates it. Labels can't contain colons when used in an instruction.
        For example, MOV label $A is valid, but MOV :label $A is not. We then return the label converted to its
        appropriate form for the .o file, with colons on each end as a bytestring.
        :param label: str, label to be evaluated
        :return: bytestring, encoded label to be returned as immediate operand
        """

        immediate = b''

        if label.count(MEMORY_REFERENCE_INDICATORS) == 0:
            immediate += b':' + label.encode("utf-8") + b':'
        else:
            raise ValueError("Syntax error, memory reference may not contain any colons in its name - \":\"")

        return immediate

    def translateRegisterName(self, registerName: str=""):
        """
        This takes a register name and returns a register code as per:
            A = 0b0000
            B = 0b0001
            C = 0b0010
            etc...
        Throws error if register is not valid
        :param registerName: str, representing the register that needs translation
        :return: int, the int that represents the register
        """

        try:
            registerCode = REGISTERS[registerName]
        except KeyError as e:
            raise ValueError("Invalid instruction format: invalid register {}".format(registerName))

        return registerCode

    def translateTextImmediate(self, textImmediate: str = ""):
        """
        This will translate an immediate value in a way that can be understood by the architecture.
        :param textImmediate: str, an immediate value to be translated
        :return: int, an immediate that can be worked on
        """

        immediate = None
        isNegative = False
        textImmediate = textImmediate.lower()  # Needed in case of 0XFF instead of 0xFF

        if textImmediate[0] == "-":
            isNegative = True
            textImmediate = textImmediate[1:]

        if len(textImmediate) > 2 and textImmediate[0:2] == "0b":
            # Indicates binary immediate
            baseToUse = 2
            textImmediate = textImmediate[2:]
        elif len(textImmediate) > 2 and textImmediate[0:2] == "0x":
            # Indicate hexadecimal immediate
            baseToUse = 16
            textImmediate = textImmediate[2:]
        else:
            # Take a leap of faith! This should be base 10
            baseToUse = 10

        immediate = int(textImmediate, baseToUse)

        validationImmediate = immediate
        immediate &= 0xFFFFFFFF  # Maximum immediate value is 32 bits

        if validationImmediate != immediate:
            raise ValueError("Given immediate value is too big, {} received but maxim value is 0xFFFFFFFF".format(
                                                                                        hex(validationImmediate)))

        if isNegative:
            # If number was negative, get the 2 complement for this number
            immediate ^= 0xFFFFFFFF  # Flips all the bits, yield the 1 complement
            immediate += 1  # 1 complement + 1 gives the 2 complement
            immediate &= 0xFFFFFFFF  # Trim down to acceptable size!

        return immediate

    def translateTextFlags(self, textFlags):
        """
        Will translate a text FLAGs to flags code as:
        FLAGS: 0b000 : Equal, Lower, Higher
        :param textFlags: str, the flags from the source file
        :return:
        """
        codeFlags = 0b000
        originalFlags = textFlags
        textFlags = textFlags.lower()

        if "z" in textFlags or "e" in textFlags:
            codeFlags |= 0b100
            textFlags = textFlags.replace("z", "")
            textFlags = textFlags.replace("e", "")

        if "l" in textFlags:
            codeFlags |= 0b010
            textFlags = textFlags.replace("l", "")

        if "h" in textFlags:
            codeFlags |= 0b001
            textFlags = textFlags.replace("h", "")

        if len(textFlags) > 0:
            # Invalid flag selection detected!
            raise ValueError("Invalid conditional flag detected {} was provided but is invalid".format(originalFlags))

        return codeFlags
