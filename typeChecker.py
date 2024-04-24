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

        

# !! Maybe is necessary to reverse the the nodes in the ast because the parsing puts the nodes in list in the inverse order !!
# To verify the correct use of var and val, context may to save if a variable is var or val, for know i only will check the type

def verify(ctx: Context, node: Node):
    # After this match we can check the ctx to verify if a main function exists, if we do that here
    match node:
        case Program(decs, defs):
            [verify(ctx, decl) for decl in decs[::-1]]
            [verify(ctx, defi) for defi in defs[::-1]]

        # declaration are always correct for the type checker ??
        case Declaration(ident, args, retType):
            [ctx.addFuncDef(node)]

        case VariableDefinition(varType, ident, type, rhs):
            assert(type == verify(ctx, rhs))
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
            verify(ctx, codeBlock)
            ctx.remove(functionHeader.ident)
            [ctx.remove(ident)  for (_, ident, _) in functionHeader.args]

        case CodeBlock(statements):
            ctx.newScope()
            # inverse the order of the statementes because the parsing puts them in reverse order
            [verify(ctx, stm) for stm in statements[::-1]]
            ctx.popScope()

        case Assignment(ident, indexing, rhs):
            type = verify(ctx, rhs) 
            # TODO: make it work for multiple indexings, for now only works with a single indexing, 
            # Hint: find the number of indexings and remove that number from the front of the list
            if indexing:
                type = type[1:]
            ctxType = ctx.getType(ident)
            if not type:
                ctx.add(ident, type)
            # TODO: handle when there is no return type
            if ctxType == Special.RETURN_VAR:
                assert(verify(ctx, rhs) == ctx.getFunDef(ident).retType)
            else:
                assert(type == ctxType)

        case While(guard, codeBlock):
            assert(verify(ctx, guard) == [Type.BOOL])
            verify(ctx, codeBlock)

        case If(condition, thenBlock, elseBlock):
            assert(verify(ctx, condition) == [Type.BOOL])
            verify(ctx, thenBlock)
            verify(ctx, elseBlock)

        case FunctionCall(ident, args):
            # can return None, do error check
            funcDef = ctx.getFunDef(ident)
            assert(len(funcDef.args) == len(args))
            for call, (_, _, defiType) in zip(args, funcDef.args):
                callType = verify(ctx, call)
                assert(defiType == callType) 
            return funcDef.retType

        case Binary(op, left, right):
            lType = verify(ctx, left)
            rType = verify(ctx, right)

            if op in [BinaryOp.EXP, BinaryOp.MULT, BinaryOp.DIV, BinaryOp.REM, BinaryOp.PLUS, BinaryOp.MINUS]:
                if lType == [Type.FLT] or rType == [Type.FLT]:
                    return [Type.FLT]
                elif lType == [Type.INT] and rType == [Type.INT]:
                    return [Type.INT]

            elif op in [BinaryOp.LT, BinaryOp.GT, BinaryOp.GTE, BinaryOp.EQ, BinaryOp.NEQ]:
                if lType == [Type.FLT] or rType == [Type.FLT]:
                    return [Type.BOOL]
                elif lType == [Type.INT] and rType == [Type.INT]:
                    return [Type.BOOL]

            else:
                if lType == [Type.BOOL] and rType == [Type.BOOL]:
                    return [Type.BOOL]

            assert(False)

        case Unary(op, expression):
            if op == UnaryOp.NEGATION:
                type = verify(ctx, expression)
                if type in [[Type.INT], [Type.FLT]]:
                    return type
                else:
                    assert(False)

            elif op == UnaryOp.NOT:
                assert(verify(ctx, expression) == [Type.BOOL])
                return [Type.BOOL]

            else:
                exit(3)

        case Ident(ident):
            # TODO: handle when variable doesnt exist (is None)
            return ctx.getType(ident)

        case Literal(val, type):
            return type
