import ply.lex

# For different types of tokens, see
# https://en.m.wikipedia.org/wiki/Lexical_analysis#Token

keywords = (
    "IF", "ELSE", "THEN", "OF", "SUM", 'DONE', "GLOBAL",
    "AUX", "INIT", "PAR", "OPTION",
)

tokens = keywords + (
    # Literals
    "FLOAT", "INTEGER", "NEWLINE",

    # Operators: + - * / ^ ** = < <= > >= <>
    "PLUS", "MINUS", "TIMES", "DIVIDE", "POWER",
    "EQUALS", "LT", "LE", "GT", "GE", "NE",

    # Separators: ( ) [ ] { } , ; '
    "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE", "COMMA",
    "DOT", "SEMICOLON", "APOSTROPHE",

    # Identifier: Variable and function names
    'ID',

)

# We ignore whitespace.
t_ignore = " \t"


# Literals

def t_NEWLINE(t):
    r"\n"
    t.lexer.lineno += 1
    return t


def t_FLOAT(t):
    r"(\d+\.(?!\.)\d*|\d*(?!\.)\.\d+)"
    # Regex needs to be so complex to cover array notation.
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
t_DOT = r'\.'
t_SEMICOLON = r";"
t_APOSTROPHE = r"\'"


def t_DONE(t):
    # TODO: Test that done has to occur at ^, not sure about this.
    r"(?m)^done"
    return t


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
    t.lexer.lineno += 1
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
