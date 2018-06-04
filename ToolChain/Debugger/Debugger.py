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

from CapuaEnvironment.Capua import Capua
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
                                        DEBUGGER_WAKEUP_TICK_COUNT

from ToolChain.Linker.Constants import DEFAULT_LOAD_ADDRESS

import struct

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.2"
__maintainer__ = "CSE"
__status__ = "Dev"


class Debugger:
    """
    This is an external debugger that aims at simulating an OnChipDebugger type of debugger. That debugger
    will create an execution environment load the input file to that environment and start execution as
    required.
    """

    outputFile = None
    capua = None
    breakPoints = None
    symbols = None

    def __init__(self, inputFile=None,
                 outputFile=None,
                 loadAddress=DEFAULT_LOAD_ADDRESS,
                 softwareLoader=False,
                 symbolsFile=None):
        """
        Building the debugger
        :param inputFile: The input file that needs to be loaded in memory
        :param outputFile: str, the name of the output file, output file is used for logging
        :param loadAddress: int, the address a which the binary will be loaded. This is required to resolve ref address
        :param softwareLoader: bool, is the loading done with the "software" option
        :param symbolsFile: str, the path to the symbols file to be loaded
        :return:
        """

        self.breakPoints = []

        # First thing we need is to setup logging facilities
        self.setupLoggingFacilities(outputFile)

        # Then setup the execution environment
        self.debugLog("Building Capua execution environment")
        self.capua = Capua(name=inputFile)

        # We now need to load the binary to the targeted memory area
        self.debugLog("Loading {} in memory".format((inputFile,)))
        self.loadProgram(inputFile=inputFile, loadAddress=loadAddress, softwareLoader=softwareLoader)

        # If we have the symbols, load them into the appropriate member
        if symbolsFile != "" and symbolsFile is not None:
            self.symbols = {}
            self.loadSymbols(symbolsFile=symbolsFile)

        # At this point, debugging session is ready to be used
        self.debugLog("Debugging session is ready to be used. Have fun!")
        self.debug(inputFile=inputFile)
        self.tearDownLoggingFacilities()

    def loadSymbols(self, symbolsFile=None):
        """
        This will simply load the symbols so that they can be used
        :param symbolsFile: str, path to the symbols file
        :return:
        """

        self.debugLog("Loading symbols from file {}".format(symbolsFile,))

        file = open(symbolsFile, "r")
        content = file.readlines()
        file.close()

        for line in content:
            if line != "":
                self.symbols[line.split(":")[0]] = line.split(":")[1][:-1]  # Remove the \n at the end

        self.debugLog("Done loading symbols")

    def translateSymbolToAddress(self, symbol=None):
        """
        This will take a symbol as input and translate it to a usable address:
            "file.symbol" if multiple files define the same symbol
            "symbol" if only one file define the symbol
        :param symbol: str, the symbol to be translated
        :return: int, the address where to find the symbol, none if symbol is can't be resolved
        """

        if "." not in symbol:
            # User is trying to go without file resolution
            found = None
            for key in self.symbols.keys():
                if key.split(".")[1] == symbol:
                    if found is None:
                        found = key
                    else:
                        self.debugLog("Symbol {} is conflicting with {}". format(symbol, key,))
                        return None
            if found is not None:
                return int(self.symbols[found], 16)

        else:
            if symbol in self.symbols.keys():
                return int(self.symbols[symbol], 16)
            else:
                self.debugLog("Symbol {} could not be resolved".format(symbol,))
                return None

    def translateAddressToSymbol(self, address=None):
        """
        This will lookup the symbol table and find a corresponding symbol for a given address
        :param address: The address that needs to be looked up
        :return:
        """
        symbolTable = self.symbols
        addressInSymbolTable = symbolTable.values()
        resolvedSymbol = None
        address = hex(address)  # Address are keep as hex string in the table

        if address in addressInSymbolTable:
            for symbol in symbolTable:
                if address == symbolTable[symbol]:
                    # We found the symbol for this address
                    resolvedSymbol = symbol
                    break

        return resolvedSymbol

    def setupLoggingFacilities(self, outputFile=None):
        """
        This will allow for setup of the logging file.
        :param outputFile: str path to the file to be used as logging file
        :return:
        """
        if outputFile is not None:
            self.outputFile = open(outputFile[0], "w")

    def tearDownLoggingFacilities(self):
        """
        This will simply close the logging file
        :return:
        """
        if self.outputFile is not None:
            self.outputFile.close()

    def loadProgram(self, inputFile=None, loadAddress=DEFAULT_LOAD_ADDRESS, softwareLoader=False):
        """
        This method allows for loading the complete binary file into memory. After this is finished
        the program has fully been loaded in memory.
        :param inputFile: The input file that needs to be loaded in memory
        :param loadAddress: int, the address a which the binary will be loaded. This is required to resolve ref address
        :param softwareLoader: bool, is the loading done with the "software" option
        :return:
        """

        # First we get the content of the binary file that needs to be loaded into memory
        content = self.getBinary(inputFile)

        # We need to validate the load address in case of software loading mode...
        if softwareLoader:
            # In this case, the load address to be used is the first 4 bytes...
            loadAddress = struct.unpack(">I", content[0:4])
            content = content[4:]  # Get rid of the first 4 bytes or we will crash

        # Now that we have a good load address, we load this in memory
        memoryIndex = loadAddress
        for dataByte in content:
            self.capua.mioc.memoryWriteAtAddressForLength(address=memoryIndex, length=1, value=dataByte)
            memoryIndex += 1  # Move on to the next byte to be written

        # Prepare the core for execution
        self.capua.eu.setupCore(I=loadAddress)

        # If we are here, the binary is technically loaded into memory
        self.debugLog("Done loading {} into memory".format((inputFile,)))
        # Program is now fully installed in memory!
        return

    def getBinary(self, inputFile=None):
        """
        This method simply gets the content of an on disk binary file.
        :param inputFile: string, path to the file that needs to be loaded into memory.
        :return: the content of the file in the form of a byte array
        """
        content = b""

        binFile = open(inputFile, "rb")
        content = binFile.read()
        binFile.close()

        return content

    def debug(self, inputFile=None):
        """
        This is an eternal loop that will run until something bad happen or until user breaks the
        debugging session.
        :return:
        """

        while True:
            self.debugLog("\nNext instruction to be executed:")
            self.displayNextInstruction()
            userCommand = input("{}: ".format((inputFile,)))
            self.debugLog(userCommand)
            if userCommand == "quit" or userCommand == "exit":
                self.capua.eu.halt()
                break
            self.runUserCommand(command=userCommand)

    def displayNextInstruction(self):
        """
        This will display the instruction that is set to be executed as specified by the "I" register
        of the execution unit
        :return:
        """
        self.displayXInstructionAtAddress(address=self.capua.eu.I, x=1)

    def displayXInstructionAtAddress(self, address=None, x: int=None):
        """
        This will display X instruction starting at address
        :param address: int, this is the start address for this task
        :param x: int, how many instructions do we want to display
        :return:
        """

        # We have to validate the user used a symbol for the address
        if type(address) is not int:
            try:
                address = int(address, 16)
            except ValueError as e:
                address = self.translateSymbolToAddress(symbol=address)
                if address is None:
                    self.debugLog("Error while processing address or symbol {}".format(address,))
                    return

        for i in range(0, x):
            instruction, nextInstructionAddress = self.getInstructionAtAddress(address)
            instructionString = self._buildInstructionString(instruction=instruction)
            self.debugLog(hex(address) + " : " + instructionString)
            address = nextInstructionAddress

    def getInstructionAtAddress(self, address: int=None):
        """
        This will simply fetch the instruction at a given address
        :param address:
        :return:
        """
        instruction, nextInstructionAddress = self.capua.eu.ifu.fetchInstructionAtAddress(address)
        return instruction, nextInstructionAddress

    def _buildInstructionString(self, instruction=None):
        """
        This will rebuild the instruction text information so it can be displayed
        :param instruction: A valid and fully built instruction
        :return:
        """
        instructionString = ""
        instructionString += instruction.operationMnemonic + " "
        instructionString += "<" + str(instruction.flags) + \
                             "> " if instruction.flags is not None else ""
        instructionString += "[" + str(instruction.width) + \
                             "] " if instruction.width is not None else ""
        instructionString += "#" + hex(instruction.sourceImmediate) + \
                             " " if instruction.sourceImmediate is not None else ""
        instructionString += "$" + self.convertNumericRegisterToRegisterName(instruction.sourceRegister) + \
                             " " if instruction.sourceRegister is not None else ""
        instructionString += "#" + hex(instruction.destinationImmediate) + \
                             " " if instruction.destinationImmediate is not None else ""
        instructionString += "$" + self.convertNumericRegisterToRegisterName(instruction.destinationRegister) + \
                             " " if instruction.destinationRegister is not None else ""
        return instructionString

    def convertNumericRegisterToRegisterName(self, numericRegister: int=None):
        """
        This will simply convert a numeric register code to the original register name
        :param numericRegister:
        :return:
        """
        result = ""

        if numericRegister == REGISTER_A:
            result = "A"
        elif numericRegister == REGISTER_B:
            result = "B"
        elif numericRegister == REGISTER_C:
            result = "C"
        elif numericRegister == REGISTER_D:
            result = "D"
        elif numericRegister == REGISTER_E:
            result = "E"
        elif numericRegister == REGISTER_F:
            result = "F"
        elif numericRegister == REGISTER_G:
            result = "G"
        elif numericRegister == REGISTER_A2:
            result = "A2"
        elif numericRegister == REGISTER_B2:
            result = "B2"
        elif numericRegister == REGISTER_C2:
            result = "C2"
        elif numericRegister == REGISTER_D2:
            result = "D2"
        elif numericRegister == REGISTER_E2:
            result = "E2"
        elif numericRegister == REGISTER_F2:
            result = "F2"
        elif numericRegister == REGISTER_G2:
            result = "G2"
        elif numericRegister == REGISTER_S:
            result = "S"
        elif numericRegister == REGISTER_S2:
            result = "S2"

        return result

    def displayCPUInformation(self, register: str=None):
        """
        This will display cpu register to the console
        :return:
        """

        # Display all registers to the console
        self.debugLog("Register information for {}".format(self.capua.eu.name,))
        self.debugLog("{} = {}  {}".format("A    ", self.capua.eu.A, hex(self.capua.eu.A),))
        self.debugLog("{} = {}  {}".format("B    ", self.capua.eu.B, hex(self.capua.eu.B),))
        self.debugLog("{} = {}  {}".format("C    ", self.capua.eu.C, hex(self.capua.eu.C),))
        self.debugLog("{} = {}  {}".format("D    ", self.capua.eu.D, hex(self.capua.eu.D),))
        self.debugLog("{} = {}  {}".format("E    ", self.capua.eu.E, hex(self.capua.eu.E),))
        self.debugLog("{} = {}  {}".format("F    ", self.capua.eu.F, hex(self.capua.eu.F),))
        self.debugLog("{} = {}  {}".format("G    ", self.capua.eu.G, hex(self.capua.eu.G),))
        self.debugLog("{} = {}  {}".format("A2   ", self.capua.eu.A2, hex(self.capua.eu.A2),))
        self.debugLog("{} = {}  {}".format("B2   ", self.capua.eu.B2, hex(self.capua.eu.B2),))
        self.debugLog("{} = {}  {}".format("C2   ", self.capua.eu.C2, hex(self.capua.eu.C2),))
        self.debugLog("{} = {}  {}".format("D2   ", self.capua.eu.D2, hex(self.capua.eu.D2),))
        self.debugLog("{} = {}  {}".format("E2   ", self.capua.eu.E2, hex(self.capua.eu.E2),))
        self.debugLog("{} = {}  {}".format("F2   ", self.capua.eu.F2, hex(self.capua.eu.F2),))
        self.debugLog("{} = {}  {}".format("G2   ", self.capua.eu.G2, hex(self.capua.eu.G2),))
        self.debugLog("{} = {}  {}".format("S    ", self.capua.eu.S, hex(self.capua.eu.S),))
        self.debugLog("{} = {}  {}".format("S2   ", self.capua.eu.S2, hex(self.capua.eu.S2),))
        self.debugLog("{} = {}  {}".format("I    ", self.capua.eu.I, hex(self.capua.eu.I),))
        self.debugLog("{} = {}  {}".format("FLAGS", self.capua.eu.FLAGS, bin(self.capua.eu.FLAGS),))
        self.debugLog("")

    def displayMemoryInFormat(self, address=None, length: int=4, displayFormat: str=""):
        """
        This will display memory data in the format of choice of the user. Three formats are possible:
            -bin - Will display octets 0b0000 0000
            -hex - Will display octets 0x00
            -dec - Will display 32 bits ints
            -char - Will display char if possible
        :param address: can be int or string (if a symbol is in use)
        :param length:
        :param displayFormat:
        :return: Nothing, simply display the thing
        """

        # We have to validate the user used a symbol for the address
        try:
            address = int(address, 16)
        except ValueError as e:
            address = self.translateSymbolToAddress(symbol=address)
            if address is None:
                self.debugLog("Error while processing address or symbol {}".format(address,))
                return

        if length <= 0:
            self.debugLog("Invalid length given, must be > 0")
            return

        # Using direct memory array access instead of memory IO controller
        # access in order to avoid the security elements related to the
        # IO controller.
        memSlice = self.capua.ma.readMemory(address=address, length=length)
        self.debugLog("Displaying {} bytes from address {}".format(str(length), hex(address), ))
        # Deal with the display part
        for i in range(0, len(memSlice)):
            valueString = ""
            # Direct access to _value is to avoid memory protection elements
            if displayFormat == "bin":
                valueString = bin(memSlice[i])
            if displayFormat == "hex":
                valueString = hex(memSlice[i])
            if displayFormat == "dec":
                valueString = str(memSlice[i])
            if displayFormat == "char":
                valueString = chr(memSlice[i])

            addressString = hex(address + i)
            self.debugLog("{} - {}".format(addressString, valueString,))

    def displayHelpMenu(self):
        """
        Will simply display the help menu
        :return:
        """
        self.debugLog("-------------------------------------------")
        self.debugLog("Available commands are")
        self.debugLog(" s - step - move to next instruction")
        self.debugLog("    ex: s")
        self.debugLog(" c - continue - run until next breakpoint")
        self.debugLog("    ex: c")
        self.debugLog(" d - display - display cpu information")
        self.debugLog("    ex: d")
        self.debugLog(" m - memory - memory inspection")
        self.debugLog("    ex: m 0x40000000 4 [bin|hex|dec|char]")
        self.debugLog(" dia - disassembleInstructionAtAddress - Will display x following instruction")
        self.debugLog("    ex: dia 3 0x4000000")
        self.debugLog(" b - break - set breakpoint at address")
        self.debugLog("    ex: b 0x40000000")
        self.debugLog(" db - dbreak - display breakpoint list")
        self.debugLog("    ex: db")
        self.debugLog(" rb - rbreak - remove breakpoint")
        self.debugLog("    ex: rb 1")
        self.debugLog(" b - break - add a breakpoint at address")
        self.debugLog("    ex: b 0x4000000")
        self.debugLog(" ss - showSymbols - Will show all loaded symbols")
        self.debugLog("    ex: ss")
        self.debugLog(" h - help - display help menu")
        self.debugLog("-------------------------------------------")

    def runUserCommand(self, command: str=None):
        """
        This is the method responsible for dispatching the user commands
            s - step - move to next instruction
            d - display - display cpu information
            m - memory - memory inspection
            h - help - display help menu
            dia - disassembleInstructionAtAddress - Will display x following instruction
        :param command: str, a string that needs to be parsed
        :return:
        """

        brokenCommand = command.split()

        if len(brokenCommand) == 0:
            return  # Return was put here in order to avoid a bid indented block...

        if brokenCommand[0] == "s" or brokenCommand[0] == "step":
            # Execute next command in line
            self.capua.eu.execute()
        elif brokenCommand[0] == "c" or brokenCommand[0] == "continue":
            # Run until breakpoint is reached
            self.runToBreakPoint()
        elif brokenCommand[0] == "d" or brokenCommand[0] == "display":
            # Display cpu information
            self.displayCPUInformation()
        elif brokenCommand[0] == "m" or brokenCommand[0] == "memory":
            # Display memory data
            self.displayMemoryInFormat(address=brokenCommand[1],
                                       length=int(brokenCommand[2]),
                                       displayFormat=brokenCommand[3])
        elif brokenCommand[0] == "dia" or brokenCommand[0] == "disassembleInstructionAtAddress":
            # Display help menu
            x = int(brokenCommand[1])
            self.displayXInstructionAtAddress(address=brokenCommand[2], x=x)
        elif brokenCommand[0] == "b" or brokenCommand[0] == "break":
            # add a break point
            address = brokenCommand[1]
            self.addBreakPoint(address)
        elif brokenCommand[0] == "db" or brokenCommand[0] == "dbreak":
            # Display breakpoints
            self.displayBreakPoints()
        elif brokenCommand[0] == "rb" or brokenCommand[0] == "rbreak":
            # Remove breakpoint
            bpNumber = int(brokenCommand[1])
            self.removeBreakPoint(bpNumber)
        elif brokenCommand[0] == "ss" or brokenCommand[0] == "showSymbols":
            self.showSymbols()
        elif brokenCommand[0] == "h" or brokenCommand[0] == "help":
            # Display help menu
            self.displayHelpMenu()
        else:
            # This is an invalid command
            self.debugLog("'{}' is not recognized as a command. use 'h' or help to display help menu".format(command,))

    def showSymbols(self):
        """
        This will simply display the loaded symbols to the console
        :return:
        """
        self.debugLog("Loaded symbols are:")
        for symbol in self.symbols.keys():
            self.debugLog("{} : {}".format(self.symbols[symbol], symbol))

    def runToBreakPoint(self):
        """
        This will run until a breakpoint is reached. It will also break every DEBUGGER_WAKEUP_TICK_COUNT tick
        :return:
        """
        tickCounter = 0
        first = True
        while True:
            if self.capua.eu.I in self.breakPoints and first is False:
                # Break point reached
                break
            first = False
            if 0 < DEBUGGER_WAKEUP_TICK_COUNT == tickCounter:
                # Just check if user want to go back to single step mode
                self.debugLog(str(DEBUGGER_WAKEUP_TICK_COUNT) + " instructions executed since last break, "
                              "do you want to go back to single step (y/n): ")
                answer = input("")
                if answer == "y":
                    break
                else:
                    tickCounter = 0

            self.capua.eu.execute()
            tickCounter += 1

    def removeBreakPoint(self, number: int=None):
        """
        This will remove a single breakpoint from the list of breakpoint
        :param number: breakpoint number to remove
        :return:
        """
        self.breakPoints.remove(self.breakPoints[number])
        self.breakPoints.sort()

    def displayBreakPoints(self):
        """
        This will display breakpoint in deletion order (number is number required when deleting
        :return:
        """
        self.debugLog("\nBreakpoints list:")
        for i in range(0, len(self.breakPoints)):
            symbolInfo = ""
            symbol = self.translateAddressToSymbol(address=self.breakPoints[i])
            if symbol is not None:
                symbolInfo = "-> " + symbol

            self.debugLog(" {} - {} {}".format(i, hex(self.breakPoints[i]), symbolInfo,))

    def addBreakPoint(self, address=None):
        """
        This will simply add a break point into the break point list
        :param address: a valid capua address written in hexadecimal
        :return:
        """
        # We have to validate the user used a symbol for the address
        try:
            address = int(address, 16)
        except ValueError as e:
            address = self.translateSymbolToAddress(symbol=address)
            if address is None:
                self.debugLog("Error while processing address or symbol {}".format(address,))
                return

        self.breakPoints.append(address)
        self.breakPoints.sort()

    def debugLog(self, message:str="", screenDisplay:bool=True):
        """
        This is simply an interface that will deal with both console printing and logging
        :param message: This is the message to be logged/displayed
        :param screenDisplay: If true, the message will be sent to the display
        :return: Nothing
        """

        if self.outputFile is not None:
            self.outputFile.write(message)
        if screenDisplay:
            print(message)
