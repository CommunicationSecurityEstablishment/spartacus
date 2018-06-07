#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

from ToolChain.Assembler.Parser.Parser import Parser

import struct


class Assembler:

    def __init__(self, inputFile=None, outputFile=None):
        """
        This allows for simple initialisation of the assembler. It will spawn the required
        instructionBuilder that will parse the assembly code into binary format.
        :param inputFile:
        :param outputFile:
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
        global_list = []                     # Temporary list to hold the names of global(external) symbols
        externalList = []                    # Master list of all external symbols to be used by linker
        internalList = []                    # Master list of all internal symbols
        offset = 0                           # Offset used to calculate a label's offset from the beginning of the file

        file = open(inputFile, mode="r")
        fileLines = file.readlines()
        file.close()

        masterString += b"<Text>"

        for line in fileLines:
            # If the file isn't empty, process the content
            if line[0] != "\n":
                # We simply ensure that there is something on the line, not just newline (empty)
                instruction, offset, label_flag = parser.parse(line)

                if label_flag == 0:
                    masterString += instruction

                elif label_flag == 1:
                    label_tuple = (instruction, offset)
                    internalList.append(label_tuple)
                    if instruction in global_list:
                        externalList.append(label_tuple)

                elif label_flag == 2:
                    global_list.append(instruction)

                elif label_flag == 3:
                    # flag for comment, we simply ignore and move on to the next line
                    pass

                else:
                    raise ValueError("Assembler code error.")

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

