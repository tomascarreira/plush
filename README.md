# PLush

A compiler for the language plush

Tomás Carreira nº50760

## Projecture Structure

**plush.py**: entry of the program
**lexer.py**: lexer of the language
**parser.py**: parser of the language
**typechecker.py**: semantic checker of the language
**interpreter.py**: an interpreter of the language. Was used at first to test the parser. Now it is used to calculate const expressions for global variables
**codegen.py**: llvm ir code generator for the language
**pretty_print.py**: used to print the tree of the language `plush -tree program.pl`

**c_functions.c** **c_functions.h** **Makefile**: location of the external functions that can be used. the makefile build the functions into an object for linking

**setup.sh** **Dockerfile**: docker file and bash script for getting an enviroment with the dependencies required to use the compiler

**test/**: directory with a lot of small programs that test the correct implemetation of the language

## How to run the program

`./setup.sh` to build and run a docker container with all the necessary dependencies. After this the terminal will be in a new environment.
`./plush program.pl` to compile a plush program into a executable.
`./plush --tree program.pl` to print the ast of the program. This will not compile the program.
