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
from ToolChain.Assembler.Constants import INSTRUCTION_FLAG, \
                                          LOCAL_REFERENCE_FLAG, \
                                          GLOBAL_REFERENCE_FLAG, \
                                          EMPTY_LINE_FLAG

import struct


class Assembler:
    """
    This is the Assembler class which takes in an input file and output file name specified by the user. The input file
    must be a .casm file, which will then be parsed and converted to write the .o file to the specified output name.
    This .o file contains the list of local and global labels, the offset of these labels relative to the beginning of
    the file, and the binary code. Each line in the file is read, and converted to binary instructions by the parser.
    """

    def __init__(self, inputFile=None, outputFile=None):
        """
        Initializes Assembler with input and output files.
        :param inputFile: str, input .casm file to be read
        :param outputFile: str, specified name of the .o file the assembler will create
        """

        if type(inputFile) is not str or len(inputFile) is 0:
            # File is invalid
            raise ValueError("Assembler error - Invalid input file selected")
        if type(outputFile) is not str or len(outputFile) is 0:
            # File is invalid
            raise ValueError("Assembler error - Invalid output file selected")

        self._AssembleFile(inputFile, outputFile)

    def _AssembleFile(self, inputFile, outputFile):
        """
        This method assembles an object file (.o) from a provided Capua assembly file (.casm)
        :param inputFile: str, the name of the .casm file to be read and parsed.
        :param outputFile: str, the name of the file .o to be created.
        :return:
        """

        parser = Parser()                    # Parser object which will return the binary code for instructions
        binaryDataString = b"<Text>"         # String that will contain our binary code
        globalSymbols = []                   # Temporary list to hold the names of global(external) symbols
        localSymbols = []                    # Temporary list to hold the names of local(internal) symbols
        externalSymbols = []                 # Master list of all external symbols to be used by linker
        internalSymbols = []                 # Master list of all internal symbols
        lineno = 0                           # Keeps track of which line we're parsing to pinpoint errors
        relativeAddressCounter = 0           # Used to determine memory address of a label at a given point in the file

        try:
            # Initial test to verify that the file we're reading actually exists
            file = open(inputFile, mode="r")
            fileLines = file.readlines()
            file.close()
        except OSError as e:
            raise OSError("Error - unable to open file: {}".format(inputFile))
        except IOError as e:
            raise IOError("Error - unable to open file: {}".format(inputFile))

        for line in fileLines:
            lineno += 1
            # Here we begin our evaluation of each line. We get the binary instruction, offset, and label flag
            # Memory locations are relative to the beginning of the file. Instructions and data are given set lengths.
            # Internal and external symbol lists contain tuples containing the symbol name, and its offset.
            # These will be used to fill the .o file information before the binary data.

            try:
                # This will catch any exception thrown by the parser. If there is one, we print the error,
                # The line at which it occurred, and we quit out.
                instruction, offset, labelFlag = parser.parse(line)
                relativeAddressCounter += offset
            except ValueError as e:
                print(str(e) + " at line: {}".format(lineno))
                quit()

            if labelFlag == INSTRUCTION_FLAG:
                # If the label flag is set to 0, it's a regular instruction, string, number, of memref.
                binaryDataString += instruction

            elif labelFlag == LOCAL_REFERENCE_FLAG:
                # If the label flag is set to 1, it's an internal symbol. We ensure labels are unique when declared
                if instruction not in localSymbols:
                    localSymbols.append(instruction)
                    labelTuple = (instruction, relativeAddressCounter)
                    internalSymbols.append(labelTuple)
                else:
                    raise ValueError("Local label already declared; cannot declare duplicate label name")
                if instruction in globalSymbols:
                    externalSymbols.append(labelTuple)

            elif labelFlag == GLOBAL_REFERENCE_FLAG:
                # If the label flag is set to 2, it's an external symbol. We ensure labels are unique when declared
                if instruction not in globalSymbols:
                    if instruction not in localSymbols:
                        globalSymbols.append(instruction)
                    else:
                        # We can't have a global label declared if it has already been set as a local one
                        raise ValueError("Global label must be declared before its local declaration.")
                else:
                    raise ValueError("Global label already declared; cannot declare duplicate label name")

            elif labelFlag == EMPTY_LINE_FLAG:
                # flag for comment, we simply ignore and move on to the next line
                pass

            else:
                raise ValueError("Couldn't parse instruction at line " + lineno)

        binaryDataString += b"</Text>"

        # Writes the label info by extracting and printing each symbol into its appropriate category.
        xmlString = b"<AssemblySize>" + struct.pack(">I", relativeAddressCounter) + \
                    b"</AssemblySize><InternalSymbols>"

        for word in internalSymbols:
            xmlString += b"<refName>" + word[0].encode("utf-8") + b"</refName>"
            xmlString += b"<refAdd>" + struct.pack(">I", word[1]) + b"</refAdd>"

        xmlString += b"</InternalSymbols><ExternalSymbols>"

        for word in externalSymbols:
            xmlString += b"<refName>" + word[0].encode("utf-8") + b"</refName>"
            xmlString += b"<refAdd>" + struct.pack(">I", word[1]) + b"</refAdd>"

        xmlString += b"</ExternalSymbols>"

        # Now we can put the xml string together with the binaryDataString to output to file
        xmlString += binaryDataString

        try:
            # Test to see if we are able to write to the output file defined by user
            file = open(outputFile, mode="wb")
            file.write(xmlString)
            file.close()
        except OSError as e:
            raise OSError("Error - unable to open file: {}".format(outputFile))
        except IOError as e:
            raise IOError("Error - unable to open file: {}".format(outputFile))

