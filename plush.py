import sys

from parser import parse
from typeChecker import verify, Context
from parser import Node, Program, Declaration, VariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, FunctionCall, Binary, Unary, Ident, Literal
from parser import Type, BinaryOp, UnaryOp

def pp_ast(node, depth=0):
    print("  "*depth, end="")
    match node:
        case Program(decs, defs):
            for dec in decs[::-1]:
                pp_ast(dec)

            for def_ in defs[::-1]:
                pp_ast(def_)

        case Declaration(ident, args, retType):
            print(f"Function Declaration {ident} {retType}")
            print("\n".join(f"  Function Argument {arg[0]} {arg[1]} {arg[2]}" for arg in args))

        case VariableDefinition(varType, ident, type, rhs):
            print(f"Variable Definition {varType} {ident} {type}")
            pp_ast(rhs, depth+1)

        case FunctionDefinition(functionHeader, codeBlock):
            pp_ast(functionHeader, depth)
            pp_ast(codeBlock, depth+1)

        case CodeBlock(statements):
            print("CodeBlock")
            for stat in statements[::-1]:
                pp_ast(stat, depth+1)

        case Assignment(ident, indexing, rhs):
            print(f"Assignment {ident}")

            if indexing:
                print(f"{depth}", "  "*depth, end="")
                print("  ", "Indexing")
                pp_ast(indexing, depth+2)

            pp_ast(rhs, depth+1)


        case While(guard, codeBlock):
            print("While")
            pp_ast(guard, depth+1)
            pp_ast(codeBlock, depth+1)

        case If(condition, thenBlock, elseBlock):
            print("If")
            pp_ast(condition, depth+1)
            pp_ast(thenBlock, depth+1)
            pp_ast(elseBlock, depth+1)

        case FunctionCall(ident, args):
            print(f"Function Call {ident}")
            for arg in args:
                pp_ast(arg, depth+1)

        case Binary(op, left, right):
            print(f"Binary {op}")
            pp_ast(left, depth+1)
            pp_ast(right, depth+1)

        case Unary(op, expression):
            print(f"Unary {op}")
            pp_ast(expression, depth+1)

        case Ident(ident):
            print(f"Ident {ident}")

        case Literal(val, type):
            print(f"Literal {val} {type}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Reading file: ", sys.argv[1])
        with open(sys.argv[1]) as file:
            input = file.read()
            ast = parse(input)
            pp_ast(ast)
            verify(Context(), ast)

    else:
        while True:
            input = sys.stdin.readline()
            ast = parse(input, parserStart="statement")
            pp_ast(ast)
            verify(Context(), ast)

