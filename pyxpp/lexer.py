import ply.lex

# For different types of tokens, see
# https://en.m.wikipedia.org/wiki/Lexical_analysis#Token
tokens = [
    # Literals
    "FLOAT", "INTEGER", "NEWLINE",

    # Operators: + - * / ^ ** = < <= > >= <>
    "PLUS", "MINUS", "TIMES", "DIVIDE", "POWER",
    "EQUALS", "LT", "LE", "GT", "GE", "NE",

    # Separators: ( ) [ ] { } , ; '
    "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE", "COMMA",
    "SEMICOLON", "APOSTROPHE",

    # Keywords: if else then of sum
    # TODO: Add t (time), pi etc
    "IF", "ELSE", "THEN", "OF", "SUM", "GLOBAL", 'SIN', 'COS',

    # Declarations
    # TODO: volt, markov, wiener, number, table, bdry, solv, special
    "AUXILIARY", "INITIALIZE", "PARAMETER", "OPTION",
    'KEYWORD',  # For keywords that are not yet implmented.

    # Array slice: [1..3]
    "ARRAYSLICE",

    # Identifier: Variable and function names
    'IDENTIFIER',

]

# We ignore whitespace.
t_ignore = " \t"


# Literals

def t_NEWLINE(t):
    r"\n"
    t.lexer.lineno += 1
    return t


def t_FLOAT(t):
    r"(\d+\.\d*|\d*\.\d+)"
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
t_NE = r"<>"

# Separators
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_COMMA = r"\,"
t_SEMICOLON = r";"
t_APOSTROPHE = r"\'"


# Ignore comments and "active comments".
def t_COMMENT(t):
    r"(?m)^(\#|\").*"
    pass


# For now we also ignore the following:
# table, bdry, volt, markov, wiener, solv, special, set,
# derived parameters, numbers, int, block pseudo-arrays.
def t_NOTUSED(t):
    r"(table|bdry|volt|markov|wiener|solv|special|set|!|number|int|\%(.|\n)*?\%).*"  # noqa: E501
    pass


def t_AUXILIARY(t):
    r"(?m)^aux"
    return t


def t_INITIALIZE(t):
    r"(?m)^i\w*"
    return t


def t_PARAMETER(t):
    r"(?m)^p\w*"
    return t


def t_OPTION(t):
    r"(?m)^\@"
    return t


def t_GLOBAL(t):
    r"(?m)^global"
    return t


# Simple keywords have to match in full and don't depend on position in line.
simple_keywords = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'of': 'OF',
    'sum': 'SUM',
    'sin': 'SIN',
    'cos': 'COS',
}


def t_simple_keyword(t):
    r'if|then|else|of|sum|sin|cos'
    t.type = simple_keywords.get(t.value, 'KEYWORD')
    return t


# NOTE: XPP has an archaic naming scheme.  Crazy stuff that works:
# _'=0  (_ is the variable name)
# .11'=0 (.11 is the variable name)
# 0.12fds(x)=x**2
#
# To simplify stuff we only allow variables that are Python conform.
def t_IDENTIFIER(t):
    r"[a-zA-Z\_]\w*"
    # Turn to lowercase since XPP is not case sensitive.
    t.value = str.lower(t.value)
    return t


def t_DONE(t):
    # TODO: Test that done has to occur at ^, not sure about this.
    r"(?m)done"
    pass


# TODO: Later on we'll have to tokenize parts of the array slice separately,
# if we want to process these expressions.
def t_ARRAYSLICE(t):
    r"\[\d+\s*\.\.\s*\d+\]"
    return t


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
