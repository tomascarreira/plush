import sys

from parser import parse, Declaration, Type, TypeEnum
from typeChecker import verify, Context as TypeContext
from interpreter import eval, Context as ValueContext
from pretty_print import pp_ast

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Reading file: ", sys.argv[1])
        with open(sys.argv[1]) as file:
            input = file.read()
            ast = parse(input)
            verify(TypeContext(), ast)
            pp_ast(ast)
            eval(ast, ValueContext())

    else:
        while True:
            input = sys.stdin.readline()
            ast = parse(input, parserStart="statement")
            typeCtx = TypeContext()
            typeCtx.addFuncDef(Declaration("print_int", [("val", "n", Type(TypeEnum.INT))], Type(TypeEnum.VOID)))
            typeCtx.addFuncDef(Declaration("print_bool", [("val", "n", Type(TypeEnum.BOOL))], Type(TypeEnum.VOID)))
            typeCtx.addFuncDef(Declaration("print_int_array", [("val", "n", Type(TypeEnum.INT, 1))], Type(TypeEnum.VOID)))
            typeCtx.addFuncDef(Declaration("int_array", [("val", "size", Type(TypeEnum.INT))], Type(TypeEnum.INT, 1)))
            typeCtx.addFuncDef(Declaration("int_array_array", [("val", "size", Type(TypeEnum.INT))], Type(TypeEnum.INT, 2)))
            verify(typeCtx, ast)
            pp_ast(ast)
            eval(ast, ValueContext())
