import sys

from parser import parse
from typeChecker import verify, Context
from pretty_print import pp_ast

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Reading file: ", sys.argv[1])
        with open(sys.argv[1]) as file:
            input = file.read()
            ast = parse(input)
            verify(Context(), ast)
            pp_ast(ast)

    else:
        while True:
            input = sys.stdin.readline()
            ast = parse(input, parserStart="statement")
            verify(Context(), ast)
            pp_ast(ast)
