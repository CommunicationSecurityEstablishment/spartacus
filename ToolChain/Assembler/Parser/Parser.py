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
__version__ = "2.1"
__maintainer__ = "CSE"
__status__ = "Dev"

from Configuration.Configuration import REGISTER_A, \
                                        REGISTER_B, \
                                        REGISTER_C, \
                                        REGISTER_D, \
                                        REGISTER_E, \
                                        REGISTER_F, \
                                        REGISTER_G, \
                                        REGISTER_A2, \
                                        REGISTER_B2, \
                                        REGISTER_C2, \
                                        REGISTER_D2, \
                                        REGISTER_E2, \
                                        REGISTER_F2, \
                                        REGISTER_G2, \
                                        REGISTER_S, \
                                        REGISTER_S2, \
                                        INSTRUCTION_LIST, \
                                        IDENTIFIER_LIST, \
                                        LABEL_INSTRUCTIONS

from CapuaEnvironment.IntructionFetchUnit.FormDescription import formDescription
from CapuaEnvironment.Instruction.OperationDescription import operationDescription

import struct


class Parser:

    relativeAddressCounter = 0                # Used to determine memory address of a label at a given point in the file
    lineno = 0                                                           # Used to pinpoint where ValueErrors are raised

    def build(self, text):
        """
        This is the main driver method for the parser. It takes in an individual line of code, parses the info and
        sends the fully built binary code to the assembler, or returns a memory reference with the appropriate offset.
        :param text: Str, The line of text as read from the file
        :return: The encoded binary instruction for the line, the current offset, and the label flag used by assembler
        """

        line = text.split()                     # We split the line with space as a delimiter. Each token is an argument
        instruction = b""                                                  # Instruction will be written as a bytestring
        arglist = []                  # We keep each argument in a list to extract their appropriate binary values later
        found = False                                          # Flag to indicate if instruction was found in state list
        form = "Ins"                                                    # We assume the first argument is an instruction
        labelFlag = 0                # Used by the assembler to determine if we return a memory reference or instruction
        dataIdentifier = line[0].upper()               # used for special identifiers such as .dataAlpha, comments etc.
        self.lineno += 1

        if (dataIdentifier in IDENTIFIER_LIST) or (dataIdentifier[0] in IDENTIFIER_LIST) or \
                                                  (dataIdentifier[-1] in IDENTIFIER_LIST):
            # First off, we need to determine if this line has a label or global label to be referenced
            # If so, we can simply return to the Assembler class with the label, the offset, and the appropriate flag
            instruction, labelFlag = self._evaluateIndicatorData(text, dataIdentifier, line, instruction, labelFlag)

            return instruction, self.relativeAddressCounter, labelFlag

        elif line[0].upper() in INSTRUCTION_LIST:
            # Next we check if the first item on the line is an instruction
            # If we make it to this line, there were no data indicators (.dataAlpha, comments, labels etc.)
            line = text.upper()
            line = line.split()
            labelFlag = 0

            # We build our instruction's form by verifying each argument after the instruction
            # This will allow us to determine which "state" the instruction belongs to.
            form, arglist = self._evaluateFormBasedOnArguments(line, form, arglist)
            instruction += self._findInstructionCode(form, line, instruction)
            state = self._definestateAndAddRelativeAddress(form)

            # Finally we evaluate how we will build our binary code. Each state has a distinct pattern we must follow
            instruction = self._buildBinaryCodeFromInstructionAndArguments(line[0], state, arglist, instruction)

        else:
            # The instruction was not in the list, and no identifier mnemonics were found.
            raise ValueError("Invalid code format at line " + str(self.lineno))

        return instruction, self.relativeAddressCounter, labelFlag

    def _findInstructionCode(self, form, line, instruction):
        """
        Finds the instruction's binary code based on its form, which relies on the arguments after the instruction.
        :param form: str, the assembled form of the particular instruction (ex: instruction-register-register)
        :param line: str list, our line read from input split into individual arguments
        :param instruction: bytestring, will contain our final binary code passed back to assembler
        :return: our instruction's correct binary code
        """

        try:
            insform = formDescription[form]
        except KeyError as e:
            raise ValueError("Invalid instruction format at line " + str(self.lineno))

        try:
            ins = operationDescription[line[0]]
        except KeyError as e:
            raise ValueError("Invalid instruction format at line " + str(self.lineno))

        found = False

        for possiblecodes in ins:
            if insform["typeCode"] is (possiblecodes >> 4):
                found = True
                instruction += bytes((possiblecodes,))
        if not found:
            # We shouldn't get to this part since the instruction was in the instruction list. Code error.
            raise ValueError("Invalid instruction format at line " + str(self.lineno))

        return instruction

    def _definestateAndAddRelativeAddress(self, form):
        """
        Takes in the form based on instruction and its arguments and determines which form it belongs to.
        This state contains all possible instructions for that particular form. This method also adds the length of
        the instruction to the relativeAddressCounter. Each form only has one possible length, so we add it here.
        :param form: str, The form of the instruction based on its arguments (ex: instruction-register-immediate)
        :return: The appropriate state string for the instruction form
        """

        if form == "Ins":
            form = "STATE0"
            self.relativeAddressCounter += 1
        elif form == "InsReg":
            form = "STATE1"
            self.relativeAddressCounter += 2
        elif form == "InsRegReg":
            form = "STATE2"
            self.relativeAddressCounter += 2
        elif form == "InsImm":
            form = "STATE3"
            self.relativeAddressCounter += 5
        elif form == "InsImmReg":
            form = "STATE4"
            self.relativeAddressCounter += 6
        elif form == "InsWidthImmImm":
            form = "STATE5"
            self.relativeAddressCounter += 10
        elif form == "InsWidthImmReg":
            form = "STATE6"
            self.relativeAddressCounter += 6
        elif form == "InsWidthRegImm":
            form = "STATE7"
            self.relativeAddressCounter += 6
        elif form == "InsWidthRegReg":
            form = "STATE8"
            self.relativeAddressCounter += 3
        elif form == "InsFlagImm":
            form = "STATE9"
            self.relativeAddressCounter += 6
        elif form == "InsFlagReg":
            form = "STATE10"
            self.relativeAddressCounter += 2
        else:
            # too many arguments or arguments' form don't fit any state description
            raise ValueError("Invalid instruction format at line " + str(self.lineno))

        return form

    def _evaluateIndicatorData(self, text, dataIdentifier, line, instruction, labelFlag):
        """
        This method indicates that we are NOT dealing with an instruction, and that we must parse data for a string,
        numeric value, a comment, a label, or global reference.
        :param text: str, The raw line of text as read from the file directly
        :param dataIdentifier: str, The first argument of the line, used to determine which identifier we have
        :param line: str list, The line split into individual arguments using a space delimiter by default
        :param instruction: bytestring, Will contain the piece of data based on the appropriate identifier
        :param labelFlag: int, Used by Assembler to determine if we return a label, global ref, or data/instruction
        :return: Instruction containing relevant data, and the appropriate flag to be used by the assembler
        """
        if dataIdentifier[-1] == ":" and dataIdentifier[0] != ";":
            # We wouldn't want to accidentally add a memory reference that was part of a comment

            if dataIdentifier.count(':') > 1:
                # Forcing coding standard: labels can't contain colons ":"
                raise ValueError("Syntax error, memory reference has too many \":\"")
            instruction = dataIdentifier[:-1].upper()
            labelFlag = 1

        elif dataIdentifier == ".GLOBAL":
            # Global (external) label that can be used by other files
            instruction = line[1].upper()
            labelFlag = 2

        elif dataIdentifier[0] == ";":
            # Just a comment, we simply ignore
            instruction = ""
            labelFlag = 3

        elif dataIdentifier == ".DATAALPHA":
            # DataAlpha text, which must be converted into bytestring
            text = text.split(maxsplit=1)
            instruction += text[1][:-1].encode("utf-8")
            self.relativeAddressCounter += len(instruction) + 1
            instruction += b'\x00'

        elif dataIdentifier == ".DATANUMERIC":
            # DataNumeric number which must be converted to binary
            numeric = self.translateTextImmediateToImmediate(line[1][1:])
            instruction += struct.pack(">I", (numeric))
            self.relativeAddressCounter += 4

        elif dataIdentifier == ".DATAMEMREF":
            # Memory reference, label will be returned as the instruction
            if line[1][0] == ":":
                memref = line[1][1:].upper()
            else:
                memref = line[1].upper()
            instruction += b':' + memref.encode("utf-8") + b':'
            self.relativeAddressCounter += 4

        else:
            # Error in code, as the mnemonic MUST be in the accepted list for this method to be called at all
            raise ValueError("Assembler code error")

        return instruction, labelFlag

    def _evaluateFormBasedOnArguments(self, line, form, arglist):
        """
        Method looks at the whole line after the initial instruction and determines its form based on the arguments.
        Registers are concatenated as "REG", immediates and lables as "IMM", etc. We also populate a list of arguments
        as they are to be constructed into binary code later.
        :param line: str list, Line split into individual arguments
        :param form: str, will be built up based on arguments on the line in this method
        :param arglist: str list, Will contain our list of arguments to be used later when assembling our binary code
        :return: Fully constructed form and newly populated list of arguments
        """

        argcount = 0

        for arg in line[1:]:
            if arg[0] == "$":
                form += "Reg"
            elif arg[0] == "#":
                form += "Imm"
            elif arg[0] == "<" and arg[-1] == ">":
                form += "Flag"
            elif arg[0] == "[" and arg[-1] == "]":
                form += "Width"
            elif arg[0] == ";":
                # We found a comment, we break out of the loop
                break
            else:
                form += "Imm"
            arglist.append(arg)                      # We store the arguments to use later when building our binary code
            argcount += 1

        if argcount > 3:
            raise ValueError("Invalid instruction format: Too many arguments at line " + str(self.lineno))

        return form, arglist

    def _buildBinaryCodeFromInstructionAndArguments(self, ins, state, arglist, instruction):
        """
        This is the last step in parsing a line of code: assembling the actual binary code. Each state has a particular
        structure that is needed to be read correctly by the Capua VM. This method takes care of every form and gets
        the binary values for each register and immediate value. Labels are converted to bytestring as they are.
        :param ins: str, the actual instruction itself
        :param state: str, State of the instruction based on evaluated form (ex: instruction-register = STATE1)
        :param arglist: str list, List of arguments to be converted to binary code and assembled
        :param instruction: bytestring, our final binary code to be returned to the assembler
        :return: The newly built binary code for the instruction and arguments
        """

        if state == "STATE0":
            # Instruction is already complete, there is only one argument (the instruction itself)
            pass

        elif state == "STATE1":
            register = self.translateRegisterNameToRegisterCode(arglist[0][1:])
            instruction += bytes(0b0000) + bytes((register,))

        elif state == "STATE2":
            register = self.translateRegisterNameToRegisterCode(arglist[0][1:])
            register2 = self.translateRegisterNameToRegisterCode(arglist[1][1:])
            register = (register << 4) + register2
            instruction += bytes((register,))

        elif state == "STATE3":
            if arglist[0][0] == "#":
                immediate = self.translateTextImmediateToImmediate(arglist[0][1:])
                instruction += immediate.to_bytes(4, byteorder='big')
            elif ins in LABEL_INSTRUCTIONS:
                instruction += b':' + arglist[0].encode("utf-8") + b':'

        elif state == "STATE4":
            register = self.translateRegisterNameToRegisterCode(arglist[1][1:])
            if arglist[0][0] == "#":
                immediate = self.translateTextImmediateToImmediate(arglist[0][1:])
                instruction += immediate.to_bytes(4, byteorder='big') + bytes(0b0000) + bytes((register,))
            elif ins in LABEL_INSTRUCTIONS:
                instruction += b':' + arglist[0].encode("utf-8") + b':' + bytes(0b0000) + bytes((register,))

        elif state == "STATE5":
            width = arglist[0][1:-1]
            immediate = self.translateTextImmediateToImmediate(arglist[1][1:])
            immediate2 = self.translateTextImmediateToImmediate(arglist[2][1:])
            width = self.translateTextImmediateToImmediate(width)
            instruction += bytes(0b0000) + bytes((width,)) + immediate.to_bytes(4, byteorder='big') + \
                                                             immediate2.to_bytes(4, byteorder='big')

        elif state == "STATE6":
            width = arglist[0][1:-1]
            immediate = self.translateTextImmediateToImmediate(arglist[1][1:])
            register = self.translateRegisterNameToRegisterCode(arglist[2][1:])
            width = self.translateTextImmediateToImmediate(width)
            width = (width << 4) + register
            instruction += bytes((width,)) + immediate.to_bytes(4, byteorder='big')

        elif state == "STATE7":
            width = arglist[0][1:-1]
            register = self.translateRegisterNameToRegisterCode(arglist[1][1:])
            immediate = self.translateTextImmediateToImmediate(arglist[2][1:])
            width = self.translateTextImmediateToImmediate(width)
            width = (width << 4) + register
            instruction += bytes((width,)) + immediate.to_bytes(4, byteorder='big')

        elif state == "STATE8":
            width = arglist[0][1:-1]
            register = self.translateRegisterNameToRegisterCode(arglist[1][1:])
            register2 = self.translateRegisterNameToRegisterCode(arglist[2][1:])
            width = self.translateTextImmediateToImmediate(width)
            width = (width << 4) + register
            instruction += bytes((width,)) + bytes((register2,))

        elif state == "STATE9":
            flag = self.translateTextFlagsToCodeFlags(arglist[0][1:-1])
            if arglist[1][0] == "#":
                immediate = self.translateTextImmediateToImmediate(arglist[1][1:])
                instruction += bytes((flag,)) + bytes(0b0000) + immediate.to_bytes(4, byteorder='big')
            elif ins in LABEL_INSTRUCTIONS:
                instruction += bytes((flag,)) + bytes(0b0000) + b':' + arglist[1].encode("utf-8") + b':'

        elif state == "STATE10":
            flag = self.translateTextFlagsToCodeFlags(arglist[0][1:-1])
            register = self.translateRegisterNameToRegisterCode(arglist[1][1:])
            flag = (flag << 4) + register
            instruction += bytes((flag,))

        else:
            # Nothing was valid in the first argument
            raise ValueError("Invalid instruction format at line " + str(self.lineno))

        return instruction

    def translateRegisterNameToRegisterCode(self, registerName: str=""):
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
        registerCode = None
        registerName = registerName.upper()

        if registerName == "A":
            registerCode = REGISTER_A
        elif registerName == "B":
            registerCode = REGISTER_B
        elif registerName == "C":
            registerCode = REGISTER_C
        elif registerName == "D":
            registerCode = REGISTER_D
        elif registerName == "E":
            registerCode = REGISTER_E
        elif registerName == "F":
            registerCode = REGISTER_F
        elif registerName == "G":
            registerCode = REGISTER_G
        elif registerName == "G":
            registerCode = REGISTER_G
        elif registerName == "A2":
            registerCode = REGISTER_A2
        elif registerName == "B2":
            registerCode = REGISTER_B2
        elif registerName == "C2":
            registerCode = REGISTER_C2
        elif registerName == "D2":
            registerCode = REGISTER_D2
        elif registerName == "E2":
            registerCode = REGISTER_E2
        elif registerName == "F2":
            registerCode = REGISTER_F2
        elif registerName == "G2":
            registerCode = REGISTER_G2
        elif registerName == "S":
            registerCode = REGISTER_S
        elif registerName == "S2":
            registerCode = REGISTER_S2
        else:
            raise ValueError("Invalid register given. '{}' seen as input, expect valid register".format(registerName))

        return registerCode

    def translateTextImmediateToImmediate(self, textImmediate: str=""):
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
            raise ValueError("Given immediate value is too big, {} received but maxim value is 0xFFFFFFFF".format(hex(validationImmediate)))

        # If number was negative, get the 2 complement for this number
        if isNegative:
            immediate ^= 0xFFFFFFFF  # Flips all the bits, yield the 1 complement
            immediate += 1  # 1 complement + 1 gives the 2 complement
            immediate &= 0xFFFFFFFF  # Trim down to acceptable size!

        return immediate

    def translateTextFlagsToCodeFlags(self, textFlags):
        """
        Will translate a text FLAGs to flags code as:
        FLAGS: 0b000 : Zero, Lower, Higher
        :param textFlags: str, the flags themselves as a string
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
