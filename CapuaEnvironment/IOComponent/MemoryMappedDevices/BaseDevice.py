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

import struct

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class BaseDevice:
    """
    This is a base device allowing other devices to be created from it. This device is not to be
    added to the system as it is not doing anything. It is just a frame
    """

    _parentMIOC = None  # The MemoryInputOutputController responsible for this device. This is put there
                        # in case a user wants to implement a device that can have direct access to write
                        # or read data in memory.
    startAddress = 0x00000000  # This is the address where the device will be mapped in memory
                               # obviously, this is different for every devices.
    mask = 0x00  # This indicate the memory range for this device. Think of this as a subnet mask in IPv4.
    data = None  # To be initialised by a device doing b"\x00" * maskValue

    def __init__(self, parentMIOC=None):
        self._parentMIOC = parentMIOC

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
        result = 0
        offset = self._translateAddressToOffset(address=address)
        self._confirmMemoryAccess(offset=offset, length=length)

        if isWrite:
            self._writeIntoDataBuffer(offset=offset, length=length, value=value, source=source)
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

        # Get the data
        rData = self.data[offset:offset+length]
        intData = struct.unpack(">I", rData)[0]

        return intData

    def _writeIntoDataBuffer(self, offset=None, length=None, value=None, source="System"):
        """
        This will prepare the data to be written and will take appropriate action depending on what
        has been written
        :param offset: int, Where are we reading
        :param length: int, For how long
        :param value: int, the value to be written in the buffer
        :param source: string, who is at the origin of this
        :return:
        """

        # Let's prepare the data for the write
        readyData = struct.pack(">I", value)

        # Now write the data
        dataFirstPart = self.data[0:offset]
        dataMiddlePart = readyData[-length:]
        dataLastPart = self.data[offset+length:]

        self.data = dataFirstPart + dataMiddlePart + dataLastPart

        self._memoryAction(source=source)

    def _memoryAction(self, source=None):
        """
        This is, technically, the only method that needs to be implemented/reimplemented by
        devices inheriting from the BaseDevice. This method is called at the end of a write operation
        to the device memory buffer. Be careful, this will not be called whenever a read is made
        to the device. In case where you need special actions done on read, YOU HAVE TO IMPLEMENT these
        on your own. See the "Clock" device for a code example.
        :param source:
        :return:
        """
        raise ValueError("Device _memoryAction needs to be implemented before it is used.")


    def _translateAddressToOffset(self, address=None):
        """
        This will simply translate a memory address into an offset that can be
        used to access data inside the memory buffer for this device
        :param address: int, the address that will be accessed
        :return: int, the offset where the address can be found
        """
        return address - self.startAddress

    def _confirmMemoryAccess(self, offset=None, length=None):
        """
        This simply throws an exception if an out of bound access is made to this device.
        It will also throw if length is too long.
        :param offset: int, where in the buffer
        :param length: int, for how long
        :return: Nothing, but throws exception in case of out of bound access
        """
        if (offset + length) > len(self.data):
            raise MemoryError("Device - out of bound memory access detected!")

        if 0 >= length > 4:
            raise ValueError("Device - invalid length detected in read instruction")
