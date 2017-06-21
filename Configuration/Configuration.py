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

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


MEMORY_START_AT = 0x40000000
MEMORY_ARRAY_NUMBER_OF_MEMORY_CELL = 0x100000  # 1 048 576 memory cells = 1 Meg
MEMORY_END_AT = MEMORY_START_AT + MEMORY_ARRAY_NUMBER_OF_MEMORY_CELL
MEMORY_CELL_INITIAL_VALUE = 0XFF  # NOP operation

CAPUA_NUMBER_OF_CORE = 0x04     # How many execution units are running in the Capua environment
CAPUA_SYSTEM_CORE_SPEED = 0x0F  # How many unit of execution a system core can run when it is tasked
CAPUA_PLAYER_CORE_SPEED = 0x04  # How many unit of execution a player core can run when tasked

SPARTACUS_MAXIMUM_CONTEXT = 3   # What is the maximum number of context a player can have

REGISTER_A = 0b00
REGISTER_B = 0b01
REGISTER_C = 0b10
REGISTER_S = 0b11
