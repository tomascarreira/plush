from parser import Node, Program, Declaration, VariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, FunctionCall, Binary, Unary, Ident, Literal
from parser import Type, BinaryOp, UnaryOp

old_type = type

class Context:
    def __init__(self):
        self.stack = [{}]
        self.funcDefs = {}

    def add(self, var, type):
        self.stack[-1][var] = type

    def remove(self, var):
        self.stack[-1].pop(var)

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
        return funcDefs.get(ident, None)

        

# !! Maybe is necessary to reverse the the nodes in the ast because the parsing puts the nodes in list in the inverse order !!
# To verify the correct use of var and val, context may to save if a variable is var or val, for know i only will check the type

def verify(ctx: Context, node: Node):
    # After this match we can check the ctx to verify if a main function exists, if we do that here
    match node:
        case Program(decs, defs):
            print("decs: ", decs)
            print("defs: ", defs)
            [verify(ctx, decl) for decl in decs]
            [verify(ctx, defi) for defi in defs]

        # declaration are always correct for the type checker ??
        case Declaration(ident, args, retType):
            pass

        case VariableDefinition(varType, ident, type, rhs):
            assert(type == verify(ctx, rhs))
            ctx.add(ident, type)

        case FunctionDefinition(functionHeader, codeBlock):
            # here we can check if a name of a function repeats
            # change here to check for val and var use
            # Maybe wrong variables get add to the old scope not the newone
            [ctx.add(ident, type)  for (varType, ident, type) in functionHeader.args]
            # TODO verify the return types of the function
            # check if return type equals the value return by the code block
            [ctx.add(ident, type)  for (varType, ident, type) in functionHeader.args]

        case CodeBlock(statements):
            ctx.newScope()
            [verify(ctx, stm) for stm in statements]
            ctx.popScope()

        case Assignment(ident, indexing, rhs):
            type = verify(ctx, rhs) 
            # getType return None if variable doesnt exist in the context, handle that error
            ctxType = ctx.getType(ident)
            assert(type, ctxType)

        case While(guard, codeBlock):
            assert(verify(ctx, guard) == Type.Bool)
            verify(ctx, codeBlock)

        case If(condition, thenBlock, elseBlock):
            assert(verify(ctx, guard) == Type.Bool)
            verify(ctx, thenBlock)
            verify(ctx, elseBlock)

        case FunctionCall(ident, args):
            # can return None, do error check
            funcDef = ctx.getFunDef(ident)
            assert(len(funcDef.args) == len(args))
            for def, (_, _, call) in zip(args, funcDef.args):
                assert(def == call) 
            return funcDef.retType

        case Binary(op, left, right):
            if op in [BinaryOp.EXP, BinaryOp.MULT, BinaryOp.DIV, BinaryOp.REM, BinaryOp.PLUS, BinaryOp.PLUS]:
                pass

            elif op in [BinaryOp.LT, BinaryOp.GT, BinaryOp.GTE, BinaryOp.EQ, BinaryOp.NEQ]:
                pass

            else:
                pass

        case Unary():
            pass

        case Ident():
            pass

        case Literal():
            pass
