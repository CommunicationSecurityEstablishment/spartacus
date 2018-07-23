# Spartacus Compiler Info
## Supported features
The compiler currently supports the following features:

* Integer data type
* Char data type
* Variable assignment
* If statements
* While loops
* Return statements
* Arrays
* Function calls
* Multiple function declaration
* Pointers
* Single-line comments (in-line comments also valid)

##Restrictions
The compiler currently has some restrictions:

* Currently, arrays may only be indexed with hard coded integers, not variables.
* If statement and while loop operands can't contain parentheses (we may opt to remove the requirement
for parentheses to fix this).
* Math expressions may only have a maximum of 7 operands.
* Function calls can't be used in complex variable assignment. They can only be used if it's the only operand.
* Pointers can't dereference other pointers.
* Array values must be assigned directly after array variable declaration. However, specific array indices can be 
assigned any time
* Only array indices may be passed into functions as arguments at the moment
* Functions called within another function must already exist before the call
- - -
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