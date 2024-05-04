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

        return res


@dataclass
class Type:
    type: TypeEnum
    listDepth: int = 0

    def __eq__(self, o):
        if isinstance(o, Type):
            return self.type == o.type and self.listDepth == o.listDepth

        return False

    def __str__(self):
        if self.listDepth == 0:
            return str(self.type)
        else:
            return "["*self.listDepth + str(self.type) + "]"*self.listDepth

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
    EXP = 0
    MULT = 1
    DIV = 2
    REM = 3
    PLUS = 4
    MINUS = 5
    LT = 6
    LTE = 7
    GT = 8
    GTE = 9
    EQ = 10
    NEQ = 11
    AND = 12
    OR = 13
    INDEXING = 14

    def __str__(self):
        match self:
            case BinaryOp.EXP:
                res = "^"
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

        return res

class Node:
    lineno: int = None
    
class Statement(Node):
    pass

class Expression(Node):
    exprType: Type = None

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
    rhs: Expression


@dataclass
class Declaration(Node):
    ident: str
    args: list[(VarType, str, Type)]
    retType: Type

class Definition(Node):
    pass

@dataclass
class VariableDefinition(Definition, Statement):
    varType: VarType
    ident: str
    type: Type
    rhs: Expression

@dataclass
class FunctionDefinition(Definition):
    functionHeader: Declaration
    codeBlock: CodeBlock

@dataclass
class Program(Node):
    declarations: list[Declaration]
    definitions: list[Definition]

precedence = (
    # WEIRD FIX SHIFT/REDUCE conflict. Não sei bem qual se isto pode causar outros problemas
    # ("nonassoc", "IDENT"),
    ("nonassoc", "FUNCTION_CALL"),
    # ("nonassoc", "INDEXING"),
    ("nonassoc", "LPAREN", "RPAREN"),
    ("nonassoc", "LSQUARE", "RSQUARE"),
    ("right", "NEGATION", "EXCLAMATION"),
    ("left", "CIRCUMFLEX"),
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

def p_declaration(p):
    "declaration : functionHeader SEMICOLON"
    p[0] = p[1]

def p_definition1(p):
    "definition : variableDefinition"
    p[0] = p[1]

def p_definition2(p):
    "definition : functionDefinition"
    p[0] = p[1]

def p_variableDefiniton(p):
    "variableDefinition : varType IDENT COLON type COLON_EQUALS expression SEMICOLON"
    varDef = VariableDefinition(p[1], p[2], p[4], p[6])
    varDef.lineno = p.lineno(2)
    p[0] = varDef

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
    dec = Declaration(p[2], p[4], p[6])
    dec.lineno = p.lineno(2)
    p[0] = dec

def p_fucntionArguments1(p):
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

def p_variableAssignment(p):
    "variableAssingment : leftHandSide COLON_EQUALS expression SEMICOLON"
    ass = Assignment(p[1][0], p[1][1], p[3])
    ass.lineno = p.lineno(2)
    p[0] = ass

def p_leftHandSide1(p):
    "leftHandSide : IDENT"
    p[0] = (p[1], None)
    
def p_leftHandSide2(p):
    "leftHandSide : IDENT indexAccess"
    p[0] = (p[1], p[2])

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
    "expression : expression CIRCUMFLEX expression"
    bin = Binary(BinaryOp.EXP, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression6(p):
    "expression : expression STAR expression"
    bin = Binary(BinaryOp.MULT, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression7(p):
    "expression : expression SLASH expression"
    bin = Binary(BinaryOp.DIV, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression8(p):
    "expression : expression PERCENT expression"
    bin = Binary(BinaryOp.REM, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression9(p):
    "expression : expression PLUS expression"
    bin = Binary(BinaryOp.PLUS, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression10(p):
    "expression : expression MINUS expression"
    bin = Binary(BinaryOp.MINUS, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression11(p):
    "expression : expression LESS expression"
    bin = Binary(BinaryOp.LT, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression12(p):
    "expression : expression LESS_EQUALS expression"
    bin = Binary(BinaryOp.LTE, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression13(p):
    "expression : expression GREATER expression"
    bin = Binary(BinaryOp.GT, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression14(p):
    "expression : expression GREATER_EQUALS expression"
    bin = Binary(BinaryOp.GTE, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression15(p):
    "expression : expression EQUALS expression"
    bin = Binary(BinaryOp.EQ, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression16(p):
    "expression : expression EXCLAMATION_EQUALS expression"
    bin = Binary(BinaryOp.NEQ, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression17(p):
    "expression : expression AMPERSAND_AMPERSAND expression"
    bin = Binary(BinaryOp.AND, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression18(p):
    "expression : expression PIPE_PIPE expression"
    bin = Binary(BinaryOp.OR, p[1], p[3])
    bin.lineno = p.lineno(2)
    p[0] = bin

def p_expression19(p):
    "expression : BOOL_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.BOOL))

# def p_expression20(p):
#     "expression : FALSE"
#     p[0] = Literal(p[1], Type(TypeEnum.BOOL))
    
def p_expression21(p):
    "expression : INT_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.INT))

def p_expression22(p):
    "expression : FLT_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.FLT))

def p_expression23(p):
    "expression : STR_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.STR))

def p_expression24(p):
    "expression : CHR_LITERAL"
    p[0] = Literal(p[1], Type(TypeEnum.CHA))

def p_expression25(p):
    "expression : IDENT"
    p[0] = Ident(p[1])

def p_expression26(p):
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

def p_error(p):
    print("Syntax error in input. ", p)
    exit(2)

def parse(data, parserStart="start"):
    parser = yacc.yacc(start=parserStart)
    return parser.parse(data)
  
