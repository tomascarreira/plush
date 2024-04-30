from enum import Enum

from parser import Node, Program, Declaration, VariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, FunctionCall, Binary, Unary, Ident, Literal
from parser import Type, BinaryOp, UnaryOp

old_type = type

class Special(Enum):
    RETURN_VAR = 0

class Context:
    def __init__(self):
        self.stack = [{}]
        self.funcDefs = {}

    def add(self, ident, type):
        self.stack[-1][ident] = type

    def remove(self, ident):
        self.stack[-1].pop(ident)

    def newScope(self):
        self.stack.append({})

    def popScope(self):
        self.stack.pop()

    def getType(self, ident):
        for scope in self.stack[::-1]:
            if ident in scope:
                return scope[ident] 

        return None

    def addFuncDef(self, functionHeader):
        self.funcDefs[functionHeader.ident] = functionHeader

    def getFunDef(self, ident):
        return self.funcDefs.get(ident, None)

# To verify the correct use of var and val, context may to save if a variable is var or val, for know i only will check the type
def verify_(ctx: Context, node: Node):
    match node:
        case Program(decs, defs):
            [verify_(ctx, decl) for decl in decs[::-1]]
            [verify_(ctx, defi) for defi in defs[::-1]]

        # declaration are always correct for the type checker ??
        case Declaration(ident, args, retType):
            [ctx.addFuncDef(node)]

        case VariableDefinition(varType, ident, type, rhs):
            rhsType = verify_(ctx, rhs)
            if type != rhsType:
                print(f"Righ hand side expression is type {rhsType} but its declare to have type {type}")
                exit(3)
            ctx.add(ident, type)

        case FunctionDefinition(functionHeader, codeBlock):
            # here we can check if a name of a function repeats
            # change here to check for val and var use
            # Maybe wrong variables get add to the old scope not the newone
            # Fix can be to havve a function block so it can have a diferent behaviour from codeBlock
            [ctx.add(ident, type)  for (_, ident, type) in functionHeader.args]
            # Add to the context the name of the functions so it is possible to verify the type of
            # the return, it is done in the assignment rule
            ctx.add(functionHeader.ident, Special.RETURN_VAR)
            ctx.addFuncDef(functionHeader)
            verify_(ctx, codeBlock)
            ctx.remove(functionHeader.ident)
            [ctx.remove(ident)  for (_, ident, _) in functionHeader.args]

        case CodeBlock(statements):
            ctx.newScope()
            # inverse the order of the statementes because the parsing puts them in reverse order
            [verify_(ctx, stm) for stm in statements[::-1]]
            ctx.popScope()

        case Assignment(ident, indexing, rhs):
            type = verify_(ctx, rhs) 
            # TODO: make it work for multiple indexings, for now only works with a single indexing, 
            # Hint: find the number of indexings and remove that number from the front of the list
            if indexing:
                type = type[1:]
            ctxType = ctx.getType(ident)
            if not type:
                print(f"Cannot do an assingment to a variable that does not exist")
                exit(3)
            # TODO: handle when there is no return type
            if ctxType == Special.RETURN_VAR:
                returnType = ctx.getFunDef(ident).retType
                if type != returnType:
                    print(f"type {type} does not match return type of function declared {returnType}")
                    exit(3)
            else:
                if type != ctxType:
                    print(f"Cannot assign {type} to a variable with type {ctxType}")
                    exit(3)

        case While(guard, codeBlock):
            guardType = verify_(ctx, guard)
            if guardType != [Type.BOOL]:
                print(f"Type of guard in while statement must be bool, got type {guardType}")
                exit(3)
            verify_(ctx, codeBlock)

        case If(condition, thenBlock, elseBlock):
            conditionType = verify_(ctx, condition)
            if conditionType != [Type.BOOL]:
                print(f"Type of condition in if statement must be bool, got type {conditionType}")
                exit(3)
            verify_(ctx, thenBlock)
            verify_(ctx, elseBlock)

        case FunctionCall(ident, args):
            # can return None, do error check
            funcDef = ctx.getFunDef(ident)
            if len(funcDef.args) == len(args):
                print(f"In function call expected {len(funcDef.args)} arguments, got {len(args)}")
                exit(3)
            for call, (_, argIdent, defiType) in zip(args, funcDef.args):
                if defiType != callType:
                    print(f"Expected {argIdent} argument to have type {defiType} got type {callType}")
                    exit(3)
            return funcDef.retType

        case Binary(op, left, right):
            lType = verify_(ctx, left)
            rType = verify_(ctx, right)

            if op in [BinaryOp.EXP, BinaryOp.MULT, BinaryOp.DIV, BinaryOp.REM, BinaryOp.PLUS, BinaryOp.MINUS]:
                if lType == [Type.FLT] or rType == [Type.FLT]:
                    return [Type.FLT]
                elif lType == [Type.INT] and rType == [Type.INT]:
                    return [Type.INT]
                else:
                    print(f"lhs and rhs must be int, int or int, float or float, float. Got type {lType}, {rType}")
                    exit(3)

            elif op in [BinaryOp.LT, BinaryOp.GT, BinaryOp.GTE, BinaryOp.EQ, BinaryOp.NEQ]:
                if lType == [Type.FLT] or rType == [Type.FLT]:
                    return [Type.BOOL]
                elif lType == [Type.INT] and rType == [Type.INT]:
                    return [Type.BOOL]
                else:
                    print(f"lhs and rhs must be int or float. Got type {lType}, {rType}")
                    exit(3)

            else:
                if lType == [Type.BOOL] and rType == [Type.BOOL]:
                    return [Type.BOOL]
                else:
                    print(f"lhs and rhs must be bool. Got type {lType}, {rType}")
                    exit(3)


        case Unary(op, expression):
            type = verify_(ctx, expression)
            if op == UnaryOp.NEGATION:
                if type in [[Type.INT], [Type.FLT]]:
                    return type
                else:
                    print(f"Operand of negation must be a int or float. Got type {type}")
                    exit(3)

            elif op == UnaryOp.NOT:
                if type == [Type.BOOL]:
                    print(f"Operand of negation must be a int or float. Got type {type}")
                    exit(3)
                return [Type.BOOL]

        case Ident(ident):
            # TODO: handle when variable doesnt exist (is None)
            return ctx.getType(ident)

        case Literal(val, type):
            return type

def verify(ctx: Context, node: Node):
    verify_(ctx, node)

    if not ctx.getFunDef("main"):
        print("ERROR: Program is required to have a main function")
        exit(3)

