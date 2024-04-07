from ply import yacc

from lexer import tokens

def p_start1(p):
    "start : functionDefinition"

def p_start2(p):
    "start : declaration start"

def p_start3(p):
    "start : definition start"

def p_declaration(p):
    "declaration : functionHeader SEMICOLON"

def p_definition1(p):
    "definition : variableDefinition"

def p_definition2(p):
    "definition : functionDefinition"

def p_variableDefiniton(p):
    "variableDefinition : varType IDENT COLON type COLON_EQUALS expression SEMICOLON"

def p_varType1(p):
    "varType : VAR"

def p_varType2(p):
    "varType : VAL"

def p_functionDefinition(p):
    "functionDefinition : functionHeader codeBlock"

def p_functionHeader(p):
    "functionHeader : FUNCTION IDENT LPAREN functionArguments RPAREN returnType"

def p_fucntionArguments1(p):
    "functionArguments : "

def p_functionArguments2(p):
    "functionArguments : nonEmptyFunctionArguments"

def p_nonEmptyFunctionArguments1(p):
    "nonEmptyFunctionArguments : argument"

def p_nonEmptyFunctionArguments2(p):
    "nonEmptyFunctionArguments : argument COLON argument nonEmptyFunctionArguments"

def p_argument(p):
    "argument : varType IDENT COLON type"

def p_returnType1(p):
    "returnType : "

def p_returnType2(p):
    "returnType : COLON type"

def p_type1(p):
    "type : INT"

def p_type2(p):
    "type : FLOAT"

def p_type3(p):
    "type : LSQUARE type RSQUARE"

def p_codeBlock1(p):
    "codeBlock : LCURLY RCURLY"

def p_codeBlock2(p):
    "codeBlock : LCURLY nonEmptyStatements RCURLY"

def p_nonEmptyStatements1(p):
    "nonEmptyStatements : statement"

def p_nonEmptyStatements2(p):
    "nonEmptyStatements : statement nonEmptyStatements"

def p_statement1(p):
    "statement : variableDefinition"

def p_statement2(p):
    "statement : ifStatement"

def p_statement3(p):
    "statement : whileStatement"

def p_statement4(p):
    "statement : variableAssingment"

def p_statement5(p):
    "statement : codeBlock"

def p_statement6(p):
    "statement : expression SEMICOLON"

def p_ifStatement1(p):
    "ifStatement : IF expression codeBlock"

def p_ifStatement2(p):
    "ifStatement : IF expression codeBlock ELSE codeBlock"

def p_wileStatement(p):
    "whileStatement : WHILE expression codeBlock"

def p_variableAssignment(p):
    "variableAssingment : IDENT COLON_EQUALS expression"

def p_expression1(p):
    "expression : LPAREN expression LPAREN"

def p_expression2(p):
    "expression : IDENT LSQUARE expression RSQUARE"

def p_expression3(p):
    "expression : MINUS expression"

def p_expression4(p):
    "expression : EXCLAMATION expression"

def p_expression5(p):
    "expression : expression CIRCUMFLEX expression"

def p_expression6(p):
    "expression : expression STAR expression"

def p_expression7(p):
    "expression : expression SLASH expression"

def p_expression8(p):
    "expression : expression PERCENT expression"

def p_expression9(p):
    "expression : expression PLUS expression"

def p_expression10(p):
    "expression : expression MINUS expression"

def p_expression11(p):
    "expression : expression LESS expression"

def p_expression12(p):
    "expression : expression LESS_EQUALS expression"

def p_expression13(p):
    "expression : expression GREATER expression"

def p_expression14(p):
    "expression : expression GREATER_EQUALS expression"

def p_expression15(p):
    "expression : expression EQUALS expression"

def p_expression16(p):
    "expression : expression EXCLAMATION_EQUALS expression"

def p_expression17(p):
    "expression : expression AMPERSAND_AMPERSAND expression"

def p_expression18(p):
    "expression : expression PIPE_PIPE expression"

def p_expression19(p):
    "expression : TRUE"

def p_expression20(p):
    "expression : FALSE"
    
def p_expression21(p):
    "expression : INTEGER_NUM"

def p_expression22(p):
    "expression : FLOAT_NUM"

def p_expression23(p):
    "expression : STRING"

def p_expression24(p):
    "expression : IDENT"

def p_expression25(p):
    "expression : functionCall"

def p_functionCall1(p):
    "functionCall : IDENT LPAREN RPAREN"

def p_functionCall2(p):
    "functionCall : IDENT LPAREN functionCallArguments RPAREN"

def p_functionCallArguments1(p):
    "functionCallArguments : expression"

def p_functionCallArguments2(p):
    "functionCallArguments : expression COMMA functionCallArguments"


def p_error(p):
    print("Syntax error in input. ", p)
    exit(2)

def parse(data, parserStart="start"):
    parser = yacc.yacc(start=parserStart)
    parser.parse(data)
    print("Parse ok")
