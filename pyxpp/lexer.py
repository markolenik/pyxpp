import ply.lex

# For different types of tokens, see
# https://en.m.wikipedia.org/wiki/Lexical_analysis#Token


# Don't need this for now.  Later want to implement a mapping from xpp
# functions to python functions.
# keywords = (
#     'SIN', 'COS', 'TAN', 'ATAN', 'ATAN2', 'SINH', 'COSH', 'TANH', 'EXP',
#     'DELAY', 'LN', 'LOG', 'LOG10', 'T', 'PI', 'IF', 'THEN', 'ELSE', 'ASIN',
#     'ACOS', 'HEAV', 'SIGN', 'CEIL', 'FLR', 'RAN', 'ABS', 'DEL_SHFT', 'MAX',
#     'MIN', 'NORMAL', 'BESSELJ', 'BESSELY', 'ERF', 'ERFC', 'SHIFT', 'INT',
#     'SUM', 'OF', 'SUM_INDEX', 'J',
# )
keywords = ()

tokens = keywords + (
    # Literals
    "FLOAT", "INTEGER", "NEWLINE",

    # Operators: + - * / ^ ** = < <= > >= != ==
    "PLUS", "MINUS", "TIMES", "DIVIDE", "POWER",
    "EQUALS", "LT", "LE", "GT", "GE", "NE", 'EE',

    # Separators: ( ) [ ] { } , ; '
    "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE", "COMMA",
    "DOT", "SEMICOLON", "APOSTROPHE",

    # Identifier: Variable and function names
    'ID',

    # Command keyword (can all be abbreviated by first letter)
    'AUX', 'INIT', 'PAR', 'OPTION', 'GLOBAL',
    'MARKOV', 'WIENER', 'TABLE', 'BNDRY', 'DONE', 'NUMBERCMD',
    # Differentiation notation
    'DIFF_LEIBNIZ',             # dv/dt
    'DIFF_EULER',               # v'
)

# We ignore whitespace.
t_ignore = " \t"


# Literals

def t_NEWLINE(t):
    r"\n"
    t.lexer.lineno += 1
    return t


def t_FLOAT(t):
    r"(\d+\.(?!\.)\d*|\d*(?<!\.)\.\d+)"
    # Regex needs to be so complex to cover array notation.  Have to include
    # negative lookahead/lookbehind.
    t.value = float(t.value)
    return t


def t_INTEGER(t):
    r"\d+"
    t.value = int(t.value)
    return t


# Operators
t_PLUS = r"\+"
t_MINUS = r"-"
t_DIVIDE = r"/"
t_TIMES = r"\*"
t_POWER = r"(\^|\*\*)"
t_EQUALS = r"="
t_LT = r"<"
t_LE = r"<="
t_GT = r">"
t_GE = r">="
t_NE = r"!="
t_EE = r'=='

# Separators
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_COMMA = r"\,"
t_DOT = r'\.'
t_SEMICOLON = r";"
t_APOSTROPHE = r"\'"


def t_SUM_INDEX(t):
    r"i\'"
    return t


# Command keywords
# NOTE: Not sure which of the command keywords can be abbreviated by single
# letter.  Will have to check later.
def t_AUX(t):
    r"(?m)^aux"
    return t


def t_INIT(t):
    r"(?m)^i\w*"
    return t


def t_PAR(t):
    r"(?m)^p\w*"
    return t


def t_OPTION(t):
    r"(?m)^\@"
    return t


def t_GLOBAL(t):
    r"(?m)^global"
    return t


def t_MARKOV(t):
    r"(?m)^markov"
    return t


def t_WIENER(t):
    r"(?m)^wiener"
    return t


def t_BNDRY(t):
    r"(?m)^bndry"
    return t


def t_TABLE(t):
    r"(?m)^table"
    return t


def t_DONE(t):
    r"(?m)^done"
    return t


# Calling this NUMBER would be confusing, hece NUMBERCMD
def t_NUMBERCMD(t):
    r"(?m)^number"
    return t


# Differentiation operators

def t_DIFF_LEIBNIZ(t):
    r"(?m)^d[a-zA-Z\_]\w*\/dt"
    return t


def t_DIFF_EULER(t):
    r"(?m)^[a-zA-Z\_]\w*\'"
    return t


# NOTE: XPP has an archaic naming scheme, for example it includes numeric only
# variables.  To simplify stuff we only allow variables that are Python conform.
# This function covers both keywords and identifiers.
def t_ID(t):
    r"[a-zA-Z\_]\w*"
    # Turn to lowercase since XPP is not case sensitive.
    value = str.upper(t.value)
    if value in keywords:
        t.type = value
    t.value = str.lower(t.value)
    return t


# Ignore comments and "active comments".
def t_COMMENT(t):
    r"(?m)^(\#|\").*"
    # No return value, token discarded.
    pass


def t_error(t):
    # print("Illegal character %s" % t.value[0])
    raise ValueError("Illegal character %s" % t.value[0])
    # t.lexer.skip(1)


# TODO: Might make sense to provide some of the kwargs here, .e.g.
# to optimize the lexer.  Also, not sure whether a temporary file
# is written down anywhere, and whether it should be permanent.
# TODO: Try out building the lexer from within parser.py.
lexer = ply.lex.lex()


def tokenize(input_string, **kwargs):
    lexer.input(input_string)
    return [token for token in lexer]
