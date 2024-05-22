from parser import Node, Expression, Program, FunctionDeclaration, StructDeclaration, GlobalVariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, VariableDefinition, FunctionCall, StructInit, Binary, Unary, Ident, Literal, Field
from parser import Type, TypeEnum, VarType, BinaryOp, UnaryOp

class Context:
    def __init__(self):
        self.stack = [{}]
        self.funcDefs = {}
        self.structDefs = {}

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

    def isGlobalVar(self, ident):
        for i, scope in enumerate(self.stack[::-1]):
            if ident in scope:
                return len(self.stack) - i == 1

    def getShadows(self, ident):
        count = 0
        for scope in self.stack:
            if ident in scope:
                count += 1

        return count - 1

    def definedCurrentScope(self, ident):
        return ident in self.stack[-1]

    def addFuncDef(self, functionHeader):
        self.funcDefs[functionHeader.ident] = functionHeader

    def getFuncDef(self, ident):
        return self.funcDefs.get(ident, None)

    def noFuncDefs(self):
        return len(self.funcDefs) == 0

    def addStructDef(self, structDef):
        self.structDefs[structDef.ident] = structDef

    def getStructDef(self, ident):
        return self.structDefs.get(ident, None)

# Verifies if my interpreter can calculate the value for the llvm ir codegen of global variables
def checkCompileTimeConst(expr: Expression) -> bool:
    match expr:
        case FunctionCall(ident, args):
            return False

        case Binary(op, left, right):
            return checkCompileTimeConst(left) and checkCompileTimeConst(right)

        case Unary(op, expression):
            return checkCompileTimeConst(expression)

        case Ident(ident):
            return False

        case Literal(val, type):
            return True

def first_pass(ctx: Context, node: Node):
    match node:
        case Program(decs, defs):
            [first_pass(ctx, decl) for decl in decs[::-1]]
            [first_pass(ctx, defi) for defi in defs[::-1]]

        case FunctionDeclaration(ident, args, retType):
            ctx.addFuncDef(node)

        case StructDeclaration(ident, fields):
            ctx.addStructDef(node)

        case GlobalVariableDefinition(varType, ident, type, rhs):
            ctx.add(ident, type, varType)

        case FunctionDefinition(functionHeader, codeBlock):
            if ctx.getFuncDef(functionHeader.ident):
                print(f"Function {functionHeader.ident} cannot be re-defined. On line {node.lineno}")
                exit(3)
            ctx.addFuncDef(functionHeader)

        case _:
            return

def second_pass(ctx: Context, node: Node):
    match node:
        case Program(decs, defs):
            [second_pass(ctx, decl) for decl in decs[::-1]]
            [second_pass(ctx, defi) for defi in defs[::-1]]

        case FunctionDeclaration(ident, args, retType):
            pass

        case StructDeclaration(ident, fields):
            pass

        case GlobalVariableDefinition(varType, ident, type, rhs):
            if not checkCompileTimeConst(rhs):
                print(f"Global variable must be compile-time constant. On line {node.lineno}")
                exit(3)
            rhsType = second_pass(ctx, rhs)
            if type != rhsType:
                print(f"Right hand side expression is type {rhsType} but its declare to have type {type}. On line {node.lineno}")
                exit(3)

        case FunctionDefinition(functionHeader, codeBlock):
            ctx.newScope()
            [ctx.add(ident, type, varType)  for (varType, ident, type) in functionHeader.args]
            ctx.add(functionHeader.ident, functionHeader.retType, VarType.VAR)
            second_pass(ctx, codeBlock)
            ctx.popScope()

        case CodeBlock(statements):
            ctx.newScope()
            [second_pass(ctx, stm) for stm in statements[::-1]]
            ctx.popScope()

        case VariableDefinition(varType, ident, type, rhs):
            rhsType = second_pass(ctx, rhs)
            if type != rhsType:
                print(f"Right hand side expression is type {rhsType} but its declare to have type {type}. On line {node.lineno}")
                exit(3)

            if ctx.definedCurrentScope(ident):
                print(f"Cannot shadow variables in the same scope. On line {node.lineno}")
                exit(3)

            ctx.add(ident, type, varType)

            if ctx.getType(ident):
                node.shadows = ctx.getShadows(ident)

        case Assignment(ident, indexing, fieldAccessing, rhs):
            type = second_pass(ctx, rhs) 
            ctxVarType = ctx.getVarType(ident)
            if ctxVarType == VarType.VAL:
                print(f"Cannot assign to val variable {ident}. On line {node.lineno}")
                exit(3)

            ctxType = ctx.getType(ident)
            if not ctxType:
                print(f"Cannot do an assingment to a variable that does not exist. On line {node.lineno}")
                exit(3)
            if indexing:
                ctxType = Type(ctxType.type, ctxType.listDepth - 1)
                if not second_pass(ctx, indexing) == Type(TypeEnum.INT):
                    print(f"Indexing expression must be of type int. On line {node.lineno}")
                    exit(3)

            if fieldAccessing:
                structDef = ctx.getStructDef(ctxType.structName)
                if not structDef:
                    print(f"Cannot access field '{fieldAccessing}' of a non struct type '{ident}'. On line {node.lineno}")
                    exit(3)

                field = structDef.fields.get(fieldAccessing, None)

                if not field:
                    print(f"Field '{fieldAccessing}' does not exist for struct '{structDef.ident}'")
                    exit(3)

                if field[0] == VarType.VAL:
                    print(f"Cannot assign to val field {fieldAcessing}. On line {node.lineno}")
                    exit(3)

                ctxType = field[1]
            
            if type != ctxType:
                print(f"Cannot assign {type} to a {'field' if fieldAccessing else 'Variable'} with type {ctxType}. On line {node.lineno}")
                exit(3)

            if ctx.isGlobalVar(ident):
                node.glob = True

        case While(guard, codeBlock):
            guardType = second_pass(ctx, guard)
            if guardType != Type(TypeEnum.BOOL):
                print(f"Type of guard in while statement must be bool, got type {guardType}. On line {node.lineno}")
                exit(3)
            second_pass(ctx, codeBlock)

        case If(condition, thenBlock, elseBlock):
            conditionType = second_pass(ctx, condition)
            if conditionType != Type(TypeEnum.BOOL):
                print(f"Type of condition in if statement must be bool, got type {conditionType}. On line {node.lineno}")
                exit(3)
            second_pass(ctx, thenBlock)
            second_pass(ctx, elseBlock)

        case FunctionCall(ident, args):
            funcDef = ctx.getFuncDef(ident)
            if not funcDef:
                print(f"Function {ident} does not exist. On line {node.lineno}")
                exit(3)
            if len(funcDef.args) != len(args):
                print(f"In function call expected {len(funcDef.args)} arguments, got {len(args)}. On line {node.lineno}")
                exit(3)
            for call, (_, argIdent, defiType) in zip(args, funcDef.args):
                argType = second_pass(ctx, call)
                if defiType != argType:
                    print(f"Expected {argIdent} argument to have type {defiType} got type {argType}. On line {node.lineno}")
                    exit(3)

            node.exprType = funcDef.retType

            return funcDef.retType

        case StructInit(ident, initFields):
            structDef = ctx.getStructDef(ident)
            if len(initFields) != len(structDef.fields):
                print(f"Wrong number of fields initialized on struct initialization. On line {node.lineno}")
                exit(3)
            for initField, fieldName in zip(initFields, structDef.fields):
                initType = second_pass(ctx, initField)
                fieldDefType = structDef.fields[fieldName]
                if  initType!= fieldDefType[1]:
                    print(f"Got wrong type of field in struct initialization, expected '{fieldDefType[1]}' but got type '{initType}'.On line {node.lineno}")
                    exit(3)

            node.exprType = Type(TypeEnum.STRUCT, structName=ident)
            return Type(TypeEnum.STRUCT, structName=ident)

        case Binary(op, left, right):
            lType = second_pass(ctx, left)
            rType = second_pass(ctx, right)

            if op == BinaryOp.INDEXING:
                if rType != Type(TypeEnum.INT):
                    print(f"Indexing expression must be an int. On line {node.lineno}")
                    exit(3)

                if lType.listDepth < 1:
                    print(f"Can only index a list and not type '{lType}'. On line {node.lineno}")
                    exit(3)

                exprType = Type(lType.type, lType.listDepth - 1)

            elif op == BinaryOp.DOT:
                if lType.type != TypeEnum.STRUCT:
                    print(f"Cannot access fields of type that is not a struct, got type '{lType}'. On line {node.lineno}")
                    exit(3)
                
                structDef = ctx.getStructDef(lType.structName)
                field = structDef.fields.get(rType, None)
                if not field:
                    print(f"Field '{rType}' of struct '{lType.structName}' does not exist. On line {node.lineno}")                
                    exit(3)

                exprType = field[1]

            elif op in [BinaryOp.MULT, BinaryOp.DIV, BinaryOp.REM, BinaryOp.PLUS, BinaryOp.MINUS]:
                if lType == Type(TypeEnum.FLT) and rType == Type(TypeEnum.FLT):
                    exprType = Type(TypeEnum.FLT)
                elif lType == Type(TypeEnum.INT) and rType == Type(TypeEnum.INT):
                    exprType = Type(TypeEnum.INT)
                else:
                    print(f"lhs and rhs must be both int or both float. Got type {lType}, {rType}. On line {node.lineno}")
                    exit(3)

            elif op in [BinaryOp.LT, BinaryOp.LTE, BinaryOp.GT, BinaryOp.GTE, BinaryOp.EQ, BinaryOp.NEQ]:
                if lType == Type(TypeEnum.FLT) and rType == Type(TypeEnum.FLT):
                    exprType =Type(TypeEnum.BOOL)
                elif lType == Type(TypeEnum.INT) and rType == Type(TypeEnum.INT):
                    exprType =Type(TypeEnum.BOOL)
                else:
                    print(f"lhs and rhs must be both int or both float. Got type {lType}, {rType}. On line {node.lineno}")
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
            type = second_pass(ctx, expression)
            if op == UnaryOp.NEGATION:
                if type in [Type(TypeEnum.INT), Type(TypeEnum.FLT)]:
                    node.exprType = type
                    return type
                else:
                    print(f"Operand of negation must be a int or float. Got type {type}. On line {node.lineno}")
                    exit(3)

            elif op == UnaryOp.NOT:
                if type != Type(TypeEnum.BOOL):
                    print(f"Operand of not must be a bool. Got type {type}. On line {node.lineno}")
                    exit(3)
                node.exprType = Type(TypeEnum.BOOL)
                return Type(TypeEnum.BOOL)

        case Ident(ident):
            idType = ctx.getType(ident)
            if not idType:
                print(f"Variable {ident} not defined. On line {node.lineno}")
                exit(3)

            node.glob = ctx.isGlobalVar(ident)
            node.shadows = ctx.getShadows(ident)

            node.exprType = idType

            return idType

        case Literal(val, type):
            node.exprType = type
            return type

        case Field(ident):
            return ident

def verify(ctx: Context, node: Node):
    first_pass(ctx, node)
    second_pass(ctx, node)

    # We check if noFuncDefs so plus in interpreter mode doesnt crash, but this moght accept an incorrect
    # program, a program with no function definitions
    if not ctx.getFuncDef("main") and not ctx.noFuncDefs:
        print("ERROR: Program is required to have a main function")
        exit(3)

