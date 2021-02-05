import pytest
from pyxpp.lexer import tokenize

# NOTE: Due to the unpythonic (but fast) implementation of PLY, we can't do
# direct unit tests, and have to rely on the tokenize function.

keyword_tests = [
    ('sin', ['SIN']),
    ('cos', ['COS']),
    ('tan', ['TAN']),
    ('atan', ['ATAN']),
    ('atan2', ['ATAN2']),
    ('sinh', ['SINH']),
    ('cosh', ['COSH']),
    ('tanh', ['TANH']),
    ('exp', ['EXP']),
    ('delay', ['DELAY']),
    ('ln', ['LN']),
    ('log', ['LOG']),
    ('log10', ['LOG10']),
    ('t', ['T']),
    # The ID at start is to prevent triggering init etc.
    ('x pi', ['ID', 'PI']),
    ('x if then else', ['ID', 'IF', 'THEN', 'ELSE']),
    ('asin', ['ASIN']),
    ('acos', ['ACOS']),
    ('heav', ['HEAV']),
    ('sign', ['SIGN']),
    ('ceil', ['CEIL']),
    ('flr', ['FLR']),
    ('ran', ['RAN']),
    ('abs', ['ABS']),
    ('del_shft', ['DEL_SHFT']),
    ('x max', ['ID', 'MAX']),
    ('x min', ['ID', 'MIN']),
    ('normal', ['NORMAL']),
    ('besselj', ['BESSELJ']),
    ('bessely', ['BESSELY']),
    ('erf', ['ERF']),
    ('erfc', ['ERFC']),
    ('shift', ['SHIFT']),
    ('x int', ['ID', 'INT']),
    ('sum', ['SUM']),
    ('of', ['OF']),
    ("x i'", ['ID', 'SUM_INDEX']),
    ('j', ['J']),
]


# @pytest.mark.parametrize('test, expected', keyword_tests)
@pytest.mark.skip(reason='keywords not implemented yet')
def test_keywords(test, expected):
    tokens = tokenize(test)
    assert [token.type for token in tokens] == expected


literal_tests = [
    ('1.0', 'FLOAT'),
    ('4', 'INTEGER'),
    ('.5', 'FLOAT'),
    ('\n', 'NEWLINE'),
]


@pytest.mark.parametrize('test, expected', literal_tests)
def test_literals(test, expected):
    tokens = tokenize(test)
    assert tokens[0].type == expected


operator_tests = [
    ('+', 'PLUS'),
    ('-', 'MINUS'),
    ('*', 'TIMES'),
    ('/', 'DIVIDE'),
    ('^', 'POWER'),
    ('**', 'POWER'),
    ('=', 'EQUALS'),
    ('<', 'LT'),
    ('<=', 'LE'),
    ('>', 'GT'),
    ('>=', 'GE'),
    ('!=', 'NE'),
    ('==', 'EE'),
]


@pytest.mark.parametrize('test, expected', operator_tests)
def test_operators(test, expected):
    tokens = tokenize(test)
    assert tokens[0].type == expected


separator_tests = [
    ('(', 'LPAREN'),
    (')', 'RPAREN'),
    ('[', 'LBRACKET'),
    (']', 'RBRACKET'),
    ('{', 'LBRACE'),
    ('}', 'RBRACE'),
    (',', 'COMMA'),
    ('.', 'DOT'),
    (';', 'SEMICOLON'),
    ("\'", 'APOSTROPHE'),
]

@pytest.mark.parametrize('test, expected', separator_tests)
def test_separators(test, expected):
    tokens = tokenize(test)
    assert tokens[0].type == expected


command_tests = [
    ('aux', 'AUX'),
    ('par', 'PAR'),
    ('p', 'PAR'),
    ('init', 'INIT'),
    ('i', 'INIT'),
    ('@', 'OPTION'),
    ('global', 'GLOBAL'),
    ('markov', 'MARKOV'),
    ('wiener', 'WIENER'),
    ('bndry', 'BNDRY'),
    ('table', 'TABLE'),
    ('done', 'DONE'),
    ('number', 'NUMBERCMD'),
    ('dv/dt', 'DIFF_LEIBNIZ'),
    ('dx1/dt', 'DIFF_LEIBNIZ'),
    ("v'", 'DIFF_EULER'),
]


@pytest.mark.parametrize('cmd, expected', command_tests)
def test_commands(cmd, expected):
    tokens = tokenize(cmd)
    assert tokens[0].type == expected


def test_array_slice():
    input_string = '[1..2]'
    expected = ['LBRACKET', 'INTEGER', 'DOT', 'DOT', 'INTEGER', 'RBRACKET']
    tokens = tokenize(input_string)
    assert [token.type for token in tokens] == expected


id_tests = [
    ('_x', 'ID'),
    ('v1', 'ID'),
    ('V_1', 'ID')
]


@pytest.mark.parametrize('test, expected', id_tests)
def test_id(test, expected):
    tokens = tokenize(test)
    assert tokens[0].type == expected
