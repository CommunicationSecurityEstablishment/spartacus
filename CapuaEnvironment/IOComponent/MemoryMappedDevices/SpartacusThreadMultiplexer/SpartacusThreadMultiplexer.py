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

from CapuaEnvironment.IOComponent.MemoryMappedDevices.BaseDevice import BaseDevice
from Configuration.Configuration import SPARTACUS_MAXIMUM_CONTEXT

import struct

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


# The following global is used to create a link between the VM and the game system.
# When GameEnvironment is None, VM understands that it is not running within the
# context of a gaming environment but rather as a standalone vm. The GameEnvironment
# variable has to be initiated by the GameManager when it is ready to start the game
GameEnvironment = None


class SpartacusThreadMultiplexer(BaseDevice):
    """
    This is a special device that allows a link between the game environment and the virtual machine. That link
    allows a player to create multiple thread that will be executed within the game environment. A maximum of
    3 thread/context can be created by the same player. Multiple threads are available only when in game mode. Using
    this device when program is running in a debugger will not result in a system exception/error but will
    simply be ignored. The device will still, however, allow for memory writes to happen in the device memory
    buffer. Bottom line is: no game, no thread. Threading is provided by the game, not the vm.
    """

    def __init__(self, parentMIOC=None):
        super(SpartacusThreadMultiplexer, self).__init__(parentMIOC=parentMIOC)
        self.data = b"\x00" * 0xFF
        self.startAddress = 0x20000200
        self.mask = 0xFFFFFF00

    def _memoryAction(self, source=None):
        """
        In this particular case, an action will only be taken if the device is used inside
        of a GameEnvironment. Otherwise it simply returns. In case where a GameEnvironment
        is available, a new thread/context will be created for that player.
        :param source:
        :return:
        """
        if GameEnvironment is not None:
            if len(GameEnvironment.currentContextBank) <= SPARTACUS_MAXIMUM_CONTEXT:
                # There is a maximum number of context that a player can have at the same time!
                # Yes the following imports are ugly, no I will not fix it.
                from CapuaEnvironment.ExecutionUnit.ExecutionUnit import ExecutionUnit
                from CapuaEnvironment.IntructionFetchUnit.InstructionFetchUnit import InstructionFetchUnit
                try:
                    newContextInstructionAddress = struct.unpack(">I", self.data[0:4])[0]
                    ifu = InstructionFetchUnit(GameEnvironment.mioc._memoryArray)
                    newContext = ExecutionUnit(mioc=GameEnvironment.mioc, ifu=ifu, name=source)
                    newContext.setupCore(I=newContextInstructionAddress)
                except Exception as e:
                    raise(ValueError("STM - Failure, unable to start new thread, likely cause: memory corruption"))

                GameEnvironment.currentContextBank.append(newContext)
