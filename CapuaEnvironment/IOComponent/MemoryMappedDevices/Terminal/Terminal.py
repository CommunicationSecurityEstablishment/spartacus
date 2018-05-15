#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

"""
This file is part of Spartacus project
Copyright (C) 2017  CSE

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
from Configuration.Configuration import DISPLAY_REFRESH_RATE, \
                                        DISPLAY_FONT_SIZE, \
                                        INTERRUPT_KEYBOARD, \
                                        KEYBOARD_BUFFER_SIZE, \
                                        KEYBOARD_REFRESH_RATE


import struct
import threading
import time
import tkinter
import tkinter.font

__author__ = "CSE"
__copyright__ = "Copyright 2017, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"


class Terminal(BaseDevice):
    """
    This device is a virtual display unit. It allows for a text mode display on an 80x25 char basis
    Char 0 line 0 char is mapped at 0x20001000, char 1 line 0 is mapped at 0x20001001. In order to
    write text to the display, one simply need to write at the appropriate memory address. Following
    a write to the display memory space, the display will then be updated.
    """

    def __init__(self, parentMIOC=None):
        super(Terminal, self).__init__(parentMIOC=parentMIOC)
        self._data = b"\x20" * 0xFFF
        self.startAddress = 0x20001000      # Display is mapped from 0x20001000 to 0x200017ff
                                            # Keyboard is mapped from 0x20001800 all the way to end of range
                                            # but only the first byte is used
        self.mask = 0xFFFFF000
        self._displayRefreshRate = float(DISPLAY_REFRESH_RATE) / 1000
        self._terminalBufferLock = threading.Lock()

        self._keyboardCodeListLock = threading.Lock()
        self._keyboardCodeList = []
        self._keyboardRefreshRate = float(KEYBOARD_REFRESH_RATE) / 1000

        self._displayThread = threading.Thread(target=self._displayLoop)
        self._displayThread.start()

        self._keyboardThread = threading.Thread(target=self._keyboardLoop)
        self._keyboardThread.start()

        self.interruptNumber = INTERRUPT_KEYBOARD

    def _generateDisplayText(self):
        """
        This method is used to generate the text to be displayed on the screen label. As of now, this is working
        but, should the bytes string be replaced with actual strings, this would break because of automatic trimming.
        TK labels seem to support non printable character relatively well when used with byte string.
        This requires more work to validate.
        TODO: Validate about non printable character
        :return: str, the display data ready for printing
        """
        displayText = b""
        self._terminalBufferLock.acquire()
        for i in range(0, 80*25, 80):
            if i != 0:
                displayText += b"\n"     # Put here at loop beginning to prevent 1 too many lines
            line = self._data[i:i + 80]
            line.replace(b"\n", b" ")   # Virtual display will break if we don't prevent \n in bytes
            displayText += line
        self._terminalBufferLock.release()

        return displayText

    def _keyboardLoop(self):
        """
        This is the threaded loop that allows to put scan codes in the memory for them to be
        processed by the machine. This is here so we can keep a "python" buffer of scan code
        instead of an "in memory" list of scan code. The scan codes are inserted and
        "signaled" at a specified (see configuration) interval in an attempt to prevent
        scan code loss.
        :return:
        """
        while True:
            if self._shutdownProcedureInAction:
                # This allows the method to return if we need to shutdown the system
                break
            time.sleep(self._keyboardRefreshRate)     # Division is to honour the milliseconds

            self._keyboardCodeListLock.acquire()
            if len(self._keyboardCodeList) > 0:
                # Get the oldest scan code
                currentCode = self._keyboardCodeList[0]
                self._writeIntoDataBuffer(offset=0x800, length=1, value=currentCode)
                sigResult = self._parentMIOC.eu.signalHardwareInterrupt(self.interruptNumber)
                if sigResult:
                    # The interrupt has been signaled, we can remove oldest scan code
                    poppedCode = self._keyboardCodeList.pop(0)
                    if poppedCode != currentCode:
                        # If this case is true, code list is corrupted
                        raise RuntimeError("Scan code list corruption has been detected")
            self._keyboardCodeListLock.release()

    def _displayLoop(self):
        """
        This is the display loop. This is in charge of asynchronous display operations and is
        launched right after device initialisation is over.
        :return:
        """
        self.window = tkinter.Tk()
        self.window.title("Spartacus Learning VM")
        self.window.bind("<KeyPress>", self._keyDown)
        self.customFont = tkinter.font.Font(family="Courier", size=DISPLAY_FONT_SIZE)
        self.displayWindow = tkinter.Label(self.window,
                                           text=self._generateDisplayText(),
                                           font=self.customFont,
                                           bg="black",
                                           fg="white",
                                           justify=tkinter.LEFT)
        self.displayWindow.grid()

        while True:
            if self._shutdownProcedureInAction:
                # This allows the method to return if we need to shutdown the system
                self.window.quit()
                break
            self.displayWindow.config(text=self._generateDisplayText())
            #TODO need more research on this
            self.window.update_idletasks()
            self.window.update()
            time.sleep(self._displayRefreshRate)

    def _keyDown(self, e):
        """
        TODO: This will be used for the virtual keyboard.
        :param e:
        :return:
        """
        self._keyboardCodeListLock.acquire()

        self._keyboardCodeList.append(e.keycode)
        if len(self._keyboardCodeList) > KEYBOARD_BUFFER_SIZE:
            self._keyboardCodeList.pop(0)     # Flush oldest char but keep the rest

        self._keyboardCodeListLock.release()

    def _writeIntoDataBuffer(self, offset=None, length=None, value=None, source="System"):
        """
        This will prepare the data to be written and will write it. Contrary to a normal device, this one need to
        acquire a lock on the memory buffer. Also, no "action" is taken after a write since the action happens
        asynchronously in order to help limit performance issues related to managing the display.
        For these reasons, this is reimplemented here and the parent version is not used.
        Important not, only write into buffer is re implemented from the parent because the display can read
        the buffer but not write it. Therefore the parent read literally can't happen at the same time
        as this write is happening.
        :param offset: int, Where are we reading
        :param length: int, For how long
        :param value: int, the value to be written in the buffer
        :param source: string, who is at the origin of this
        :return:
        """

        # Let's prepare the data for the write
        readyData = struct.pack(">I", value)

        # Now write the data
        self._terminalBufferLock.acquire()
        dataFirstPart = self._data[0:offset]
        dataMiddlePart = readyData[-length:]
        dataLastPart = self._data[offset + length:]

        self._data = dataFirstPart + dataMiddlePart + dataLastPart
        self._terminalBufferLock.release()
