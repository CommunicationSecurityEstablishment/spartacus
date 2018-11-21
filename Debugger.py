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
from pathlib import Path

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
                        type=str,
                        default=None,
                        help="This is an optional argument. If present, debugger will load breakpoints "
                        "previously defined and stored in the specified file.")

    args = parser.parse_args()

    return args


def validateFilePath(filename, ext=None):
    """
    This function will simply validate file existence and file extension.
    If either is not true, then will raise an error.
    :param filename: str, file path to be validated
    :param ext: str, expected extension
    :return: boolean True,
    """
    if not os.path.exists(filename):
        raise ValueError("ERROR: File {} does not exists.".format(filename,))
    else:
        fileExt = filename.split(".")[-1]
        if fileExt != ext:
            raise ValueError("ERROR: Incorrect file extension on file {}".format(filename,))

    return True


def validateBreakPointFile(usable_args, ext=None):
    """
    This function will check the inputted breakpoint file and handle the cases.
    If either is not true will raise error.
    :param usable_args: An input parsed object as provided by argparse.parse_args()
    :param ext: str, expected extension for breakpoint file
    :return inputBreakpointFile: str, name of the breakpointFile that will be used by Debugger
    """
    inputBreakpointFile = usable_args.breakpoint

    if inputBreakpointFile is None:
        inputBreakpointFile = usable_args.input.split(".")[0]+".bp"
        Path(inputBreakpointFile).touch()
        return inputBreakpointFile
    elif not os.path.exists(inputBreakpointFile):
        inputFileExt = inputBreakpointFile.split(".")[-1]
        if inputFileExt != ext:
            raise ValueError("ERROR: Incorrect file extension on Breakpoint file {}".format(inputBreakpointFile,))
        Path(inputBreakpointFile).touch()
        return inputBreakpointFile
    elif os.path.exists(inputBreakpointFile):
        inputFileExt = inputBreakpointFile.split(".")[-1]
        if inputFileExt != ext:
            raise ValueError("ERROR: Incorrect file extension on Breakpoint file {}".format(inputBreakpointFile,))
        return inputBreakpointFile


if __name__ == '__main__':
    usableArgs = parseCommandLineArgs()

    goodInputFile = False
    gotSymbols = False
    symbolsFile = None
    breakpointFile = None

    if usableArgs.input is not None:
        # Make sure the parsed info is usable before using it!
        goodInputFile = validateFilePath(usableArgs.input, ext="bin")
        gotSymbols = validateFilePath(usableArgs.input.split(".")[0] + ".sym", ext="sym")
        breakpointFile = validateBreakPointFile(usableArgs, ext="bp")
    else:
        usableArgs.input = FIRMWARE_BINARY_FILE_PATH
        usableArgs.software = False
        usableArgs.address = FIRMWARE_LOAD_ADDRESS

    if gotSymbols:
        symbolsFile = usableArgs.input.split(".")[0] + ".sym"

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
