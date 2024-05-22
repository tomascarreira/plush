import sys
import os

from parser import parse, FunctionDeclaration, Type, TypeEnum
from typeChecker import verify, Context as TypeContext
from interpreter import eval, Context as ValueContext
from codegen import codegen
from pretty_print import pp_ast

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as file:
            input = file.read()
            ast = parse(input)

        pp_ast(ast)
        verify(TypeContext(), ast)
        # print("=====AST=====")
        if len(sys.argv) > 2:
            pp_ast(ast)
            exit(0)

        emitter = codegen(ast)
        # print("=====Codegen=====")
        # print("\n".join(emitter.lines))
        # print("\n".join(emitter.decls))

        outName = sys.argv[1].rsplit(".", 1)[0].rsplit("/", 1)[-1] + ".ll"
        with open(outName, "w") as out:
            out.write("\n".join(emitter.lines))
            out.write("\n".join(emitter.decls))

        os.system(f"llc {outName} -o {outName.rsplit('.', 1)[0].rsplit('/', 1)[-1]+'.s'}")  
        os.system("make c_functions")  
        os.system(f"gcc -g -c {outName.rsplit('.', 1)[0].rsplit('/', 1)[-1]+'.s'} -o {outName.rsplit('.', 1)[0].rsplit('/', 1)[-1]+'.o'}")
        os.system(f"gcc -g -lm c_functions.o {outName.rsplit('.', 1)[0].rsplit('/', 1)[-1]+'.o'} -o {outName.rsplit('.', 1)[0].rsplit('/', 1)[-1]}")

    else:
        while True:
            input = sys.stdin.readline()
            ast = parse(input, parserStart="statement")
            typeCtx = TypeContext()
            typeCtx.addFuncDef(FunctionDeclaration("print_int", [("val", "n", Type(TypeEnum.INT))], Type(TypeEnum.VOID)))
            typeCtx.addFuncDef(FunctionDeclaration("print_bool", [("val", "n", Type(TypeEnum.BOOL))], Type(TypeEnum.VOID)))
            typeCtx.addFuncDef(FunctionDeclaration("print_int_array", [("val", "arr", Type(TypeEnum.INT, 1)), ("val", "size", Type(TypeEnum.INT))], Type(TypeEnum.VOID)))
            typeCtx.addFuncDef(FunctionDeclaration("int_array", [("val", "size", Type(TypeEnum.INT))], Type(TypeEnum.INT, 1)))
            typeCtx.addFuncDef(FunctionDeclaration("int_array_array", [("val", "size", Type(TypeEnum.INT))], Type(TypeEnum.INT, 2)))
            typeCtx.addFuncDef(FunctionDeclaration("pow", [("val", "b", Type(TypeEnum.INT)), ("val", "e", Type(TypeEnum.INT))], Type(TypeEnum.INT)))
            verify(typeCtx, ast)
            pp_ast(ast)
            eval(ast, ValueContext())
