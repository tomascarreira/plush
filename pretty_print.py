from parser import Node, Program, FunctionDeclaration, StructDeclaration, GlobalVariableDefinition, FunctionDefinition, CodeBlock, Assignment, Variable, ArrayIndexing, FieldAccessing, While, If, VariableDefinition, FunctionCall, Binary, Unary, StructInit, Ident, Literal, Field
from parser import Type, BinaryOp, UnaryOp

def pp_ast(node, depth=0):
    print("  "*depth, end="")
    match node:
        case Program(decs, defs):
            for dec in decs[::-1]:
                pp_ast(dec)

            for def_ in defs[::-1]:
                pp_ast(def_)

        case FunctionDeclaration(ident, args, retType):
            print(f"Function Declaration {ident} {retType}")
            if len(args) > 0:
                print("\n".join(f"  Function Argument {arg[0]} {arg[1]} {arg[2]}" for arg in args))

        case StructDeclaration(ident, fields):
            print(f"Struct Declaration {ident}")
            print("\n".join(f"  Struct Field {varType} {name} {type}" for name, varType, type in fields))

        case GlobalVariableDefinition(varType, ident, type, rhs):
            print(f"GlobalVariable Definition {varType} {ident} {type}")
            pp_ast(rhs, depth+1)

        case FunctionDefinition(functionHeader, codeBlock):
            pp_ast(functionHeader, depth)
            pp_ast(codeBlock, depth+1)

        case CodeBlock(statements):
            print("CodeBlock")
            for stat in statements[::-1]:
                pp_ast(stat, depth+1)

        case Assignment(lhs, rhs, glob):
            print(f"Assignment")

            match lhs:
                case Variable(ident):
                    pp_ast(lhs, depth+1)
                case ArrayIndexing(array, index):
                    pp_ast(lhs, depth+1)
                case FieldAccessing(struct, field):
                    pp_ast(lhs, depth+1)
            
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

        case VariableDefinition(varType, ident, type, rhs, shadow):
            print(f"Variable Definition {varType} {ident} {type} {'shadow' if node.shadow > 0 else ''}")
            pp_ast(rhs, depth+1)

        case FunctionCall(ident, args):
            print(f"Function Call {ident}", f"{node.exprType}" if node.exprType else "")
            for arg in args:
                pp_ast(arg, depth+1)

        case StructInit(ident, initFields):
            print(f"Struct Init {ident}", f"{node.exprType}" if node.exprType else "")
            for field in initFields:
                pp_ast(field, depth+1)

        case Binary(op, left, right):
            print(f"Binary {op}", f"{node.exprType}" if node.exprType else "")
            pp_ast(left, depth+1)
            pp_ast(right, depth+1)

        case Unary(op, expression):
            print(f"Unary {op}", f"{node.exprType}" if node.exprType else "")
            pp_ast(expression, depth+1)

        case Ident(ident):
            print(f"Ident {ident}", f"global" if node.glob else "", f"{node.exprType}" if node.exprType else "", f"shadow" if node.shadows > 0 else "")

        case Literal(val, type):
            print(f"Literal {val} {type}", f"{node.exprType}" if node.exprType else "")

        case Field(ident, type, index):
            print(f"Field {ident}")

        case Variable(ident):
            pp_ast(ident, depth+1)

        case ArrayIndexing(array, index):
            print(f"Array Indexing", f"{node.exprType}" if node.exprType else "")
            pp_ast(array, depth+1)
            pp_ast(index, depth+1)

        case FieldAccessing(struct, field):
            print(f"Field Accessing ", f"{node.exprType}" if node.exprType else "")
            pp_ast(struct, depth+1)
            pp_ast(field, depth+1)

