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

from ToolChain.Assembler.Assembler import Assembler
from ToolChain.Assembler.Constants import UNDEFINED, DEFAULT_OUTPUT_EXTENSION

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
    As implied by the name, this will parse the command line arguments so we can use them. Important note,
    after this function is called, no need to use the "extension" attribute since this one is concatenated
    with the "output". This results in cleaner code since those two are always(? most of the time at least)
    used together.
    :return: A parsed object as provided by argparse.parse_args()
    """
    parser = argparse.ArgumentParser(prog="Assembler.py",
                                     description="Capua Assembler Version {}".format(__version__,),
                                     epilog="This tool is provided as part of Spartacus learning environment under {} "
                                            "licence. Feel free to distribute, modify, "
                                            "contribute and learn!".format(__license__,))
    parser.add_argument("-i", "--input",
                        required=True,
                        nargs=1,
                        type=str,
                        help="Define the input file to be used by the assembler.")

    parser.add_argument("-o", "--output",
                        required=False,
                        nargs=1,
                        type=str,
                        default=UNDEFINED,
                        help="Define the output file where the assembled data will be written. If not specified, this "
                             "will default to the input file name, minus the extension, plus the --extension "
                             "provided value.")

    parser.add_argument("-e", "--extension",
                        required=False,
                        nargs=1,
                        type=str,
                        default=DEFAULT_OUTPUT_EXTENSION,
                        help="Default output extension for the output file. This is useful if changing extension value "
                             "while keeping default output file name. Default value for this is {} please note that "
                             "the '.' has to be provided by the user!".format(DEFAULT_OUTPUT_EXTENSION,))

    args = parser.parse_args()
    args.input = args.input[0]  # This originally come out as a list
    args.output = args.output[0] if type(args.output) is not str else args.input.split(".")[0]  # Using input as default
    args.extension = args.extension[0] if type(args.extension) is not str else args.extension
    args.output = args.output + args.extension if args.output.split(".")[-1] != "o" else args.output  # Just so we don't have to keep typing this...

    return args


def validatePaths(argsWithPaths):
    """
    This function will simply validate that the input path exists
    :param argsWithPaths: An input parsed object as provided by argparse.parse_args()
    :return: This does not return. Simply raises ValueError in cases where paths are not valid.
    """
    if not os.path.exists(argsWithPaths.input):
        raise ValueError("ERROR: file {} does not exists.".format(argsWithPaths.input,))


if __name__ == '__main__':
    usableArgs = parseCommandLineArgs()
    validatePaths(usableArgs)  # Make sure the parsed info is usable before using it!

    print("Assembler about to begin, following options will be used")
    print("  input file:             {}".format(usableArgs.input,))
    print("  output file:            {}".format(usableArgs.output,))

    assembler = Assembler(usableArgs.input, usableArgs.output)
    if os.path.exists(usableArgs.output):
        # The assembler did the job correctly and the out file has been written to disk!
        print("Assembler done, output file has been written to {}". format(usableArgs.output,))
    else:
        raise ValueError("An unknown error occurred while assembling the input file. Please validate "
                         "input file syntax (I know this error sucks... Sorry :) ). This 'should not' "
                         "have happened, please report this error to maintainer so we can all get a more "
                         "stable assembler. If you don't report, don't whine about this!")
