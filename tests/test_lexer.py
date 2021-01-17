import pytest
from pyxpp.lexer import tokenize


def test_literals():
    literals = '1.0 4 \n'
    expected = ['FLOAT', 'INTEGER', 'NEWLINE']
    tokens = tokenize(literals)
    assert [token.type for token in tokens] == expected


def test_operators():
    operators = '+ - * / ^ ** = < <= > >= <>'
    expected = ["PLUS", "MINUS", "TIMES", "DIVIDE", "POWER",
                'POWER', "EQUALS", "LT", "LE", "GT", "GE",
                "NE", ]
    tokens = tokenize(operators)
    assert [token.type for token in tokens] == expected


def test_separators():
    separators = '( ) [ ] { } , . ; \''
    expected = [
        "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE",
        "COMMA", 'DOT', "SEMICOLON", "APOSTROPHE",
    ]
    tokens = tokenize(separators)
    assert [token.type for token in tokens] == expected


def test_keywords():
    keywords = 'sum if else then of'
    expected = ['SUM', "IF", "ELSE", "THEN", "OF"]
    tokens = tokenize(keywords)
    assert [token.type for token in tokens] == expected


def test_declarations():
    declarations = 'aux \np \npar \ni \ninit \n@ \nglobal'
    expected = [
        'AUX', 'NEWLINE', 'PAR', 'NEWLINE', 'PAR',
        'NEWLINE', 'INIT', 'NEWLINE', 'INIT', 'NEWLINE',
        'OPTION', 'NEWLINE', 'GLOBAL',
    ]
    tokens = tokenize(declarations)
    assert [token.type for token in tokens] == expected


def test_array_slice():
    input_string = '[1..2]'
    expected = ['LBRACKET', 'INTEGER', 'DOT', 'DOT', 'INTEGER', 'RBRACKET']
    tokens = tokenize(input_string)
    assert [token.type for token in tokens] == expected


def test_id():
    input_string = '_x v1 V_1'
    expected = ['ID', 'ID', 'ID']
    tokens = tokenize(input_string)
    assert [token.type for token in tokens] == expected


def test_done():
    tokens = tokenize('done')
    assert [token.type for token in tokens] == ['DONE']


def test_unpythonic_identifiers():
    input_string = 'v1. 1v 1.V'
    expected = ['ID', 'DOT', 'INTEGER', 'ID', 'FLOAT', 'ID']
    tokens = tokenize(input_string)
    assert [token.type for token in tokens] == expected
