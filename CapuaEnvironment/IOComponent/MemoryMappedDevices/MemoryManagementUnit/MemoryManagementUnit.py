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

import struct

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class MemoryManagementUnit(BaseDevice):
    """
    The MemoryManagementUnit allows the user to change the permission associated with a
    region of the memory. The set of permission is RWX (in that same order). While it is
    possible to change the permission associated with a region of the memory, it is not
    possible too know ahead of time what are the permissions associated with a
    specific region of the memory. Careful users should take for granted that they
    do not have any permission in regions of memory where they are not already executing.
    """

    addressOffset = 0  # Where is the start address in the buffer this is 4 bytes
    maskOffset = 4  # Where The length in memory for action format MMMM MMMM This is 1 bytes long
    confirmPermissionOffset = 5  # Confirmation flag and new permission set format is CPPP 0000 This is 1 byte long

    def __init__(self, parentMIOC=None):
        super(MemoryManagementUnit, self).__init__(parentMIOC=parentMIOC)
        self.data = b"\x00" * 0xFF
        self.startAddress = 0x20000000
        self.mask = 0xFFFFFF00

    def _memoryAction(self, source="System"):
        """
        This only happens after a write. If an action should be taken, the action will be taken here
        In the case of the current device, the only possible actions are memory permission management actions
        :param source: String, who is at the origin of this action
        :return:
        """

        confirmationMask = 0b10000000
        readMask = 0b01000000
        writeMask = 0b00100000
        executeMask = 0b00010000

        # Do we have an action to take?
        confirmData = self.data[self.confirmPermissionOffset]
        confirmData &= confirmationMask

        if confirmData <= 0:
            # No need to take action, simply return to keep code clean
            return

        # If we are here, actions needs to be take
        permissionData = (readMask | writeMask | executeMask) & self.data[self.confirmPermissionOffset]

        read = True if (permissionData & readMask) > 0 else False
        write = True if (permissionData & writeMask) > 0 else False
        execute = True if (permissionData & executeMask) > 0 else False

        addressToGo = struct.unpack(">I", self.data[self.addressOffset:self.addressOffset + 4])[0]
        lengthToGo = int(self.data[self.maskOffset])

        memoryCells = self._parentMIOC._memoryArray.extractMemory(address=addressToGo, length=lengthToGo)

        # Our individual memoryCells are in the memoryCells list
        # The inside of the next loop could be done in a fancy loop avoiding code
        # repetition. However, performance analysis showed that doing it that way
        # saves between 0.0001 to 0.0005 seconds at execution. Since this is a tight
        # loop that would usually be executed repetitively, this is worth it.
        for cell in memoryCells:
            # READ
            if cell.canRead():
                if not read:
                    # We need to toggle the read flag
                    cell.toggleRead(accessedBy=source)
            else:
                if read:
                    cell.toggleRead(accessedBy=source)

            # WRITE
            if cell.canWrite():
                if not write:
                    # We need to toggle the read flag
                    cell.toggleWrite(accessedBy=source)
            else:
                if write:
                    cell.toggleWrite(accessedBy=source)

            # EXECUTE
            if cell.canExecute():
                if not execute:
                    # We need to toggle the read flag
                    cell.toggleExecute(accessedBy=source)
            else:
                if execute:
                    cell.toggleExecute(accessedBy=source)
