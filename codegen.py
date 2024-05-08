from parser import Node, Program, Declaration, GlobalVariableDefinition, FunctionDefinition, CodeBlock, Assignment, While, If, VariableDefinition, FunctionCall, Binary, Unary, Ident, Literal
from parser import Type, TypeEnum, VarType, BinaryOp, UnaryOp
from interpreter import eval, Context as ValueContext

class Emitter:
    def __init__(self):
        self.lines = []
        self.decls = []
        self.counter = 0
        self.literal = 0
        self.branch = 0

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

    def nextBranch(self):
        res = self.branch
        self.branch += 1
        return res


def codegen(node, emitter=None):
    match node:
        case Program(decs, defs):
            emitter = Emitter()
            [codegen(dec, emitter) for dec in decs[::-1]]
            [codegen(def_, emitter) for def_ in defs[::-1]]
            return emitter

        case Declaration(ident, args, retType):
            emitter.addDec(f"declare {retType.llvm()} @{ident}("\
                + "".join(f"{argType.llvm()} %{argIdent}" for (_, argIdent, argType) in args)\
                + ")")

        case GlobalVariableDefinition(varType, ident, type, rhs):
            emitter.addTop(f"@{ident} = global {type.llvm()} {eval(rhs, ValueContext())}")

        case FunctionDefinition(functionHeader, codeBlock):
            ident = functionHeader.ident
            args = functionHeader.args
            retType = functionHeader.retType

            # Permitir não escrever que a função main devolve um int e main := 0
            if ident == "main":
                retType = Type(TypeEnum.INT)

            emitter << f"define {retType.llvm()} @{ident}("\
                + "".join(f"{argType.llvm()} %{argIdent}" for (_, argIdent, argType) in args)\
                + ") {"
            emitter << "entry:"
            if retType.type != TypeEnum.VOID:
                emitter << f"  %{ident}.addr = alloca {retType.llvm()}"
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

        case Assignment(ident, indexing, rhs):
            # TODO: Handle indexing
            reg = codegen(rhs, emitter)
            emitter << f"  store {rhs.exprType.llvm()}  {reg}, ptr %{ident}.addr"

        case While(guard, codeBlock):

            guardLabel = emitter.nextBranch()
            bodyLabel = emitter.nextBranch()
            endLabel = emitter.nextBranch()

            emitter << f"  br label %while.guard{guardLabel}"

            emitter << f"while.guard{guardLabel}:"
            guardReg = codegen(guard, emitter)
            emitter << f"  br i1 %{guardReg}, label %while.body{bodyLabel}, label %while.end{endLabel}"

            emitter << f"while.body{bodyLabel}:"
            codegen(codeBlock, emitter)
            emitter << f"  br label %while.guard{guardLabel}"

            emitter << f"while.end{endLabel}:"

        case If(condition, thenBlock, elseBlock):

            thenLabel = emitter.nextBranch()
            elseLabel = emitter.nextBranch()
            endLabel = emitter.nextBranch()

            conditionReg = codegen(condition, emitter)
            emitter << f"  br i1 %{conditionReg}, label %if.then{thenLabel}, label %if.else{elseLabel}"

            emitter << f"if.then{thenLabel}:"
            codegen(thenBlock, emitter)
            emitter << f"  br label %if.end{endLabel}"

            emitter << f"if.else{elseLabel}:"
            codegen(elseBlock, emitter)
            emitter << f"  br label %if.end{endLabel}"

            emitter << f"if.end{endLabel}:"


        case VariableDefinition(varType, ident, type, rhs):
            reg = codegen(rhs, emitter)
            emitter << f"  %{ident}.addr = alloca {type.llvm()}"
            emitter << f"  store {type.llvm()} {reg}, ptr %{ident}.addr"

        case FunctionCall(ident, args):
            llvmArgs = ",".join(f"{arg.exprType.llvm()} {codegen(arg, emitter)}" for arg in args)
            if node.exprType.type == TypeEnum.VOID:
                emitter << f"  call {node.exprType.llvm()} @{ident} ({llvmArgs})"
                ret = None
            else:
                ret = emitter.next()
                emitter << f"  %{ret} = call {node.exprType.llvm()} @{ident} ({llvmArgs})"

            return f"%{ret}"

        case Binary(op, left, right):

            lReg = codegen(left, emitter)
            rReg = codegen(right, emitter)

            res = emitter.next()

            match op:
                case BinaryOp.EXP:
                    print("Por enquanto não suporta exponenciação")
                    exit(4)

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
                    emitter << f"  %{res} = {node.exprType.llvm()} and {lReg}, {rReg}"

                case BinaryOp.OR:
                    emitter << f"  %{res} = {node.exprType.llvm()} or {lReg}, {rReg}"

                case BinaryOp.INDEXING:
                    print("Por enquanto não suporta indexing")
                    exit(4)

            return f"%{res}"
                

        case Unary(op, expression):

            reg = codegen(expression, emitter)

            match op:
                case UnaryOp.NEGATION:
                    emitter << f"  {res} = {node.exprType.llvm()} {'sub' if node.exprType.type == TypeEnum.INT else 'fsub'} 0, {reg}"

                case UnaryOp.NOT:
                    emitter << f"  {res} = xor {reg}, true"

            return f"%{reg}"

        case Ident(ident):
            reg = emitter.next()
            if node.glob:
                emitter << f"  %{reg} = load {node.exprType.llvm()}, ptr @{ident}"
            else:
                emitter << f"  %{reg} = load {node.exprType.llvm()}, ptr %{ident}.addr"

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
                    val = ord(c)
                case TypeEnum.BOOL:
                    val = "true" if val else "false"
                case _:
                    exit(5)

            return val
        
