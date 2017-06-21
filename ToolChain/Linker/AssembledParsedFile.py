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

import os
import re
import struct

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class AssembledParsedFile:
    """
    This is an helper class that aims at providing an interface to an assembled file. Using this
    class, the linker will be able to access inner file data so that It can link multiple files together
    in a single final flat binary file.
    """

    name = ""
    externalReferences = None  # End up as a dict {"referenceName": textOffset, ...}
    internalReferences = None  # End up as a dict {"referenceName": textOffset, ...}
    text = b""  # Yeah, this is binary even if it is called text
    assemblySize = 0  # The expected size of the text section after linking

    def __init__(self, inputFile=None, skipValidationAndLogic=False):
        """
        This method, while initialising the object, will load a single file into the
        :param inputFile: The input file that needs to be used in order to populate this object
        :return: Nothing, at that point, the object is simply usable
        """
        if not skipValidationAndLogic:
            if not os.path.exists(inputFile):
                raise ValueError("AssembledParsedFile - Invalid file path provided {}".format(inputFile,))

            self.name = inputFile.replace(" ", "")  # No white space!
            self._parseInputFile(inputFile)
        return

    def _parseInputFile(self, inputFile=None):
        """
        This will parse the input file and populate current object data structures so that
        they can be used by the parser from whom call originated.
        :param inputFile: The input file that needs to be used in order to populate this object
        :return: No return this will simply set the object attributes accordingly
        """
        with open(inputFile, "rb") as binFile:
            data = binFile.read()

        self.externalReferences = self._extractGlobalReferences(data=data)
        self.internalReferences = self._extractInternalReferences(data=data)
        self.text = self._extractText(data=data)
        self.assemblySize = self._extractAssemblySize(data=data)

    def _extractGlobalReferences(self, data=b""):
        """
        This will parse out the GlobalScope reference from the data provided. Raises
        an error if completely empty since all section should be there.
        :param data: Byte string, Complete data in need to be parsed.
        :return: Dict with the required parsed info
        """
        result = {}
        innerData = b""
        sResult = re.search(b"<ExternalSymbols>.{0,}</ExternalSymbols>", data, flags=re.DOTALL)
        innerData = sResult.group(0)
        innerData = innerData.replace(b"<ExternalSymbols>", b"")
        innerData = innerData.replace(b"</ExternalSymbols>", b"")

        result = self._buildDictFromInnerReferenceData(data=innerData)
        return result

    def _extractInternalReferences(self, data=b""):
        """
        This will parse out the InternalSymbols reference from the data provided.
        :param data: Byte string, Complete data in need to be parsed.
        :return: Dict with the required parsed info
        """
        result = {}
        innerData = b""
        sResult = re.search(b"<InternalSymbols>.{0,}</InternalSymbols>", data, flags=re.DOTALL)
        innerData = sResult.group(0)
        innerData = innerData.replace(b"<InternalSymbols>", b"")
        innerData = innerData.replace(b"</InternalSymbols>", b"")

        result = self._buildDictFromInnerReferenceData(data=innerData)
        return result

    def _buildDictFromInnerReferenceData(self, data=b""):
        """
        This will build a dictionary linking the reference name to the reference offset. Same logic
        is used for both Global an Inner reference parsing.
        :param data: Byte string as <refName>START</refName><refAdd>    </refAdd>
        :return: Dict with the required parsed info
        """
        result = {}

        # Regular expression used to do the extraction
        reRefName = b"<refName>[A-Z_0-9]{1,15}</refName>"
        reRefAdd = b"<refAdd>[\x00-\xFF]{4}</refAdd>"

        # Extract the info into two lists
        allReferenceNameEx = re.findall(reRefName, data, flags=re.DOTALL)
        allReferenceAddEx = re.findall(reRefAdd, data, flags=re.DOTALL)

        # Let's remove the tags and only keep the data...
        allReferenceName = []
        allReferenceAdd = []
        for ref in allReferenceNameEx:
            ref = ref.replace(b"<refName>", b"")
            ref = ref.replace(b"</refName>", b"")
            allReferenceName.append(ref)
        for ref in allReferenceAddEx:
            ref = ref.replace(b"<refAdd>", b"")
            ref = ref.replace(b"</refAdd>", b"")
            allReferenceAdd.append(ref)

        # Build a dictionary from the two list!
        result = dict(zip(allReferenceName, allReferenceAdd))
        return result

    def _extractText(self, data=b""):
        """
        This will parse out the Text section from the input data. This is the part that the linker will
        modify in order to build usable code.
        :param data: Byte string
        :return: ByteString limited to only the data inside the text section
        """
        result = b""
        sResult = re.search(b"<Text>.{0,}</Text>", data, flags=re.DOTALL)
        result = sResult.group(0)
        result = result.replace(b"<Text>", b"")
        result = result.replace(b"</Text>", b"")
        return result

    def _extractAssemblySize(self, data=b""):
        """
        This will parse the AssemblySize so we can validate our work and calculate in file offset
        :param data: Byte string
        :return: int, the size of the expected assembled binary for this file
        """
        result = b""
        sResult = re.search(b"<AssemblySize>[\x00-\xFF]{4}</AssemblySize>", data, flags=re.DOTALL)
        result = sResult.group(0)
        result = result.replace(b"<AssemblySize>", b"")
        result = result.replace(b"</AssemblySize>", b"")
        result = struct.unpack(">I", result)[0]
        return result
