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

from CapuaEnvironment.Instruction.Instruction import Instruction
from CapuaEnvironment.Instruction.OperationDescription import operationDescription
from CapuaEnvironment.IntructionFetchUnit.FormDescription import formDescription
from Configuration.Configuration import REGISTER_A, \
                                        REGISTER_B, \
                                        REGISTER_C, \
                                        REGISTER_S
from ToolChain.Assembler.Constants import REGISTER_PREFIX, \
                                          IMMEDIATE_PREFIX, \
                                          WIDTH_INDICATORS, \
                                          FLAGS_INDICATORS, \
                                          COMMENT_INDICATORS, \
                                          MEMORY_REFERENCE_INDICATORS, \
                                          DATA_ALPHA_INDICATOR, \
                                          DATA_NUMERIC_INDICATOR, \
                                          EXPORTED_REFERENCE_INDICATOR

import struct

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class Parser:
    """
    This class is used to parse the text format code and build a list of instruction from it.
    To do so, it has a direct link into CapuaEnvironment instruction information. Those class
    and description files are directly used in order to help build the binary code required
    to run code inside of the Capua environment.
    """

    loadAddress = 0x00
    instructionList = None
    fileContent = None
    referenceDict = None
    finalSize = 0

    def __init__(self, file: str="", skipValidation=False):
        """
        The initial read of the file and parsing of the file is done when Parser is initialized.
        This is a "one stop shop" to get the information easily and fast without requiring multiple
        step. The point of the whole class, is, after all to get these information. No need for
        multiple steps.
        :param file: String, the name of the file that needs to be read in to build the code
        :return: Nothing. Just the normal init stuff...
        """

        if file is None or type(file) is not str or len(file) <= 1 and not skipValidation:
            raise ValueError("Parser error - file has to be defined")

        if len(file) > 0:
            self.fileContent = self._readFileContent(file)
            self.instructionList, self.referenceDict, self.finalSize = self._parseCodeFile()
        return

    def _readFileContent(self, file: str=""):
        """
        This will simply read the content into the local buffer for it to be parsed
        :param file: String, the name of the file that needs to be read in to build the code
        :return: list: Content of the file, line by line.
        """

        with open(file, "r") as codeFile:
            origContent = codeFile.readlines()

        content = []
        for line in origContent:
            content.append(line.replace("\n", ""))

        return content

    def _parseCodeFile(self):
        """
        This method will take the content of the file and build a list of instruction with it.
        That list is in the same order as what is in the actual file content.
        :return: list: this returns a list of instruction that are present in the file.
        """
        instructionList = []  # Will be built as [binaryInstruction, ...]
        memoryReferenceDict = {}  # Will be built as [{"ref": relAddress}, ...]
        relativeAddressCounter = 0
        lineNo = 0

        for line in self.fileContent:
            lineNo += 1
            try:
                sline = line.split()
                if len(sline) > 0:
                    # We are here, we have a code line
                    buildInstruction, lineInstruction = self._parseCodeLine(sline)
                    if buildInstruction is not None:
                        # There was something on this line
                        if type(buildInstruction.instructionCode) is str:
                            # We have a memory location reference!
                            memoryReferenceDict[buildInstruction.instructionCode] = relativeAddressCounter
                        else:
                            # We have an instruction!
                            instructionList.append(lineInstruction)
                            relativeAddressCounter += buildInstruction.instructionLength
            except Exception as e:
                print("ERROR while asssembling line {}: '{}'".format(str(lineNo), line,))
                print(e)
                quit()

        return instructionList, memoryReferenceDict, relativeAddressCounter

    def _parseCodeLine(self, line: list=None):
        """
        This will parse an extracted line of code and build an instruction from that code line
        Parsing a line of code requires many steps.

            1- Find the possible codes for the mnemonic from OperationDescription
            2- Based on the possible codes and parts of the lines, find the correct form
            3- Based on the form, build the instruction
            4- Return the instruction
                If the instruction returned has a string as instruction mnemonic, this means that the
                instruction simply represent a label in the code. It will be removed from the final
                program.

        :param line:
        :return:
        """
        lineInstruction = None

        buildInstruction = Instruction(skipValidation=True)  # This is used as model in early instruction building
        finalCode = 0x00
        form = None
        possibleCodes = None

        self._evaluateAndExtractInfoFromLine(line, buildInstruction)

        if type(buildInstruction.instructionCode) is not str:
            # Instruction is real not just memory address or comment
            possibleCodes = self._findPossibleCodesForInstruction(buildInstruction)
            instructionCode, instructionForm = self._getInstructionCodeAndFormUsingPossibleCodes(buildInstruction,
                                                                                                 possibleCodes)
            if instructionForm is None or instructionCode is None:
                raise ValueError("Assembler general error")
            else:
                buildInstruction.instructionCode = instructionCode
                buildInstruction.instructionLength = formDescription[instructionForm]["length"]
                lineInstruction = self._generateBinaryInstructionFromInstruction(buildInstruction,
                                                                                 formDescription[instructionForm])
        else:
            if COMMENT_INDICATORS in buildInstruction.instructionCode:
                # Simply ignore a comment line
                buildInstruction = None
                lineInstruction = None
            elif DATA_ALPHA_INDICATOR in buildInstruction.instructionCode:
                # This is a bunch of alpha data
                lineInstruction = buildInstruction.sourceImmediate
                buildInstruction.instructionCode = 0  # Calling code expect this to be non STR for non mem ref
            elif DATA_NUMERIC_INDICATOR in buildInstruction.instructionCode:
                # This is a numeric data field
                lineInstruction = struct.pack(">I", buildInstruction.sourceImmediate)
                buildInstruction.instructionCode = 0  # Calling code expect this to be non STR for non mem ref
            else:
                lineInstruction = None

        return buildInstruction, lineInstruction

    def translateRegisterNameToRegisterCode(self, registerName: str=""):
        """
        This takes a register name and returns a register code as per:
            A = 0x00
            B = 0x01
            C = 0x10
            S = 0x11
        Throws error if register is not A, B, C or S
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
        elif registerName == "S":
            registerCode = REGISTER_S
        else:
            raise ValueError("Invalid register provided. '{}' seen as input, expect A, B, C or S.".format(registerName))

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
        :param textFlags:
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

    def _evaluateAndExtractInfoFromLine(self, line, buildInstruction):
        """
        This is an helper method. The aim to this is to keep caller code cleaner
        TODO: refactor this... it's ugly
        :param line:
        :param buildInstruction:
        :return:
        """
        foundSource = False  # Found source operand
        foundDestination = False  # Keep us from abusive operation

        if (len(line) == 1 and MEMORY_REFERENCE_INDICATORS == line[0][-1]) or COMMENT_INDICATORS == line[0][0]:
            # This is no code line... No need for further work, return!
            # We keep the comment indicator so we can later discard the instruction.
            # Put text into instructionCode since this is an impossible case... Easy to
            # follow in calling code. And put in some indicator for the linker.
            buildInstruction.instructionCode = line[0].replace(MEMORY_REFERENCE_INDICATORS, "").upper()
            return

        # First thing is either a mnemonic or a data identifier or a global memory reference
        buildInstruction.operationMnemonic = line[0].upper()

        if EXPORTED_REFERENCE_INDICATOR in buildInstruction.operationMnemonic:
            # This is a memory reference... However, this one is on a global scale (exported)
            # this is a special case
            buildInstruction.instructionCode = line[0].upper() + " "
            buildInstruction.instructionCode += line[1].replace(MEMORY_REFERENCE_INDICATORS, "").upper()
            return
        if DATA_NUMERIC_INDICATOR in buildInstruction.operationMnemonic:
            # Treat this as a numeric field!
            # The numeric value will be but in source immediate value
            numericValue = self.translateTextImmediateToImmediate(line[1])
            buildInstruction.sourceImmediate = numericValue
            buildInstruction.instructionLength = 4
            buildInstruction.instructionCode = line[0].upper()
            return
        if DATA_ALPHA_INDICATOR in buildInstruction.operationMnemonic:
            # Treat this as an alphabetic field!
            # The alpha value will be put in the source immediate value
            # We need to rebuild the alpha into a byte string.
            alpha = b""
            for part in line[1:]:
                alpha += part.encode("utf-8") + b" "
            alpha = alpha[0:-1]  # Remove trailing space
            alpha += b"\x00"  # Strings are null terminated
            buildInstruction.sourceImmediate = alpha
            buildInstruction.instructionLength = len(alpha)
            buildInstruction.instructionCode = line[0].upper()
            return

        # We don't want to redo the first part. That would cause problem with in code memory references.
        for part in line[1:]:
            if part[0] is COMMENT_INDICATORS:
                break  # We are done with this line of code, we found a comment

            if part[0] is FLAGS_INDICATORS[0]:
                if part[-1] is FLAGS_INDICATORS[-1]:
                    # This is FLAGS Indicator!!
                    buildInstruction.flags = self.translateTextFlagsToCodeFlags(part[1:-1])
                else:
                    raise ValueError("Syntax error, opening {} missing closing {}".format(FLAGS_INDICATORS[0],
                                                                                          FLAGS_INDICATORS[-1]))
                continue

            if part[0] is WIDTH_INDICATORS[0]:
                if part[-1] is WIDTH_INDICATORS[-1]:
                    # This is WIDTH Indicator!!
                    buildInstruction.width = self.translateTextImmediateToImmediate(part[1:-1])  # Reusing immediate logic
                else:
                    raise ValueError("Syntax error, opening {} missing closing {}".format(WIDTH_INDICATORS[0],
                                                                                          WIDTH_INDICATORS[-1]))
                continue

            if part[0] is REGISTER_PREFIX:
                # This is a register
                if not foundSource:
                    foundSource = True
                    buildInstruction.sourceRegister = self.translateRegisterNameToRegisterCode(part[1:])
                else:
                    if foundDestination:
                        raise ValueError("Invalid operation format")
                    foundDestination = True
                    buildInstruction.destinationRegister = self.translateRegisterNameToRegisterCode(part[1:])
                continue

            if part[0] is IMMEDIATE_PREFIX:
                # This is an immediate
                if not foundSource:
                    foundSource = True
                    buildInstruction.sourceImmediate = self.translateTextImmediateToImmediate(part[1:])
                else:
                    if foundDestination:
                        raise ValueError("Invalid operation format")
                    foundDestination = True
                    buildInstruction.destinationImmediate = self.translateTextImmediateToImmediate(part[1:])
                continue

            if part[0] is MEMORY_REFERENCE_INDICATORS:
                # This is a memory reference to be treated as an immediate
                if not foundSource:
                    foundSource = True
                    buildInstruction.sourceImmediate = part.upper() + MEMORY_REFERENCE_INDICATORS
                else:
                    if foundDestination:
                        raise ValueError("Invalid operation format")
                    foundDestination = True
                    buildInstruction.destinationImmediate = part.upper() + MEMORY_REFERENCE_INDICATORS
                continue

            raise ValueError("Unexpected code line format detected {}".format(line))

    def _findPossibleCodesForInstruction(self, partialInstruction: Instruction=None):
        """
        This will find the possible instruction codes for a given partial instruction.
        It will return the complete list of possible instruction code. Another method will be used
        to sort out the bad codes.
        :param partialInstruction: Instruction, the expected instruction is only partial in the sense that the code
                                    is not in there yet.
        :return: list, will return the complete list of possible instruction code for a given partial instruction
                    return None if no instruction code matches... This is likely to be a memory identifier.
        """
        possibleCodes = None

        try:
            possibleCodes = operationDescription[partialInstruction.operationMnemonic]
        except KeyError as e:
            pass  # Do nothing for now, this is possibly a memory identifier

        return possibleCodes

    def _getInstructionCodeAndFormUsingPossibleCodes(self,
                                                     partialInstruction: Instruction=None,
                                                     possibleCodes: list=None):
        """
        This will complete the partial instruction by using the possible codes list. It will attempt at finding the
        correct form for the instruction.
        :param partialInstruction: Instruction, the partial instruction that needs to be completed
        :param possibleCodes: list, a list of possible partials
        :return: return the instructionCode and the form to be used to further work on the instruction
        """

        instructionCode = None
        instructionForm = None

        for code in possibleCodes:
            for form in formDescription:
                if formDescription[form]["typeCode"] is not (code >> 4):
                    continue
                found = True
                for subElem in formDescription[form]["description"]:
                    if subElem == "instructionCode":
                        continue
                    if getattr(partialInstruction, subElem) is None:
                        # This is not what we are looking for
                        found = False
                        break
                    else:
                        found = True

                if found:
                    instructionCode = code
                    instructionForm = form

        goodInstructionParams = ["instructionCode",
                                 "sourceRegister",
                                 "destinationRegister",
                                 "sourceImmediate",
                                 "destinationImmediate",
                                 "width",
                                 "flags",
                                 "instructionLength"]
        # This deals with overlong instructions ex: JMP $A $B <- one too many register
        for param in goodInstructionParams:
            if param not in formDescription[instructionForm]["description"]:
                insParam = getattr(partialInstruction, param)
                if insParam is not None:
                    raise ValueError("Invalid instruction provided")

        return instructionCode, instructionForm

    def _generateBinaryInstructionFromInstruction(self, instruction: Instruction=None, form: dict=None):
        """
        This is in charge of generating the actual binary code for an instruction. It will take each parts
        of the instruction and build a binary number with it by using AND logic and bit shifts
        :param instruction: Instruction, the instruction to work with
        :param form: dict, a form dict that allows creation of the code
        :return:
        """
        binaryInstruction = 0
        instructionPartOriginal = None
        instructionPartToBeUsed = None
        memoryRefSymbol = None

        for instructionPart in form["description"]:
            shiftValue = 0x00  # This will be used in the last shifting operation for this part
            instructionPartBitMask = form["description"][instructionPart]

            # This is so we are able to use an and followed by a right shift to build the instruction
            # easiest way that my brain could come up with. All other ways of building instructions
            # seems to rely on ugly logic based on if chaining... Ugly. This is better. We are shifting
            # until we find the "edge" of this part of the instruction.
            while instructionPartBitMask % 2 is not 1:
                instructionPartBitMask >>= 1  # Shift right one bit
                shiftValue += 1

            instructionPartOriginal = getattr(instruction, instructionPart)
            # We need an intermediate step because a part could be text...
            if type(instructionPartOriginal) is str:
                # This is a memory reference
                # yes it will cause a bug it this specific chain is naturally present inside  an
                # instruction code TODO fix this bug
                # However, at time of writing many other problems are more pressing... This requires more thinking
                # and can safely wait for quite a while...
                memoryRefSymbol = instructionPartOriginal
                instructionPartToBeUsed = 0xDEADBEEF
            else:
                instructionPartToBeUsed = instructionPartOriginal

            instructionPartBinaryValue = instructionPartBitMask & instructionPartToBeUsed
            binaryInstruction |= (instructionPartBinaryValue << shiftValue)

        # At this point, logic is we have a fully built binary instruction. Yay!
        # We now need to transform this into a byte string
        binaryInstructionByteString = b""

        for i in range(0, form["length"]):
            byte = binaryInstruction & 0xFF
            binaryInstructionByteString = bytes((byte,)) + binaryInstructionByteString
            binaryInstruction >>= 8  # One complete byte shift to the right in order to prepare for next byte

        # Now, we need to put back the original memory reference if there was one
        if memoryRefSymbol is not None:
            binaryInstructionByteString = binaryInstructionByteString.replace(b"\xDE\xAD\xBE\xEF",
                                                                              memoryRefSymbol.encode())

        return binaryInstructionByteString
