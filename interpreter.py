from parser import Node, Program, Declaration, VariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, FunctionCall, Binary, Unary, Ident, Literal
from parser import Type, TypeEnum, VarType, BinaryOp, UnaryOp

class Context:
    def __init__(self):
        self.environment = [{}]
        self.funDefs = {}

    def newScope(self):
        self.environment.append({})

    def popScope(self):
        self.environment.pop()

    def addVal(self, ident, val):
        for scope in self.environment[::-1]:
            if ident in scope:
                scope[ident] = val
                return
        self.environment[-1][ident]= val

    def getVal(self, ident):
        for scope in self.environment[::-1]:
            if ident in scope:
                return scope[ident] 

    def addFunDef(self, ident, functionHeader, codeBlock):
        self.funDefs[ident] = (functionHeader, codeBlock)

    def getFunDef(self, ident):
        return self.funDefs.get(ident, None)

def eval(node, ctx: Context):
    match node:
        case Program(decs, defs):
            [eval(dec, ctx) for dec in decs[::-1]]
            [eval(def_, ctx) for def_ in defs[::-1]]

        case Declaration(ident, args, retType):
            pass

        case VariableDefinition(varType, ident, type, rhs):
            ctx.addVal(ident, eval(rhs, ctx))

        case FunctionDefinition(functionHeader, codeBlock):
            if functionHeader.ident == "main":
                eval(codeBlock, ctx)
            else:
                ctx.addFunDef(functionHeader.ident, functionHeader, codeBlock)

        case CodeBlock(statements):
            ctx.newScope()
            [eval(stmt, ctx) for stmt in statements[::-1]]
            ctx.popScope()

        case Assignment(ident, indexing, rhs):
            # TODO: support indexing
            ctx.addVal(ident, eval(rhs,ctx))

        case While(guard, codeBlock):
            while eval(guard, ctx):
                eval(codeBlock, ctx)

        case If(condition, thenBlock, elseBlock):
            if eval(condition, ctx):
                eval(thenBlock, ctx)
            else:
                eval(elseBlock, ctx)

        case FunctionCall(ident, args):
            funDef = ctx.getFunDef(ident)
            if not funDef:

                match ident:
                    case "print_int":
                        print(eval(args[0], ctx))
                    case "print_bool":
                        print(eval(args[0], ctx))
                
                    case _:
                        print(f"Dont recognonize function {ident}")
                        exit(4)

                return

            functionHeader, codeBlock = funDef

            ctx.newScope()
            ctx.addVal(ident, None)
            for (_, argIdent, _), argVal in zip(functionHeader.args, args):
                ctx.addVal(argIdent, eval(argVal, ctx))

            eval(codeBlock, ctx)

            res = ctx.getVal(ident)
            ctx.popScope()

            return res


        case Binary(op, left, right):
            l = eval(left, ctx)
            r = eval(right, ctx)
            match op:
                case BinaryOp.EXP:
                    res = l ** r
                case BinaryOp.MULT:
                    res = l * r
                case BinaryOp.DIV:
                    res = l / r
                case BinaryOp.REM:
                    res = l % r
                case BinaryOp.PLUS:
                    res = l + r
                case BinaryOp.MINUS:
                    res = l - r
                case BinaryOp.LT:
                    res = l < r
                case BinaryOp.LTE:
                    res = l <= r
                case BinaryOp.GT:
                    res = l > r
                case BinaryOp.GTE:
                    res = l >= r
                case BinaryOp.EQ:
                    res = l == r
                case BinaryOp.NEQ:
                    res = l != r
                case BinaryOp.AND:
                    res = l and r
                case BinaryOp.OR:
                    res = l or r
                # TODO: support indexing
                case BinaryOp.INDEXING:
                    pass

            return res

        case Unary(op, expression):
            val = eval(expression, ctx)
            match op:
                case UnaryOp.NEGATION:
                    res = -val
                case UnaryOp.NOT:
                    res = not val

            return res

        case Ident(ident):
            return ctx.getVal(ident)

        case Literal(val, type):
            return val
