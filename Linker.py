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

from ToolChain.Linker.StaticFlatLinker import StaticFlatLinker
from ToolChain.Linker.Constants import DEFAULT_LOAD_ADDRESS, UNDEFINED

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
    As implied by the name, this will parse the command line arguments so we can use them.
    :return: A parsed object as provided by argparse.parse_args()
    """
    parser = argparse.ArgumentParser(prog="Linker.py",
                                     description="Capua Static Flat Linker Version {}".format(__version__,),
                                     epilog="This tool is provided as part of Spartacus learning environment under {} "
                                            "licence. Feel free to distribute, modify, "
                                            "contribute and learn!".format(__license__,))
    parser.add_argument("-i", "--input",
                        required=True,
                        nargs="+",  # Using "+" here allows for variable number or parameters associated with this option
                        type=str,
                        help="Define the input file(s) to be used by the linker.")

    parser.add_argument("-o", "--output",
                        required=False,
                        nargs=1,
                        type=str,
                        default=UNDEFINED,
                        help="Define the output file where the linker data will be written. If not specified, this "
                             "will default to the input file name.")

    parser.add_argument("-a", "--address",
                        required=False,
                        nargs=1,
                        type=int,
                        default=DEFAULT_LOAD_ADDRESS,
                        help="Define the address at which a binary should be loaded. Don't mess this up, "
                             "Capua does not currently have virtual addressing mode... This means that you"
                             "HAVE TO MAKE SURE that your binary is loaded in a free memory region otherwise"
                             "you will destroy other programs!")

    parser.add_argument("-s", "--software",
                        required=False,
                        nargs=1,
                        type=bool,
                        default=False,
                        help="This specifies if the load happens by hardware or software. If it happens by"
                             "software, the load address will be but in the first 4 bytes of the final file"
                             "so that software can know where to put the binary in memory. Otherwise, the address"
                             "will not be added and the load will happen at hardware specified address.")

    args = parser.parse_args()
    args.output = args.output[0] if type(args.output) is not str else args.input[0].split(".")[0]  # Using input as default

    return args


def validatePaths(argsWithPaths):
    """
    This function will simply validate that the input path exists and that the output path
    is free for the system to use
    :param argsWithPaths: An input parsed object as provided by argparse.parse_args()
    :return: This does not return. Simply raises ValueError in cases where paths are not valid.
    """
    for file in argsWithPaths.input:
        if not os.path.exists(file):
            raise ValueError("ERROR: file {} does not exists.".format(file,))

if __name__ == '__main__':
    usableArgs = parseCommandLineArgs()
    validatePaths(usableArgs)  # Make sure the parsed info is usable before using it!
    symbolsFile = usableArgs.output.split(".")[0] + ".sym"

    print("Linker about to begin, following options will be used")
    print("  input file:             {}".format(usableArgs.input,))
    print("  symbols file:           {}".format(symbolsFile,))
    print("  output file:            {}".format(usableArgs.output,))

    linker = StaticFlatLinker(inputFileList=usableArgs.input,
                              outputFile=usableArgs.output,
                              loadAddress=usableArgs.address,
                              softwareLoader=usableArgs.software,
                              symbolsFile=symbolsFile)
    if os.path.exists(usableArgs.output):
        # The assembler did the job correctly and the out file has been written to disk!
        print("Linker done, output file has been written to {}". format(usableArgs.output,))
    else:
        raise ValueError("An unknown error occurred while linking the input files. Please validate "
                         "input files (I know this error sucks... Sorry :) ). This 'should not' "
                         "have happened, please report this error to maintainer so we can all get a more "
                         "stable linker. If you don't report, don't whine about this!")
