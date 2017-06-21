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

from CapuaEnvironment.ExecutionUnit.ExecutionUnit import ExecutionUnit
from CapuaEnvironment.IntructionFetchUnit.InstructionFetchUnit import InstructionFetchUnit
from CapuaEnvironment.IOComponent.MemoryIOController import MemoryIOController
from CapuaEnvironment.MemoryArray.MemoryArray import MemoryArray

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class Capua:
    """
    This is the heart of the whole system. This is the glue that is holding all of CapuaEnvironment
    devices together.
    """

    ma = None
    mioc = None
    ifu = None
    eu = None

    def __init__(self, ma=None, mioc=None, name="System"):
        """
        Preparing the whole execution environment for this Capua instance. Note that a single memory
        array can be shared between multiple Capua environment.
        """

        # Two execution units CAN share a single memory array and MIOC
        if ma is None:
            self.ma = MemoryArray()
        else:
            self.ma = ma

        if mioc is None:
            self.mioc = MemoryIOController(self.ma)
        else:
            self.mioc = mioc

        self.ifu = InstructionFetchUnit(self.ma)
        self.eu = ExecutionUnit(self.mioc, self.ifu, name)
