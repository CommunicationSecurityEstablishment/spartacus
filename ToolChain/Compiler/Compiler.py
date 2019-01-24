#!/usr/bin/env python
#  -*- coding: <utf-8> -*-

"""
This file is part of Spartacus project
Copyright (C) 2018  CSE

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

from ToolChain.Compiler.Constants import ACCEPTED_TYPES, \
                                         IGNORE_CHARS, \
                                         BOOLEAN_OPERATORS, \
                                         ALLOWED_CHARS, \
                                         ARRAY_PATTERN, \
                                         SINGLE_QUOTE, \
                                         DOUBLE_QUOTE, \
                                         BINARY_OPERATORS, \
                                         MEMORY_START

from ToolChain.Compiler.MathParser import tokenize, \
                                          infixToPostfix, \
                                          evaluatePostfix

import re

__author__ = "CSE"
__copyright__ = "Copyright 2018, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "3.0"
__maintainer__ = "CSE"
__status__ = "Dev"


class Compiler:
    """
    This is a compiler that converts C code to Capua ASM. It currently supports a small subset of the C programming
    language, and functionality will progressively be added. It makes use of a finite state machine type model, using
    states to determine the next expected input, and how to handle the information. Consult the documentation for
    details on supported features and limitations.
    """

    memoryLocation = MEMORY_START  # Memory location for local variables.
    state = 0                      # "States" are used to determine our next path for processing the C file
    lineno = 0                     # Line number for printing error messages

    currentVar = ""                # Name of variable being evaluated
    currentType = ""               # Current data type being read, before method/variable declaration
    currentMethod = ""             # String containing the current method being evaluated
    identifier = ""                # Used to determine first token of a line
    functionCall = ""              # Name of the function we're calling when doing variable assignment
    functionArg = ""               # Used to read a function call's arguments
    mathFormula = ""               # Will contain our fully assembled math expressions for variable assignments
    ifOperator = ""                # Holds the logical operator between two sides of an if boolean expression
    binaryOperator = ""            # Holds the current binary operator being used in if/while statements
    arrayLength = ""               # Length of current array variable being evaluated
    quoteFlag = ""                 # Keeps track of whether we used single or double quote to declare a char variable

    expectFlag = 0                 # Used to control what input we expect next
    whileFlag = 0                  # Lets the compiler know if we're in a while loop
    nestedFlag = 0                 # Lets the compiler know if we're in an if statement

    argCount = 0                   # Used for number of operands in math expression, args in function calls, etc.
    variableCount = 0              # Number of variables declared in current function.

    ifLabel = 0                    # For jump instructions, we need a unique label for every if statement
    binaryLabel = 0                # For unique labels when dealing with binary operators in if/while statements
    whileLabel = 0                 # For while loops, we need a unique label

    binaryList = []                # To pop/push labels when dealing with binary operators in if/while statements
    labelList = []                 # List containing names of labels for if/while jumps
    whileList = []                 # List containing the names of while loops
    pointerList = []               # List containing variables that are pointers
    charList = []                  # List containing variables that are chars
    varList = []                   # Contains a list of variable names
    arrayList = {}                 # Dict containing variables that are arrays
    varLocation = {}               # Contains the memory location for all variables
    methodList = {}                # List of methods, along with their return type, variables (and types), and # of args

    mainFunctionASM = ""           # String that will contain all the assembled casm code for the main function
    otherFunctionASM = ""          # String that will contain all the assembled casm code for all other functions

    def __init__(self, inputFile=None, outputFile=None):
        """
        This allows for simple initialisation of the Compiler. It will check if the input/output files are valid,
        and then call the parseFile method to begin the compiling process.
        :param inputFile: inputFile: str, name of file to read from
        :param outputFile: str, name of file that will be created and written to
        :return:
        """

        if type(inputFile) is not str or len(inputFile) is 0:
            # File is invalid
            raise ValueError("Assembler error - Invalid input file selected")
        if type(outputFile) is not str or len(outputFile) is 0:
            # File is invalid
            raise ValueError("Assembler error - Invalid output file selected")

        self.readFile(inputFile, outputFile)

    def readFile(self, inputFile, outputFile):
        """
        Initializes parsing process. Opens the input file to read from, and initializes the output file we will create.
        We then read each line and feed every character into the parse method individually. Once done, we close the
        input/output files.
        :param inputFile: str, name of file to read from
        :param outputFile: str, name of file that will be created and written to
        :return:
        """

        try:
            file = open(inputFile, mode="r")
            inputFile = file.readlines()
        except OSError as e:
            raise OSError("Couldn't open file {}".format(inputFile))
        try:
            output = open(outputFile, mode="w")
        except OSError as e:
            raise OSError("Couldn't open file {}".format(outputFile))

        for line in inputFile:
            # read each line individually
            line = line.split("//", maxsplit=1)[0]  # Remove comments from line
            self.lineno += 1

            for x in line:
                # parse each character at a time to make use of each state correctly
                asmText = self.parse(x, "")

                if self.currentMethod == "main":
                    # we check if the method being evaluated is the main method
                    self.mainFunctionASM += asmText
                else:
                    # otherwise, we assume it's another function and append to the otherFunctionASM string
                    self.otherFunctionASM += asmText

        # We want the program to read the main function first, so we'll print that to the output first
        output.write(self.mainFunctionASM)
        output.write("    JMP <> end\n")
        output.write(self.otherFunctionASM)
        output.write("end:\n")

        if self.currentMethod != "":
            # If we finish reading input and we still have a method being evaluated, there's a curly brace missing
            raise ValueError("Missing closing curly brace for end of method/if/while.")

        try:
            file.close()
            output.close()
        except OSError as e:
            raise OSError("Couldn't close file.")

    def parse(self, char, output):
        """
        Receives characters one by one and makes use of states to determine the next appropriate action. Each state has
        its own restrictions based on what input it expects next. This parse method is essentially the controller that
        directs input.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if self.state == 0:
            output = self.parseFunctionReturnType(char, output)

        elif self.state == 1:
            output = self.parseFunctionName(char, output)

        elif self.state == 2:
            output = self.parseFunctionArgumentType(char, output)

        elif self.state == 3:
            output = self.parseFunctionArgumentName(char, output)

        elif self.state == 4:
            output = self.countFunctionArguments(char, output)

        elif self.state == 5:
            output = self.parsePrimaryIdentifier(char, output)

        elif self.state == 6:
            output = self.parseIntegerVariableName(char, output)

        elif self.state == 7:
            output = self.beginIntegerAssignment(char, output)

        elif self.state == 8:
            output = self.parseFunctionCall(char, output)

        elif self.state == 9:
            output = self.parseIfStatement(char, output)

        elif self.state == 10:
            output = self.parseWhileLoop(char, output)

        elif self.state == 11:
            output = self.parseReturnStatement(char, output)

        elif self.state == 12:
            output = self.parseArrayDeclaration(char, output)

        elif self.state == 13:
            output = self.assignValueAtArrayIndex(char, output)

        elif self.state == 14:
            output = self.parsePointerInitialization(char, output)

        elif self.state == 15:
            output = self.assignPointerValue(char, output)

        elif self.state == 16:
            output = self.dereferencePointer(char, output)

        elif self.state == 17:
            output = self.assignImmediateValueToPointer(char, output)

        elif self.state == 18:
            output = self.parseCharVariable(char, output)

        elif self.state == 19:
            output = self.assignCharValue(char, output)

        return output

    def parseFunctionReturnType(self, char, output):
        """
        First step in parsing data. At this step, we begin to read the method header. We expect to read the return data
        type.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # white space or new line before any relevant information
            pass

        elif char in IGNORE_CHARS and self.expectFlag == 1:
            # if we read a space while reading the method's return type, then we assume we're done
            if self.currentType in ACCEPTED_TYPES:
                self.state = 1
                self.expectFlag = 0
            else:
                # the return type read is invalid in this case
                raise ValueError("Incorrect return type for method declaration at line {}.".format(self.lineno))

        else:
            # we simply append the char to the current type
            self.currentType += char
            self.expectFlag = 1

        return output

    def parseFunctionName(self, char, output):
        """
        Here we expect to read the method's name. Once we reach a space or an opening parentheses, we add the method
        to the methodlist along with its data type.
        TODO: figure out a way to have the main method printed first in the .casm file
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # white space or new line before any relevant information
            pass

        elif char == " " and self.expectFlag == 1:
            # we have our method name, we expect an opening parentheses some time after the first space
            self.resetGlobalValues("01000000000000")
            self.state = 2

        elif char == "(":
            # We read the opening parentheses after the method name, no need to check for it later
            self.methodList[self.currentMethod] = {"retType": self.currentType}
            output += (self.currentMethod + ":\n")
            self.resetGlobalValues("11000000000000")
            self.state = 2

        else:
            self.currentMethod += char
            self.expectFlag = 1

        return output

    def parseFunctionArgumentType(self, char, output):
        """
        Deals with an argument's data type. This is the first step in determining the tuple: arg data type/arg name.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 1:
            # we have our method name and return type, but have not yet seen the opening bracket for arguments "("
            pass

        elif char == "(" and self.expectFlag == 1:
            # We have our opening parentheses for arguments, we can now look for the first variable's data type
            self.expectFlag = 0
            self.methodList[self.currentMethod] = {"retType": self.currentType}
            output += (self.currentMethod + ":\n")

            if self.currentMethod == "main":
                output += "    MOV end $S\n"

        elif self.expectFlag == 0:
            # Here we expect to read the first character of the variable's data type
            if char == ")":
                # If instead we simply read a closing parentheses, we assume there are no arguments.
                self.state = 4
            elif char == " ":
                # If we have a space, we have not yet seen the first char of the variable's data type.
                pass
            else:
                # We read the first character of the variable's data type
                self.currentType += char
                self.expectFlag = 2

        elif self.expectFlag == 2:
            # Here we read the remainder of the variable's data type. If we read a comma, there are other
            if char == ")":
                self.state = 4
                self.expectFlag = 0
            elif char == " ":
                # we need to read a space before our variable's name. Now we're ready to read the name itself.
                if self.currentType in ACCEPTED_TYPES:
                    self.state = 3
                    self.expectFlag = 0
                else:
                    raise ValueError("Data type not supported for method variable: {}.".format(self.currentType))
            else:

                # append the character to the current type being read.
                self.currentType += char

        return output

    def parseFunctionArgumentName(self, char, output):
        """
        This state reads the name of a method argument. Once we have the full name, we couple it with the data type
        read in state2, and we add it to the method's dict of variables. If we read a comma, we know we're ready to
        read another argument, and then we jump back to state2.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if self.expectFlag == 0 and char == " ":
            # Here we're still reading whitespace after variable's data type declaration
            pass

        elif self.expectFlag == 1 and char == " ":
            # We read the variable's name, now we wait for the next character to decide where to go
            self.addVariableToMethodDict()
            self.expectFlag = 2

        elif self.expectFlag == 1 and char == ",":
            # We read a comma immediately after variable name (no space), so we expect to read more variables
            self.addVariableToMethodDict()
            self.expectFlag = 3

        elif self.expectFlag == 1 and char == ")":
            # Closing parentheses right after variable name. We go to method's body
            self.addVariableToMethodDict()
            self.state = 4
            self.expectFlag = 0

        elif self.expectFlag == 2:
            # We've read a space after variable's name, now we wait for the next key character to know where to go
            if char == " ":
                pass
            elif char == ",":
                self.expectFlag = 3
            elif char == ")":
                self.state = 4
                self.expectFlag = 0
            else:
                raise ValueError("Syntax error at line {}.".format(self.lineno))

        elif self.expectFlag == 3:
            # After reading a comma, we either read the beginning of a new variable declaration, or some more whitespace
            if char == " ":
                pass
            else:
                self.currentType = char
                self.state = 2
                self.expectFlag = 2

        else:
            # append the character to the current variable's name
            self.currentVar += char
            self.expectFlag = 1

        return output

    def countFunctionArguments(self, char, output):
        """
        In this method, we've read all the arguments of a method declaration. Now we simply expect to read the opening
        curly brace "{" to signify the opening body of the method. Here, we also write the appropriate casm instructions
        to the output file. The stack pointer gets moved to "end" if it's the main method, and the S2 pointer must point
        to the first argument pushed to the stack (if any). This offset is determined by the number of arguments counted
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        self.expectFlag = 0

        if char in IGNORE_CHARS:
            # whitespace or newline characters when not expecting a particular input
            pass

        elif char == "{":
            # We add the total amount of variables present in the method's argument list. Used for function calls
            # in the body of another method to ensure the correct amount of variables are passed in.
            self.methodList[self.currentMethod]["totalVars"] = self.argCount
            self.state = 5

            if self.currentMethod == "main":
                # the main method would technically be the bottom of the stack frame, so we initialize the stack pointer
                output += "    MOV end $S\n"
            else:
                # we offset the S2 pointer by the amount of arguments passed into the method
                if self.argCount > 0:
                    output += "    MOV $S $S2\n"
                    output += ("    SUB #" + str(self.argCount * 4 + 4) + " $S2\n")

            self.argCount = 0

        else:
            raise ValueError("Syntax error, expecting \"{\", got {}".format(char))

        return output

    def parsePrimaryIdentifier(self, char, output):
        """
        Initial evaluation of a line within the body of a method. We read the input and concatenate to identifier
        string. Once we read a key token we check various cases to see where we need to go with out identifier. This is
        where most features can be implemented later.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # whitespace or newline characters when not expecting a particular input
            pass

        elif char == "*" and self.expectFlag == 0:
            # assigning a value to a pointer, it should be the first thing we read
            self.state = 17

        elif char == " " and self.expectFlag == 1:
            # we read a space, now we evaluate our indicator to determine what sort of operation we're dealing with
            if self.identifier == "if":
                # identifier is an if statement
                self.state = 9
                self.resetGlobalValues("10000100000000")
                self.nestedFlag += 1

            elif self.identifier == "while":
                # identifier is a while loop indicator
                output += ("LOOP" + str(self.whileLabel) + ":\n")
                self.whileList.append("LOOP" + str(self.whileLabel))
                self.state = 10
                self.whileLabel += 1
                self.nestedFlag += 1
                self.whileFlag += 1
                self.resetGlobalValues("10000100000000")

            elif self.identifier == "return":
                # identifier is a return statement
                self.resetGlobalValues("10000100000000")
                self.state = 11

            elif (self.identifier in self.varList) or self.identifier in self.methodList[self.currentMethod]:
                # the identifier is a variable that has already been declared
                self.currentVar = self.identifier
                self.resetGlobalValues("00000100000000")
                self.state = 6
                self.expectFlag = 2

            elif self.identifier in ACCEPTED_TYPES:
                # identifier is a data type, new variable declaration
                self.currentType = self.identifier

                if self.currentType == "int":
                    # new integer variable declaration goes to state 6
                    self.state = 6
                elif self.currentType == "char":
                    # new char variable declaration goes to state 18
                    self.state = 18

                self.resetGlobalValues("10000100000000")

            elif self.identifier in self.methodList:
                # identifier is a function call
                self.state = 8
                self.functionCall = self.identifier
                self.resetGlobalValues("10000100000000")

            elif self.identifier in self.pointerList:
                # identifier is a pointer
                self.expectFlag = 2
                self.state = 14
                self.currentVar = self.identifier
                self.resetGlobalValues("00000100000000")

            elif self.identifier in self.charList:
                # identifier is a char variable
                self.expectFlag = 4
                self.currentVar = self.identifier
                self.state = 19
                self.resetGlobalValues("00000100000000")

            else:
                # identifier was not valid
                raise ValueError("Error at line {}".format(self.lineno))

        elif char == "=" and self.expectFlag == 1:
            # here we have a variable assignment. Variable must be already declared in this case

            if (self.identifier in self.varList) or self.identifier in self.methodList[self.currentMethod]:
                self.currentVar = self.identifier
                self.state = 7
                self.resetGlobalValues("10000100000000")

            elif self.identifier in self.pointerList:
                # identifier is a pointer
                self.state = 15
                self.currentVar = self.identifier
                self.resetGlobalValues("10000100000000")

            elif self.identifier in self.charList:
                # identifier is a char variable
                self.expectFlag = 4
                self.currentVar = self.identifier
                self.state = 19
                self.resetGlobalValues("00000100000000")

            else:
                raise ValueError("Invalid assignment at line {}: must be valid variable".format(self.lineno))

        elif char == "[" and self.expectFlag == 1:
            # this implies an already declared array
            self.currentVar = self.identifier
            self.state = 13
            self.resetGlobalValues("10000100000000")

        elif char == "(" and self.expectFlag == 1:
            # immediately after the identifier, we read an opening parentheses. Here we cover all possible cases

            if self.identifier in self.methodList:
                # identifier is a function call
                self.state = 8
                self.functionCall = self.identifier
                self.resetGlobalValues("00000100000000")

            elif self.identifier == "if":
                # identifier is an if statement
                self.state = 9
                self.nestedFlag += 1
                self.resetGlobalValues("00000100000000")

            elif self.identifier == "while":
                # identifier is a while loop indicator
                output += ("LOOP" + str(self.whileLabel) + ":\n")
                self.whileList.append("LOOP" + str(self.whileLabel))
                self.state = 10
                self.whileLabel += 1
                self.whileFlag += 1
                self.nestedFlag += 1
                self.resetGlobalValues("00000100000000")

            else:
                # identifier was not valid
                raise ValueError("Error at line {}".format(self.lineno))

        elif char == "}":
            # end of method, if statement, or while loop

            if self.nestedFlag == 0:
                # if we aren't in any while/if statements, this is the end of our method
                self.state = 0
                self.varList.clear()
                self.varLocation.clear()
                self.resetGlobalValues("01110100000010")

            else:
                # otherwise, we print the appropriate instructions to end the while loop or if statement
                self.nestedFlag -= 1
                if self.whileFlag > 0:
                    self.whileFlag -= 1
                    output += ("    JMP <> " + self.whileList.pop() + "\n")

                output += (self.labelList.pop() + ":\n")

        else:
            # append the character to the identifier string is nothing else of interest was read.
            self.identifier += char
            self.expectFlag = 1

        return output

    def parseIntegerVariableName(self, char, output):
        """
        Initial variable name declaration. We already have the data type, so now we read its name until we get a
        relevant token to determine what to do with the variable.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # ignore spaces/new line chars if we're not expecting any input in particular
            pass

        elif char == "*" and self.expectFlag == 0:
            # we're dealing with a new pointer variable in this case
            self.state = 14

        elif char == " " and self.expectFlag == 1:
            # we have the variable name, now we move to the next phase to determine appropriate action
            self.expectFlag = 2

        elif char == "=" and self.expectFlag == 1:
            # we have the variable name, and we see that an assignment will happen
            self.verifyVariable()
            self.state = 7
            self.resetGlobalValues("10000000000000")

        elif char == ";" and self.expectFlag == 1:
            # end of variable declaration. we assign its memory location and add it to the variable list
            self.verifyVariable()
            self.state = 5
            self.resetGlobalValues("11100000000000")

        elif char == "[" and self.expectFlag == 1:
            # Here we're ready to declare a new array
            self.validName(self.currentVar)
            self.state = 12
            self.resetGlobalValues("10000000000000")

        elif self.expectFlag == 2:
            # We reach this step if we have the variable name and we read at least one space

            if char in IGNORE_CHARS:
                # we may keep reading spaces/ new line until we reach a relevant token
                pass

            elif char == "=":
                # variable assignment. if the variable was not in the list, we add it
                if (self.currentVar not in self.varList) and self.currentVar not in self.methodList[self.currentMethod]:
                    # we're dealing with a new variable
                    self.varList.append(self.currentVar)
                    self.varLocation[self.currentVar] = self.memoryLocation
                    self.memoryLocation += 4
                    self.variableCount += 1
                self.validName(self.currentVar)
                self.state = 7
                self.resetGlobalValues("10000000000000")

            elif char == ";":
                # simple declaration (e.g. int a;), we add it to the variable list and allocate a memory location
                self.verifyVariable()
                self.state = 5
                self.resetGlobalValues("11100000000000")

            else:
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        else:
            # append the character to the current variable's name
            self.currentVar += char
            self.expectFlag = 1

        return output

    def beginIntegerAssignment(self, char, output):
        """
        Begins variable assignment. This could either be a math formula, or a function call
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # whitespace or newline character before any important tokens are read
            pass

        elif char == "(" and self.expectFlag == 1:
            # we read an opening parentheses, it could either be a function call or part of a normal math expression

            if self.mathFormula in self.methodList:
                # if we have a function call for a variable assignment, we jump to state 8 which deals with functions
                self.functionCall = self.mathFormula
                self.state = 8
            else:
                # otherwise, the parentheses is just part of a normal math expression
                self.mathFormula += char

        elif char == "*" and self.expectFlag == 0:
            # we're dereferencing a pointer, so we need to handle this differently than a normal variable assignment
            self.state = 16

        elif char == " " and self.expectFlag == 1:
            # we read a space, so we evaluate what the math formula holds thus far.

            if self.mathFormula in self.methodList:
                # if we have a function call for a variable assignment, we jump to state 8 which deals with functions
                self.functionCall = self.mathFormula
                self.state = 8
            else:
                # otherwise, the parentheses is just part of a normal math expression
                self.mathFormula += char

        elif char == ";":
            # End of our math statement. We may begin the evaluation and assign the result to the current variable
            output = self.evaluateMathExpression(output)

            if self.currentVar in self.methodList[self.currentMethod]:
                # The variable is an argument passed into the function. We use the stack pointer to fetch its
                # location before writing the value.
                output += "    MOV $A2 $S2\n"
                output += ("    ADD #" + str(self.methodList[self.currentMethod][self.currentVar][1] * 4)
                             + " $A2\n")
                output += "    MEMW [4] $A $A2\n"

            else:
                # The variable is local, so we just write the result to its memory location from the local list.
                output += ("    MEMW [4] $A #" + str(self.varLocation[self.currentVar]) + "\n")

            # now we reset everything
            self.state = 5
            self.resetGlobalValues("11101000000000")

        else:
            # if we don't read anything else of interest, we simply append the character to the math formula string
            self.mathFormula += char
            self.expectFlag = 1

        return output

    def parseFunctionCall(self, char, output):
        """
        This deals with a function call. This may be on its own line or part of a variable assignment.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # whitespace or newline before any relevant tokens are read
            pass

        elif char == "(" and self.expectFlag == 0:
            # this is in case we haven't read the opening parentheses of a function call yet.
            self.expectFlag = 1

        elif self.expectFlag == 1:
            # here we read our opening parentheses, so we read whitespace until we get our first char for an argument
            if char in IGNORE_CHARS:
                pass
            else:
                self.functionArg += char
                self.expectFlag = 2

        elif self.expectFlag == 2:
            # Here we read the argument name. If we read a space, we wait for appropriate token.
            # Tokens ("," and ")") may show up without spaces, so we handle that here too
            if char == ",":
                if self.functionArg in self.varList:
                    output += ("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")

                elif re.match(ARRAY_PATTERN, self.functionArg):
                    # variable is an array index
                    operands = self.parseArrayPattern()
                    output += ("    PUSH #" + str(self.varLocation[operands[0]] + int(operands[1]) * 4) + "\n")

                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))

                self.expectFlag = 1
                self.resetGlobalValues("00000001000000")
                self.argCount += 1

            elif char in IGNORE_CHARS:
                self.expectFlag = 3

            elif char == ")":
                # we're done reading arguments for the function. Now we expect to read ";" to end the statement
                if self.functionArg in self.varList:
                    # must be a valid variable to pass into function
                    output += ("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")

                elif re.match(ARRAY_PATTERN, self.functionArg):
                    # variable is an array index
                    operands = self.parseArrayPattern()
                    output += ("    PUSH #" + str(self.varLocation[operands[0]] + int(operands[1]) * 4) + "\n")

                else:
                    # variable wasn't declared or isn't valid
                    raise ValueError("Invalid variable at line {}".format(self.lineno))
                self.expectFlag = 4
                self.argCount += 1

            else:
                # append char to the current argument being passed into the function
                self.functionArg += char

        elif self.expectFlag == 3:
            # We fully read the argument name, now we wait for valid token
            if char == ",":
                # here we're notified that other variables will be read.
                if self.functionArg in self.varList:
                    output += ("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))

                self.expectFlag = 1
                self.resetGlobalValues("00000001000000")
                self.argCount += 1

            elif char in IGNORE_CHARS:
                # we can keep ignoring whitespace/new line until we read a correct token
                pass

            elif char == ")":
                # end of arguments. we now expect ";" to end the statement
                if self.functionArg in self.varList:
                    output += ("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))
                self.expectFlag = 4
                self.argCount += 1
            else:
                raise ValueError("Error at line {}".format(self.lineno))

        elif self.expectFlag == 4:
            # Here we're done our function call. We need to read ";" to end the statement and write function to output

            if char == ";":
                # we make sure the amount of arguments passed in matches how many are accepted by the method
                if self.argCount == self.methodList[self.functionCall]["totalVars"]:

                    output += ("    CALL " + self.functionCall + "\n")
                    self.state = 5

                    if self.currentVar != "":
                        output += ("    MEMW [4] $A #" + str(self.varLocation[self.currentVar]) + "\n")

                    output += ("    SUB #" + str(self.argCount * 4) + " $S\n")
                    self.resetGlobalValues("10101011000010")

                else:
                    raise ValueError("# of arguments don't match that of function call at line {}".format(self.lineno))

            elif char in IGNORE_CHARS:
                # we can read more whitespace before the semi-colon
                pass

            else:
                # we read something that wasn't whitespace or a semi-colon, invalid statement
                raise ValueError("invalid syntax after function call at line {}".format(self.lineno))

        else:
            # after a valid function call, we don't read an opening parentheses or whitespace. this is invalid syntax
            raise ValueError("Invalid syntax after function call at line {}".format(self.lineno))

        return output

    def parseIfStatement(self, char, output):
        """
        This state will deal with if statements. We begin by evaluating the left hand side and placing the result in
        register C2. Then we evaluate the right hand side and place in register D2. It's important to note that at this
        time, while loops don't support expressions that contain additional parentheses.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # whitespace or newline before anything relevant is read
            pass

        elif char == "(" and self.expectFlag == 0:
            # if we haven't read the opening parentheses for an if statement
            self.expectFlag = 1

        elif self.expectFlag == 1:
            # we're expecting to read a part of the left hand side's expression. if we read an operator, we evaluate
            # the expression and move on to reading the right hand side's expression.

            if char in BOOLEAN_OPERATORS:
                # if we read an operator, we may need to read another operator, so we go to flag 4
                self.ifOperator = char
                self.expectFlag = 4

            else:
                # otherwise we keep appending to our left hand side's math formula string
                self.mathFormula += char

        elif self.expectFlag == 2:
            # here we evaluate the right hand side of an if expression.
            if char == "{":
                # opening curly brace, end of entire expression
                if self.mathFormula == "":
                    # empty expression (e.g. if ( a > ) )
                    raise ValueError("Empty expression in if statement at line {}".format(self.lineno))

                # check the math expression to see if it ends with a closing parentheses (needed for if/while)
                self.checkForClosingParentheses()
                output = self.evaluateMathExpression(output)

                output += "    MOV $A $D2\n"
                output += "    CMP $D2 $C2\n"
                output += ("    JMP " + self.ifOperator + " L" + str(self.ifLabel) + "\n")

                self.labelList.append(" L" + str(self.ifLabel))
                self.ifLabel += 1
                self.state = 5
                self.resetGlobalValues("10001000110000")

                if len(self.binaryList) > 0:
                    output +=("B" + self.binaryList.pop() + ":\n")

            elif char in BINARY_OPERATORS:
                # in this case we've got some more expressions to evaluate.
                self.binaryOperator = char
                self.expectFlag = 3

            else:
                # otherwise, append to the right hand side's math formula string
                self.mathFormula += char

        elif self.expectFlag == 3:
            output = self.evaluateMathExpression(output)
            if char == self.binaryOperator:

                output += "    MOV $A $D2\n"
                output += "    CMP $D2 $C2\n"

                if char == "|":
                    # or binary operator causes the conditional flag to flip, since if true, we can skip immediately
                    self.reverseFlag()
                    output += ("    JMP " + self.ifOperator + " B" + str(self.binaryLabel) + "\n")

                    if self.binaryLabel not in self.binaryList:
                        self.binaryList.append(str(self.binaryLabel))
                        self.binaryLabel += 1
                        self.resetGlobalValues("00001000000000")

                else:
                    output += ("    JMP " + self.ifOperator + " L" + str(self.ifLabel) + "\n")
                    self.resetGlobalValues("00001000000000")
                self.expectFlag = 1

            else:
                raise ValueError("Mismatch in binary operator at line {}".format(self.lineno))

        elif self.expectFlag == 4:
            # here we expect to read another piece of the operator. if not, we just add the char to the RHS's formula
            if char in BOOLEAN_OPERATORS:
                self.ifOperator += char
                temp = ""
            else:
                temp = char

            output = self.evaluateMathExpression(output)
            self.ifOperator = self.convertOperatorToFlags(self.ifOperator)
            self.expectFlag = 2
            self.mathFormula = temp
            output += "    MOV $A $C2\n"

        return output

    def parseWhileLoop(self, char, output):
        """
        This state will deal with while loops. We begin by evaluating the left hand side and placing the result in
        register C2. Then we evaluate the right hand side and place in register D2. When writing the assembly code, we
        do exactly as an if statement; however, at the end of the while loop, we need to have a jump condition to go
        back to the beginning of the loop.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # whitespace or newline before anything relevant is read
            pass

        elif char == "(" and self.expectFlag == 0:
            # if we haven't read the opening parentheses for an if statement
            self.expectFlag = 1

        elif self.expectFlag == 1:
            # we're expecting to read a part of the left hand side's expression. if we read an operator, we evaluate
            # the expression and move on to reading the right hand side's expression.

            if char in BOOLEAN_OPERATORS:
                # if we read an operator, we may need to read another operator, so we go to flag 4
                self.ifOperator = char
                self.expectFlag = 4

            else:
                # otherwise we keep appending to our left hand side's math formula string
                self.mathFormula += char

        elif self.expectFlag == 2:
            # here we evaluate the right hand side of an if expression.
            if char == "{":
                # opening curly brace, end of entire expression
                if self.mathFormula == "":
                    # empty expression (e.g. if ( a > ) )
                    raise ValueError("Empty expression in if statement at line {}".format(self.lineno))

                # check the math expression to see if it ends with a closing parentheses (needed for if/while)
                self.checkForClosingParentheses()
                output = self.evaluateMathExpression(output)

                output += "    MOV $A $D2\n"
                output += "    CMP $D2 $C2\n"
                output += ("    JMP " + self.ifOperator + " L" + str(self.ifLabel) + "\n")

                self.labelList.append(" L" + str(self.ifLabel))
                self.ifLabel += 1
                self.state = 5
                self.resetGlobalValues("10001000110000")

                if len(self.binaryList) > 0:
                    output += ("B" + self.binaryList.pop() + ":\n")

            elif char in BINARY_OPERATORS:
                # in this case we've got some more expressions to evaluate.
                self.binaryOperator = char
                self.expectFlag = 3

            else:
                # otherwise, append to the right hand side's math formula string
                self.mathFormula += char

        elif self.expectFlag == 3:
            output = self.evaluateMathExpression(output)
            if char == self.binaryOperator:

                output += "    MOV $A $D2\n"
                output += "    CMP $D2 $C2\n"

                if char == "|":
                    self.reverseFlag()
                    output += ("    JMP " + self.ifOperator + " B" + str(self.binaryLabel) + "\n")

                    if self.binaryLabel not in self.binaryList:
                        self.binaryList.append(str(self.binaryLabel))
                        self.binaryLabel += 1
                else:
                    output += ("    JMP " + self.ifOperator + " L" + str(self.ifLabel) + "\n")
                self.expectFlag = 1
                self.resetGlobalValues("00001000000000")

            else:
                raise ValueError("Mismatch in binary operator at line {}".format(self.lineno))

        elif self.expectFlag == 4:
            # here we expect to read another piece of the operator. if not, we just add the char to the RHS's formula
            if char in BOOLEAN_OPERATORS:
                self.ifOperator += char
                temp = ""
            else:
                temp = char

            output = self.evaluateMathExpression(output)
            self.ifOperator = self.convertOperatorToFlags(self.ifOperator)
            self.expectFlag = 2
            self.mathFormula = temp
            output += "    MOV $A $C2\n"

        return output

    def parseReturnStatement(self, char, output):
        """
        This state deals with return statements. When returning values, we follow the cdecl calling convention.
        Variables in function calls are pushed onto the stack, and the values returned are placed into register A.
        However, unlike cdecl, we push the arguments onto the stack from left to right, not right to left.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # whitespace or newline before anything relevant is read
            pass

        elif char == ";":
            # End of our math statement.
            output = self.evaluateMathExpression(output)
            self.state = 5
            self.resetGlobalValues("10001000000000")
            if self.nestedFlag > 0 or self.currentMethod != "main":
                # we don't need a return statement if it's the end of the main method
                output += "    RET\n"

        else:
            # we continue to append the chars to our math formula for the return statement
            self.expectFlag = 1
            self.mathFormula += char

        return output

    def parseArrayDeclaration(self, char, output):
        """
        This state handles the declaration of an array. We check to see if any character before closing bracket "]"
        is a valid integer for the size of the array. We also verify if there is a value assignment following the array
        declaration.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if self.expectFlag == 0:
            # we expect to read the array's size until we read "]"

            if char != "]":
                # if the character read isn't a closing bracket, we assume it's part of the size
                try:
                    int(char)
                except ValueError as e:
                    raise ValueError("Array size declaration invalid at line {}".format(self.lineno))
                self.arrayLength += char

            else:
                # otherwise, we read "]" and we're ready to prepare the newly declared array
                if self.arrayLength is not None:
                    self.arrayList[self.currentVar] = int(self.arrayLength)
                    self.varLocation[self.currentVar] = self.memoryLocation
                    self.memoryLocation += int(self.arrayLength) * 4
                    self.resetGlobalValues("00000000001000")
                    self.expectFlag = 1
                else:
                    # we have a case where nothing was put in the brackets, ex: "int a[];"
                    raise ValueError("Empty array size at line {}".format(self.lineno))

        elif self.expectFlag == 1:
            # at this point, we're either done with the array declaration, or we're assigning values to the array

            if char == " ":
                # we can still accept empty spaces before a key token is read
                pass

            elif char == "=":
                # we're assigning values to the array, so we move on to the next section
                self.expectFlag = 2

            elif char == ";":
                # we're done with the declaration.
                self.state = 5
                self.resetGlobalValues("11100000000000")

            else:
                # we read a character that's not a semicolon, equal sign, or space
                raise ValueError("Invalid syntax at line {}".format(self.lineno))

        elif self.expectFlag == 2:
            # array has an assignment immediately after its declaration

            if char == " ":
                # we can still accept empty spaces before a key token is read
                pass

            elif char == "{":
                # initial array declarations can only be assigned values in its entirety. ex: int a[2] = {1,2,3};
                self.expectFlag = 3

            else:
                # we can only accept an opening curly brace at this point
                raise ValueError("Invalid array value assignment at line {}".format(self.lineno))

        elif self.expectFlag == 3:
            # Here we're declaring the variables inside our array
            if char == "}":
                self.expectFlag = 4

            else:
                # otherwise we just append the character to the math formula
                self.mathFormula += char

        elif self.expectFlag == 4:
            # here we're just waiting for a semi-colon since nothing else can be added at this point

            if char == " ":
                # we can still accept empty spaces before a key token is read
                pass

            elif char == ";":
                # end of statement, math expression is done, everything is set to go back to state 5.
                output = self.assignArrayValues(output)
                self.state = 5
                self.resetGlobalValues("11101000001000")

            else:
                # we read something other than a semi-colon or a space
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        return output

    def assignValueAtArrayIndex(self, char, output):
        """
        This state deals with assigning a value to a specific array index. Here we assume the array has already been
        declared, and we're simply assigning a value to a specific index.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if self.expectFlag == 0:
            # here we expect to read the index of the array

            if char == "]":
                # we're done reading characters for the index, so we check if it's a valid integer and within bounds

                try:
                    int(self.arrayLength)
                except ValueError as e:
                    raise ValueError("Invalid array index at line {}".format(self.lineno))

                if int(self.arrayLength) > int(self.arrayList[self.currentVar] - 1) or int(self.arrayLength) < 0:
                    raise ValueError("Array index out of bounds at line {}".format(self.lineno))

                self.expectFlag = 1

            else:
                # otherwise, we're still reading the index
                self.arrayLength += char

        elif self.expectFlag == 1:

            if char == " ":
                # we can still accept empty spaces before a key token is read
                pass
            elif char == "=":
                self.expectFlag = 3
            else:
                raise ValueError("Syntax error at line {}".format(self.lineno))

        elif self.expectFlag == 3:
            # here we keep reading input for the math formula until the end of the input ";"

            if char == ";":
                # we're done reading the math expression, so we call the mathparser functions and reset
                output = self.evaluateMathExpression(output)
                output += ("    MEMW [4] $A #" + str(self.varLocation[self.currentVar] + int(self.arrayLength) * 4) +
                           "\n")
                self.state = 5
                self.resetGlobalValues("11101100001000")

            else:
                # otherwise the char gets added to the math formula
                self.mathFormula += char

        return output

    def parsePointerInitialization(self, char, output):
        """
        This method deals with initialization of pointers. Pointer variable can only be assigned a single variable,
        with the & prefix. The variable must already be declared, and cannot be paired with any other operand.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if self.expectFlag == 0 and char == " ":
            # we can still accept empty spaces before a key token is read
            pass

        elif self.expectFlag == 0:
            # here we read the first non-space character
            self.currentVar += char
            self.expectFlag = 1

        elif self.expectFlag == 1:
            # after reading the first non-space character, we read the name of the variable for the pointer

            if char in IGNORE_CHARS:
                # we can still accept empty spaces before a key token is read
                self.expectFlag = 2
                self.validName(self.currentVar)

            elif char == "=":
                # equals sign means we're assigning a value to the pointer (memory address)
                self.state = 15
                self.validName(self.currentVar)
                self.pointerList.append(self.currentVar)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += 4

            elif char == ";":
                # end of declaration, we simple allocate memory location without giving a value
                self.state = 5
                self.pointerList.append(self.currentVar)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += 4
                self.resetGlobalValues("11100000000000")

            else:
                # otherwise we assume we're still reading the name of the variable being declared
                self.currentVar += char

        elif self.expectFlag == 2:
            # We read a space, so we expect either another space or newline, or a valid operator

            if char in IGNORE_CHARS:
                # we can still accept empty spaces before a key token is read
                pass

            elif char == "=":
                # equals sign means we're assigning a value to the pointer (memory address)
                self.state = 15
                self.pointerList.append(self.currentVar)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += 4
                self.resetGlobalValues("10000000000000")

            elif char == ";":
                # end of declaration, we simple allocate memory location without giving a value
                self.state = 5
                self.pointerList.append(self.currentVar)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += 4
                self.resetGlobalValues("11100000000000")

            else:
                # we read something other than "=" or ";" in this context, which would be incorrect
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        return output

    def assignPointerValue(self, char, output):
        """
        This method assigns a value to a pointer. The value must be a valid memory address (and must thus be referenced
        by a valid variable using the & character).
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if self.expectFlag == 0:
            # we can read spaces or new line chars, but the first non-empty character MUST be an ampersand "&"

            if char in IGNORE_CHARS:
                pass

            elif char == "&":
                self.expectFlag = 1

            else:
                # We read something other than space, new line, or ampersand
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        elif self.expectFlag == 1:
            # here we read the name of the variable whose address we're assigning to the pointer

            if char in IGNORE_CHARS:
                # if we read a space, we evaluate the variable name to see if it exists

                if self.mathFormula in self.varList:
                    # variable is in regular variable list, we're good and can move on to flag 2
                    pass

                elif self.mathFormula in self.methodList[self.currentMethod]:
                    # variable is argument passed into current method, so variable is valid
                    pass

                elif re.match(ARRAY_PATTERN, self.functionArg):
                    # variable is an array index. we parse the variable name and index to determine if they're valid
                    operands = self.parseArrayPattern()

                    if operands[0] not in self.arrayList:
                        raise ValueError("Invalid array variable at line {}".format(self.lineno))
                    if operands[1] > self.arrayList[self.currentVar] - 1:
                        raise ValueError("Array index out of bounds at line {}".format(self.lineno))

                else:
                    # variable didn't match any pattern or was not present in any valid list
                    raise ValueError("Invalid variable name at line {}".format(self.lineno))

                self.expectFlag = 2

            elif char == ";":
                # we immediately read the end of the statement, so we evaluate the variable and write the correct output

                if self.mathFormula in self.varList:
                    # variable is in regular list, so we assign its memory location to the pointer
                    output += ("    MEMW [4] #" + str(self.varLocation[self.mathFormula]) + " #" +
                                 str(self.varLocation[self.currentVar]) + "\n")

                elif self.mathFormula in self.methodList[self.currentMethod]:
                    # variable is passed in as argument, we just write the pointer register's value at the right index
                    output += "    MOV $A2 $S2\n"
                    output += ("    ADD #" + str(self.methodList[self.currentMethod][self.currentVar][1] * 4)
                                 + " $A2\n")
                    output += ("    MEMW [4] $A2 #" + str(self.varLocation[self.currentVar]) + "\n")

                elif re.match(ARRAY_PATTERN, self.functionArg):
                    # variable is an array index, we get the memory location at index 0 and add the correct offset
                    operands = self.parseArrayPattern()
                    output += ("    #" + str(self.varLocation[self.mathFormula] + operands[1] * 4) + " #" +
                               str(self.varLocation[self.currentVar]) + "\n")

                else:
                    raise ValueError("Invalid variable name at line {}".format(self.lineno))
                self.state = 5
                self.resetGlobalValues("111010000000000")

            else:
                self.mathFormula += char

        elif self.expectFlag == 2:
            if char in IGNORE_CHARS:
                pass
            elif char == ";":
                if self.mathFormula in self.varList:
                    # variable is in regular list, so we assign its memory location to the pointer
                    output += ("    MEMW [4] #" + str(self.varLocation[self.mathFormula]) + " #" +
                                 str(self.varLocation[self.currentVar] + "\n"))

                elif self.mathFormula in self.methodList[self.currentMethod]:
                    # variable is passed in as argument, we just write the pointer register's value at the right index
                    output += "    MOV $A2 $S2\n"
                    output += ("    ADD #" + str(self.methodList[self.currentMethod][self.currentVar][1] * 4) +
                               " $A2\n")
                    output += ("    MEMW [4] $A2 #" + str(self.varLocation[self.currentVar]) + "\n")

                elif re.match(ARRAY_PATTERN, self.functionArg):
                    # variable is an array index, we get the memory location at index 0 and add the correct offset
                    operands = self.parseArrayPattern()
                    output += ("    #" + str(self.varLocation[self.mathFormula] + operands[1] * 4) + " #" +
                                 str(self.varLocation[self.currentVar]) + "\n")

                else:
                    # we already did the check in flag 1, so this technically shouldn't execute and something went wrong
                    raise ValueError("Invalid variable name at line {}".format(self.lineno))

                self.state = 5
                self.resetGlobalValues("111010000000000")

            else:
                # we're expecting the end of the statement ";", so anything else in invalid
                raise ValueError("Syntax error at line {}".format(self.lineno))

        return output

    def dereferencePointer(self, char, output):
        """
        This state deals with dereferencing a pointer. Any variable can be assigned a pointer dereference, but it must
        stand alone as an operand. The memory location stored in the pointer must be a valid variable. It should be
        noted that pointers cannot dereference other pointers.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # we can still accept empty spaces before a key token is read
            pass

        elif self.expectFlag == 0:
            # we read our first non space character, so we append to mathformula to determine our variable name
            self.mathFormula += char
            self.expectFlag = 1

        elif self.expectFlag == 1:
            # here we read the rest of the variable name until we reach a space character or semi colon

            if char == " ":
                # we read a space, so we're no longer reading variable name
                self.expectFlag = 2

            elif char == ";":
                # end of statement, the variable must be a valid pointer. We grab the value at the memory location
                # stored inside the pointer

                if self.mathFormula not in self.pointerList:
                    raise ValueError("Invalid pointer variable at line {}".format(self.lineno))
                output += ("    MEMR [4] #" + str(self.varLocation[self.mathFormula]) + " $A\n")
                output += "    MEMR [4] $A $B\n"
                output += ("    MEMW [4] $B #" + str(self.varLocation[self.currentVar]) + "\n")

                self.state = 5
                self.resetGlobalValues("111010000000000")

            else:
                # otherwise, we're still reading the pointer variable's name
                self.mathFormula += char

        elif self.expectFlag == 2:
            # at this point, we can keep reading spaces but the next non-space character must be a semi-colon

            if char in IGNORE_CHARS:
                pass

            elif char == ";":
                # end of statement, the variable must be a valid pointer. We grab the value at the memory location
                # stored inside the pointer

                if self.mathFormula not in self.pointerList:
                    raise ValueError("Invalid pointer variable at line {}".format(self.lineno))
                output += ("    MEMR [4] #" + str(self.varLocation[self.mathFormula]) + " $A\n")
                output += "    MEMR [4] $A $B\n"
                output += ("    MEMW [4] $B #" + str(self.varLocation[self.currentVar]) + "\n")

                self.state = 5
                self.resetGlobalValues("111010000000000")

            else:
                # we didn't read a semi colon or space character, so the syntax is incorrect
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        return output

    def assignImmediateValueToPointer(self, char, output):
        """
        This method allows you to assign an immediate value to a pointer. You're risking accessing an invalid memory
        location by doing this, however. The format should be "*var = int"
        :param char:
        :param output:
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # we can still accept empty spaces before a key token is read
            pass

        elif self.expectFlag == 0:
            # first non-space character is read, so we start reading the variable's name
            self.currentVar += char
            self.expectFlag = 1

        elif self.expectFlag == 1:
            # here we read the pointer variable's name

            if char == "=":
                # assignment operator means we're done reading the name. We check if it's in the list
                self.expectFlag = 3
                if self.currentVar not in self.pointerList:
                    raise ValueError("Invalid pointer variable at line {}".format(self.lineno))

            elif char in IGNORE_CHARS:
                # we read a space character, so we're done reading the variable name
                self.expectFlag = 2

            else:
                # otherwise we keep reading the variable's name
                self.currentVar += char

        elif self.expectFlag == 2:
            # we expect to read an assignment operator, since no other operations are valid for *pointer

            if char in IGNORE_CHARS:
                # we can still read space characters
                pass

            elif char == "=":
                # assignment operator means we're done reading the name. We check if it's in the list
                self.expectFlag = 3
                if self.currentVar not in self.pointerList:
                    raise ValueError("Invalid pointer variable at line {}".format(self.lineno))

            else:
                # there are no other valid characters we can read, so the syntax is incorrect
                raise ValueError("Invalid syntax at line {}".format(self.lineno))

        elif self.expectFlag == 3:
            # here we read the value that will be assigned to the pointer

            if char == ";":
                # end of statement, we evaluate the mathformula and assign the value to the pointer variable

                if len(self.mathFormula) == 0:
                    # can't have an empty expression (ex: *pointer = ;)
                    raise ValueError("Empty operand at line {}".format(self.lineno))

                output = self.evaluateMathExpression(output)
                output += ("    MEMW [4] $A #" + str(self.varLocation[self.currentVar]) + "\n")

                self.state = 5
                self.resetGlobalValues("111010000000000")

            else:
                # otherwise we keep appending to our math formula
                self.mathFormula += char

        return output

    def parseCharVariable(self, char, output):
        """
        This state takes in the name of the char variable, then appends it to the char list.
        :param char:
        :param output:
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            pass
        elif self.expectFlag == 0:
            self.currentVar += char
            self.expectFlag = 1

        elif self.expectFlag == 1:

            if char in IGNORE_CHARS:
                self.expectFlag = 2

            elif char == ";":
                self.charList.append(self.currentVar)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += 4
                self.state = 5
                self.resetGlobalValues("111000000000000")

            elif char == "=":
                self.charList.append(self.currentVar)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += 4
                self.state = 19
                self.resetGlobalValues("100000000000000")

            else:
                self.currentVar += char

        elif self.expectFlag == 2:
            if char in IGNORE_CHARS:
                pass

            elif char == ";":
                self.charList.append(self.currentVar)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += 4
                self.state = 5
                self.resetGlobalValues("111000000000000")

            elif char == "=":
                self.charList.append(self.currentVar)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += 4
                self.state = 19
                self.resetGlobalValues("100000000000000")

            else:
                raise ValueError("Invalid syntax at line {}".format(self.lineno))

        return output

    def assignCharValue(self, char, output):
        """
        This method accepts a value for a char variable. It should be noted that chars will always be a single
        character. The char must be surrounded by either single quotes or double quotes. These must match, meaning we
        can't use a single quote and double quote at the same time.
        :param char:
        :param output:
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            pass

        elif self.expectFlag == 0:
            # here we read the value expected for the char variable. This must be a single or double quote
            self.expectFlag = 1
            if char == SINGLE_QUOTE:
                self.quoteFlag = SINGLE_QUOTE
            elif char == DOUBLE_QUOTE:
                self.quoteFlag = DOUBLE_QUOTE
            else:
                raise ValueError("Incorrect syntax at line {}. Char should begin with \" or \'".format(self.lineno))

        elif self.expectFlag == 1:
            if char in IGNORE_CHARS:
                pass
            else:
                self.mathFormula = char
                self.expectFlag = 2

        elif self.expectFlag == 2:

            if char == SINGLE_QUOTE and self.quoteFlag == SINGLE_QUOTE:
                self.expectFlag = 3
            elif char == DOUBLE_QUOTE and self.quoteFlag == DOUBLE_QUOTE:
                self.expectFlag = 3
            else:
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        elif self.expectFlag == 3:

            if char in IGNORE_CHARS:
                pass
            elif char == ";":
                output += ("    MEMW [4] #" + str(ord(self.mathFormula)) + " #" +
                           str(self.varLocation[self.currentVar]) + "\n")
                self.state = 5
                self.resetGlobalValues("111010000000100")
            else:
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        elif self.expectFlag == 4:
            if char in IGNORE_CHARS:
                pass
            elif char == "=":
                self.expectFlag = 0
            else:
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        return output

    def validName(self, name):
        """
        Verifies whether the variable's name contains only acceptable characters (A-Z, $, _, #)
        :param name: str, the variable name that we're verifying
        :return:
        """

        for char in name:
            if char not in ALLOWED_CHARS:
                raise ValueError("Illegal variable name declaration at line {}".format(self.lineno))

    def verifyVariable(self):
        """
        Method checks whether the variable is already present in the list. If so, we raise an error since we can't have
        duplicate variable names. Otherwise, we add it to the list, assign it a memory location, increment the memory
        location counter, and increase the total variable count. This is used for state 6 to clean up the code
        :return:
        """

        self.validName(self.currentVar)

        if (self.currentVar not in self.varList) and self.currentVar not in self.methodList[self.currentMethod]:
            self.varList.append(self.currentVar)
            self.varLocation[self.currentVar] = self.memoryLocation
            self.memoryLocation += 4
            self.variableCount += 1
        else:
            # can't have duplicate variable names
            raise ValueError("Duplicate variable declaration at line {}".format(self.lineno))

    def addVariableToMethodDict(self):
        """
        When called, we assume we have a new variable declaration to add to our method's dict of variables. The info
        should already be stored in the static variables, so we don't need to pass in any arguments. We take this
        opportunity to reset the values for current data type and current variable name, and we increase the argcount
        counter. Argcount holds the cumulative number of the variable being evaluated. In the method's dict, we also
        store in which order of appearance the variables are read. This is useful for our math parser, among other
        tools, to determine how far the S2 pointer must travel to reach that specific variable.
        :return:
        """

        self.methodList[self.currentMethod][self.currentVar] = (self.currentType, self.argCount)
        self.argCount += 1
        self.resetGlobalValues("011000000000000")

    def convertOperatorToFlags(self, char):
        """
        This converts an operator to the appropriate flags for a JMP instruction
        :param char: char, our operator (<, >, =) to convert to a JMP flag
        :return:
        """

        if char == "<":
            flag = "<HE>"
        elif char == "<=":
            flag = "<H>"
        elif char == "==":
            flag = "<LH>"
        elif char == ">":
            flag = "<LE>"
        elif char == ">=":
            flag = "<L>"
        else:
            raise ValueError("Incorrect operator for if statement.")

        return flag

    def assignArrayValues(self, output):
        """
        This method takes in a list of values to populate an array. These values are already kept in our global
        mathFormula string variable.
        :return:
        """

        list = self.mathFormula.split(",")
        startingLocation = self.varLocation[self.currentVar]

        if len(list) != self.arrayList[self.currentVar]:
            raise ValueError("Incorrect number of values for array assignment at line {}".format(self.lineno))

        for element in list:
            try:
                int(element)
            except ValueError as e:
                raise ValueError("Invalid value for array assignment at line {}".format(self.lineno))

            output += ("    MEMW [4] #" + str(element) + " #" + str(startingLocation) + "\n")
            startingLocation += 4

        return output

    def checkForClosingParentheses(self):
        """
        This method checks if the math expression ends with a closing parentheses. This is necessary for if statements
        and while loops.
        :return:
        """

        found = False

        length = len(self.mathFormula) - 1
        while not found and length > 0:

            if self.mathFormula[length] in IGNORE_CHARS:
                # reading in reverse, we can still read spaces until the first relevant token
                pass
            elif self.mathFormula[length] == ")":
                # closing parentheses means this expression may be valid. function has served its purpose and we break
                found = True
                self.mathFormula = self.mathFormula[0:length]
            else:
                # we read something that is not a closing parentheses, thus the expression is not valid
                raise ValueError("Missing closing parentheses in statement at line {}".format(self.lineno))
            length -= 1

    def reverseFlag(self):
        """
        Function takes a flag for || binary operator and reverses the logic. This is needed because if an OR binary
        operation is true, we can just jump straight to the expression within an if statement or while loop.
        :return:
        """

        if self.ifOperator == "<HE>":
            self.ifOperator = "<L>"
        elif self.ifOperator == "<H>":
            self.ifOperator = "<LE>"
        elif self.ifOperator == "<LE>":
            self.ifOperator = "<H>"
        elif self.ifOperator == "<LH>":
            self.ifOperator = "<E>"
        elif self.ifOperator == "<L>":
            self.ifOperator = "<HE>"

    def resetGlobalValues(self, binaryValue):
        """
        Due to the large number of temporary variables, this method acts as a global "reset" method that handles every
        class variable necessary. The binary number passed in represents whether or not each variable needs to be reset.
        For example, 1010001 would mean the first, third, and last variable require a reset. This is used to simplify
        the compiler's code, since many variables need resets at different intervals.
        :param binaryValue:
        :return:
        """

        if binaryValue[0] == "1":
            self.expectFlag = 0

        if binaryValue[1] == "1":
            self.currentType = ""

        if binaryValue[2] == "1":
            self.currentVar = ""

        if binaryValue[3] == "1":
            self.currentMethod = ""

        if binaryValue[4] == "1":
            self.mathFormula = ""

        if binaryValue[5] == "1":
            self.identifier = ""

        if binaryValue[6] == "1":
            self.functionCall = ""

        if binaryValue[7] == "1":
            self.functionArg = ""

        if binaryValue[8] == "1":
            self.ifOperator = ""

        if binaryValue[9] == "1":
            self.binaryOperator = ""

        if binaryValue[10] == "1":
            self.arrayLength = ""

        if binaryValue[11] == "1":
            self.quoteFlag = ""

        if binaryValue[11] == "1":
            self.argCount = 0

        if binaryValue[11] == "1":
            self.variableCount = 0

    def evaluateMathExpression(self, output):
        """
        This is a helper method that removes redundancy from the compiler code. When we want to evaluate a math
        expression, the same steps are followed universally. We tokenize the string into individual arguments,
        parse the tokens from infix to postfix, then we evaluate the postfix.
        :return:
        """

        tokens = tokenize(self.mathFormula)
        postfix = infixToPostfix(tokens)
        output += evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod],
                                 self.arrayList, output, self.lineno)

        return output

    def parseArrayPattern(self):
        """
        This is a helper method that removes redundancy from the compiler code. When we're looking to match a pattern
        for an array value at a specific index, the same steps are followed universally. We search for an array pattern
        (a value followed by a closing square bracket, i.e. "45]"), and extract the value which will be the array's
        desired index.
        :return:
        """

        match = re.search(ARRAY_PATTERN, self.functionArg)
        operands = match.group(0)
        operands = operands.split("[")
        operands[1] = operands[1].replace("]", "")

        return operands
