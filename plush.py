import sys

from lexer import lex

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Reading file: ", sys.argv[1])
        with open(sys.argv[1]) as file:
            print(file.readlines())
    else:
        while True:
            lex(sys.stdin.readline())
