import sys

from parser import parse, Declaration, Type, TypeEnum
from typeChecker import verify, Context as TypeContext
from interpreter import eval, Context as ValueContext
from codegen import codegen
from pretty_print import pp_ast

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Reading file: ", sys.argv[1])
        with open(sys.argv[1]) as file:
            input = file.read()
            ast = parse(input)

        print("=====AST=====")
        verify(TypeContext(), ast)
        pp_ast(ast)

        print("=====Codegen=====")
        emitter = codegen(ast)
        print("\n".join(emitter.lines))
        print("\n".join(emitter.decls))

        outName = sys.argv[1].rsplit(".", 1)[0].rsplit("/", 1)[-1]+".ll"
        with open(outName, "w") as out:
            out.write("\n".join(emitter.lines))
            out.write("\n".join(emitter.decls))

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
