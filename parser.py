from dataclasses import dataclass
from enum import Enum

from ply import yacc

from lexer import tokens

class Type(Enum):
    INT = 0
    FLT = 1 
    STR = 2
    CHA = 3
    BOOL = 4
    VOID = 5
    LIST = 6

class VarType(Enum):
    VAR = 0
    VAL = 1

class UnaryOp(Enum):
    NEGATION = 0
    NOT = 1

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

class Node:
    pass
    
class Statement(Node):
    pass

class Expression(Node):
    pass

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
    type: list[Type]

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
    args: list[(VarType, str, list[Type])]
    retType: list[Type]

class Definition(Node):
    pass

@dataclass
class VariableDefinition(Definition, Statement):
    varType: VarType
    ident: str
    type: list[Type]
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
    p[0] = VariableDefinition(p[1], p[2], p[4], p[6])

def p_varType1(p):
    "varType : VAR"
    p[0] = VarType.VAR

def p_varType2(p):
    "varType : VAL"
    p[0] = VarType.VAL

def p_functionDefinition(p):
    "functionDefinition : functionHeader codeBlock"
    p[0] = FunctionDefinition(p[1], p[2])

def p_functionHeader(p):
    "functionHeader : FUNCTION IDENT LPAREN functionArguments RPAREN returnType"
    if not p[6]:
        p[6] = Type.VOID
    p[0] = Declaration(p[2], p[4], p[6])

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
    p[0] = [Type.INT]

def p_type2(p):
    "type : FLOAT"
    p[0] = [Type.FLT]

def p_type3(p):
    "type : CHAR"

def p_type4(p):
    "type : STRING"
    p[0] = [Type.STR]

def p_type5(p):
    "type : BOOL"
    p[0] = [Type.BOOL]

def p_type6(p):
    "type : VOID"
    p[0] = [Type.VOID]

def p_type7(p):
    "type : LSQUARE type RSQUARE"
    p[2].append(Type.LIST)
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

# def p_statement6(p):
#     "statement : expression SEMICOLON"
#     p[0] = p[1]

def p_statement6(p):
    "statement : functionCall SEMICOLON"
    p[0] = p[1]

def p_ifStatement1(p):
    "ifStatement : IF expression codeBlock"
    p[0] = If(p[2], p[3], None)

def p_ifStatement2(p):
    "ifStatement : IF expression codeBlock ELSE codeBlock"
    p[0] = If(p[2], p[3], p[5])

def p_wileStatement(p):
    "whileStatement : WHILE expression codeBlock"
    p[0] = While(p[2], p[3])

def p_variableAssignment(p):
    "variableAssingment : leftHandSide COLON_EQUALS expression SEMICOLON"
    p[0] = Assignment(p[1][0], p[1][1], p[3])

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
    p[0] = Binary(BinaryOp.INDEXING, p[1], p[2])

def p_expression3(p):
    "expression : MINUS expression %prec NEGATION"
    p[0] = Unary(UnaryOp.NEGATION, p[2])

def p_expression4(p):
    "expression : EXCLAMATION expression"
    p[0] = Unary(UnaryOp.NOT, p[2])

def p_expression5(p):
    "expression : expression CIRCUMFLEX expression"
    p[0] = Binary(BinaryOp.EXP, p[1], p[3])

def p_expression6(p):
    "expression : expression STAR expression"
    p[0] = Binary(BinaryOp.MULT, p[1], p[3])

def p_expression7(p):
    "expression : expression SLASH expression"
    p[0] = Binary(BinaryOp.DIV, p[1], p[3])

def p_expression8(p):
    "expression : expression PERCENT expression"
    p[0] = Binary(BinaryOp.REM, p[1], p[3])

def p_expression9(p):
    "expression : expression PLUS expression"
    p[0] = Binary(BinaryOp.PLUS, p[1], p[3])

def p_expression10(p):
    "expression : expression MINUS expression"
    p[0] = Binary(BinaryOp.MINUS, p[1], p[3])

def p_expression11(p):
    "expression : expression LESS expression"
    p[0] = Binary(BinaryOp.LT, p[1], p[3])

def p_expression12(p):
    "expression : expression LESS_EQUALS expression"
    p[0] = Binary(BinaryOp.LTE, p[1], p[3])

def p_expression13(p):
    "expression : expression GREATER expression"
    p[0] = Binary(BinaryOp.GT, p[1], p[3])

def p_expression14(p):
    "expression : expression GREATER_EQUALS expression"
    p[0] = Binary(BinaryOp.GTE, p[1], p[3])

def p_expression15(p):
    "expression : expression EQUALS expression"
    p[0] = Binary(BinaryOp.EQ, p[1], p[3])

def p_expression16(p):
    "expression : expression EXCLAMATION_EQUALS expression"
    p[0] = Binary(BinaryOp.NEQ, p[1], p[3])

def p_expression17(p):
    "expression : expression AMPERSAND_AMPERSAND expression"
    p[0] = Binary(BinaryOp.AND, p[1], p[3])

def p_expression18(p):
    "expression : expression PIPE_PIPE expression"
    p[0] = Binary(BinaryOp.OR, p[1], p[3])

def p_expression19(p):
    "expression : TRUE"
    p[0] = Literal(p[1], [Type.BOOL])

def p_expression20(p):
    "expression : FALSE"
    p[0] = Literal(p[1], [Type.BOOL])
    
def p_expression21(p):
    "expression : INT_LITERAL"
    p[0] = Literal(p[1], [Type.INT])

def p_expression22(p):
    "expression : FLT_LITERAL"
    p[0] = Literal(p[1], [Type.FLT])

def p_expression23(p):
    "expression : STR_LITERAL"
    p[0] = Literal(p[1], [Type.STR])

def p_expression24(p):
    "expression : IDENT"
    p[0] = Ident(p[1])

def p_expression26(p):
    "expression : functionCall %prec FUNCTION_CALL"
    p[0] = p[1]

def p_functionCall1(p):
    "functionCall : IDENT LPAREN RPAREN"
    p[0] = FunctionCall(p[1], [])

def p_functionCall2(p):
    "functionCall : IDENT LPAREN functionCallArguments RPAREN"
    p[0] = FunctionCall(p[1], p[3])

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
    
def pp_program(ast: Program):
    print(ast.pp())
