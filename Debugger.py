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

from Configuration.Configuration import FIRMWARE_BINARY_FILE_PATH, \
                                        FIRMWARE_LOAD_ADDRESS
from ToolChain.Debugger.Debugger import Debugger
from ToolChain.Linker.Constants import DEFAULT_LOAD_ADDRESS, UNDEFINED

import argparse
import os

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "CSE"
__status__ = "Dev"


def parseCommandLineArgs():
    """
    As implied by the name, this will parse the command line arguments so we can use them.
    :return: A parsed object as provided by argparse.parse_args()
    """
    parser = argparse.ArgumentParser(prog="Debugger.py",
                                     description="Capua On Chip Debugger Version {}".format(__version__,),
                                     epilog="This tool is provided as part of Spartacus learning environment under {} "
                                            "licence. Feel free to distribute, modify, "
                                            "contribute and learn!".format(__license__,))
    parser.add_argument("-i", "--input",
                        required=False,
                        type=str,
                        help="Define the input file(s) to be used.")

    parser.add_argument("-o", "--output",
                        required=False,
                        nargs=1,
                        type=str,
                        help="This is optional. If present, debugging session will be logged to specified file")

    parser.add_argument("-a", "--address",
                        required=False,
                        nargs=1,
                        type=int,
                        default=None,
                        help="Define the address at which a binary should be loaded.")

    parser.add_argument("-s", "--software",
                        required=False,
                        nargs=1,
                        type=bool,
                        default=False,
                        help="This is required if -s option was used on the linker. That will allow "
                             "binary to be loader at correct address specified inside the binary")

    parser.add_argument("-bp", "--breakpoint",
                        required=False,
                        nargs =1,
                        type=str,
                        help="This is an optional argument. If present, debugger will load breakpoints "
                        "previously defined and stored in the specified file.")

    args = parser.parse_args()

    return args


def validatePaths(argsWithPaths):
    """
    This function will simply validate that the input path exists and that the output path
    is free for the system to use
    :param argsWithPaths: An input parsed object as provided by argparse.parse_args()
    :return: This does not return. Simply raises ValueError in cases where paths are not valid.
    """
    gotSymbols = False
    if not os.path.exists(argsWithPaths.input):
        raise ValueError("ERROR: file {} does not exists.".format(argsWithPaths.input,))
    else:
        # condition only depends on input existence
        if os.path.exists(argsWithPaths.input.split(".")[0] + ".sym"):
            gotSymbols = True

    return gotSymbols


if __name__ == '__main__':
    usableArgs = parseCommandLineArgs()

    gotSymbols = False
    symbolsFile = None
    breakpointFile = None

    if usableArgs.input is not None:
        gotSymbols = validatePaths(usableArgs)  # Make sure the parsed info is usable before using it!
        symbolsFile = usableArgs.input.split(".")[0] + ".sym" if gotSymbols else ""
    else:
        usableArgs.input = FIRMWARE_BINARY_FILE_PATH
        usableArgs.software = False
        usableArgs.address = FIRMWARE_LOAD_ADDRESS

    if usableArgs.breakpoint is not None:
        breakpointFile = usableArgs.input.split(".")[0] + ".bp"

    print("Debug session about to begin, following options will be used")
    print("  input file:             {}".format(usableArgs.input,))
    if gotSymbols:
        print("  symbols file:             {}".format(symbolsFile,))
    if usableArgs.output is not None:
        print("  output file:            {}".format(usableArgs.output,))

    if usableArgs.address is None:
        usableArgs.address = DEFAULT_LOAD_ADDRESS

    debugger = Debugger(inputFile=usableArgs.input,
                        outputFile=usableArgs.output,
                        loadAddress=usableArgs.address,
                        softwareLoader=usableArgs.software,
                        symbolsFile=symbolsFile,
                        breakpointFile=breakpointFile)
    if usableArgs.output is not None and os.path.exists(usableArgs.output[0]):
        # The assembler did the job correctly and the out file has been written to disk!
        print("Debug session is over, output file has been written to {}". format(usableArgs.output,))
