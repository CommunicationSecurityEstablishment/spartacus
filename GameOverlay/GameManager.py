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
import CapuaEnvironment.IOComponent.MemoryMappedDevices.SpartacusThreadMultiplexer.SpartacusThreadMultiplexer as STMP
from Configuration.Configuration import MEMORY_START_AT, MEMORY_END_AT
from GameOverlay.Arena import Arena
from GameOverlay.GameConfiguration import MAX_PROGRAM_SIZE
from ToolChain.Assembler.Assembler import Assembler
from ToolChain.Debugger.Debugger import Debugger  # Do not delete... There is a commented out line in this file that allows to plug in the debugger
from ToolChain.Linker.StaticFlatLinker import StaticFlatLinker

import random
import time

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.4"
__maintainer__ = "CSE"
__status__ = "Dev"


class GameManager:

    arena = None

    p1Capua = None
    p1ContextBank = None
    p1CurrentContext = 0

    p2Capua = None
    p2ContextBank = None
    p2CurrentContext = 0

    currentPlayer = None        # Capua instance of the current player
    currentContextBank = None   # List of contexts for the current player
    currentContext = 0          # index for the current context relative to currentContextBank

    mioc = None
    ifu = None

    def __init__(self, p1File, p1Name, p2File, p2Name):
        """
        This method setup the game environment. The first thing it will do is build the
        required fighter programs into usable binaries. After that, it will build a Capua
        environment and load these fighter into the environment.
        :param p1File: String, path the to file to be used
        :param p1Name: String, usable display name
        :param p2File: String, path the to file to be used
        :param p2Name: String, usable display name
        :return:
        """

        # The Arena is the "graphic" (yeah right...) display for the game.
        self.arena = Arena()

        # Setup core environment after this step, 2 cores will share the same memory elements
        self.p1Capua = Capua(name=p1Name)
        self.mioc = self.p1Capua.mioc
        self.p2Capua = Capua(ma=self.p1Capua.ma, mioc=self.p1Capua.mioc, name=p2Name)

        # We need to get load address for both fighter. These are random otherwise game is boring
        p1Address, p2Address = self.getRandomLoadAddresses()

        # If we are here, we have valid random load address for both fighter
        # We can now build both fighters
        self.buildFiles(fileName=p1File, baseAddress=p1Address)
        self.buildFiles(fileName=p2File, baseAddress=p2Address)

        # If we are here, both files have been built! Yeah!

        # Following line is there for debugging purposes it will allow
        # to run the debugger in the environment using p1 random load address
        # Warning, Threading will not be available even if we are in game mode
        # deb = Debugger(inputFile=p1File.split(".")[0] + ".bin", loadAddress=p1Address)

        # Time to load binaries in memory
        p1Size = self.loadBinaryInMemory(capua=self.p1Capua,
                                         loadAddress=p1Address,
                                         binaryPath=p1File.split(".")[0] + ".bin")
        p2Size = self.loadBinaryInMemory(capua=self.p2Capua,
                                         loadAddress=p2Address,
                                         binaryPath=p2File.split(".")[0] + ".bin")

        # Just to make sure no player is trying to destroy the game with a big
        # empty battle program
        if p1Size > MAX_PROGRAM_SIZE or p2Size > MAX_PROGRAM_SIZE:
            print("{} is {} bytes".format(p1Name, hex(p1Size)))
            print("{} is {} bytes".format(p2Name, hex(p2Size)))
            print("Over {} = disqualified!!".format(hex(MAX_PROGRAM_SIZE)))
            quit()

        # Insert info into context bank before player can play
        # Could have hidden this away in a method but feels clearer this way
        self.p1ContextBank = []
        self.p1ContextBank.append(self.p1Capua.eu)

        self.p2ContextBank = []
        self.p2ContextBank.append(self.p2Capua.eu)

        # The smallest binary starts first. If equal random start
        self.pickFirstToPlay(p1Size=p1Size, p2Size=p2Size)

        # This creates the link with the hardware device that allows for thread support
        STMP.GameEnvironment = self

        # Right here, right now, the game has been setup, we are ready to play! YAY!
        self.play()

    def buildFiles(self, fileName=None, baseAddress=None):
        """
        This will do a full build of the file given as input. The file will be built
        so that it can be loaded at the baseAddress
        :param fileName: str, the name of the file that is to be used for the build.
        :param baseAddress: int, the base address that is to be used for the build load address.
        :return:
        """
        try:
            baseFile = fileName.split(".")[0]
            assembler = Assembler(fileName, baseFile + ".o")
            linker = StaticFlatLinker(inputFileList=[baseFile + ".o"],
                                      outputFile=baseFile + ".bin",
                                      loadAddress=baseAddress)
        except Exception as e:
            raise ValueError("{} failed to build. Game over".format(fileName))

    def getRandomLoadAddresses(self):
        """
        This is an helper method that will return two valid random load address. Both address
        have 4k of contiguous memory following the address.
        :return:
        """
        p1Address = random.randint(MEMORY_START_AT, MEMORY_END_AT - MAX_PROGRAM_SIZE)  # See GameConfiguration
        p1AddMax = p1Address + MAX_PROGRAM_SIZE
        p2Address = p1Address  # This forces the loop and avoid code duplication

        while p2Address in range(p1Address, p1AddMax) or (p2Address + MAX_PROGRAM_SIZE) in range(p1Address, p1AddMax):
            p2Address = random.randint(MEMORY_START_AT, MEMORY_END_AT - MAX_PROGRAM_SIZE)

        return p1Address, p2Address

    def pickFirstToPlay(self, p1Size=None, p2Size=None):
        """
        This method is a simple helper that will choose the first player to play based
        on the size of both binaries. Is case where both binaries are of the same size,
        a random pick is made.
        :param p1Size:
        :param p2Size:
        :return:
        """
        if p1Size < p2Size:
            self.setCurrentPlayer(player=self.p1Capua,
                                  contextBank=self.p1ContextBank,
                                  currentContext=self.p1CurrentContext)
        elif p2Size < p1Size:
            self.setCurrentPlayer(player=self.p2Capua,
                                  contextBank=self.p2ContextBank,
                                  currentContext=self.p2CurrentContext)
        else:
            randomChoice = random.randint(0, 1)
            if randomChoice == 0:
                self.setCurrentPlayer(player=self.p1Capua,
                                      contextBank=self.p1ContextBank,
                                      currentContext=self.p1CurrentContext)
            else:
                self.setCurrentPlayer(player=self.p2Capua,
                                      contextBank=self.p2ContextBank,
                                      currentContext=self.p2CurrentContext)

    def setCurrentPlayer(self, player, contextBank, currentContext):
        """
        Simply sets the current game player.
        :param player: Capua, a valid capua environment.
        :param contextBank: List, a list with all a player contexts.
        :param currentContext: int, a int indicating the currently executing context for a player.
        :return:
        """
        self.currentPlayer = player
        self.currentContextBank = contextBank
        self.currentContext = currentContext

    def getBinary(self, inputFile=None):
        """
        This method simply gets the content of an on disk binary file.
        :param inputFile: string, path to the file that needs to be loaded into memory.
        :return: the content of the file in the form of a byte array
        """

        with open(inputFile, "rb") as binFile:
            content = binFile.read()

        return content

    def loadBinaryInMemory(self, capua=None, loadAddress=None, binaryPath=None):
        """
        This will load a binary into the correct memory region. It will return the
        size of the loaded binary
        :param capua:
        :param loadAddress:
        :param binaryPath:
        :return:
        """
        content = self.getBinary(inputFile=binaryPath)

        memoryIndex = loadAddress
        for dataByte in content:
            capua.mioc.memoryWriteAtAddressForLength(address=memoryIndex,
                                                     length=1,
                                                     value=dataByte,
                                                     source=capua.eu.name)
            memoryIndex += 1  # Move on to the next byte to be written

        # Prepare the core for execution
        capua.eu.setupCore(I=loadAddress)

        return len(content)

    def play(self):
        """
        This is the game being played. This method control the execution flow and scheduling for
        all players and contexts.
        :return:
        """
        cycles = 0

        stime = time.time()
        while cycles < 1000000:  # maximum of 1 000 000 instruction in a game
            for i in range(0, 10):
                # Activate current context
                context = self.currentContextBank[self.currentContext]

                try:
                    # Execute one step in this context
                    context.execute()
                except Exception as e:
                    if len(self.currentContextBank) == 1:
                        # When exception occurs, game is over if only a single
                        # context is available for that player...
                        playerName = context.name
                        message = "{} caused error '{}' - no more thread, \n\nGame Over\n".format(playerName,str(e))
                        self.arena.displayGameStop(message=message)
                        etime = time.time()
                        print("Duration: " + str(etime-stime))
                        return
                    else:
                        # Simply remove faulty context no need to do
                        # anything else, context will simply get flushed away...
                        playerName = context.name
                        message = "{} caused error '{}' - one less thread, game continues".format(playerName,str(e))
                        self.arena.displayContextCrash(message=message, contextDump=context)
                        self.currentContextBank.remove(context)
                        time.sleep(5)

                # Save context information before we switch

                # Context switch to next context
                if self.currentContext + 1 < len(self.currentContextBank):
                    # More context are available increment
                    self.currentContext += 1
                else:
                    # No more context available, switch back to 0
                    self.currentContext = 0

            # After each full run, update the "interface" (yeah this is an overstatement...)
            if cycles % 5000 == 0:
                self.arena.displayGameState(self.p1Capua, self.p2Capua)
                time.sleep(1)
                pass
            # Now allow the other player to play!
            self.switchPlayer()
            cycles += 10

        etime = time.time()
        print("Duration: " + str(etime-stime))
        # If we are here, both players are still alive...
        self.arena.displayGameStop(message="The game ended as a draw")

    def switchPlayer(self):
        """
        Simple helper method to make player switch less ugly in the code.
        :return:
        """
        if self.currentPlayer == self.p1Capua:
            # Save p1 information
            self.p1CurrentContext = self.currentContext
            self.p1ContextBank = self.currentContextBank

            # Load p2 information
            self.setCurrentPlayer(player=self.p2Capua,
                                  contextBank=self.p2ContextBank,
                                  currentContext=self.p2CurrentContext)
        else:
            # Save p2 information
            self.p2CurrentContext = self.currentContext
            self.p2ContextBank = self.currentContextBank

            # Load p1 information
            self.setCurrentPlayer(player=self.p1Capua,
                                  contextBank=self.p1ContextBank,
                                  currentContext=self.p1CurrentContext)
