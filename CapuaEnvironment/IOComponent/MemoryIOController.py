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

from CapuaEnvironment.MemoryArray.MemoryArray import MemoryArray
from CapuaEnvironment.IOComponent.MemoryMappedDevices.Clock.Clock import Clock
from CapuaEnvironment.IOComponent.MemoryMappedDevices.MemoryManagementUnit.MemoryManagementUnit import MemoryManagementUnit
from CapuaEnvironment.IOComponent.MemoryMappedDevices.SpartacusThreadMultiplexer.SpartacusThreadMultiplexer import SpartacusThreadMultiplexer
from Configuration.Configuration import MEMORY_START_AT

import struct

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class MemoryIOController:
    """
    High level memory access controller. This is meant to be used by ExecutionUnit to simplify memory access.
    This is also responsible for hardware memory mapping in the main memory space.


    Note about memory mapped device:
    Devices are mapped using their start address and mask. Overlaps between devices is NOT
    validated. It is the programmer's job to make sure that he is not overlapping.

    Determining if an address belongs to a memory mapped device:
    Lets say that the device is mapped at 0x10000000 with a 0xFFFF0000 mask
    Address: 0b 0001 0000  0000 0000  0000 0000  0000 0000
    Mask:    0b 1111 1111  1111 1111  0000 0000  0000 0000

    Start:   0b 0001 0000  0000 0000  0000 0000  0000 0000
    End:     0b 0001 0000  0000 0000  1111 1111  1111 1111

    This basically works like a subnet in the IP protocol. Each device has it's own "network address"
    The actual selection process is done using:
    A = the address being accessed
    dS = Start address for a specific device
    dM = Mask for a specific device

    First step, make sure an address is within the range of a device
    dS == A & dM    <- if this condition evaluates to True, the address A belongs the the device

    Let's take the  access address 0b0000 0001  0000 0000  0000 0000  1000 0000
    imagine we have a device mapped at address 0b0000 0001  0000 0000  0000 0000  0000 0000
    with the mask 0b1111 1111

    First, we xor
    A  = 0b0000 0001  0000 0000  0000 0000  1000 0000
    dS = 0b0000 0001  0000 0000  0000 0000  0000 0000
    dM = 0b1111 1111  1111 1111  1111 1111  0000 0000

    formula will be A & dM and then validate the result with dS

    A  = 0b0000 0001  0000 0000  0000 0000  1000 0000
    &
    dM = 0b1111 1111  1111 1111  1111 1111  0000 0000
    r  = 0b0000 0001  0000 0000  0000 0000  0000 0000

    r == dS therefore the address belongs to the device.

    If you need more information about this, simply do online searches about the
    IP protocol and how subnet mask works. You will find plenty of information.

    """

    _memoryArray = None
    _memoryMappedDevice = None

    def __init__(self, memoryArray: MemoryArray=None):
        """
        Simple initialisation, this class is dependant on the presence of a memory array
        for it to work properly.
        :param memoryArray: A valid MemoryArray
        """
        if memoryArray is None or type(memoryArray) is not MemoryArray:
            raise RuntimeError("Capua MemoryIOController Error")

        self._memoryArray = memoryArray
        self._memoryMappedDevice = []

        mmu = MemoryManagementUnit(parentMIOC=self)
        self.registerMemoryMappedDevice(device=mmu,
                                        startAddress=mmu.startAddress,
                                        mask=mmu.mask)

        clock = Clock(parentMIOC=self)
        self.registerMemoryMappedDevice(device=clock,
                                        startAddress=clock.startAddress,
                                        mask=clock.mask)

        stmp = SpartacusThreadMultiplexer(parentMIOC=self)
        self.registerMemoryMappedDevice(device=stmp,
                                        startAddress=stmp.startAddress,
                                        mask=stmp.mask)

    def memoryWriteAtAddressForLength(self, address=0x00, length=4, value=0x00, source="System"):
        """
        This handle a memory write and is meant to be the memory access point for the execution unit.
        It is also the memory access point for memory mapped hardware.
        :param address: int, Address at which we will write
        :param length: int, the length for the write (maximum is 4 bytes)
        :param value:  int, the value we need to write
        :param source: string, who is at the origin of this
        :return: None
        """

        # If action taken on memory mapped hardware we need to send it to the hardware!
        if address < MEMORY_START_AT:
            self._passMemoryReadWriteToMemoryMappedHardware(address=address,
                                                            length=length,
                                                            value=value,
                                                            isWrite=True,
                                                            source=source)
            return

        # First, we get the memory slice that we need to use and value to be written in individual bytes
        memorySlice = self._memoryArray.extractMemory(address, length)
        valueArray = self._prepareNumericValueToBeWrittenToMemory(length, value)

        # Now we write to memory!
        for i in range(0, len(valueArray)):
            memorySlice[i].writeValue(valueArray[i], accessedBy=source)

        return

    def memoryReadAtAddressForLength(self, address=0x00, length=4):
        """
        This handle a memory read and is meant to be the memory access point for the execution unit.
        It is also the memory access point for memory mapped hardware.
        :param address: int, Address at which we will read
        :param length: int, the length for the read (maximum is 4 bytes)
        :return: int value
        """

        # If action taken on memory mapped hardware we need to send it to the hardware!
        if address < MEMORY_START_AT:
            extractedValue = self._passMemoryReadWriteToMemoryMappedHardware(address=address,
                                                                             length=length,
                                                                             isWrite=False)
        else:
            extractedMemoryCells = self._memoryArray.extractMemory(address, length)
            valueToBeUnpacked = b""

            # Build a value list to be unpacked
            for i in range(0, length):
                valueToBeUnpacked += bytes([extractedMemoryCells[i].readValue()])

            # For the unpack to work, we need a 4 bytes len bytes object
            # This loop make sure that we have a usable bytes object
            while len(valueToBeUnpacked) < 4:
                valueToBeUnpacked = b'\x00' + valueToBeUnpacked
            extractedValue = struct.unpack(">I", valueToBeUnpacked)[0]

        return extractedValue

    def _passMemoryReadWriteToMemoryMappedHardware(self,
                                                   address=0x00,
                                                   length=4,
                                                   value=0x00,
                                                   isWrite=False,
                                                   source="System"):
        """
        This method is meant to act as a gateway to access memory mapped hardware
        :param address: int, Address at which we will read
        :param length: int, the length for the read (maximum is 4 bytes)
        :param value:  int, the value we need to read
        :param isWrite: If true will do a write operation otherwise do read
        :param source: str, this is a marker to identify an action, usually the name associated with an execution unit
        :return: int value if read, None otherwise
        """

        # We need to find a device that accept response for this memory access
        selectedDevice = None
        for device in self._memoryMappedDevice:
            if device.mask & address == device.startAddress:
                # We found a device mapped at the right place!
                # for more info about how the selection works, please see note at beginning of the class
                selectedDevice = device
                break

        if selectedDevice is not None:
            returnValue = selectedDevice.takeAction(address=address,
                                                    length=length,
                                                    value=value,
                                                    isWrite=isWrite,
                                                    source=source)
        else:
            # If we are here, no device responded to this device "call"
            raise MemoryError("Access to Memory Mapped Hardware with invalid address")
        return returnValue

    def _prepareNumericValueToBeWrittenToMemory(self, length=0, value=0):
        """
        This will prepare a numeric value so that it can be written to memory.
        :param length: int, Size to use in bytes
        :param value: int, the value to be written
        :return: list, list of number to be written to individual memory bytes
        """

        maximumValue = 0x00

        for i in range(0, length):
            maximumValue <<= 8
            maximumValue |= 0xFF

        if value > maximumValue or (1 > length > 4):
            raise ValueError("Invalid instruction format detected")

        memoryReadyValue = struct.pack(">I", value)[-length:]

        return memoryReadyValue

    def registerMemoryMappedDevice(self, device=None, startAddress=None, mask=None):
        """
        This will add a device to the memory mapped device list
        For more information about how devices are mapped into memory, please see note
        at the beginning of the class.
        :param device: The device object to be added
        :param startAddress: int, the start address where the hardware is to be mapped
        :param mask: int, the mask that is associated with the device
        :return:
        """

        if device is None:
            raise ValueError("Invalid device registered")

        if type(startAddress) is not int or startAddress >= MEMORY_START_AT:
            raise ValueError("Invalid start address for memory mapped device")

        if startAddress & mask != startAddress:
            raise ValueError("Invalid mask for memory mapped device")

        self._memoryMappedDevice.append(device)

