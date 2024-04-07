import sys

from parser import parse

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Reading file: ", sys.argv[1])
        with open(sys.argv[1]) as file:
            input = file.read()
            parse(input)
    else:
        while True:
            input = sys.stdin.readline()
            parse(input, parserStart="codeBlock")

