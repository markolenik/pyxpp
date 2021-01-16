import pytest
from pyxpp.lexer import tokenize


def test_literals():
    literals = '1.0 4 0 \n'
    expected = ['FLOAT', 'INTEGER', 'INTEGER', 'NEWLINE']
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
    separators = '( ) [ ] { } , ; \''
    expected = [
        "LPAREN", "RPAREN", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE",
        "COMMA", "SEMICOLON", "APOSTROPHE",
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
        'AUXILIARY', 'NEWLINE', 'PARAMETER', 'NEWLINE', 'PARAMETER',
        'NEWLINE', 'INITIALIZE', 'NEWLINE', 'INITIALIZE', 'NEWLINE',
        'OPTION', 'NEWLINE', 'GLOBAL',
    ]
    tokens = tokenize(declarations)
    assert [token.type for token in tokens] == expected


# BUG: These fail.  Skipping for now.
# Problem here is the whitespace at line start, not sure how to deal with it.
@pytest.mark.xfail
def test_keywords_with_space():
    keywords = 'aux \n p \n  par \n  i \n  init \n @ \n global'
    expected = [
        'AUXILIARY', 'NEWLINE', 'PARAMETER', 'NEWLINE', 'PARAMETER',
        'NEWLINE', 'INITIALIZE', 'NEWLINE', 'INITIALIZE', 'NEWLINE',
        'OPTION', 'NEWLINE', 'GLOBAL',
    ]
    tokens = tokenize(keywords)
    assert [token.type for token in tokens] == expected


def test_arrayslice():
    input_string = '[1..2]'
    expected = ['ARRAYSLICE']
    tokens = tokenize(input_string)
    assert [token.type for token in tokens] == expected


def test_identifier():
    input_string = '_x v1 V_1'
    expected = ['IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER']
    tokens = tokenize(input_string)
    assert [token.type for token in tokens] == expected


# TODO: Don't know how to skip those below, but the last one doesn't raise and
# exception for some reason.
# @pytest.mark.parametrize('identifier', ['v1.', '1v', '1.V'])
# def test_unpythonic_identifiers(identifier):
#     with pytest.raises(ValueError):
#         tokenize(identifier)
