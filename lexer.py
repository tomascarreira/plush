from ply import lex

reserved = {
	"val": "VAL",
	"var": "VAR",
	"function": "FUNCTION",
	"if": "IF",
	"else": "ELSE",
	"while": "WHILE",
	"int": "INT",
	"float": "FLOAT",
	"char": "CHAR",
	"string": "STRING",
	"bool": "BOOL",
	"void": "VOID",
	"struct": "STRUCT"
}

tokens = [
	"STR_LITERAL",
	"INT_LITERAL",
	"FLT_LITERAL",
	"BOOL_LITERAL",
	"CHR_LITERAL",
	"IDENT",
	"LPAREN",
	"RPAREN",
	"LSQUARE",
	"RSQUARE",
	"LCURLY",
	"RCURLY",
	"PERIOD",
	"COMMA",
	"COLON",
	"COLON_EQUALS",
	"EQUALS",
	"EXCLAMATION_EQUALS",
	"SEMICOLON",
	"AMPERSAND_AMPERSAND",
	"PIPE_PIPE",
	"EXCLAMATION",
	"GREATER",
	"GREATER_EQUALS",
	"LESS",
	"LESS_EQUALS",
	"PLUS",
	"MINUS",
	"STAR",
	"SLASH",
	"PERCENT",
] + list(reserved.values())

t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LSQUARE = r"\["
t_RSQUARE = r"\]"
t_LCURLY = r"\{"
t_RCURLY = r"\}"
t_PERIOD = r"\."
t_COMMA = r","
t_COLON = r"\:"
t_COLON_EQUALS = r"\:\="
t_EQUALS = r"\="
t_EXCLAMATION_EQUALS = r"\!\="
t_SEMICOLON = r";"
t_AMPERSAND_AMPERSAND = r"&&"
t_PIPE_PIPE = r"\|\|"
t_EXCLAMATION = r"\!"
t_GREATER = r">"
t_GREATER_EQUALS = r">\="
t_LESS = r"<"
t_LESS_EQUALS = r"<\="
t_PLUS = r"\+"
t_MINUS = r"\-"
t_STAR = r"\*"
t_SLASH = r"/"
t_PERCENT = r"%"

def t_FLT_LITERAL(t):
	r"\d*\.\d+"
	t.value = float(t.value)
	return t

def t_INT_LITERAL(t):
	r"\d((_*\d*)*\d)?"
	t.value = int(t.value.replace("_", ""))
	return t

def t_BOOL_LITERAL(t):
	r"true | false"
	t.value = True if t.value == "true" else False 
	return t

def t_STR_LITERAL(t):
	r"\".*\""
	t.value = str(t.value)[1:-1]
	return t

def t_CHR_LITERAL(t):
	r"'.'"
	t.value = str(t.value)[1:-1]
	return t

def t_IDENT(t):
	r"[a-zA-Z_][a-zA-Z_0-9]*"
	t.type = reserved.get(t.value, "IDENT")
	return t

def t_newline(t):
	r"\n+"
	t.lexer.lineno += len(t.value)

t_ignore = " \t"
t_ignore_COMMENT = r"\#.*" 

def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	exit(1)

lexer = lex.lex()
