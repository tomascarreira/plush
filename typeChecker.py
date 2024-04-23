from parser import Node, Program, Declaration, VariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, FunctionCall, Binary, Unary, Ident, Literal
from parser import Type, BinaryOp, UnaryOp

old_type = type

class Context:
    def __init__(self):
        self.stack = [{}]

    def push(self, var, type):
        self.stack[-1][var] = type

    def newScope(self):
        self.stack.append({})

    def popScope(self):
        self.stack.pop()

    def getType(self, ident):
        for scope in self.stack[::-1]:
            if ident in scope:
                return scope[ident] 

        return None

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
            ctx.push(ident, type)

        case FunctionDefinition(functionHeader, codeBlock):
            # here we can check if a name of a function repeats
            # change here to check for val and var use
            [ctx.push(ident, type)  for (varType, ident, type) in functionHeader.args]
            verify(ctx, codeBlock)

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

        case FunctionCall():
            pass

        case Binary():
            pass

        case Unary():
            pass

        case Ident():
            pass

        case Literal():
            pass
