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

from GameOverlay.Arena import Arena
from GameOverlay.GameManager import GameManager

import argparse
import os

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


def parseCommandLineArgs():
    """
    This simply parses the command line so we can get both players file information
    :return: A parsed object as provided by argparse.parse_args()
    """
    parser = argparse.ArgumentParser(prog="Game.py",
                                     description="Capua Assembler Version {}".format(__version__,),
                                     epilog="This tool is provided as part of Spartacus learning environment under {} "
                                            "licence. Feel free to distribute, modify, "
                                            "contribute and learn!".format(__license__,))
    parser.add_argument("-1", "--p1",
                        required=True,
                        nargs=1,
                        type=str,
                        help="Define the player 1 binary file to be loaded")

    parser.add_argument("-2", "--p2",
                        required=True,
                        nargs=1,
                        type=str,
                        help="Define the player 2 binary file to be loaded")

    args = parser.parse_args()
    args.p1 = os.path.abspath(args.p1[0])  # This originally come out as a list
    args.p2 = os.path.abspath(args.p2[0])

    return args


def validatePaths(argsWithPaths):
    """
    This function will simply validate that both paths exists
    :param argsWithPaths: An input parsed object as provided by argparse.parse_args()
    :return: This does not return. Simply raises ValueError in cases where paths are not valid.
    """
    if not os.path.exists(argsWithPaths.p1):
        raise ValueError("ERROR: file {} does not exists.".format(argsWithPaths.p1,))
    if not os.path.exists(argsWithPaths.p2):
        raise ValueError("ERROR: file {} does not exists.".format(argsWithPaths.p2,))


if __name__ == '__main__':
    usableArgs = parseCommandLineArgs()
    # import pdb; pdb.set_trace()
    validatePaths(usableArgs)  # Make sure the parsed info is usable before using it!

    print("Game about to begin, following options will be used")
    print("  Player 1 file:             {}".format(usableArgs.p1,))
    print("  Player 2 file:             {}".format(usableArgs.p2,))

    p1UsableName = usableArgs.p1.split("\\")[-1]
    p1UsableName = p1UsableName.split(".")[0]

    p2UsableName = usableArgs.p2.split("\\")[-1]
    p2UsableName = p2UsableName.split(".")[0]

    arena = Arena()
    arena.displayFirstInterface(p1=p1UsableName, p2=p2UsableName)

    gm = GameManager(p1File=usableArgs.p1, p1Name=p1UsableName, p2File=usableArgs.p2, p2Name=p2UsableName)
