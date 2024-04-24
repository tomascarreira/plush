import sys

from parser import parse
from typeChecker import verify, Context

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Reading file: ", sys.argv[1])
        with open(sys.argv[1]) as file:
            input = file.read()
            ast = parse(input)
            # print(ast)
            verify(Context(), ast)

    else:
        while True:
            input = sys.stdin.readline()
            ast = parse(input, parserStart="statement")
            print(ast)
            verify(Context(), ast)

