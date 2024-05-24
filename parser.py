from dataclasses import dataclass
from enum import Enum

from ply import yacc

from lexer import tokens

class TypeEnum(Enum):
    INT = 0
    FLT = 1 
    STR = 2
    CHA = 3
    BOOL = 4
    VOID = 5
    STRUCT = 6

    def __str__(self):
        match self:
            case TypeEnum.INT:
                res = "int"
            case TypeEnum.FLT:
                res = "flt"
            case TypeEnum.STR:
                res = "string"
            case TypeEnum.CHA:
                res = "char"
            case TypeEnum.BOOL:
                res = "bool"
            case TypeEnum.VOID:
                res = "void"
            case TypeEnum.STRUCT:
                res = "struct"

        return res

    def llvm(self):
        match self:
            case TypeEnum.INT:
                res = "i32"
            case TypeEnum.FLT:
                res = "float"
            case TypeEnum.STR:
                res = "ptr"
            case TypeEnum.CHA:
                res = "i8"
            case TypeEnum.BOOL:
                res = "i1"
            case TypeEnum.VOID:
                res = "void"

        return res

@dataclass
class Type:
    type: TypeEnum
    listDepth: int = 0
    structName: str = ""

    def __eq__(self, o):
        if isinstance(o, Type):
            return self.type == o.type and self.listDepth == o.listDepth and self.structName == o.structName

        return False

    def __str__(self):
        if self.listDepth > 0:
            return "["*self.listDepth + str(self.type) + "]"*self.listDepth
        elif self.structName != "":
            return str(self.type) + " " + self.structName
        else:
            return str(self.type)

    def llvm(self):
        if self.listDepth > 0:
            return "ptr"
        elif self.structName:
            return f"%struct.{self.structName}"
        else:
            return self.type.llvm()


class VarType(Enum):
    VAR = 0
    VAL = 1

    def __str__(self):
        match self:
            case VarType.VAR:
                res = "var"
            case VarType.VAL:
                res = "val"
        return res

class UnaryOp(Enum):
    NEGATION = 0
    NOT = 1

    def __str__(self):
        match self:
            case UnaryOp.NEGATION:
                res = "-"
            case UnaryOp.NOT:
                res = "!"

        return res

class BinaryOp(Enum):
    MULT = 0
    DIV = 1
    REM = 2
    PLUS = 3
    MINUS = 4
    LT = 5
    LTE = 6
    GT = 7
    GTE = 8
    EQ = 9
    NEQ = 10
    AND = 11
    OR = 12
    INDEXING = 13
    DOT = 14

    def __str__(self):
        match self:
            case BinaryOp.MULT:
                res = "*"
            case BinaryOp.DIV:
                res = "/"
            case BinaryOp.REM:
                res = "%"
            case BinaryOp.PLUS:
                res = "+"
            case BinaryOp.MINUS:
                res = "-"
            case BinaryOp.LT:
                res = "<"
            case BinaryOp.LTE:
                res = "<="
            case BinaryOp.GT:
                res = ">"
            case BinaryOp.GTE:
                res = ">="
            case BinaryOp.EQ:
                res = "="
            case BinaryOp.NEQ:
                res = "!="
            case BinaryOp.AND:
                res = "&&"
            case BinaryOp.OR:
                res = "||"
            case BinaryOp.INDEXING:
                res = "[]"
            case BinaryOp.DOT:
                res = "."

        return res

    def llvmInt(self):
        match self:
            case BinaryOp.LT:
                res = "slt"
            case BinaryOp.LTE:
                res = "sle"
            case BinaryOp.GT:
                res = "sgt"
            case BinaryOp.GTE:
                res = "sge"
            case BinaryOp.EQ:
                res = "eq"
            case BinaryOp.NEQ:
                res = "ne"

        return res

    def llvmFloat(self):
        match self:
            case BinaryOp.LT:
                res = "ult"
            case BinaryOp.LTE:
                res = "ule"
            case BinaryOp.GT:
                res = "ugt"
            case BinaryOp.GTE:
                res = "uge"
            case BinaryOp.EQ:
                res = "ueq"
            case BinaryOp.NEQ:
                res = "une"

        return res

class Node:
    lineno: int = None
    
class Statement(Node):
    # DO THIS TO KNOW THE STRUCT TYPE in the codegen
    # VERY BAD, IM ASHAMED
    structName: str = ""

class Expression(Node):
    exprType: Type = None

@dataclass
class Field(Expression):
    ident: str
    type: TypeEnum = None
    index: int = 0

@dataclass
class Unary(Expression):
    op: UnaryOp
    expression: Expression

@dataclass
class Binary(Expression):
    op: BinaryOp
    left: Expression
    right: Expression

@dataclass
class FunctionCall(Expression):
    ident: str
    args: list[Expression]

@dataclass
class Literal(Expression):
    val: any
    type: Type

@dataclass
class Ident(Expression):
    ident: str
    glob: bool
    shadows: int

@dataclass
class StructInit(Expression):
    ident: str
    initFields: list[Expression]

@dataclass
class CodeBlock(Node):
    statements: list[Statement]

@dataclass
class If(Statement):
    condition: Expression
    thenBlock: CodeBlock
    elseBlock: CodeBlock

@dataclass
class While(Statement):
    guard: Expression
    codeBlock: CodeBlock

@dataclass
class Assignment(Statement):
    ident: str
    indexing: Expression
    fieldAccessing: (str, TypeEnum, int)
    rhs: Expression
    glob: bool

@dataclass
class VariableDefinition(Statement):
    varType: VarType
    ident: str
    type: Type
    rhs: Expression
    shadow: int

class Declaration(Node):
    pass

@dataclass
class FunctionDeclaration(Declaration):
    ident: str
    args: list[(VarType, str, Type)]
    retType: Type

@dataclass
class StructDeclaration(Declaration):
    ident: str
    fields: list[(VarType, str, Type)]

class Definition(Node):
    pass

@dataclass
class GlobalVariableDefinition(Definition):
    varType: VarType
    ident: str
    type: Type
    rhs: Expression

@dataclass
class FunctionDefinition(Definition):
    functionHeader: FunctionDeclaration
    codeBlock: CodeBlock

@dataclass
class Program(Node):
    declarations: list[FunctionDeclaration]
    definitions: list[Definition]

precedence = (
    ("nonassoc", "FUNCTION_CALL"),
    ("left", "PERIOD"),
    ("nonassoc", "LPAREN", "RPAREN"),
    ("nonassoc", "LSQUARE", "RSQUARE"),
    ("right", "NEGATION", "EXCLAMATION"),
    ("left", "STAR", "SLASH", "PERCENT"),
    ("left", "PLUS", "MINUS"),
    ("nonassoc", "LESS", "LESS_EQUALS", "GREATER", "GREATER_EQUALS"),
    ("left", "EQUALS", "EXCLAMATION_EQUALS"),
    ("left", "AMPERSAND_AMPERSAND"),
    ("left", "PIPE_PIPE"),
)[::-1]

def p_start1(p):
    "start : "
    p[0] = Program([], [])

def p_start2(p):
    "start : declaration start"
    p[2].declarations.append(p[1])
    p[0] = p[2]

def p_start3(p):
    "start : definition start"
    p[2].definitions.append(p[1])
    p[0] = p[2]

def p_declaration1(p):
    "declaration : functionHeader SEMICOLON"
    p[0] = p[1]

def p_declaration2(p):
    "declaration : structDeclaration"
    p[0] = p[1]

def p_structDeclaration(p):
    "structDeclaration : STRUCT IDENT LCURLY structFields RCURLY"
    structDecl = StructDeclaration(p[2], p[4])
    structDecl.lineno = p.lineno(1)
    p[0] = structDecl

def p_structFields1(p):
    "structFields : structField"
    p[0] = [p[1]]

def p_structFields2(p):
    "structFields : structField COMMA"
    p[0] = [p[1]]

def p_structFields3(p):
    "structFields : structField COMMA structFields"
    p[3].append(p[1])
    p[0] = p[3]

def p_structField(p):
    "structField : varType IDENT COLON type"
    p[0] = (p[1], p[2], p[4])

def p_definition1(p):
    "definition : globalVariableDefinition"
    p[0] = p[1]

def p_definition2(p):
    "definition : functionDefinition"
    p[0] = p[1]

def p_globalVariableDefiniton(p):
    "globalVariableDefinition : varType IDENT COLON type COLON_EQUALS expression SEMICOLON"
    globVarDef = GlobalVariableDefinition(p[1], p[2], p[4], p[6])
    globVarDef.lineno = p.lineno(2)
    p[0] = globVarDef

def p_varType1(p):
    "varType : VAR"
    p[0] = VarType.VAR

def p_varType2(p):
    "varType : VAL"
    p[0] = VarType.VAL

def p_functionDefinition(p):
    "functionDefinition : functionHeader codeBlock"
    funcDef = FunctionDefinition(p[1], p[2])
    funcDef.lineno = p[1].lineno
    p[0] = funcDef

def p_functionHeader(p):
    "functionHeader : FUNCTION IDENT LPAREN functionArguments RPAREN returnType"
    if not p[6]:
        p[6] = Type(TypeEnum.VOID)
    dec = FunctionDeclaration(p[2], p[4], p[6])
    dec.lineno = p.lineno(2)
    p[0] = dec

def p_functionArguments1(p):
    "functionArguments : "
    p[0] = []

def p_functionArguments2(p):
    "functionArguments : nonEmptyFunctionArguments"
    p[0] = p[1]

def p_nonEmptyFunctionArguments1(p):
    "nonEmptyFunctionArguments : argument"
    p[0] = [p[1]]

def p_nonEmptyFunctionArguments2(p):
    "nonEmptyFunctionArguments : argument COMMA nonEmptyFunctionArguments"
    p[3].append(p[1])
    p[0] = p[3]

def p_argument(p):
    "argument : varType IDENT COLON type"
    p[0] = (p[1], p[2], p[4])

def p_returnType1(p):
    "returnType : "
    p[0] = None

def p_returnType2(p):
    "returnType : COLON type"
    p[0] = p[2]

def p_type1(p):
    "type : INT"
    p[0] = Type(TypeEnum.INT)

def p_type2(p):
    "type : FLOAT"
    p[0] = Type(TypeEnum.FLT)

def p_type3(p):
    "type : CHAR"
    p[0] = Type(TypeEnum.CHA)

def p_type4(p):
    "type : STRING"
    p[0] = Type(TypeEnum.STR)

def p_type5(p):
    "type : BOOL"
    p[0] = Type(TypeEnum.BOOL)

def p_type6(p):
    "type : VOID"
    p[0] = Type(TypeEnum.VOID)

def p_type7(p):
    "type : LSQUARE type RSQUARE"
    p[2].listDepth += 1
    p[0] = p[2]

def p_type8(p):
    "type : STRUCT IDENT"
    p[0] = Type(TypeEnum.STRUCT, structName=p[2])

def p_codeBlock1(p):
    "codeBlock : LCURLY RCURLY"
    p[0] = CodeBlock([])

def p_codeBlock2(p):
    "codeBlock : LCURLY nonEmptyStatements RCURLY"
    p[0] = CodeBlock(p[2])

def p_nonEmptyStatements1(p):
    "nonEmptyStatements : statement"
    p[0] = [p[1]]

def p_nonEmptyStatements2(p):
    "nonEmptyStatements : statement nonEmptyStatements"
    p[2].append(p[1])
    p[0] = p[2]

def p_statement1(p):
    "statement : variableDefinition"
    p[0] = p[1]

def p_statement2(p):
    "statement : ifStatement"
    p[0] = p[1]

def p_statement3(p):
    "statement : whileStatement"
    p[0] = p[1]

def p_statement4(p):
    "statement : variableAssingment"
    p[0] = p[1]

def p_statement5(p):
    "statement : codeBlock"
    p[0] = p[1]

def p_statement6(p):
    "statement : functionCall SEMICOLON"
    p[0] = p[1]

def p_ifStatement1(p):
    "ifStatement : IF expression codeBlock"
    if_ = If(p[2], p[3], None)
    if_.lineno = p.lineno(1)
    p[0] = if_

def p_ifStatement2(p):
    "ifStatement : IF expression codeBlock ELSE codeBlock"
    p[0] = If(p[2], p[3], p[5])

def p_wileStatement(p):
    "whileStatement : WHILE expression codeBlock"
    whl = While(p[2], p[3])
    whl.lineno = p.lineno(1)
    p[0] = whl

def p_variableDefiniton(p):
    "variableDefinition : varType IDENT COLON type COLON_EQUALS expression SEMICOLON"
    varDef = VariableDefinition(p[1], p[2], p[4], p[6], 0)
    varDef.lineno = p.lineno(2)
    p[0] = varDef

def p_variableAssignment(p):
    "variableAssingment : leftHandSide COLON_EQUALS expression SEMICOLON"
    ass = Assignment(p[1][0], p[1][1], (p[1][2], None, 0), p[3], False)
    ass.lineno = p.lineno(2)
    p[0] = ass

def p_leftHandSide1(p):
    "leftHandSide : IDENT"
    p[0] = (p[1], None, None)
    
def p_leftHandSide2(p):
    "leftHandSide : IDENT indexAccess"
    p[0] = (p[1], p[2], None)

def p_leftHandSide3(p):
    "leftHandSide : IDENT PERIOD IDENT"
    p[0] = (p[1], None, p[3])

def p_indexAccess(p):
    "indexAccess : LSQUARE expression RSQUARE"
    p[0] = p[2]

def p_expression1(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]

def p_expression2(p):
    "expression : expression indexAccess"
    bin = Binary(BinaryOp.INDEXING, p[1], p[2])
    bin.lineno = p[1].lineno
    p[0] = bin

def p_expression3(p):
    "expression : MINUS expression %prec NEGATION"
    un = Unary(UnaryOp.NEGATION, p[2])
    un.lineno = p.lineno(1)
    p[0] = un

def p_expression4(p):
    "expression : EXCLAMATION expression"
    un = Unary(UnaryOp.NOT, p[2])
    un.lineno = p.lineno(1)
    p[0] = un

def p_expression5(p):
    "expression : expression STAR expression"
    bin = Binary(BinaryOp.MULT, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression6(p):
    "expression : expression SLASH expression"
    bin = Binary(BinaryOp.DIV, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression7(p):
    "expression : expression PERCENT expression"
    bin = Binary(BinaryOp.REM, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression8(p):
    "expression : expression PLUS expression"
    bin = Binary(BinaryOp.PLUS, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression9(p):
    "expression : expression MINUS expression"
    bin = Binary(BinaryOp.MINUS, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression10(p):
    "expression : expression LESS expression"
    bin = Binary(BinaryOp.LT, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression11(p):
    "expression : expression LESS_EQUALS expression"
    bin = Binary(BinaryOp.LTE, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression12(p):
    "expression : expression GREATER expression"
    bin = Binary(BinaryOp.GT, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression13(p):
    "expression : expression GREATER_EQUALS expression"
    bin = Binary(BinaryOp.GTE, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression14(p):
    "expression : expression EQUALS expression"
    bin = Binary(BinaryOp.EQ, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression15(p):
    "expression : expression EXCLAMATION_EQUALS expression"
    bin = Binary(BinaryOp.NEQ, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression16(p):
    "expression : expression AMPERSAND_AMPERSAND expression"
    bin = Binary(BinaryOp.AND, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression17(p):
    "expression : expression PIPE_PIPE expression"
    bin = Binary(BinaryOp.OR, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression18(p):
    "expression : BOOL_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.BOOL))

def p_expression19(p):
    "expression : INT_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.INT))

def p_expression20(p):
    "expression : FLT_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.FLT))

def p_expression21(p):
    "expression : STR_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.STR))

def p_expression22(p):
    "expression : CHR_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.CHA))

def p_expression23(p):
    "expression : IDENT"
    ident = Ident(p[1], False, 0)
    ident.lineno = p.lineno(1)
    p[0] = ident

def p_expression24(p):
    "expression : functionCall %prec FUNCTION_CALL"
    p[0] = p[1]

def p_functionCall1(p):
    "functionCall : IDENT LPAREN RPAREN"
    funcCall = FunctionCall(p[1], [])
    funcCall.lineno = p.lineno(1)
    p[0] = funcCall

def p_functionCall2(p):
    "functionCall : IDENT LPAREN functionCallArguments RPAREN"
    funcCall = FunctionCall(p[1], p[3])
    funcCall.lineno = p.lineno(1)
    p[0] = funcCall

def p_functionCallArguments1(p):
    "functionCallArguments : expression"
    p[0] = [p[1]]

def p_functionCallArguments2(p):
    "functionCallArguments : expression COMMA functionCallArguments"
    p[3].append(p[1])
    p[0] = p[3]

def p_expression25(p):
    "expression : STRUCT IDENT LPAREN initFields RPAREN"
    structInit = StructInit(p[2], p[4])
    structInit.lineno = p.lineno(1)
    p[0] = structInit

def p_intiFields1(p):
    "initFields : expression"
    p[0] = [p[1]]

def p_intiFields2(p):
    "initFields : expression COMMA initFields"
    p[3].append(p[1])
    p[0] = p[3]

def p_expression26(p):
    "expression : expression PERIOD field"
    bin = Binary(BinaryOp.DOT, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_field(p):
    "field : IDENT"
    p[0] = Field(p[1])

def p_error(p):
    if not p:
        print("Syntax error in code. Cannot give more information, sorry. Probably there is a missing ';'")
    else:
        print(f"Syntax error at '{p.value}'. On line {p.lineno}")
    exit(2)

def parse(data, parserStart="start"):
    parser = yacc.yacc(start=parserStart)
    return parser.parse(data)
  
