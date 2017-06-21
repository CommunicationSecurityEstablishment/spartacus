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

from ToolChain.Assembler.Parser.Parser import Parser
from ToolChain.Assembler.Constants import EXPORTED_REFERENCE_INDICATOR

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class Assembler:
    """
    This class is the center piece of the assembler. Files created by this assembler
    are ready to be submited to the linker for final linking and creation of the final
    binary file.
    """

    parser = None

    def __init__(self, inputFile=None, outputFile=None):
        """
        This allows for simple initialisation of the assembler. It will spawn the required
        parser that will parse the assembly code into binary format. It will then call
        buildAssembledFile so that the final file can be created.
        :return:
        """

        if type(inputFile) is not str or len(inputFile) is 0:
            # File is invalid
            raise ValueError("Assembler error - Invalid input file selected")
        if type(outputFile) is not str or len(outputFile) is 0:
            # File is invalid
            raise ValueError("Assembler error - Invalid output file selected")

        self.parser = Parser(file=inputFile)
        data = self.buildAssembledFile()
        self.writeAssembledFile(file=outputFile, outputData=data)

    def buildAssembledFile(self):
        """
        This method is responsible for creating the final XML based "binary" (yes, this is
        an abused of language),
        :return:
        """
        import struct
        fileContent = b""
        # First we need the assembly size, this is to help linker do its job
        fileContent += b"<AssemblySize>"
        fileContent += struct.pack(">I", self.parser.finalSize)
        fileContent += b"</AssemblySize>"

        # External symbols allow for a file to be linked with another file
        fileContent += b"<ExternalSymbols>"
        for reference in self.parser.referenceDict:
            if EXPORTED_REFERENCE_INDICATOR in reference:
                refName = reference.split()[1]
                fileContent += b"<refName>" + refName.encode("utf-8") + b"</refName>"
                fileContent += b"<refAdd>" + struct.pack(">I", self.parser.referenceDict[reference]) + b"</refAdd>"
        fileContent += b"</ExternalSymbols>"

        # Deal with internal symbols
        fileContent += b"<InternalSymbols>"
        for reference in self.parser.referenceDict:
            if EXPORTED_REFERENCE_INDICATOR not in reference:
                fileContent += b"<refName>" + reference.encode("utf-8") + b"</refName>"
                fileContent += b"<refAdd>" + struct.pack(">I", self.parser.referenceDict[reference]) + b"</refAdd>"
        fileContent += b"</InternalSymbols>"

        # Deal with the text section
        fileContent += b"<Text>"
        for instruction in self.parser.instructionList:
            fileContent += instruction
        fileContent += b"</Text>"

        return fileContent

    def writeAssembledFile(self, file=None, outputData=None):
        """
        This will write the assembled file to disk
        :param file: str, output file path
        :param outputData: bytes, the data to be written on the disk
        :return:
        """

        with open(file, mode="wb") as f:
            f.write(outputData)
