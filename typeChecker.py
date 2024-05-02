from parser import Node, Program, Declaration, VariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, FunctionCall, Binary, Unary, Ident, Literal
from parser import Type, TypeEnum, VarType, BinaryOp, UnaryOp

class Context:
    def __init__(self):
        self.stack = [{}]
        self.funcDefs = {}

    def add(self, ident, type, varType):
        self.stack[-1][ident] = (type, varType)

    def remove(self, ident):
        self.stack[-1].pop(ident)

    def newScope(self):
        self.stack.append({})

    def popScope(self):
        self.stack.pop()

    def getType(self, ident):
        for scope in self.stack[::-1]:
            if ident in scope:
                return scope[ident][0] 

        return None

    def getVarType(self, ident):
        for scope in self.stack[::-1]:
            if ident in scope:
                return scope[ident][1] 

        return None

    def addFuncDef(self, functionHeader):
        self.funcDefs[functionHeader.ident] = functionHeader

    def getFuncDef(self, ident):
        return self.funcDefs.get(ident, None)

    def noFuncDefs(self):
        return len(self.funcDefs) == 0

# To verify the correct use of var and val, context may to save if a variable is var or val, for know i only will check the type
def verify_(ctx: Context, node: Node):
    match node:
        case Program(decs, defs):
            [verify_(ctx, decl) for decl in decs[::-1]]
            [verify_(ctx, defi) for defi in defs[::-1]]

        case Declaration(ident, args, retType):
            [ctx.addFuncDef(node)]

        case VariableDefinition(varType, ident, type, rhs):
            rhsType = verify_(ctx, rhs)
            if type != rhsType:
                print(f"Righ hand side expression is type {rhsType} but its declare to have type {type}. On line {node.lineno}")
                exit(3)
            ctx.add(ident, type, varType)

        case FunctionDefinition(functionHeader, codeBlock):
            # here we can check if a name of a function repeats
            # change here to check for val and var use
            # Maybe wrong variables get add to the old scope not the newone
            # Fix can be to havve a function block so it can have a diferent behaviour from codeBlock
            [ctx.add(ident, type, varType)  for (varType, ident, type) in functionHeader.args]
            # Add to the context the name of the functions so it is possible to verify the type of
            # the return, it is done in the assignment rule
            ctx.newScope()
            ctx.add(functionHeader.ident, functionHeader.retType, VarType.VAR)
            ctx.addFuncDef(functionHeader)
            verify_(ctx, codeBlock)
            ctx.popScope()

        case CodeBlock(statements):
            ctx.newScope()
            # inverse the order of the statementes because the parsing puts them in reverse order
            [verify_(ctx, stm) for stm in statements[::-1]]
            ctx.popScope()

        case Assignment(ident, indexing, rhs):
            type = verify_(ctx, rhs) 
            if not type:
                print(f"Cannot do an assingment to a variable that does not exist. On line {node.lineno}")
                exit(3)
            # TODO: handle when there is no return type
            # if ctxType == Special.RETURN_VAR:
            #     returnType = ctx.getFunDef(ident).retType
            #     if type != returnType:
            #         print(f"type {type} does not match return type of function declared {returnType}")
            #         exit(3)
            # else:
            ctxVarType = ctx.getVarType(ident)
            if ctxVarType == VarType.VAL:
                print(f"Cannot assign to val variable {ident}. On line {node.lineno}")
                exit(3)

            ctxType = ctx.getType(ident)
            # TODO: make it work for multiple indexings, for now only works with a single indexing, 
            # Hint: find the number of indexings and remove that number from the front of the list
            if indexing:
                ctxType = Type(ctxType.type, ctxType.listDepth - 1)

            if type != ctxType:
                print(f"Cannot assign {type} to a variable with type {ctxType}. On line {node.lineno}")
                exit(3)

        case While(guard, codeBlock):
            guardType = verify_(ctx, guard)
            if guardType != Type(TypeEnum.BOOL):
                print(f"Type of guard in while statement must be bool, got type {guardType}. On line {node.lineno}")
                exit(3)
            verify_(ctx, codeBlock)

        case If(condition, thenBlock, elseBlock):
            conditionType = verify_(ctx, condition)
            if conditionType != Type(TypeEnum.BOOL):
                print(f"Type of condition in if statement must be bool, got type {conditionType}. On line {node.lineno}")
                exit(3)
            verify_(ctx, thenBlock)
            verify_(ctx, elseBlock)

        case FunctionCall(ident, args):
            funcDef = ctx.getFuncDef(ident)
            if not funcDef:
                print(f"Function {ident} does not exist. On line {node.lineno}")
                exit(3)
            if len(funcDef.args) != len(args):
                print(f"In function call expected {len(funcDef.args)} arguments, got {len(args)}. On line {node.lineno}")
                exit(3)
            for call, (_, argIdent, defiType) in zip(args, funcDef.args):
                argType = verify_(ctx, call)
                if defiType != argType:
                    print(f"Expected {argIdent} argument to have type {defiType} got type {argType}. On line {node.lineno}")
                    exit(3)

            node.exprType = funcDef.retType

            return funcDef.retType

        case Binary(op, left, right):
            lType = verify_(ctx, left)
            rType = verify_(ctx, right)

            if op == BinaryOp.INDEXING:
                if rType != Type(TypeEnum.INT):
                    print(f"Indexing expression must be an int. On line {node.lineno}")
                    exit(3)

                if lType.listDepth < 1:
                    print(f"Cannot index not list type. On line {node.lineno}")
                    exit(3)

                exprType = Type(lType.type, lType.listDepth - 1)

            elif op in [BinaryOp.EXP, BinaryOp.MULT, BinaryOp.DIV, BinaryOp.REM, BinaryOp.PLUS, BinaryOp.MINUS]:
                if lType == Type(TypeEnum.FLT) or rType == Type(TypeEnum.FLT):
                    exprType = Type(TypeEnum.FLT)
                elif lType == Type(TypeEnum.INT) and rType == Type(TypeEnum.INT):
                    exprType = Type(TypeEnum.INT)
                else:
                    print(f"lhs and rhs must be int, int or int, float or float, float. Got type {lType}, {rType}. On line {node.lineno}")
                    exit(3)


            elif op in [BinaryOp.LT, BinaryOp.LTE, BinaryOp.GT, BinaryOp.GTE, BinaryOp.EQ, BinaryOp.NEQ]:
                if lType == Type(TypeEnum.FLT) or rType == Type(TypeEnum.FLT):
                    exprType =Type(TypeEnum.BOOL)
                elif lType == Type(TypeEnum.INT) and rType == Type(TypeEnum.INT):
                    exprType =Type(TypeEnum.BOOL)
                else:
                    print(f"lhs and rhs must be int or float. Got type {lType}, {rType}. On line {node.lineno}")
                    exit(3)

            else:
                if lType == Type(TypeEnum.BOOL) and rType == Type(TypeEnum.BOOL):
                    exprType =Type(TypeEnum.BOOL)
                else:
                    print(f"lhs and rhs must be bool. Got type {lType}, {rType}. On line {node.lineno}")
                    exit(3)

            node.exprType = exprType

            return exprType



        case Unary(op, expression):
            type = verify_(ctx, expression)
            if op == UnaryOp.NEGATION:
                if type in [Type(TypeEnum.INT), Type(TypeEnum.FLT)]:
                    node.exprType = type
                    return type
                else:
                    print(f"Operand of negation must be a int or float. Got type {type}. On line {node.lineno}")
                    exit(3)

            elif op == UnaryOp.NOT:
                if type == Type(TypeEnum.BOOL):
                    print(f"Operand of negation must be a int or float. Got type {type}. On line {node.lineno}")
                    exit(3)
                node.exprType = Type(TypeEnum.BOOL)
                return Type(TypeEnum.BOOL)

        case Ident(ident):
            idType = ctx.getType(ident)
            if not idType:
                print(f"Variable {ident} not defined. On line {node.lineno}")
                exit(3)

            node.exprType = idType

            return idType

        case Literal(val, type):
            node.exprType = type
            return type

def verify(ctx: Context, node: Node):
    verify_(ctx, node)

    # We check if noFuncDefs so plus in interpreter mode doesnt crash, but this moght accept an incorrect
    # program, a program with no function definitions
    if not ctx.getFuncDef("main") and not ctx.noFuncDefs:
        print("ERROR: Program is required to have a main function")
        exit(3)

