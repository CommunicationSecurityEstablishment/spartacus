![Spartacus Logo](Images/spartacus-logo.jpg)
# Spartacus Reference Manual
Version 2.0
December 2017

This document does not repeat the information available in the quick start guide.
Please read the quick start before reading this document.

## Document history
* December 2018
    * Complete rewrite of the document. Current version of the VM is no longer
    compatible with V1.0. The game has been removed from the project. Multiple
    instructions have been added. Some language rules have
    changed.
    
## Introduction
The Capua environment is a virtual core designed to help new comers to assembly, and
operating system programming in general, learn the basics associated with such concepts. Capua was
developed after witnessing a diminution in the abilities of recent graduated students to evolve in
low level programming environment. Therefore, Capua functionality is stripped down to bare
minimum so users can benefit from the simplicity of its design in a learning context.

### Note
Through this document, every reference to "hardware", unless specified otherwise should
be understood as "virtual hardware".

## Capua versus Spartacus
Spartacus is the whole project. Capua is the virtual environment.

## Important changes from version 1.0 to version 2.0
* Capua now supports software and hardware interrupts
* Multiple instructions have been added: 
    * **ACTI, DACTI, HIRET, INT, SFSTOR, SIVR**
    * These allow for the minimum required for operating system development
* Capua now have 16 general purpose registers (GPRs)
    * This addition forced a change in machine code. Code assembled and linked
    with previous version of the tool chain will not run properly on Capua V. 2.0
* Support for multiple hardware elements was added:
    * Hard drive, Interrupt clock and Terminal
* Every hardware elements that was highly tied with the game environment was removed
* The game environment has been removed from the project

## Capua
Capua is a load/store architecture. This means that only load (**MEMR**) and store (**MEMW**) 
instructions can do memory access. Stack related instructions also have access to
memory but in a much stricter way.
## Registers
Capua now has 16 GPRs named from **A** to **G**, and **A2** to **G2**. It also now has **S** and **S2**. The **S** and **S2**
GPRs are intended to be used as stack registers. All registers are 32 bits wide. The
instruction pointer is named **I** and is not user accessible. A flag register named **FLAGS**
is used by the core but is also not user accessible. 
## Memory
At the current time, no memory management unit or equivalent device is available to the
Capua environment. We are working on this and one should be available in a soon to be
released version of the VM.
Physical memory is, therefore, always directly accessed. Start of the user memory is
defined in the **Configuration/Configuration.py** file. By default, this value is
0x40000000. By default, the VM has 1 MB of memory. These defaults values can be changed.
However, it is not recommended to do so.
## Memory mapped devices
On capua, all hardware is memory mapped. Every single hardware piece is accessible at
addresses located bellow the start of the memory (0x40000000). Presence of memory mapped
hardware is one of the reasons why we do not recommend changing memory values in the
configuration file.
## General architecture
As of December 2017 Capua architecture looks like:
![Capua Architecture](Images/Architecture-En.png)

As you can see, architecture is very simple but resembles that of a real computer.

# Instruction set
The syntax for the Capua assembly language is organised in a source -> destination fashion.
When 2 elements, either immediate or registers, are present in an instruction,
the first is always the source and the second one is always the destination. Following
is the full instruction listing. Examples of various forms an instruction can have are also
presented.
###### Registers, immediate values and memory references
The assembler currently requires the programmer to prefix any registers with the **$** sign.
Every immediate value has to be prefixed with the **#** sign. Use of memory reference (labels)
within an instruction is permitted where immediate values can be used. It does not require
any prefix.
### ACTI
This instruction will activate the interrupt handling mechanism. After it is issued,
INT instruction and hardware interrupts can be handled. The handling of the interrupts
is described in the appropriate section bellow. The ACTI instruction does not use
any registers or immediate values.
>**ACTI**
### ADD
This instruction allows for integer addition. The
following shows the different variants of the
add instruction.
>**ADD #0xFF $A**

>**ADD $B $A**
### AND
The AND instruction is used for binary operation. It
is a binary comparison and follows normal AND
truth table:

* 1 and 1 = 1
* 1 and 0 = 0
* 0 and 1 = 0
* 0 and 0 = 0

Obviously this verification is extended to the full
length of the compared elements (32 bits).
>**AND #0xFF $A**

>**AND $B $A**
### CALL
You must fulfill the instruction prerequisite to use
the CALL instruction. Doing otherwise will result in
bad things, usually a memory error. Before using
this instruction, you have to make sure that the
S register points to a valid and
available region of memory that can be used as a stack. The call instruction
will cause the address of the instruction following
the CALL instruction to be pushed on top of the
stack in order for that one to be used as return
address.
>**CALL #0x40000010**

>**CALL $A**

>**CALL testFunction**
### CMP
The compare instruction is the only one that allows
for FLAGS register modification. The FLAGS register
is, at current time, only 3 bits wide. The top bit
( 0b100 ) will be set when the source element of the
comparison is equal to the destination element.
The middle bit ( 0b010 ) is set when source is lower
than destination and the rightmost bit ( 0b001 ) is set
when source is higher than destination.    
>**CMP #0xFF $A**

>**CMP $A $B**
### DACTI
The DACTI instruction is the inverse of the ACTI instruction. It will
disable the interrupt handling mechanism. It also does not use any
registers of immediate values.
>**DACTI**
### DIV
The div instruction allows for division. The source
element will be divided by the destination element.
The quotient of the division is placed in register A and
the remainder of the division is placed in register B.
>**DIV $C $B**
### HIRET
The HIRET instruction means Hardware Interrupt Return. It is to be used as a return
instruction for the hardware interrupt handling routine. It is not to be used as part
of software interrupt handling routine. When issued, it will return to the routine
that was previously interrupted by the hardware while also making
sure that the flags is reset to the value it held before the hardware interrupt. HIRET
does not use any registers of immediate values.
>**HIRET**
### INT
The INT instruction is used to generate a software interrupt. When issued, if interrupts are
activated, the core will jump to the appropriate handling routine based on the number of
the interrupt. Please see the interrupt handling section for more details on interrupt
handling. The instruction is available in two forms. It can either be used with an
immediate value or with a register
>**INT #4**

>**INT $A**
### JMP
The jump instruction allows the user to skip parts of the
code either unconditionally or conditionally by
looking at the FLAGS register value. This instruction
is special in the sense that it uses a flag indicator to
allow the user to select the conditions where the
jump should be taken. Next is a listing of the
possible conditions:

* <> Jump is always taken
* <E> or <Z> Jump is taken if 0b100 is set (E Flag)
* <L> Jump is taken if 0b010 is set (L Flag)
* <H> Jump is taken if 0b001 is set (H Flag)

These flags indicators can be combined to form
complex conditions. For example, the <LE>
indicator would allow the jump to happen if the E
flag is set or if the L flag is set. Note that the
immediate or register used by this instruction must
hold a valid memory address from where code can be
fetched.
>**JMP <E\> #0x40000010**

>**JMP <LH\> $B**

>**JMP <\> testLoop**
### JMPR
The JMPR instruction is identical to the JMP
instruction with a major difference. The immediate
or register used by the JMPR instruction must hold a
relative offset to the instruction pointer "I" where the
jump should result. For example, using the
immediate value #0xFF will cause the execution
unit to start fetching instruction 0xFF bytes after the
JMPR instruction.
>**JMPR <E\> #0x10**

>**JMPR <LH\> $B**
### MEMR
The MEMR instruction allows for memory read
operation. MEMR uses a width indicator that allows
the user to read 1 to 4 bytes from memory into a
register. The source can either be a register or an
immediate value but must be a valid memory
address. The width indicator is defined by using the
\[ and \] characters.
>**MEMR \[4\] #0x40000000 $B**

>**MEMR \[4\] $A $B**
### MEMW
The MEMW instruction allows for memory write
operation. Like the MEMR instruction, it uses a width
indicator. Because of its nature, the MEMW
instruction is available in more form than the MEMR
instruction. The destination can be a register or an
immediate but must be a valid memory address.
>**MEMW \[4\] #0xFF #0x40000000**

>**MEMW \[4\] #0xFF $A**
### MOV
The MOV instruction allows for data displacement
between register or for loading a register with an
immediate value. This instruction could be used, for
example, to set the stack pointer S to a valid
memory region in order for the stack to be usable.
>**MOV #0x40000200 $S**

>**MOV $A $B**
### MUL
The MUL instruction allows for integer multiplication
between two registers. It is not possible to use the
MUL instruction with an immediate value. Since
multiplication can result in numbers that are bigger
than 32 bits, the B register holds the higher 32 bits
and the A register holds the lower 32 bits of the
resulting number. The number should read as B:A
after the multiplication.
>**MUL $A $B**
### NOP
The NOP instruction is the no operation instruction.
It does nothing. Since Capua does not need to be 4
bytes aligned, the NOP instruction is typically
useless. However, it can be use to fill the memory at
boot time in order to ease development.
>**NOP**
### NOT
The NOT instruction will inverse the bits of a
register. For example, if register A is equal to 0x01
before the NOT instruction, it will be equal to
0xFFFFFFFE after the NOT instruction. The not
instruction can, obviously, only be used with a
register.
>**NOT $A**
### OR
The OR instruction is a bitwise or operation. It
works following the Boolean logic or rules. Here is
its truth table:

* 1 or 1 = 1
* 0 or 1 = 1
* 1 or 0 = 1
* 0 or 0 = 0

It will impact all the bits in a register.
>**OR #0xFF $A**

>**OR $A $B**
### POP
The POP instruction removes 32 bits from the stack
and decreases the stack pointer 4 bytes back. The
data that was on the top of the stack will be
available in the register specified by the POP
instruction. For the POP instruction to be safely
used, the stack pointer S must be set to a valid
memory address.
>**POP $A**
### PUSH
The PUSH instruction will add a 32 bits value on the
top of the stack and increase the stack pointer S 4
bytes forward. In order for the PUSH instruction to
be safely used, the stack pointer S must be set to a
valid memory address before using the PUSH
instruction.
>**PUSH #0xFF**

>**PUSH $A**
### RET
The return instruction is typically used to return
back from a call. It will take the element on the top
of the stack and set the instruction pointer I value to
it. In order to use the RET instruction, the caller has
to make sure that the top of the stack value is a
pointer to a region of memory where code can be
fetched by the execution unit.
>**RET**
### SFSTOR
The SFSTOR instruction means Safe Store. The "safe" part means safe as in thread safe. 
IT will take the value present in the source operand (either imm or reg) and will copy it at 
address in $A  if condition is meet by doing a comparison between the data held at memory address 
defined in $A. The condition used are the same as for the JMP instruction. The instruction will also
change the flags according to the result of the comparison. The order of the comparison goes as 
(Immediate or Register) against data pointed to by register A. Not the other way around.
>**SFSTOR <LH\> #1**

>**SFSTOR <LH\> $B**

This instruction aims at making it possible for a programmer to write thread synchronisation code like mutexes.
### SHL
The SHL instruction mnemonic stands for SHift
Left. It allows its user to shift the value of a register
X bits to the left where X is a number from 1 to 8.
The exceeding values are simply lost. As an
example, consider the value 0x80000001 . Applying
a one-bit shift left to this value will result in that
value being transformed to 0x00000002.
>**SHL #0x01 $A**

>**SHL $B $A**
### SHR
The SHR instruction is the same as SHL instruction
except that the shift happens to the right. Therefore
a one-bit right shift applied to the value
0x80000001 will result in the value 0x40000000 .
>**SHR #0x01 $A**

>**SHR $B $A**
### SIVR
This instruction means Set Interrupt Vector Register. This is used to configure the interrupt vector pointer.
It must be configured to point to a valid vector of handling routine addresses. It can only be used
with a register.
>**SIVR $A**

The following code snippet shows an example of setting the IVR
```
.global start:

start:
MOV end $S                      ; Stack grows up, setting S to the end is generally safer
                                ; The stack needs to be configure for interrupt handling to work
MOV vector $A
SIVR $A                         ; Set the interrupt vector to "vector"
ACTI                            ; Interrupt handling activation

loop:
    NOP
    JMP <> loop

clockHandler:                   ; All hardware interrupts are mapped to this empty handler
keyboardHandler:
hardDriveReadHandler:
hardDriveWriteHandler:
    HIRET


vector:                         ; The vector is built using the dataMemRef marker
.dataMemRef clockHandler
.dataMemRef keyboardHandler
.dataMemRef hardDriveReadHandler
.dataMemRef hardDriveWriteHandler
end:
```
### SUB
The SUB instruction allows for subtracting values. It
is important to understand that the operation works
like this:
* destination = destination - source

Not the other way around. Beware. It is also
important to know that the SUB instruction only
considers 32 bits signed, in the two’s complement
format, integer numbers.
>**SUB #0x01 $A**

>**SUB $B $A**
### XOR
The XOR instruction is a bitwise operation, just like
the AND and OR instructions. It follows the normal
XOR logic and has the following truth table:

* 1 xor 1 = 0
* 1 xor 0 = 1
* 0 xor 1 = 1
* 0 xor 0 = 0

It can be used to set a register value to 0.
>**XOR #0x01 $A**

>**XOR $B $A**

# Tool Chain
Capua, being an architecture, needs its own
assembler. For this project, 4 tools were developed
in order to help software development and testing
of the platform.

* Assembler.py
* Linker.py
* Debugger.py
* HardDriverCreator.py

The following sections explain each tool. Please
keep in mind that these tools were
developed, at first, to allow for Capua to be tested.
The second goal of these tools was to allow for
software development. Therefore, they do
present some bugs and, as a developer, you have to
be careful to use these tools exactly as this text
explains their use. Know that these bugs are being
addressed. We are planning to re-write some of these.

## Compiler
We do not currently have a compiler. This is one of the major area where
open source contribution would be more than welcome!

## Assembler.py
##### Overview
Capua has its own assembler. It’s easy to use. The implementation is fairly
straightforward. Be extra careful to
fully respect the syntax described here since error
messages might not always be easy to understand.
Every part of an instruction needs
to be separated by a white space. 

When running the assembler, the input file is
transformed into a .o file. Please note that, the
extension has been chosen because of the historic
signification of a .o file. Capua is not actually using the .o file format. The file format used by the
Capua tool chain has been made (designed would
be an overstatement here) with the intent of
being able to link multiple files together in order to
form a flat binary file. The current format is also
very simple to understand and is a mix of XML and
binary data. This format is not perfect and will change in the future.
A full description of this format is available lower in this document.

##### Writing assembly
This part concentrate not on the code but on assembler
directives. These directives are to be used when writing code.

* "symbolName:"
    * An arbitrary name, by itself, on a line
    followed by a “:” character indicates a
    symbol. The assembler will add this in the
    symbol list and code will be able to
    reference symbolName anywhere an
    immediate could be used. Note that to use
    the symbol name in code No “:” is
    required after the symbol name when using
    the name in code. For example:
    **MOV stackAddress $A**
    Would result in the linked address of
    stackAddress being put as an immediate
    value in the mov instruction displayed. Colons
    are not permitted to be a part of the label name
    itself. Thus the only colon should be the last
    character on the line when labels are declared initially. Symbols 
    may also be used in loops:
    **JMP <> loopStart**
* ".global symbolName"
    * Will allow the assembler to add a symbol to
    the external symbols list. This ultimately allows the linker to use this symbol
    for linking with external files
* ";"
    * The “;” character, like in many other
    assembly languages, indicates a comment.
    These can either be on a line of their own or
    at the end of a line, after an instruction. Note that
    anything following a semi-colon ";" character will be ignored
    by the assembler. 
    
* ".dataAlpha"
    * This can be used anywhere as long as it sits
    on a line of it’s own. This directive is
    followed by a white space and by free
    formed text. The text does not need to be
    quoted. If you do, the quotes will simply be included in your text.
    The string ends at the end of the line. The
    assembler will add a 0x00 termination
    character at the end of the string at
    assembling time. Usage example
    testString:
    **.dataAlpha This is a test string**
    *Please note that comments can't be added after a .dataAlpha 
    declaration. If you do, comments will simply be included in the string.*
* ".dataMemRef"
    * This is similar to .dataNumeric except that it
    allows the programmer to specify a memory reference.
    When the code is linked, the memory reference will
    be replaced with the address of the said reference.
    This is mainly used to create interrupt vectors.
    This is used like this: **.dataMemref randomLabel**
* ".dataNumeric"
    * This is the same as .dataAlpha except that it
    allows the programmer to use 32 bit
    numeric values. Usage example:
    testInt:
    .dataNumeric 0xFFFFFFFF
* "$"
    * Is the register prefix. Every register, when
    used in an assembly instruction, must be
    preceded by the “$” character
* "#"
    * Is the immediate prefix. Every immediate
    value (except when using the .dataNumeric directive) must be
    preceded by the “#” character.
    Multiple variants are possible for immediate
    values:
    \#0xFF
    \#255
    \#-1
    \#0b11111111

##### Short program example
The following table simply shows a working
program that will calculate the length of a string.
```
; File Length.casm
; This will calculate the length of testString
.global start
start:
    JMP <> stackSetup   ;Jump over the string
    
testString:
.dataAlpha This is a test string

stackSetup:
    MOV stack $S        ;Stack is now usable
codeStart:
    PUSH testString
    CALL strlen
    SUB #0x4 $S         ;stack reset
end:

;Following is the length calculation
;strlen(stringPointer)
strlen:
    MOV $S $A
    SUB #0x4 $A         ;Calculate parameter offset
    MEMR [4] $A $A      ;Get parameter in register A
    MOV $A $C           ;Keep pointer to string start
lenover:
    MEMR [1] $A $B
    CMP #0x00 $B        ;are we at the end of the string?
    JMP <E> gotlen
    ADD #0x1 $A
    JMP <> lenover      ;not at the end, jump back
gotlen:
    SUB $C $A           ;A will hold the len of the string at this point.
    RET                 ;return value in register A

; Stack is at the end of the program.
; No risk of overwriting the program
stack:
```

In order to assemble this file, one would use the following command:
> python3 Assembler.py -i strlen.casm -o strlen.o

You can get help about the assembler usage by
executing the assembler with the “-h” option.

## Linker.py
##### Overview
Capua also has its own linker. This linker is
intended to be used to assist in the creation of flat
binary file. The linker can link multiple files
together. Since the binary files produced by the
linker are meant to be used “bare metal”, no
dynamic linking is available. All addresses, after
linking, will be hardcoded into the resulting binary
file. This means that the linker needs to know, at
linking time, the memory address where the binary
is to be loaded in memory. Not providing the load
address will result in the binary being linked to be
loaded at the MEMORY_START_AT address
(default is 0x40000000). This is fine for testing
purposes since the execution unit starts fetching
instructions at that address.
##### Beware!
When linking multiple files together, the order in
which you tell the linker to input the files IS OF
MAJOR IMPORTANCE. The files will be put into
the final binary in the same order as you input them
into the linker.
##### Note about symbols
The linker will output a “ .sym ” file in the same
folder as the final binary. That file is simply a
symbol and address listing. This file, if available,
will be loaded when you run the binary in the
debugger and will allow you to use symbol names
instead of memory addresses when executing the
binary in the context of the debugger. Note that all
the symbols present in that file have been modified
with the name of their origin file as prefix. The
symbol names themselves are also transformed to
upper case.
##### Usage
In order to link the .o file previously generated, one would use the following command:
> python3 Linker.py -i strlen.o -o strlen.bin

In the case where one would like to link multiple files together, multiple
.o files can be added to the input files. Like:
> python3 Linker.py -i main.o subFile.o -o main.bin

## Debugger.py
The debugger is the programmer interface into the VM. Launching the debugger
is the same as launching the VM.
The debugger is really simple. It has many of the
basic features that other debuggers offer. At current
time, three big limitations exist. The first is that you
can’t modify a register value or an in memory value
through the debugger. You can also not “step over”
a function call easily. To do so, you would have to
put a break point at the return of the function call.
The last one is that you can’t simply “reload” the
program without relaunching the debugger. All of
these features are noted and will be added at some
point in the future (feel free to contribute code!). Using the debugger is simple
and very straightforward. Simply run the debugger
with the “-h” option to learn how to launch it. Once
launched, the debugger will break right at the
beginning of your binary file. You can access the
debugger help menu by typing “h” or “help” at the
debugger prompt.

In order to launch the previously linked file in the debugger, one would use
the following command:
> python3 Debugger.py -i main.bin

##### Important note about virtual boot
If the debugger is launched without any parameters. It will launch using the firmware code
present in CapuaEnvironment/firmware.bin. In order for this to work, one needs to assemble and link
CapuaEnvironment/firmware.casm into CapuaEnvironment/firmware.bin. This firmware will then attempt
a disk validation. Should the disk validation succeed, it will load the first sector of the disk
at MEMORY_START_AT (default is 0x40000000) and will transfer the execution to this newly loaded code.
This aims at simulating a boot process. The firmware code can be inspected for more details.

## HardDriveCreator.py
The hard drive creator tool is nothing more than a helper tool that will generate an
empty binary file of the proper length for the VM. It will check the VM configuration
and generate the file according to the hard drive size configured within. Default configuration
is for 1MB.
In order to work properly, the VM needs a HD.bin (hard drive file) to be located 
at the root of the project directory. You can generate this file with the following
command:
> python3 HardDriveCreator.py -o HD.bin

The absence of the HD.bin at the root of the project will cause a failure when
launching the VM (either with or without the firmware).

# Interrupts handling in Capua
Capua allows for interrupts to be handled from both hardware and software source.
In order for interruption to be handled, they first need to be enabled. At boot time,
interrupt handling is disabled. One can enable interrupt handling by using the following
instruction
> ACTI

Inversely, interrupt handling can be disabled by using
> DACTI

On Capua, interrupt handling is done with the help of the Interrupt Vector Register (IVR).
The IVR has to be set with a pointer to a vector of 32 bit pointers to interruption handling
routine. Every hardware interrupt is associated with a number (software interrupt specify their own).
When a hardware interrupt occurs, interrupt handling becomes disabled and execution resumes
at the interrupt handling routine corresponding to the interrupt number. This is almost the same
for software interrupts. The handling of interruption is not disabled when handling
a software interrupt. This is so the system can receive hardware interrupts while handling
a software interrupt. The handling routine is selected from the interrupt vector following this formula:
```
IN is the Interrupt Number
Vector is Address of the interrupt vector
Routine is the address where the address of the handling routine is found for an interrupt number

Routine = Vector + (IN * 4)
```

It is of the utmost importance that the programmer understands that, while handling
an hardware interrupt, all interrupts are disabled on the system. Most devices on Capua will cache
interrupts and wait in order to be able to deliver these. However, this is not guaranteed.
Some interrupts could be lost if the code stays for an extended period of time
within an interrupt handling routine. At the end of the routine, in the case of a hardware interrupt
handling routine, a special return instruction is used:
>HIRET

The HIRET instruction does a little more than just return. It also reactivates interrupts handling
on the core and make sure that the flags are reset to the same value they were before the handling
of the interruption begun. HIRET is not to be used to return from software interrupt handling routines.

Returning from a software interrupt handling routine is the same as returning from a function. Simply
use the RET instruction.
##### Interrupt configuration
On capua, as of now, only the 4 first interrupts vectors are used. However, vectors 0 to 31 should
all be considered reserved. Software interrupts handler should therefore not use them. Here is the
current interrupt mapping:

* 0 is mapped to INTERRUPT_CLOCK
    * Interrupt 0 is generated by the interrupt clock at the configured interval
* 1 Is mapped to INTERRUPT_KEYBOARD
    * Interrupt 1 is generated by the terminal keyboard whenever a key is pressed
* 2 Is mapped to INTERRUPT_HARD_DRIVE_DONE_READ
    * Interrupt 2 is generated by the hard drive whenever a read operation is over
* 3 Is mapped to INTERRUPT_HARD_DRIVE_DONE_WRITE
    * Interrupt 3 is generated by the hard drive whenever a write operation is over


###### Important note:
One might not understand why he/she would go to the extent of setting up interrupt
handling for software. As of now, there is no difference, or at least close to no difference between
software interrupts and function calls. However, please know that, support for virtual memory
and multiple levels of privilege are on the Capua development road map. Therefore, it is 
currently recommended to use the interruption facilities for everything that would normally
be provided to the user from the kernel of an operating system. This will hopefully 
prevent future code breakage.

The following code snippet shows how to handle both software and hardware interrupts. It also
shows how to setup the code in order to be able to handle interrupts.
```
; This example shows how multiple hardware interrupts
; can be mapped to the same code. It also shows how to
; properly handle software interrupts and setup the
; IVR
.global start:

start:
    MOV end $S                      ; Stack grows up, setting S to the end is generally safer
                                    ; The stack needs to be configured for interrupt handling to work
    MOV vector $A
    SIVR $A                         ; Set the interrupt vector to "vector"
    ACTI                            ; Interrupt handling activation
    int #4                          ; Software interrupt #4
                                    ; Since IVR is set to vector, the routine used when int #4 is executed will be
                                    ; determined by:
                                    ; routine = vector + (4 * 4)
                                    ; Since each entry is 4 bytes long
                                    ; routine = testHandler

loop:
    NOP
    JMP <> loop

clockHandler:                   ; All hardware interrupts are mapped to this empty handler
keyboardHandler:
hardDriveReadHandler:
hardDriveWriteHandler:
    HIRET

testHandler:                    ; Just a demonstrative software handler
    MOV #0xFFFFFFFF $A
    MOV #0xAAAAAAAA $B
    RET

vector:                         ; The vector is built using the dataMemRef marker
.dataMemRef clockHandler
.dataMemRef keyboardHandler
.dataMemRef hardDriveReadHandler
.dataMemRef hardDriveWriteHandler
.dataMemRef testHandler
end:
```

# Memory Mapped Hardware
The virtual machine offers support for memory
mapped hardware. Memory mapped hardware is
accessible at specific memory addresses. Different
addresses have different meanings. The way each device
behaves is specific to a single device.

## Clock
```
Mapping address: 0x20000100
Allowed operation(s): Read
```
The clock aims at providing the VM user with a source of entropy. It is not meant
to provide time to the user. Reading 4 bytes at mapped address will provide a value
based on the following python code:
>int((time.time() * 10000000)) & 0xFFFFFFFF

The following snippet shows how to access the clock:
```
MOV #0x20000100 $A
MEMR [4] $A $B          ; The clock value will be in register $B
```

## Interrupt Clock
```
Mapping address: 0x20000300
Allowed operation(s): Read/Write
```
When writing 4 bytes at a mapped address, the Interrupt Clock will start generating
clock hardware interrupts at a frequency (milliseconds) set by the 4 bytes value written at the
mapped address. In order for the core to receive the generated interrupts, 
interrupts must have been activated on the core. No interrupts are generated (even
if interrupts are activated) if no write operations were made at the mapped address.

The following snippet shows how to set the interrupt clock frequency:
```
MOV #0x20000300 $A
MEMW [4] #0xFF $A       ; Will set the frequency to 255 ms
```
## Hard Drive
```
Mapping address: 0x20000400
Allowed operation(s): Read/Write
```
One should note an important element. The hard drive it self is not mapped at the given
mapped address. The hard drive controller is. It is the controller
that is to be used to access the hard drive.

A specific structure needs to be written at mapped address for access to the hard drive
to be possible. For every access operation, the structure needs to be set properly.

Hard drive access operation structure:

* 0x20000400 = 0x0 for a read operation or 0x01 for a write operation
* 0x20000404 = LBA to be written or read (512 byte offset number)
* 0x20000408 = Memory Address to write TO or to read FROM
* 0x2000040C = Trigger memory action = When this is set to 1, the action is triggered
    * This needs to be manually reset to 0 in between hard drive access operation otherwise 
    any new write to the mapped address structure will cause an operation on the disk

Following an operation on the drive, the corresponding interrupt will be generated by the
drive and sent to the core.

The following code snippet shows how to read a block of data from the drive:
```
; This will test the correct working order of the hard drive read operation
.global start

start:
    MOV readBuffer $S
    ADD #1024 $S            ; Set the stack (needs to be set to handle interrupts
    MOV vector $A
    SIVR $A                 ; Set the Interrupt vector
    ACTI                    ; activates the interrupts
    
    MOV #0x20000400 $A
    MEMW [4] #0x0 $A        ; Set read action
    ADD #4 $A
    MEMW [4] #0x0 $A        ; Set LBA
    ADD #4 $A
    MEMW [4] readBuffer $A ; Set destination buffer
    ADD #4 $A
    MEMW [4] #0x01 $A       ; Set the trigger

waitLoop:
    NOP
    JMP <> waitLoop

clockHandler:
    HIRET
keyboardHandler:
    HIRET
hardDriveReadHandler:
    ; Do nothing in the handler, this is just an example
    HIRET

hardDriveWriteHandler:
    HIRET

vector:
.dataMemRef clockHandler
.dataMemRef keyboardHandler
.dataMemRef hardDriveReadHandler
.dataMemRef hardDriveWriteHandler

readBuffer:
end:
```

Writing to the drive is very similar except that one needs to trigger the write operation.

## Terminal
```
Mapping address: 0x20001000 (Display), 0x20001800 (Keyboard)
Allowed operation(s): Read/Write
```
The terminal is a special device. It allows output (on the display) and input (from the keyboard).
Therefore, it is essentially 2 devices in 1.
##### Terminal - display
The display is 80x25 characters. Character 0 (x=0, y=0, or top left corner) is mapped at address 0x20001000.
Character 1 (x=1, y=0) is mapped at address 0x20001001. The memory is fully linear. This
means that character 0 from line 1 (x=0, y=1) is the 80th character. This is mapped at
address 0x20001000 + 80. In order to display a character to the screen one needs to
write the ascii code value for a character to the appropriated address.

The following snippet shows an example of code that will display "ABCD" at the
top left corner of the screen.
```
; This will print ABCD on the screen
.global codeStart

codeStart:
    MOV #0x20001000 $A      ; Display address
    MOV #0x41424344 $B      ; ABCD ascii code
    MEMW [4] $B $A
```
##### Terminal - keyboard
The keyboard requires the interrupts to be activated and configured in order to work.
A proper keyboard handler needs to be provided. When a user presses a key on the 
keyboard, a keyboard interrupt is generated and control is transferred to the keyboard
handler. At that point, the scan code (beware, scan code, not character) for the key
that was pressed on the keyboard will be available for read at address 0x20001800.
In the case where an interrupt for a key press can't be delivered to the core (if the core 
is already handling another hardware interrupt for example), the
keyboard has a buffer for 20 key presses and will try delivering the interrupt later as long
as its 20 key buffer is not full. When the buffer is full, the oldest key strokes will be flushed out.

The following snippet show an example of keyboard read and interrupt handling.
```
; This will print scan code to the top left of the screen
; if a scan code does not happen to map to a printable
; character, nothing will be visible.
.global start

start:
    MOV end $S
    MOV vector $A
    SIVR $A
    ACTI

loop:
    NOP
    JMP <> loop

clockHandler:
    HIRET

keyboardHandler:
    MOV #0x20001800 $A
    MEMR [1] $A $B
    MOV #0x20001000 $A
    MEMW [1] $B $A
    HIRET

vector:
.dataMemRef clockHandler
.dataMemRef keyboardHandler
end:
```
## Capua ".o" file format
The Capua file format is very simple. For obvious reasons, there are bugs 
associated with the file format. This will be addressed when we update this
format. For now, this is usable in most cases.

Here is the general form:

```
<AssemblySize></AssemblySize>
<ExternalSymbols>
    <refName></refName>
    <refAdd></refAdd>
    ...
</ExternalSymbols>
<InternalSymbols>
    <refName></refName>
    <refAdd></refAdd>
    ...
</InternalSymbols>
<Text>...</Text>
</code>
```

The following explains the various parts of the file format.

* AssemblySize
    * This tag holds the projected size of the final
    linked version of this file. The size is kept big
    endian binary encoded inside the tag. The size
    calculation was put in the assembler since it was
    easier and faster to put it there. Also, the info is
    readily available for the linker when this one
    needs to calculate a file wide address across
    multiple files that need to be linked together.
* ExternalSymbols
    * This tag holds a list of tags (refName/refAdd
    couples). The symbols present in the
    ExternalSymbols list are seen as “global” and,
    therefore, are available to the linker when linking
    multiple object together
* InternalSymbols
    * This tag is the same as ExternalSymbols except
    that the symbols listed in this tag are not available
    to the linker when linking multiple files together.
    This was originally made that way to prevent
    name collision on the global (external) scale at
    linking time. The linking process later adds the
    source file name to the symbols so that all
    symbols are available (internal and external) when
    using the debugger while still avoiding collision.
* refName
    * A refName tag must be inside of an
    ExternalSymbols or an InternalSymbols tag. It
    also has to be followed by a refAdd tag. The
    refName simply holds a text version of the
    symbol name. The symbol name is determined
    by memory reference/naming in the assembly
    code written by the programmer
* refAdd
    * This follows a refName tag and simply
    indicates the offset where the symbol can be found
    from the 0 address (relative to the beginning of
    the current file). Note that the offset is relative to
    a fully linked file. Not to an object file. That
    address eventually replaces the symbol name when
    the file is linked
* Text
    * The text tag holds the assembled binary of the
    object file. A close look will reveal the presence of
    symbols names inside the text tag. These are
    replaced at linking time. The symbols are present
    in the text section like: “:SymbolName:”. This is
    not a perfect (not even a good one) solution but
    it was fast. (Always keep in mind these tools were
    originally written to test the execution unit, not to
    write usable code with them)

- - -
This file is part of Spartacus project
Copyright (C) 2017  CSE

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




