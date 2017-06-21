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
import time

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class Clock(BaseDevice):
    """
    This device is a Clock allowing users to know the EPOCH time in seconds. It can only be read
    from. A write to this device will result in a system error/exception effectively crashing
    the context that was using the Clock device.
    """

    def __init__(self, parentMIOC=None):
        super(Clock, self).__init__(parentMIOC=parentMIOC)
        self.data = b"\x00" * 0xFF
        self.startAddress = 0x20000100
        self.mask = 0xFFFFFF00

    def takeAction(self, address=None, length=None, value=None, isWrite=False, source="System"):
        """
        This is the public facing interface for the device. Both read and write happens from
        this interface. No matter what the operation is, it will return a numeric value. If
        operation was a read, it returns the value that has been read. Otherwise it simply returns 0
        :param address: The address where the operation must happen
        :param length: The length of the operation
        :param value: The value to be written if is write
        :param isWrite: Is this a read or a write
        :param source: string, who is at the origin of this
        :return: Numeric value
        """
        # House keeping!
        offset = self._translateAddressToOffset(address=address)
        self._confirmMemoryAccess(offset=offset, length=length)

        if isWrite:
            raise MemoryError("Memory is not writable for device - CLOCK")
        else:
            result = self._readFromDataBuffer(offset=offset, length=length)
        return result

    def _readFromDataBuffer(self, offset=None, length=None):
        """
        This will read length number of bytes from the buffer, The max read is 4 bytes
        :param offset: int, Where are we reading
        :param length: int, For how long
        :return: int representing the value read from the buffer
        """
        timeData = struct.pack(">I", int(time.time()))
        # Get the time in place
        self.data = timeData + self.data[4:]

        # Now get the data
        rData = self.data[offset:offset+length]
        intData = struct.unpack(">I", rData)[0]

        return intData
























