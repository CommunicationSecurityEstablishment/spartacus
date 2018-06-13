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

from ToolChain.Assembler.Parser.Parser import Parser

import struct


class Assembler:

    def __init__(self, inputFile=None, outputFile=None):
        """
        This allows for simple initialisation of the assembler. This class reads the input file line by line and sends
        to the parser for evaluation. Based on the information retrieved, the assembler will sort the information
        accordingly to write to the .o file.
        :param inputFile: str, input textfile name to be read and parsed
        :param outputFile: str, output texfile name to write to output
        """

        if type(inputFile) is not str or len(inputFile) is 0:
            # File is invalid
            raise ValueError("Assembler error - Invalid input file selected")
        if type(outputFile) is not str or len(outputFile) is 0:
            # File is invalid
            raise ValueError("Assembler error - Invalid output file selected")

        self._parseAssembledFile(inputFile, outputFile)

    def _parseAssembledFile(self, inputFile, outputFile):
        """
        This method assembles the binary data itself. It will parse each line individually and extract the info needed:
        1.If the label flag is set to 0, it's a regular instruction, string, number, of memref.
        2.If the label flag is set to 1, it's an internal symbol.
        3.If the label flag is set to 2, it's an external symbol.
        In cases 2 and 3, the symbols are added to their respective lists along with their memory location.
        Memory locations are relative to the beginning of the file. Instructions and data are given set lengths.
        Internal and external symbol lists contain tuples containing the symbol name, and its offset.
        These will be used to fill the .o file information before the binary data.
        :param inputFile: str, the name of the file to be read.
        :param outputFile: str, the name of the file to be written to.
        :return:
        """

        parser = Parser()                    # Parser object which will return the binary code for instructions
        masterString = b""                   # String that will eventually be our output file
        xmlstring = b""                      # String that will contain the "xml" data at the beginning of the .o file
        globalList = []                      # Temporary list to hold the names of global(external) symbols
        externalList = []                    # Master list of all external symbols to be used by linker
        internalList = []                    # Master list of all internal symbols
        offset = 0                           # Offset used to calculate a label's offset from the beginning of the file
        lineno = 0                           # Keeps track of which line we're parsing to pinpoint errors

        instructionFlag = 0                  # Flag for an operand, meaning parser found a valid instruction
        localReferenceFlag = 1               # Flag for local function, internal symbol
        globalReferenceFlag = 2              # Flag for external function, global symbol
        commentFlag = 3                      # Flag for comment

        file = open(inputFile, mode="r")
        fileLines = file.readlines()
        file.close()

        masterString += b"<Text>"

        for line in fileLines:
            lineno += 1
            # If the file isn't empty, process the content


            instruction, offset, labelFlag = parser.parse(line)

            if labelFlag == instructionFlag:
                masterString += instruction

            elif labelFlag == localReferenceFlag:
                labelTuple = (instruction, offset)
                internalList.append(labelTuple)
                if instruction in globalList:
                    externalList.append(labelTuple)

            elif labelFlag == globalReferenceFlag:
                globalList.append(instruction)

            elif labelFlag == commentFlag:
                # flag for comment, we simply ignore and move on to the next line
                pass

            else:
                raise ValueError("Couldn't parse instruction at line " + lineno)

        masterString += b"</Text>"

        # builds the output file by extracting and printing each symbol into its appropriate category.
        xmlstring = b"<AssemblySize>" + struct.pack(">I", parser.relativeAddressCounter) + \
                    b"</AssemblySize><InternalSymbols>"

        for word in internalList:
            xmlstring += b"<refName>" + word[0].encode("utf-8") + b"</refName>"
            xmlstring += b"<refAdd>" + struct.pack(">I", word[1]) + b"</refAdd>"

        xmlstring += b"</InternalSymbols><ExternalSymbols>"

        for word in externalList:
            xmlstring += b"<refName>" + word[0].encode("utf-8") + b"</refName>"
            xmlstring += b"<refAdd>" + struct.pack(">I", word[1]) + b"</refAdd>"

        xmlstring += b"</ExternalSymbols>"

        # Now we can put the xml string together with the masterString to output to file
        xmlstring += masterString
        file = open(outputFile, mode="wb")
        file.write(xmlstring)
        file.close()

