from parser import Node, Program, FunctionDeclaration, StructDeclaration, GlobalVariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, VariableDefinition, FunctionCall, StructInit, Binary, Unary, Ident, Literal, Field, Variable, ArrayIndexing, FieldAccessing
from parser import Type, TypeEnum, VarType, BinaryOp, UnaryOp
from interpreter import eval, Context as ValueContext

class Emitter:
    def __init__(self):
        self.lines = []
        self.decls = []
        self.counter = 0
        self.literal = 0
        self.branch = 0
        self.arrayIdx = 0

    def __lshift__(self, line):
        self.lines.append(line)

    def addTop(self, line):
        self.lines.insert(0, line)

    def addDec(self, line):
        self.decls.append(line)

    def next(self):
        res = self.counter
        self.counter += 1
        return res

    def nextLiteral(self):
        res = self.literal
        self.literal += 1
        return res

    def reset(self):
        self.counter = 0
        self.literal = 0
        self.arrayIdx = 0

    def nextBranch(self):
        res = self.branch
        self.branch += 1
        return res

    def nextArrayIdx(self):
        res = self.arrayIdx
        self.arrayIdx += 1
        return res


def codegen(node, emitter=None, structPtr=None, firstFieldAccessing=True, assignment=False):
    match node:
        case Program(decs, defs):
            emitter = Emitter()
            [codegen(dec, emitter) for dec in decs[::-1]]
            [codegen(def_, emitter) for def_ in defs[::-1]]
            return emitter

        case FunctionDeclaration(ident, args, retType):
            emitter.addDec(f"declare {retType.llvm()} @{ident}("\
                + ", ".join(f"{argType.llvm()} %{argIdent}" for (_, argIdent, argType) in args[::-1])\
                + ")")

        case StructDeclaration(ident, fields):
            emitter.addTop(f"%struct.{ident} = type {{{', '.join(type.llvm() for _, _, type in fields)}}}")

        case GlobalVariableDefinition(varType, ident, type, rhs):
            emitter.addTop(f"@{ident} = global {type.llvm()} {eval(rhs, ValueContext())}")

        case FunctionDefinition(functionHeader, codeBlock):
            ident = functionHeader.ident
            args = functionHeader.args[::-1]
            retType = functionHeader.retType

            if ident == "main":
                retType = Type(TypeEnum.INT)

            emitter << f"define {retType.llvm()} @{ident}("\
                + ", ".join(f"{argType.llvm()} %{argIdent}" for (_, argIdent, argType) in args)\
                + ") {"

            emitter << "entry:"
            if retType.type != TypeEnum.VOID:
                emitter << f"  %{ident}.addr = alloca {retType.llvm()}"
                # TODO: handle default return type for string and list
                if retType.listDepth > 0 or retType.type == TypeEnum.STR:
                    pass
                else:
                    emitter << f"  store {retType.llvm()} 0, ptr %{ident}.addr"
            for (_, argIdent, argType) in args:
                emitter << f"  %{argIdent}.addr = alloca {argType.llvm()}"
                emitter << f"  store {argType.llvm()} %{argIdent}, ptr %{argIdent}.addr"

            codegen(codeBlock, emitter)

            if retType.type == TypeEnum.VOID:
                emitter << f"  ret void"
            else:
                ret = emitter.next()
                emitter << f"  %{ret} = load {retType.llvm()}, ptr %{ident}.addr"
                emitter << f"  ret {retType.llvm()} %{ret}"
            emitter << "}"

            emitter.reset()

        case CodeBlock(statements):
            [codegen(stmt, emitter) for stmt in statements[::-1]]

        case Assignment(lhs, rhs):
            lhsReg = codegen(lhs, emitter, assignment=True)
            rhsReg = codegen(rhs, emitter)

            emitter << f"  store {rhs.exprType.llvm()}  {rhsReg}, ptr {lhsReg}"

        case While(guard, codeBlock):

            guardLabel = emitter.nextBranch()
            bodyLabel = emitter.nextBranch()
            endLabel = emitter.nextBranch()

            emitter << f"  br label %while.guard{guardLabel}"

            emitter << f"while.guard{guardLabel}:"
            guardReg = codegen(guard, emitter)
            emitter << f"  br i1 {guardReg}, label %while.body{bodyLabel}, label %while.end{endLabel}"

            emitter << f"while.body{bodyLabel}:"
            codegen(codeBlock, emitter)
            emitter << f"  br label %while.guard{guardLabel}"

            emitter << f"while.end{endLabel}:"

        case If(condition, thenBlock, elseBlock):

            thenLabel = emitter.nextBranch()
            elseLabel = emitter.nextBranch()
            endLabel = emitter.nextBranch()

            conditionReg = codegen(condition, emitter)
            emitter << f"  br i1 {conditionReg}, label %if.then{thenLabel}, label %if.else{elseLabel}"

            emitter << f"if.then{thenLabel}:"
            codegen(thenBlock, emitter)
            emitter << f"  br label %if.end{endLabel}"

            emitter << f"if.else{elseLabel}:"
            codegen(elseBlock, emitter)
            emitter << f"  br label %if.end{endLabel}"

            emitter << f"if.end{endLabel}:"


        case VariableDefinition(varType, ident, type, rhs):
            if isinstance(rhs, StructInit):
                structPtr = f"%{ident}{node.shadows if node.shadows > 0 else ''}.addr"
                emitter << f"  {structPtr} = alloca {type.llvm()}"
                reg = codegen(rhs, emitter, structPtr=structPtr)
            elif rhs.exprType.type == TypeEnum.STRUCT:
                reg = codegen(rhs, emitter, assignment=True)
                emitter << f"  %{ident}{node.shadows if node.shadows > 0 else ''}.addr = alloca {type.llvm()}"
                # Trick for getting the size of a type
                sizeReg = emitter.next()
                emitter << f"  %{sizeReg} = getelementptr {type.llvm()}*, ptr null, i32 1" 
                sizeRegI = emitter.next()
                emitter << f"  %{sizeRegI} = ptrtoint {type.llvm()}* %{sizeReg} to i32"
                emitter << f"  call void @llvm.memcpy.p0.p0.i32(ptr %{ident}{node.shadows if node.shadows > 0 else ''}.addr, ptr {reg}, i32 %{sizeRegI}, i1 false)"
                emitter.addDec("declare void @llvm.memcpy.p0.p0.i32(ptr, ptr, i32, i1)")
                
            else:
                reg = codegen(rhs, emitter)
                emitter << f"  %{ident}{node.shadows if node.shadows > 0 else ''}.addr = alloca {type.llvm()}"
                emitter << f"  store {type.llvm()} {reg}, ptr %{ident}{node.shadows if node.shadows > 0 else ''}.addr"

        case FunctionCall(ident, args):
            llvmArgs = ",".join(f"{arg.exprType.llvm()} {codegen(arg, emitter)}" for arg in args[::-1])
            if node.exprType.type == TypeEnum.VOID:
                emitter << f"  call {node.exprType.llvm()} @{ident} ({llvmArgs})"
                ret = None
            else:
                ret = emitter.next()
                emitter << f"  %{ret} = call {node.exprType.llvm()} @{ident}({llvmArgs})"

            return f"%{ret}"

        case StructInit(ident, initFields):
            for i, initField in enumerate(initFields[::-1]):
                fieldPtr = emitter.next()
                emitter << f"  %{fieldPtr} = getelementptr %struct.{ident}, ptr {structPtr}, i32 0, i32 {i}"
                if isinstance(initField, StructInit):
                    codegen(initField, emitter, f"%{fieldPtr}")
                else:
                    initFieldReg = codegen(initField, emitter)
                    emitter << f"  store {initField.exprType.llvm()} {initFieldReg}, ptr %{fieldPtr}"

        case Binary(op, left, right):
            lReg = codegen(left, emitter)
            rReg = codegen(right, emitter)
            res = emitter.next()
                

            match op:
                case BinaryOp.MULT:
                    emitter << f"  %{res} = {'mul' if node.exprType.type == TypeEnum.INT else 'fmul'} {node.exprType.llvm()}  {lReg}, {rReg}"

                case BinaryOp.DIV:
                    emitter << f"  %{res} = {'sdiv' if node.exprType.type == TypeEnum.INT else 'fdiv'} {node.exprType.llvm()}  {lReg}, {rReg}"

                case BinaryOp.REM:
                    emitter << f"  %{res} = {'srem' if node.exprType.type == TypeEnum.INT else 'frem'} {node.exprType.llvm()}  {lReg}, {rReg}"

                case BinaryOp.PLUS:
                    emitter << f"  %{res} = {'add' if node.exprType.type == TypeEnum.INT else 'fadd'} {node.exprType.llvm()}  {lReg}, {rReg}"

                case BinaryOp.MINUS:
                    emitter << f"  %{res} = {'sub' if node.exprType.type == TypeEnum.INT else 'fsub'} {node.exprType.llvm()}  {lReg}, {rReg}"


                case BinaryOp.LT | BinaryOp.LTE | BinaryOp.GT | BinaryOp.GTE | BinaryOp.EQ | BinaryOp.NEQ:
                    emitter << f"  %{res} = {'icmp' if left.exprType.type == TypeEnum.INT else 'fcmp'} {op.llvmInt() if left.exprType.type == TypeEnum.INT else op.llvmFloat()} {left.exprType.llvm()} {lReg}, {rReg}"

                case BinaryOp.AND:
                    emitter << f"  %{res} = and {node.exprType.llvm()} {lReg}, {rReg}"

                case BinaryOp.OR:
                    emitter << f"  %{res} = or {node.exprType.llvm()} {lReg}, {rReg}"

            return f"%{res}"
                

        case Unary(op, expression):

            res = emitter.next()
            reg = codegen(expression, emitter)

            match op:
                case UnaryOp.NEGATION:
                    emitter << f"  %{res} = {'sub' if node.exprType.type == TypeEnum.INT else 'fsub'} {node.exprType.llvm()} {0 if node.exprType.type == TypeEnum.INT else 0.0}, {reg}"

                case UnaryOp.NOT:
                    emitter << f"  %{res} = xor i1 {reg}, true"

            return f"%{res}"

        case Ident(ident):
            if assignment:
                if node.glob:
                    return f"@{ident}"
                else:
                    return f"%{ident}{node.shadows if node.shadows > 0 else ''}.addr"
            else:                
                reg = emitter.next()
                if node.glob:
                    emitter << f"  %{reg} = load {node.exprType.llvm()}, ptr @{ident}"
                else:
                    emitter << f"  %{reg} = load {node.exprType.llvm()}, ptr %{ident}{node.shadows if node.shadows > 0 else ''}.addr"

                return f"%{reg}"

        case Literal(val, type):

            match type.type:
                case TypeEnum.INT:
                    pass
                case TypeEnum.FLT:
                    pass
                case TypeEnum.STR:
                    lit = emitter.nextLiteral()
                    emitter.addTop(f"@str.{lit} = constant [{len(val)+1} x i8] c\"{val}\\00\"")
                    val = f"@str.{lit}"
                case TypeEnum.CHA:
                    val = ord(val)
                case TypeEnum.BOOL:
                    val = "true" if val else "false"
                case _:
                    exit(5)

            return val

        case Field(ident, type, index):
            pass

        case Variable(ident):
            return codegen(ident, emitter, assignment=assignment)

        case ArrayIndexing(array, index):
            # Não gosto disto, mas não arranjo outro solução :/
            if isinstance(array, ArrayIndexing):
                arrReg = codegen(array, emitter, assignment=assignment, firstFieldAccessing=False)
            else:
                arrReg = f"%{array.ident}{array.shadows if array.shadows > 0 else ''}.addr"
                arrPtr = emitter.next()                    
                emitter << f"  %{arrPtr} = load ptr, ptr {arrReg}"
                arrReg = f"%{arrPtr}"

            idxReg = codegen(index, emitter)

            arrIdx = emitter.nextArrayIdx()
            # array pointers are i32 because i dont want to cast them when the indexing comes from an expression
            emitter << f"  %arrayidx{arrIdx} = getelementptr {node.exprType.llvm()}, ptr {arrReg}, i32 {idxReg}"

            if assignment or not firstFieldAccessing:
                return f"%arrayidx{arrIdx}"
            else:
                arrNext = emitter.next()
                emitter << f"  %{arrNext} = load {node.exprType.llvm()}, ptr %arrayidx{arrIdx}"
                return f"%{arrNext}"

        case FieldAccessing(struct, field):
            # Não gosto disto, mas não arranjo outro solução :/
            if isinstance(struct, Ident):
                structReg = f"%{struct.ident}{struct.shadows if struct.shadows > 0 else ''}.addr"
            else:
                structReg = codegen(struct, emitter, firstFieldAccessing=False, assignment=assignment) 

            fieldPtr = emitter.next()
            emitter << f"  %{fieldPtr} = getelementptr {struct.exprType.llvm()}, ptr {structReg}, i32 0, i32 {field.index}"

            if not firstFieldAccessing or assignment:
                return f"%{fieldPtr}"
            else:
                 structNext = emitter.next()
                 emitter << f"  %{structNext} = load {node.exprType.llvm()}, ptr %{fieldPtr}"
                 return f"%{structNext}"

