import sys

from lexer import lex
from parser import parse

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Reading file: ", sys.argv[1])
        with open(sys.argv[1]) as file:
            input = file.read()
            lex(input)
            parse(input)
    else:
        while True:
            input = sys.stdin.readline()
            lex(input)
            parse(input, parserStart="start")

