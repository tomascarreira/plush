import ply.lex as plylex

reserved = {
	"val": "VAL",
	"var": "VAR",
	"function": "FUNCTION",
	"if": "IF",
	"else": "ELSE",
	"while": "WHILE",
	"true": "TRUE",
	"false": "FALSE",
	"int": "INT",
	"float": "FLOAT",
}

tokens = [
	"STRING",
	"INTEGER_NUM",
	"FLOAT_NUM",
	"IDENT",
	"LPAREN",
	"RPAREN",
	"LSQUARE",
	"RSQUARE",
	"LCURLY",
	"RCURLY",
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
	"START",
	"CIRCUMFLEX",
	"SLASH",
	"PERCENT",
] + list(reserved.values())

t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LSQUARE = r"\["
t_RSQUARE = r"\]"
t_LCURLY = r"\{"
t_RCURLY = r"\}"
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
t_START = r"\*"
t_CIRCUMFLEX = r"\^"
t_SLASH = r"/"
t_PERCENT = r"%"

def t_FLOAT_NUM(t):
	r"\d*\.\d+"
	t.value = float(t.value)
	return t

def t_INTEGER_NUM(t):
	r"\d+"
	t.value = int(t.value)
	return t

def t_STRING(t):
	r"\".*\""
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
	t.lexer.skip(1)

lexer = plylex.lex()

def lex(data):
	lexer.input(data)
	for tok in lexer:
		print(tok)
