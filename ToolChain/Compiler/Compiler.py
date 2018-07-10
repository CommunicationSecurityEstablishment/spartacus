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
                                         ALLOWED_CHARS

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

    state = 0                    # "States" are used to determine our next path for processing the C file
    currentVar = ""              # Name of variable being evaluated
    currentType = ""             # Current data type being read, before method/variable declaration
    currentMethod = ""           # String containing the current method being evaluated
    expectFlag = 0               # Used to control what input we expect next
    mathFormula = ""             # Will contain our fully assembled math expressions for variable assignments
    memoryLocation = 0x40000000  # Memory location for local variables.
    varList = []                 # Contains a list of variable names
    varLocation = {}             # Contains the memory location for all variables
    methodList = {}              # List of methods, along with their return type, variables (and types), and # of args
    argCount = 0                 # Used for number of operands in math expression, args in function calls, etc.
    variableCount = 0            # Number of variables declared in current function.
    identifier = ""              # Used to determine first token of a line
    functionCall = ""            # Name of the function we're calling when doing variable assignment
    whileFlag = 0                # Lets the compiler know if we're in a while loop
    ifOperator = ""              # Holds the logical operator between two sides of an if boolean expression
    nestedFlag = 0               # Lets the compiler know if we're in an if statement
    ifLabel = 0                  # For jump instructions, we need a unique label for every if statement
    lineno = 0                   # Line number for printing error messages
    functionArg = ""             # Used to read a function call's arguments
    whileLabel = 0               # For while loops, we need a unique label
    labelList = []               # List containing names of labels for if/while jumps
    whileList = []               # List containing the names of while loops
    arrayList = {}               # Dict containing variables that are arrays
    arrayLength = ""             # Length of current array variable being evaluated

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
            self.lineno += 1
            for x in line:
                self.parse(x, output)

        output.write("end:\n")

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
            self.state0(char, output)

        elif self.state == 1:
            self.state1(char, output)

        elif self.state == 2:
            self.state2(char, output)

        elif self.state == 3:
            self.state3(char, output)

        elif self.state == 4:
            self.state4(char, output)

        elif self.state == 5:
            self.state5(char, output)

        elif self.state == 6:
            self.state6(char, output)

        elif self.state == 7:
            self.state7(char, output)

        elif self.state == 8:
            self.state8(char, output)

        elif self.state == 9:
            self.state9(char, output)

        elif self.state == 10:
            self.state10(char, output)

        elif self.state == 11:
            self.state11(char, output)

        elif self.state == 12:
            self.state12(char, output)

        elif self.state == 13:
            self.state13(char, output)

    def state0(self, char, output):
        """
        First step in parsing data. At this step, we begin to read the method header. We expect to read the return data
        type.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            pass
        elif char in IGNORE_CHARS and self.expectFlag == 1:
            if self.currentType in ACCEPTED_TYPES:
                self.state = 1
                self.expectFlag = 0
            else:
                raise ValueError("Incorrect return type for method declaration at line {}.".format(self.lineno))
        else:
            self.currentType += char
            self.expectFlag = 1

    def state1(self, char, output):
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
            self.currentVar = ""
            self.currentType = ""
            self.state = 2

        elif char == "(":
            # We read the opening parentheses after the method name, no need to check for it later
            self.methodList[self.currentMethod] = {"retType": self.currentType}
            output.write(self.currentMethod + ":\n")
            self.currentVar = ""
            self.currentType = ""
            self.state = 2
            self.expectFlag = 0

        else:
            self.currentMethod += char
            self.expectFlag = 1

    def state2(self, char, output):
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
            output.write(self.currentMethod + ":\n")
            if self.currentMethod == "main":
                output.write("    MOV end $S\n")

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

    def state3(self, char, output):
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

    def state4(self, char, output):
        """
        In this state, we've read all the arguments of a method declaration. Now we simply expect to read the opening
        curly brace "{" to signify the opening body of the method. Here, we also write the appropriate casm instructions
        to the output file. The stack pointer gets moved to "end" if it's the main method, and the S2 pointer must point
        to the first argument pushed to the stack (if any).
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
                output.write("    MOV end $S\n")
            else:
                if self.argCount > 0:
                    output.write("    MOV $S $S2\n")
                    output.write("    SUB #" + str(self.argCount * 4 + 4) + " $S2\n")

            self.argCount = 0

        else:
            raise ValueError("Syntax error, expecting \"{\", got {}".format(char))

    def state5(self, char, output):
        """
        Initial evaluation of a line within the body of a method. We read the input and concatenate to identifier
        string. Once we read a key token we check various cases to see where we need to go with out identifier:
        space:
            -valid data type
            -if statement (we later check for opening parentheses)
            -variable (already declared)
            -while loop
            -return statement
        "=":
            -variable assignment only
        "(":
            -if statement
            -while loop
            -function call (e.g. add(a,b))
        "}"
            -end of method, loop, or if statement

        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if char in IGNORE_CHARS and self.expectFlag == 0:
            # whitespace or newline characters when not expecting a particular input
            pass

        elif char == " " and self.expectFlag == 1:
            # we read a space, now we evaluate our indicator to determine what sort of operation we're dealing with
            if self.identifier == "if":
                # identifier is an if statement
                self.state = 9
                self.identifier = ""
                self.expectFlag = 0
                self.nestedFlag += 1

            elif self.identifier == "while":
                # identifier is a while loop indicator
                output.write("LOOP" + str(self.whileLabel) + ":\n")
                self.whileList.append("LOOP" + str(self.whileLabel))
                self.state = 10
                self.whileLabel += 1
                self.nestedFlag += 1
                self.whileFlag += 1
                self.identifier = ""
                self.expectFlag = 0

            elif self.identifier == "return":
                # identifier is a return statement
                self.expectFlag = 0
                self.state = 11
                self.identifier = ""

            elif (self.identifier in self.varList) or self.identifier in self.methodList[self.currentMethod]:
                # the identifier is a variable that has already been declared
                self.currentVar = self.identifier
                self.identifier = ""
                self.state = 6
                self.expectFlag = 2

            elif self.identifier in ACCEPTED_TYPES:
                # identifier is a data type, new variable declaration
                self.currentType = self.identifier
                self.identifier = ""
                self.state = 6
                self.expectFlag = 0

            elif self.identifier in self.methodList:
                # identifier is a function call
                self.expectFlag = 0
                self.state = 8
                self.functionCall = self.identifier
                self.identifier = ""

            else:
                # identifier was not valid
                raise ValueError("Error at line {}".format(self.lineno))

        elif char == "=" and self.expectFlag == 1:
            # here we have a variable assignment. Variable must be already declared in this case
            if (self.identifier in self.varList) or self.identifier in self.methodList[self.currentMethod]:
                self.expectFlag = 0
                self.state = 7
            else:
                raise ValueError("Invalid assignment at line {}: must be valid variable".format(self.lineno))

        elif char == "[" and self.expectFlag == 1:
            # this implies an already declared array
            self.expectFlag = 0
            self.identifier = ""
            self.state = 13

        elif char == "(" and self.expectFlag == 1:
            # immediately after the identifier, we read an opening parentheses. Here we cover all possible cases
            if self.identifier in self.methodList:
                # identifier is a function call
                self.state = 8
                self.functionCall = self.identifier
                self.identifier = ""

            elif self.identifier == "if":
                # identifier is an if statement
                self.state = 9
                self.identifier = ""
                self.nestedFlag += 1

            elif self.identifier == "while":
                # identifier is a while loop indicator
                output.write("LOOP" + str(self.whileLabel) + ":\n")
                self.whileList.append("LOOP" + str(self.whileLabel))
                self.state = 10
                self.whileLabel += 1
                self.whileFlag += 1
                self.nestedFlag += 1
                self.identifier = ""

            else:
                # identifier was not valid
                raise ValueError("Error at line {}".format(self.lineno))

        elif char == "}":
            # end of method, if statement, or while loop
            if self.nestedFlag == 0:
                # if we aren't in any while/if statements, this is the end of our method
                self.state = 0
                self.currentMethod = ""
                self.argCount = 0
                self.currentVar = ""
                self.currentType = ""
                self.varList.clear()
                self.varLocation.clear()

            else:
                # otherwise, we print the appropriate instructions to end the while loop or if statement
                self.nestedFlag -= 1
                if self.whileFlag > 0:
                    self.whileFlag -= 1
                    output.write("    JMP <> " + self.whileList.pop() + "\n")

                output.write(self.labelList.pop() + ":\n")

        else:
            # append the character to the identifier string is nothing else of interest was read.
            self.identifier += char
            self.expectFlag = 1

    def state6(self, char, output):
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

        elif char == " " and self.expectFlag == 1:
            # we have the variable name, now we move to the next phase to determine appropriate action
            self.expectFlag = 2

        elif char == "=" and self.expectFlag == 1:
            # we have the variable name, and we see that an assignment will happen
            self.verifyVariable()
            self.state = 7
            self.expectFlag = 0

        elif char == ";" and self.expectFlag == 1:
            # end of variable declaration. we assign its memory location and add it to the variable list
            self.verifyVariable()
            self.currentVar = ""
            self.currentType = ""
            self.state = 5
            self.expectFlag = 0

        elif char == "[" and self.expectFlag == 1:
            # Here we're ready to declare a new array
            self.validName(self.currentVar)
            self.state = 12
            self.expectFlag = 0

        elif self.expectFlag == 2:
            # We reach this step if we have the variable name and we read at least one space
            if char in IGNORE_CHARS:
                # we may keep reading spaces/ new line until we reach a relevant token
                pass

            elif char == "=":
                # variable assignment. if the variable was not in the list, we add it
                if (self.currentVar not in self.varList) and self.currentVar not in self.methodList[self.currentMethod]:
                    self.varList.append(self.currentVar)
                    self.varLocation[self.currentVar] = self.memoryLocation
                    self.memoryLocation += 4
                    self.variableCount += 1

                self.validName(self.currentVar)
                self.state = 7
                self.expectFlag = 0

            elif char == ";":
                # simple declaration (e.g. int a;), we add it to the variable list and allocate a memory location
                self.verifyVariable()
                self.currentVar = ""
                self.currentType = ""
                self.state = 5
                self.expectFlag = 0

            else:
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

        else:
            # append the character to the current variable's name
            self.currentVar += char
            self.expectFlag = 1

    def state7(self, char, output):
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
            tokens = tokenize(self.mathFormula)
            postfix = infixToPostfix(tokens)
            evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod],
                            self.arrayList, output)

            if self.currentVar in self.methodList[self.currentMethod]:
                # The variable is an argument passed into the function. We use the stack pointer to fetch its
                # location before writing the value.
                output.write("    MOV $A2 $S2\n")
                output.write("    ADD #" + str(self.methodList[self.currentMethod][self.currentVar][1] * 4)
                             + " $A2\n")
                output.write("    MEMW [4] $A $A2\n")

            else:
                # The variable is local, so we just write the result to its memory location from the local list.
                output.write("    MEMW [4] $A #" + str(self.varLocation[self.currentVar]) + "\n")

            # now we reset everything
            self.state = 5
            self.mathFormula = ""
            self.currentType = ""
            self.currentVar = ""
            self.expectFlag = 0

        else:
            # if we don't read anything else of interest, we simply append the character to the math formula string
            self.mathFormula += char
            self.expectFlag = 1

    def state8(self, char, output):
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
                    output.write("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))
                self.expectFlag = 1
                self.functionArg = ""
                self.argCount += 1

            elif char in IGNORE_CHARS:
                self.expectFlag = 3

            elif char == ")":
                # we're done reading arguments for the function. Now we expect to read ";" to end the statement
                if self.functionArg in self.varList:
                    # must be a valid variable to pass into function
                    output.write("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
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
                    output.write("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
                else:
                    raise ValueError("Invalid variable at line {}".format(self.lineno))

                self.expectFlag = 1
                self.functionArg = ""
                self.argCount += 1

            elif char in IGNORE_CHARS:
                # we can keep ignoring whitespace/new line until we read a correct token
                pass
            elif char == ")":
                # end of arguments. we now expect ";" to end the statement
                if self.functionArg in self.varList:
                    output.write("    PUSH #" + str(self.varLocation[self.functionArg]) + "\n")
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

                    output.write("    CALL " + self.functionCall + "\n")
                    self.state = 5

                    if self.currentVar != "":
                        output.write("    MEMW [4] $A #" + str(self.varLocation[self.currentVar]) + "\n")
                    output.write("    SUB #" + str(self.argCount * 4) + " $S\n")
                    self.functionCall = ""
                    self.functionArg = ""
                    self.mathFormula = ""
                    self.argCount = 0
                    self.expectFlag = 0

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

    def state9(self, char, output):
        """
        This state will deal with if statements. We begin by evaluating the left hand side and placing the result in
        register C2. Then we evaluate the right hand side and place in register D2. It's important to note that at this
        time, while loops don't support expressions that contain additional parentheses.
        TODO: figure out how to handle multiple parentheses
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
                if self.mathFormula == "":
                    # empty expression (e.g. if ( a > ) )
                    raise ValueError("Empty expression in if statement at line {}".format(self.lineno))

                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod],
                                self.arrayList, output)
                self.ifOperator = self.convertOperatorToFlags(char)
                self.expectFlag = 2
                self.mathFormula = ""
                output.write("    MOV $A $C2\n")

            else:
                # otherwise we keep appending to our left hand side's math formula string
                self.mathFormula += char

        elif self.expectFlag == 2:
            # here we evaluate the right hand side of an if expression.
            if char == ")":
                # closing parentheses, this indicates the end of our expression
                if self.mathFormula == "":
                    # empty expression (e.g. if ( a > ) )
                    raise ValueError("Empty expression in if statement at line {}".format(self.lineno))

                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod],
                                self.arrayList, output)
                self.expectFlag = 2
                self.mathFormula = ""
                output.write("    MOV $A $D2\n")
                self.expectFlag = 3

            else:
                # otherwise, append to the right hand side's math formula string
                self.mathFormula += char

        elif self.expectFlag == 3:
            # we've finished reading our if statement, now we wait for an opening curly brace

            if char in IGNORE_CHARS:
                # we can still read whitespace or newline chars meanwhile
                pass

            elif char == "{":
                # we have our opening curly brace, we can go back to state 5 and begin evaluating a new line
                output.write("    CMP $D2 $C2\n")
                output.write("    JMP " + self.ifOperator + " L" + str(self.ifLabel) + "\n")
                self.labelList.append(" L" + str(self.ifLabel))
                self.ifLabel += 1
                self.state = 5
                self.expectFlag = 0
                self.mathFormula = ""

            else:
                # we read something other than whitespace or an opening curly brace, this is invalid
                raise ValueError("Syntax error at line {}".format(self.lineno))

    def state10(self, char, output):
        """
        This state will deal with while loops. We begin by evaluating the left hand side and placing the result in
        register C2. Then we evaluate the right hand side and place in register D2. When writing the assembly code, we
        do exactly as an if statement; however, at the end of the while loop, we need to have a jump condition to go
        back to the beginning of the loop. It's important to note that at this time, while loops don't support
        expressions that contain additional parentheses. TODO: figure out how to handle multiple parentheses
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
                if self.mathFormula == "":
                    # empty expression (e.g. if ( a > ) )
                    raise ValueError("Empty expression in if statement at line {}".format(self.lineno))

                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod],
                                self.arrayList, output)
                self.ifOperator = self.convertOperatorToFlags(char)
                self.expectFlag = 2
                self.mathFormula = ""
                output.write("    MOV $A $C2\n")

            else:
                # otherwise we keep appending to our left hand side's math formula string
                self.mathFormula += char

        elif self.expectFlag == 2:
            # here we evaluate the right hand side of a while loop.
            if char == ")":
                # closing parentheses, this indicates the end of our expression
                if self.mathFormula == "":
                    # empty expression (e.g. if ( a > ) )
                    raise ValueError("Empty expression in if statement at line {}".format(self.lineno))

                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod],
                                self.arrayList, output)
                self.expectFlag = 2
                self.mathFormula = ""
                output.write("    MOV $A $D2\n")
                self.expectFlag = 3

            else:
                # otherwise, append to the right hand side's math formula string
                self.mathFormula += char

        elif self.expectFlag == 3:
            # we've finished reading our if statement, now we wait for an opening curly brace

            if char in IGNORE_CHARS:
                # we can still read whitespace or newline chars meanwhile
                pass

            elif char == "{":
                # we have our opening curly brace, we can go back to state 5 and begin evaluating a new line
                output.write("    CMP $D2 $C2\n")
                output.write("    JMP " + self.ifOperator + " L" + str(self.ifLabel) + "\n")
                self.labelList.append(" L" + str(self.ifLabel))
                self.ifLabel += 1
                self.state = 5
                self.expectFlag = 0
                self.mathFormula = ""

            else:
                # we read something other than whitespace or an opening curly brace, this is invalid
                raise ValueError("Syntax error at line {}".format(self.lineno))

    def state11(self, char, output):
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
            tokens = tokenize(self.mathFormula)
            postfix = infixToPostfix(tokens)
            evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod],
                            self.arrayList, output)
            self.expectFlag = 0
            self.mathFormula = ""
            self.state = 5
            output.write("    RET\n")

        else:
            # we continue to append the chars to our math formula for the return statement
            self.expectFlag = 1
            self.mathFormula += char

    def state12(self, char, output):
        """
        This state handles the declaration of an array. We check to see if any character before closing bracket "]"
        is a valid integer for the size of the array. We also verify if there is a value assignment following the array
        declaration.
        :param char: char, Individual character read from input file
        :param output: file, output file to write to
        :return:
        """

        if self.expectFlag == 0:
            if char != "]":
                try:
                    int(char)
                except ValueError as e:
                    raise ValueError("Array size declaration invalid at line {}".format(self.lineno))
                self.arrayLength += char
            else:
                self.arrayList[self.currentVar] = int(self.arrayLength)
                self.varLocation[self.currentVar] = self.memoryLocation
                self.memoryLocation += int(self.arrayLength) * 4
                self.arrayLength = ""
                self.expectFlag = 1

        elif self.expectFlag == 1:
            if char == " ":
                pass
            elif char == "=":
                self.expectFlag = 2
            elif char == ";":
                self.expectFlag = 0
                self.state = 5
            else:
                raise ValueError("Invalid syntax at line {}".format(self.lineno))

        elif self.expectFlag == 2:
            # array has an assignment immediately after its declaration
            if char == " ":
                pass
            elif char == "{":
                self.expectFlag = 3
            else:
                raise ValueError("Invalid array value assignment at line {}".format(self.lineno))

        elif self.expectFlag == 3:
            # Here we're declaring the variables inside our array
            if char == "}":
                self.expectFlag = 4

            else:
                self.mathFormula += char

        elif self.expectFlag == 4:
            if char == " ":
                pass
            elif char == ";":
                self.assignArrayValues(output)
                self.expectFlag = 0
                self.mathFormula = ""
                self.arrayLength = ""
                self.state = 5
            else:
                raise ValueError("Incorrect syntax at line {}".format(self.lineno))

    def state13(self, char, output):
        """
        This state deals with assigning a value to a specific array index
        :param char:
        :param output:
        :return:
        """

        if self.expectFlag == 0:
            if char == "]":
                try:
                    int(self.arrayLength)
                except ValueError as e:
                    raise ValueError("Invalid array index at line {}".format(self.lineno))

                if int(self.arrayLength) > int(self.arrayList[self.currentVar] - 1) or int(self.arrayLength) < 0:
                    raise ValueError("Array index out of bounds at line {}".format(self.lineno))

                self.expectFlag = 1

            else:
                self.arrayLength += char

        elif self.expectFlag == 1:
            if char == " ":
                pass
            elif char == "=":
                self.expectFlag = 3

        elif self.expectFlag == 3:
            if char == ";":
                tokens = tokenize(self.mathFormula)
                postfix = infixToPostfix(tokens)
                evaluatePostfix(postfix, self.varList, self.varLocation, self.methodList[self.currentMethod],
                                self.arrayList, output)
                output.write("    MEMW [4] $A #" + str(self.varLocation[self.currentVar] + int(self.arrayLength) * 4) +
                             "\n")

                self.expectFlag = 0
                self.mathFormula = ""
                self.arrayLength = ""
                self.state = 5
            else:
                self.mathFormula += char

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
        location counter, and increase the total variable count.
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
        self.currentType = ""
        self.currentVar = ""

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
        elif char == "=":
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
            print(list)
            raise ValueError("Incorrect number of values for array assignment at line {}".format(self.lineno))

        for element in list:
            try:
                int(element)
            except ValueError as e:
                raise ValueError("Invalid value for array assignment at line {}".format(self.lineno))

            output.write("    MEMW [4] #" + str(element) + " #" + str(startingLocation) + "\n")
            startingLocation += 4


    def arrayBoundsCheck(self):
        pass

