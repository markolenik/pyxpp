"""Tests for the XPP lexer."""

import pytest
from pyxpp.lexer import lexer


def tokenize(data):
    """Helper function to tokenize input and return list of tokens."""
    lexer.input(data)
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)
    return tokens


class TestBasicTokens:
    """Test basic token recognition."""

    def test_operators(self):
        """Test arithmetic operators."""
        data = "+ - * / ^ **"
        tokens = tokenize(data)
        assert len(tokens) == 6
        assert tokens[0].type == "PLUS"
        assert tokens[1].type == "MINUS"
        assert tokens[2].type == "TIMES"
        assert tokens[3].type == "DIVIDE"
        assert tokens[4].type == "POWER"
        assert tokens[5].type == "POWER"

    def test_comparison_operators(self):
        """Test comparison operators."""
        data = "< <= > >= <>"
        tokens = tokenize(data)
        assert len(tokens) == 5
        assert tokens[0].type == "LT"
        assert tokens[1].type == "LE"
        assert tokens[2].type == "GT"
        assert tokens[3].type == "GE"
        assert tokens[4].type == "NE"

    def test_delimiters(self):
        """Test delimiters and brackets."""
        data = "( ) { } [ ] , ; ="
        tokens = tokenize(data)
        assert len(tokens) == 9
        assert tokens[0].type == "LPAREN"
        assert tokens[1].type == "RPAREN"
        assert tokens[2].type == "LBRACE"
        assert tokens[3].type == "RBRACE"
        assert tokens[4].type == "LBRACKET"
        assert tokens[5].type == "RBRACKET"
        assert tokens[6].type == "COMMA"
        assert tokens[7].type == "SEMI"
        assert tokens[8].type == "EQUALS"

    def test_apostrophe(self):
        """Test apostrophe for derivatives."""
        data = "'"
        tokens = tokenize(data)
        assert len(tokens) == 1
        assert tokens[0].type == "APOSTROPHE"


class TestNumbers:
    """Test number recognition."""

    def test_integers(self):
        """Test integer parsing."""
        data = "42 0 123"
        tokens = tokenize(data)
        assert len(tokens) == 3
        assert all(tok.type == "INTEGER" for tok in tokens)
        assert tokens[0].value == 42
        assert tokens[1].value == 0
        assert tokens[2].value == 123

    def test_floats(self):
        """Test float parsing."""
        data = "3.14 0.5 .5 123."
        tokens = tokenize(data)
        assert len(tokens) == 4
        assert all(tok.type == "FLOAT" for tok in tokens)
        assert tokens[0].value == 3.14
        assert tokens[1].value == 0.5
        assert tokens[2].value == 0.5
        assert tokens[3].value == 123.0


class TestIdentifiers:
    """Test identifier recognition."""

    def test_simple_id(self):
        """Test simple identifier."""
        data = "variable"
        tokens = tokenize(data)
        assert len(tokens) == 1
        assert tokens[0].type == "ID"
        assert tokens[0].value == "variable"

    def test_case_insensitive(self):
        """Test that identifiers are lowercased."""
        data = "MyVar MYVAR myvar"
        tokens = tokenize(data)
        assert len(tokens) == 3
        assert all(tok.value == "myvar" for tok in tokens)

    def test_alphanumeric_id(self):
        """Test alphanumeric identifiers."""
        data = "var1 x2 state99"
        tokens = tokenize(data)
        assert len(tokens) == 3
        assert all(tok.type == "ID" for tok in tokens)


class TestKeywords:
    """Test keyword recognition."""

    def test_if_then_else(self):
        """Test if-then-else keywords."""
        data = "if then else"
        tokens = tokenize(data)
        assert len(tokens) == 3
        assert tokens[0].type == "IF"
        assert tokens[1].type == "THEN"
        assert tokens[2].type == "ELSE"

    def test_sum_of(self):
        """Test sum and of keywords."""
        data = "sum of"
        tokens = tokenize(data)
        assert len(tokens) == 2
        assert tokens[0].type == "SUM"
        assert tokens[1].type == "OF"

    def test_global(self):
        """Test global keyword."""
        data = "global"
        tokens = tokenize(data)
        assert len(tokens) == 1
        assert tokens[0].type == "GLOBAL"


class TestCommands:
    """Test command keyword recognition."""

    def test_par_command(self):
        """Test parameter command."""
        data = "par\nparam\nparameter"
        tokens = tokenize(data)
        # Filter out newlines
        par_tokens = [t for t in tokens if t.type == "PAR"]
        assert len(par_tokens) == 3

    def test_init_command(self):
        """Test init command."""
        data = "init"
        tokens = tokenize(data)
        assert tokens[0].type == "INIT"

    def test_aux_command(self):
        """Test auxiliary command."""
        data = "aux"
        tokens = tokenize(data)
        assert tokens[0].type == "AUX"

    def test_opt_command(self):
        """Test option command."""
        data = "@"
        tokens = tokenize(data)
        assert tokens[0].type == "OPT"


class TestArrays:
    """Test array slice recognition."""

    def test_array_slice(self):
        """Test array slice notation."""
        data = "[1..10]"
        tokens = tokenize(data)
        assert len(tokens) == 1
        assert tokens[0].type == "ARRAYSLICE"

    def test_array_slice_with_spaces(self):
        """Test array slice with spaces."""
        data = "[1  ..  10]"
        tokens = tokenize(data)
        assert len(tokens) == 1
        assert tokens[0].type == "ARRAYSLICE"


class TestComments:
    """Test comment handling."""

    def test_hash_comment(self):
        """Test # style comments."""
        data = "# This is a comment\nvar"
        tokens = tokenize(data)
        # Comments are ignored, should only get newline and var
        assert len(tokens) == 2
        assert tokens[0].type == "NEWLINE"
        assert tokens[1].type == "ID"

    def test_quote_comment(self):
        """Test quote style comments."""
        data = '"This is also a comment\nvar'
        tokens = tokenize(data)
        assert len(tokens) == 2
        assert tokens[0].type == "NEWLINE"
        assert tokens[1].type == "ID"


class TestNewlines:
    """Test newline handling."""

    def test_newlines(self):
        """Test newline tokens."""
        data = "a\nb\nc"
        tokens = tokenize(data)
        assert len(tokens) == 5
        assert tokens[0].type == "ID"
        assert tokens[1].type == "NEWLINE"
        assert tokens[2].type == "ID"
        assert tokens[3].type == "NEWLINE"
        assert tokens[4].type == "ID"


class TestIgnored:
    """Test ignored constructs."""

    def test_whitespace_ignored(self):
        """Test that spaces and tabs are ignored."""
        data = "a   \t  b"
        tokens = tokenize(data)
        assert len(tokens) == 2
        assert tokens[0].value == "a"
        assert tokens[1].value == "b"

    def test_notused_commands(self):
        """Test that unsupported commands are ignored."""
        data = "table something\nvar"
        tokens = tokenize(data)
        # table line should be ignored
        assert len(tokens) == 2
        assert tokens[0].type == "NEWLINE"
        assert tokens[1].type == "ID"


class TestComplexExpressions:
    """Test tokenization of complex expressions."""

    def test_ode_definition(self):
        """Test ODE definition."""
        data = "dv/dt=-GL*(v-VL)"
        tokens = tokenize(data)
        types = [t.type for t in tokens]
        assert "ID" in types  # dv
        assert "DIVIDE" in types
        assert "ID" in types  # dt
        assert "EQUALS" in types
        assert "MINUS" in types
        assert "TIMES" in types

    def test_function_definition(self):
        """Test function definition."""
        data = "minf(v)=.5*(1+tanh((v-VA)/VB))"
        tokens = tokenize(data)
        assert tokens[0].type == "ID"
        assert tokens[1].type == "LPAREN"
        # Should contain floats, operators, etc.
        assert any(t.type == "FLOAT" for t in tokens)
        assert any(t.type == "RPAREN" for t in tokens)

    def test_if_expression(self):
        """Test if-then-else expression."""
        data = "if(x<0)then(1)else(0)"
        tokens = tokenize(data)
        types = [t.type for t in tokens]
        assert "IF" in types
        assert "THEN" in types
        assert "ELSE" in types
        assert "LT" in types
