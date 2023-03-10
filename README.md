# Cimple language compiler
Python script that converts a program written in Cimple into MIPS Assemply and C.

## Motivation
The script was developed for the purposes of an undergraduate class in Computer Science and Engineering Department of University of Ioannina and it aims to familirize the student with the stages of program compilation.

## Requirements
+ [Python](https://www.python.org/)

## Description
The script uses a .ci file as input and implements lexical analysis, syntactic analysis, semantic analysis, intermediate code generation and final code generation using the Cimple language that is a subset of C.

## Usage
1. Run python3 cimple.py filename (where filename is the name of a .ci file)
2. The results prodeces a .txt files containing the symbols' array, an .asm file that is the result of the compiling from the .ci file and if the Cimple code does not include functions, a .c file is produced with the code compiled in C.

## Contributors
+ [Marios Iakovidis](https://github.com/mariosjkb)
+ [Theofilos-Georgios Petsios](https://github.com/teopets)