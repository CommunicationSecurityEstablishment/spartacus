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

from ToolChain.Linker.AssembledParsedFile import AssembledParsedFile
from ToolChain.Linker.Constants import DEFAULT_LOAD_ADDRESS

import re
import struct
from os import sep

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class StaticFlatLinker:
    """
    This class will allow for linking multiple files together. Please note that, at current time,
    only static linking will be performed and that the resulting file will be a flat binary file
    usable as boot rom code for Capua cores. The hope is to add more linking capabilities over time.
    For now, simply a flat file will be more than enough to validate the correct working of the ecosystem.
    """

    parsedFiles = None
    parsedFilesOffset = None
    finalFileContent = b""
    symbols = None

    def __init__(self,
                 inputFileList=None,
                 outputFile=None,
                 loadAddress=DEFAULT_LOAD_ADDRESS,
                 softwareLoader=False,
                 symbolsFile=None):
        """
        This will trigger parsing for the list of provided files and will write the final
        linked content to disk.
        :param inputFileList: a list of path to files that needs to be linked together. Linking order = list order
        :param outputFile: str, the name of the output file
        :param loadAddress: int, the address where the binary will be loaded. This is required to resolve ref address
        :return:
        """
        # Before we start, be aware that I DO KNOW that this is not the "fastest most optimal" way fo doing this...
        # Also know that this is how I want it to be. This is meant to be educational, not fast.

        self.parsedFiles = []
        self.parsedFilesOffset = []
        self.symbols = {}

        # First, load and parse all the files that are to be linked together
        # also populate the parsedFilesOffset
        currentFileOffset = loadAddress
        for file in inputFileList:
            parsedFile = AssembledParsedFile(file)
            self.parsedFiles.append(parsedFile)
            self.parsedFilesOffset.append(currentFileOffset)
            # Calculate offset for next file
            currentFileOffset += parsedFile.assemblySize

        # Then resolve internal references for each files individually
        # This needs to be done before the globals!!!
        # This is required in case there is an overlap with a global reference
        for i in range(0, len(self.parsedFiles)):
            self._resolveInternalReferences(file=self.parsedFiles[i], offset=self.parsedFilesOffset[i])

        # Now resolve global reference
        self._resolveGlobalReferences()

        # Build the final file
        for file in self.parsedFiles:
            self.finalFileContent += file.text

        # Try to look for unresolved reference, this technique is REALLY naive... But will have to be it for now...
        isValid, unresolvedReference = self._isThereSomeUnresolvedReferences()

        if not isValid:
            # If we are software loader mode, add the load address to beginning
            if softwareLoader:
                self.finalFileContent = struct.pack(">I", loadAddress) + self.finalFileContent
            # Write the file to disk
            with open(outputFile, 'wb') as finalFile:
                finalFile.write(self.finalFileContent)
        else:
            raise ValueError("Unresolved reference {}".format((unresolvedReference.decode(),)))

        if symbolsFile is not None:
            self._writeSymbolsFile(symbolsFile)

    def _writeSymbolsFile(self, fileName=None):
        """
        This will simply write the symbols to the correct file.
        :param fileName:
        :return:
        """

        symbolsList = sorted(self.symbols.keys())

        with open(fileName, 'w') as f:
            for symbol in symbolsList:
                f.write('{}:{}\n'.format(
                    symbol, hex(struct.unpack(">I", self.symbols[symbol])[0]))
                )


    def _resolveInternalReferences(self, file=None, offset=0):
        """
        This method will go through all of the files and replace references with their correct offset
        inside the final binary file.
        :param file: This is a parsed assembled file ready to be worked on
        :param offset: int, this is the offset at which the file will be in the final binary file
        :return: Nothing
        """
        # Before we start, be aware that I DO KNOW that this is not the "fastest most optimal" way fo doing this...
        # Also know that this is how I want it to be. This is meant to be educational, not fast.

        # Lets go through all of the offset and make adjustment
        for reference in file.internalReferences:
            tempReference = struct.unpack(">I", file.internalReferences[reference])[0] + offset
            file.internalReferences[reference] = struct.pack(">I", tempReference)

        # Now, used the previously calculated reference to do some magic in code
        # ... Or simply said, replace the reference for their address
        for reference in file.internalReferences:
            file.text = file.text.replace(b":" + reference + b":", file.internalReferences[reference])
            self.symbols[file.name.split(sep)[-1].split(".")[0] + "." + reference.decode()] = file.internalReferences[reference]

        # At this point, all internal references for the current file should have
        # been resolved... Job done, time to return!
        return

    def _resolveGlobalReferences(self):
        """
        This method will go through global references and resolve them taking into account the global
        position of a reference inside the final binary
        :return: Nothing
        """
        # Before we start, be aware that I DO KNOW that this is not the "fastest most optimal" way fo doing this...
        # Also know that that this is how I want it to be. This is meant to be educational, not fast.

        # Ok first, we need address for references that will be used globally
        for i in range(0, len(self.parsedFiles)):
            for reference in self.parsedFiles[i].externalReferences:
                tempReference = struct.unpack(">i", self.parsedFiles[i].externalReferences[reference])[0]
                tempReference += self.parsedFilesOffset[i]
                self.parsedFiles[i].externalReferences[reference] = struct.pack(">I", tempReference)

        # Ok, all global references should now have a usable address
        # We can start going through the code and swapping references for actual addresses
        for file in self.parsedFiles:
            for subFile in self.parsedFiles:
                for reference in file.externalReferences:
                    subFile.text = subFile.text.replace(b":" + reference + b":", file.externalReferences[reference])
                    self.symbols[file.name.split(sep)[-1].split(".")[0] + "." + reference.decode()] = file.externalReferences[reference]

        # That should be it! Globals should now have been resolved!
        return

    def _isThereSomeUnresolvedReferences(self):
        """
        This method as it states will try to locate unresolved references in the code. The technique implemented
        here is pretty much garbage but have to deal with this to keep things simple. This will be changed for
        something else in the future that will require a file format change. For now, I simply need something
        fast that will allow me to work on some core testing... Therefore, for now, this will have to do!
        :return: Bool, true if we think there are un resolved reference, false otherwise.
        """
        foundUnresolved = False
        reference = b""

        referenceRe = b":[A-Z_0-9]{1,15}:"
        result = re.search(referenceRe, self.finalFileContent)

        if result is not None:
            foundUnresolved = True
            reference = result.group(0)

        return foundUnresolved, reference
