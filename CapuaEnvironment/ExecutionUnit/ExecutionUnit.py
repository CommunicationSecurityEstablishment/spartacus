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

from CapuaEnvironment.Instruction.Instruction import Instruction
from CapuaEnvironment.IntructionFetchUnit.InstructionFetchUnit import InstructionFetchUnit
from CapuaEnvironment.IOComponent.MemoryIOController import MemoryIOController
from Configuration.Configuration import (
    MEMORY_START_AT, MEMORY_END_AT, REGISTER_A, REGISTER_B, REGISTER_C, REGISTER_S)

__author__ = "CSE"
__copyright__ = "Copyright 2015, CSE"
__credits__ = ["CSE"]
__license__ = "GPL"
__version__ = "1.3"
__maintainer__ = "CSE"
__status__ = "Dev"


class ExecutionUnit:
    """
    The execution unit represent a single core in the system. Registers are hosted here. This can be
    seen as the "heart" of the system in the sense that everything happen inside of the ExecutionUnit
    """

    # All registers are hosted in the ExecutionUnit
    A = 0           # Software limited to 32 bits General purpose register
    B = 0           # Software limited to 32 bits General purpose register
    C = 0           # Software limited to 32 bits General purpose register
    S = 0           # Software limited to 32 bits Stack pointer. Can be used as a GPR is not using the stack
    I = 0           # Software limited to 32 bits Instruction pointer. This one is not accessible from instructions
    FLAGS = 0b000   # 3 bits limited ZLH = Zero, Lower, Higher

    # Other required hardware components
    mioc = None # MemoryInputOutputController
    ifu = None  # InstructionFetchUnit
    lu = None   # LogicUnit

    # Simple "process" identification token, this is changed to the name of the player
    # program when in game mode
    name = "System"

    _registers = dict(zip(
        (REGISTER_A, REGISTER_B, REGISTER_C, REGISTER_S), 'ABCS'))

    def __init__(self, mioc: MemoryIOController=None, ifu: InstructionFetchUnit=None, name: str="System"):
        """
        This will setup the ExecutionUnit so that it is in a state that it can be used to run code
        from memory.
        :param mioc: A MemoryIOController for this core so that it can have access to memory
        :param ifu: An InstructionFetchUnit so this core can correctly get the instruction from memory
        :param name: str, a name identifying the core
        """
        if mioc is None or type(mioc) is not MemoryIOController:
            raise RuntimeError("Capua core initialisation error - unstable state")
        if ifu is None or type(ifu) is not InstructionFetchUnit:
            raise RuntimeError("Capua core initialisation error - unstable state")
        if name is None or type(name) is not str:
            raise RuntimeError("Capua core initialisation error - unstable state")

        self.mioc = mioc
        self.ifu = ifu
        self.name = name
        self.lu = LogicUnit(self) # LogicUnit is lower in this file

    def setupCore(self, I: int=MEMORY_START_AT):
        """
        Before execution can happen on a given core, that core needs to be "setup" so that the I pointer points to
        a valid address in memory. Almost no validation is made here. Calling code is responsible for giving a correct
        address.
        :param I: int, a memory address where I pointer should be pointing
        :return: Nothing just does what it's being asked.
        """
        if MEMORY_START_AT <= I <= MEMORY_END_AT:
            self.I = I
        else:
            raise RuntimeError("Capua core {} Initialisation failed".format(self.name))


    def execute(self):
        """
        A call to this will cause the next instruction (the one where I points) to be executed. IMPORTANT
        note, the I pointer is incremented right before the execution of the instruction. This has the
        side effect that the I value while an instruction is being executed is, really the I value for the
        next instruction to be executed.
        :return: Nothing
        """

        # Get next instruction to be executed
        instruction, nextInstructionAddress = self.ifu.fetchInstructionAtAddress(self.I)
        self.I = nextInstructionAddress
        self.lu.executeInstruction(instruction)

    def setRegisterValue(self, registerCode: int=None, value: int=None):
        """
        This is the gate keeper to setting registers value. It make sure that the
        value set into the registerCode has a max value of 0xFFFFFFFF and truncate any
        overflowing value. It also makes sure that only valid registerCode are referenced
        :param registerCode: str, a string representing a valid registerCode
        :param value: int, the value that needs to be written into the registerCode
        :return:
        """
        value &= 0xFFFFFFFF
        try:
            setattr(self, self._registers[registerCode], value)
        except KeyError:
            raise ValueError(
                "Core {} caused an invalid instruction to be executed - GameOver".format(self.name))

    def getRegisterValue(self, registerCode=None):
        """
        This method simply returns the value of a specific register based on the
        register code.
        :param registerCode: int, from 0b00 to 0b11
        :return:
        """
        try:
            return getattr(self, self._registers[registerCode])
        except KeyError:
            raise ValueError("Core exception access to invalid register")


class LogicUnit:
    """
    The LogicUnit is tightly coupled with the ExecutionUnit. It is integral part of the
    ExecutionUnit and is not meant to be accessed outside of the ExecutionUnit. It has
    full access to everything that the execution unit has. It has been taking out of
    the ExecutionUnit for code cleanliness purposes only. Nothing else.
    The LogicUnit is almost analogous to the ALU in a normal architecture...
    Here, it is put on steroids and it does a bit more than a normal ALU would be doing.

    Note about getting the source information:
    As you will see, many methods bellow uses the following lines of code in order
    to get the source value:

    if self.ci.sourceImmediate is None:
        sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
    else:
        sourceValue = self.ci.sourceImmediate

    These lines repeats in many of the methods present in this class. I made the decision
    of NOT TAKING these lines out into a helper method in order to avoid the method call
    overhead. Keep in mind that the code in the LogicUnit class is typically called from
    within a very tight loop. Therefore, code performance here is of the utmost importance.

    """

    eu = None  # The execution unit.
    ci = None  # The current instruction that is being executed.

    def __init__(self, executionUnit: ExecutionUnit=None):
        """
        Prepare this LogicUnit so that it has access to the ExecutionUnit where it sits.
        :param executionUnit: ExecutionUnit, the "Parent" execution unit for this LogicUnit
        :return:
        """

        if executionUnit is not None and type(executionUnit) is ExecutionUnit:
            self.eu = executionUnit
        else:
            RuntimeError("Capua environment, error initializing the logic unit")

    def executeInstruction(self, instruction: Instruction=None):
        """
        This is the "public" entry point for the LogicUnit. The individual operations are not to be directly
        called. This method will call the individual instruction and make sure that the FLAGS register gets
        correctly updated after each instruction is executed.
        :param instruction: Instruction, the instruction to be executed.
        :return: Nothing!
        """
        if instruction is None or type(instruction) is not Instruction:
            raise RuntimeError("Capua execution error, got into unstable state")

        self.ci = instruction

        if hasattr(self, self.ci.operationMnemonic):
            # Using the mnemonic to find the correct method for the call
            callableOperation = getattr(self, self.ci.operationMnemonic)
            # This simply calls the correct mnemonic method
            result = callableOperation()

            # Some mnemonic return values causing FLAGS update
            if 0 <= result <= 0b111:
                # If that is the case, update the FLAGS register
                self.eu.FLAGS = result
            else:
                RuntimeError("LogicUnit error, core flags are in an inconsistent state")
        else:
            RuntimeError("LogicUnit Unknown error,operation {} went bad".format(instruction.operationMnemonic))

    def ADD(self):
        """
        2 possibilities:
        ADD sReg, dReg       : Total Length 2B : ID 0b0111 10 : sR 00 : dR 1B : exec time = 1 : Addition
        ADD imm, dReg        : Total Length 5B : ID 0b0111 11 : dR 00 : sI 4B: exec time = 1 : Addition
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = sourceValue + destinationValue
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0

    def AND(self):
        """
        2 possibilities:
        AND sReg, dReg   : Total Length 2B : ID 0b0101 00 : sR 00 : dR 1B : exec time = 1 : Binary and
        AND imm, dReg    : Total Length 5B : ID 0b0101 01 : dR 00 : sI 4B : exec time = 1 : Binary and
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = sourceValue & destinationValue
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0

    def CALL(self):
        """
        More complex case. This does multiple things:
            1- Push next I on top of stack
            2- Change I to given value
            3- return 0

        2 possible cases:
        CALL imm   : Total Length 5B : ID 0b0010 11 : I 4B : exec time = 2 : Transfer execution to imm pointer pushing return address to the stack
        CALL reg   : Total Length 1B : ID 0b0011 00 : R 00 : exec time = 2 : Transfer execution to imm pointer pushing return address to the stack
        :return:
        """

        # Lets adjust the stack!
        stackPointer = self.eu.S + 4  # Stack grows upward!!!
        self.eu.S = stackPointer

        # return I address
        # I has already been incremented at this point we can simply use it as is for return address
        returnIAddress = self.eu.I

        # Write value to top of stack
        self.eu.mioc.memoryWriteAtAddressForLength(stackPointer, 4, returnIAddress, source=self.eu.name)

        # Now we can transfer execution to CALL destination for next execution
        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        self.eu.I = sourceValue
        return 0

    def CMP(self):
        """
        This will not change the register values... simply set the flags accordingly.
        2 possibilities:
        CMP imm, reg : Total Length 5B : ID 0b0011 01 : R 00 : I 4B : exec time = 1 : Compare immediate with register, set flags accordingly
        CMP reg, reg : Total Length 2B : ID 0b0011 10 : R1 00 : R2 1B exec time = 1 : Compare register with register, set flags accordingly

        FLAGS: 0b000 : Zero, Lower, Higher

        :return: This affects the FLAGS!!!!
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = sourceValue - destinationValue
        flagsResult = 0b000

        if result == 0:
            flagsResult = 0b100  # Zero or equal
        elif result < 0:
            flagsResult = 0b010  # Less
        elif result > 0:
            flagsResult = 0b001  # Higher

        return flagsResult

    def DIV(self):
        """
        1 possibility:
        DIV sReg, dReg  : Total Length 2B : ID 0b1001 10 : sR 00 : dR 1B : exec time = 3 : Division, result is put in A, rest is put in B
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        resultA = sourceValue // destinationValue
        resultB = sourceValue % destinationValue
        self.eu.setRegisterValue(REGISTER_A, resultA)
        self.eu.setRegisterValue(REGISTER_B, resultB)

        return 0

    def JMP(self):
        """
        More complex case. This does multiple things:
            1- Check for condition
            2- Change I to given value
            3- return 0

        2 possible cases:
        JMP[FLAGS] imm  : Total Length 5B : ID 0b0100 10 : FL 00 : I 4B : exec time = 2 : Jump to imm, can use flag modifier
        JMP[FLAGS] reg  : Total Length 2B : ID 0b0100 11 : FL 00 : R 1B: exec time = 2 : Jump to register, can use flag modifier        :return:
        """

        # Validate flags
        if 0 > self.ci.flags > 0b111:
            raise ValueError("Invalid instruction format detected")

        nextI = self.eu.I  # This is already calculated with the next I value

        # As strange as the next conditional looks, the second part is for
        # unconditional jump detection.
        if ((self.ci.flags & self.eu.FLAGS) > 0) or (self.ci.flags == self.eu.FLAGS):
            # Condition is met, jump has to occur...
            if self.ci.sourceImmediate is None:
                sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
            else:
                sourceValue = self.ci.sourceImmediate

            nextI = sourceValue

        self.eu.I = nextI
        return 0

    def JMPR(self):
        """
        More complex case. This does multiple things:
            1- Check for condition
            2- Change I to given value
            3- return 0

        The Relative part of the jump is calculated based on the I value of the instruction following
        the JMPR instruction. I gets incremented to the next instruction before the execution of the
        current instruction happens.

        2 possible cases:
        JMPR[FLAGS] imm  : Total Length 5B : ID 0b0011 11 : FL 00 : I 4B : exec time = 1 : Jump relative to register I to imm, can use flag modifier
        JMPR[FLAGS] reg  : Total Length 2B : ID 0b0100 01 : FL 00 : R 1B : exec time = 1 : Jump relative to register I to imm, can use flag modifier
        """

        # Validate flags
        if 0 > self.ci.flags > 0b111:
            raise ValueError("Invalid instruction format detected")

        nextI = self.eu.I  # This is already calculated with the next I value

        # As strange as the next conditional looks, the second part is for
        # unconditional jump detection.
        if ((self.ci.flags & self.eu.FLAGS) > 0) or (self.ci.flags == self.eu.FLAGS):
            # Condition is met, jump has to occur...
            if self.ci.sourceImmediate is None:
                sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
            else:
                sourceValue = self.ci.sourceImmediate

            if (0x1 << 31) & sourceValue != 0:
                # This is a negative number!!! Converting binary neg to usable, base 10, neg
                sourceValue ^= 0xFFFFFFFF  # Two's complement
                sourceValue += 1
                sourceValue *= -1 # Simply making the number negative...

            nextI = self.eu.I + sourceValue

        self.eu.I = nextI
        return 0

    def MEMR(self):
        """
        2 possibilities:
        MEMR[WIDTH] sImm, dReg          : Total Length 6B : ID 0b0000 10 : wD 00 : sI 4B : dR 1B : exec time = 2 : Read a pointer value to the register
        MEMR[WIDTH] sReg, dReg          : Total Length 2B : ID 0b0000 11 : wD 00 : sR 0000 : dR 0000 : exec time = 2 : Same as previous, content of reg is used as a pointer
        :return: 0, resets the flags
        """

        # Validate width
        if 0 >= self.ci.width > 4:
            raise ValueError("Invalid instruction format detected")

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = self.eu.mioc.memoryReadAtAddressForLength(sourceValue, self.ci.width)
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0

    def MEMW(self):
        """
        4 possibilities:
        MEMW[WIDTH] sReg, dReg          : Total Length 2B : ID 0b0001 00 : wD 00 : sR 0000 : dR 0000 : exec time = 3 : Write the content of a register to a given memory address (in register)
        MEMW[WIDTH] sImm, dReg          : Total Length 6B : ID 0b0001 01 : wD 00 : sI 4B : dR 1B : exec time = 3 : Write an immediate value to a memory address (in register)
        MEMW[WIDTH] sReg, dImm          : Total Length 6B : ID 0b0001 10 : wD 00 : sR 1B : dI 4B : exec time = 3 : Write an immediate value to a memory address (given as an immediate value)
        MEMW[WIDTH] sImm, dImm          : Total Length 9B : ID 0b0001 11 : wD 00 : sI 4B : dI 4B : exec time = 3 : Write an immediate value to a memory address (given as an immediate value)
        :return: 0, resets the flags
        """

        # Validate width
        if 0 >= self.ci.width > 4:
            raise ValueError("Invalid instruction format detected")

        if self.ci.destinationImmediate is None:
            destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)
        else:
            destinationValue = self.ci.destinationImmediate

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        valueMask = 0x00
        for i in range(0, self.ci.width):
            valueMask <<= 8
            valueMask |= 0xFF
        sourceValue &= valueMask

        self.eu.mioc.memoryWriteAtAddressForLength(destinationValue,
                                                   self.ci.width,
                                                   sourceValue,
                                                   source=self.eu.name)

        return 0

    def MOV(self):
        """
        2 possibilities:
        MOV sReg, dReg  : Total Length 2B : ID 0b0000 00 : sR 00 : dR 1B : exec time = 1 : Mov content of register to other register
        MOV sImm, dReg  : Total Length 5B : ID 0b0000 01 : dR 00 : sI 4B : exec time = 1 : Mov an immediate to a register
        :return: 0, resets the flags
        """

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = sourceValue
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0

    def MUL(self):
        """
        1 possibility:
        MUL sReg, dReg : Total Length 2B : ID 0b1001 01 : sR 00 : dR 1B : exec time = 2 : Multiplication, result is put in B:A
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = sourceValue * destinationValue
        resultA = 0x00000000FFFFFFFF & result
        resultB = 0xFFFFFFFF00000000 & destinationValue
        self.eu.setRegisterValue(REGISTER_A, resultA)
        self.eu.setRegisterValue(REGISTER_B, resultB)

        return 0

    def NOP(self):
        """
        No operation, simply return 0
        :return:
        """
        return 0

    def NOT(self):
        """
        1 possibility:
        NOT Reg     : Total Length 1B : ID 0b1000 10 : R 00 : exec time = 1 : Negation (bit inversion)
        :return: 0, resets the flags
        """

        sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)

        result = sourceValue ^ 0xFFFFFFFF
        self.eu.setRegisterValue(self.ci.sourceRegister, result)

        return 0

    def OR(self):
        """
        2 possibilities:
        OR sReg, dReg       : Total Length 2B : ID 0b0101 10 : sR 00 : dR 1B : exec time = 1 : Binary or
        OR imm, dReg        : Total Length 5B : ID 0b0101 11 : dR 00 : sI 4B : exec time = 1 : Binary or
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = sourceValue | destinationValue
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0

    def POP(self):
        """
        More complex case. This does multiple things:
            1- Get value from stack
            2- Adjust stack pointer
            3- return 0

        1 possible case:
        POP Reg     : Total Length 1B : ID 0b0010 10 : R 00 : exec time = 1 : Pop to pof stack to register
        :return:
        """

        stackPointer = self.eu.S

        # Read value to top of stack
        topStackValue = self.eu.mioc.memoryReadAtAddressForLength(stackPointer, 4)

        # Lets adjust the stack!
        stackPointer = self.eu.S - 4  # Stack grows upward!!!
        self.eu.S = stackPointer

        # Save value to register
        self.eu.setRegisterValue(self.ci.sourceRegister, topStackValue)

        return 0

    def PUSH(self):
        """
        More complex case. This does multiple things:
            1- Get current stack pointer + adjust stack pointer
            2- Write value to top of stack
            3- return 0

        2 possible cases:
        PUSH Reg   : Total Length 1B : ID 0b0010 00 : R 00 : exec time = 2 : Push value of register on top of the stack
        PUSH Imm   : Total Length 5B : ID 0b0010 01 : I 4B : exec time = 2 : Push value of register on top of the stack
        :return:
        """

        # Lets adjust the stack!
        stackPointer = self.eu.S + 4  # Stack grows upward!!!
        self.eu.S = stackPointer

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        # Now write value to top of stack!
        self.eu.mioc.memoryWriteAtAddressForLength(stackPointer, 4, sourceValue, source=self.eu.name)

        return 0

    def RET(self):
        """
        More complex case. This does multiple things:
            1- Get value from stack
            2- CAdjust stack pointer
            3- Adjust next instruction pointer
            3- return 0

        1 possible case:
        RET       : Total Length 1B : ID 0b1001 0100 : exec time = 1 : Return from a function call
        :return:
        """

        stackPointer = self.eu.S

        # Read value to top of stack
        topStackValue = self.eu.mioc.memoryReadAtAddressForLength(stackPointer, 4)

        # Lets adjust the stack!
        stackPointer = self.eu.S - 4  # Stack grows upward!!!
        self.eu.S = stackPointer

        # Adjust next instruction pointer
        self.eu.I = topStackValue

        return 0

    def SHL(self):
        """
        2 possibilities:
        SHL sReg, dReg        : Total Length 2B : ID 0b0111 00 : sR 00 : dR 1B : exec time = 1 : Shift Left
        SHL imm, dReg         : Total Length 5B : ID 0b0111 01 : dR 00 : sI 4B: exec time = 1 : Shift Left
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = destinationValue << sourceValue
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0

    def SHR(self):
        """
        2 possibilities:
        SHR sReg, dReg       : Total Length 2B : ID 0b0110 10 : sR 00 : dR 1B : exec time = 1 : Shift Right
        SHR imm, dReg        : Total Length 5B : ID 0b0110 11 : dR 00 : sI 4B : exec time = 1 : Shift Right
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = destinationValue >> sourceValue
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0

    def SNT(self):
        """
        Not implemented yet!
        :return:
        """
        return 0

    def SUB(self):
        """
        2 possibilities:
        SUB sReg, dReg     : Total Length 2B : ID 0b1000 00 : sR 00 : dR 1B : exec time = 1 : Subtraction
        SUB imm, dReg      : Total Length 5B : ID 0b1000 01 : dR 00 : sI 4B : exec time = 1 : Subtraction
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = destinationValue - sourceValue
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0

    def XOR(self):
        """
        2 possibilities:
        XOR sReg, dReg       : Total Length 2B : ID 0b0110 00 : sR 00 : dR 1B : exec time = 1 : Binary xor
        XOR imm, dReg        : Total Length 5B : ID 0b0110 01 : dR 00 : sI 4B : exec time = 1 : Binary xor
        :return: 0, resets the flags
        """

        destinationValue = self.eu.getRegisterValue(registerCode=self.ci.destinationRegister)

        if self.ci.sourceImmediate is None:
            sourceValue = self.eu.getRegisterValue(registerCode=self.ci.sourceRegister)
        else:
            sourceValue = self.ci.sourceImmediate

        result = sourceValue ^ destinationValue
        self.eu.setRegisterValue(self.ci.destinationRegister, result)

        return 0
