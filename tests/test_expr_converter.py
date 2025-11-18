"""Tests for expression converter and function-to-lambda conversion."""

import pytest
import numpy as np
from pyxpp import expr_converter


class TestExprToPython:
    """Test expr_to_python function."""

    def test_number(self):
        """Test converting numbers."""
        expr = ("NUM", 42)
        result = expr_converter.expr_to_python(expr)
        assert result == "42"

    def test_variable(self):
        """Test converting variables."""
        expr = ("VAR", "x")
        result = expr_converter.expr_to_python(expr)
        assert result == "x"

    def test_binary_addition(self):
        """Test binary addition."""
        expr = ("BINOP", "+", ("VAR", "x"), ("NUM", 1))
        result = expr_converter.expr_to_python(expr)
        assert result == "(x + 1)"

    def test_binary_multiplication(self):
        """Test binary multiplication."""
        expr = ("BINOP", "*", ("VAR", "x"), ("NUM", 2))
        result = expr_converter.expr_to_python(expr)
        assert result == "(x * 2)"

    def test_power_operator(self):
        """Test power operator conversion."""
        expr = ("BINOP", "^", ("VAR", "x"), ("NUM", 2))
        result = expr_converter.expr_to_python(expr)
        assert result == "(x ** 2)"

    def test_unary_minus(self):
        """Test unary minus."""
        expr = ("UNARY", "-", ("VAR", "x"))
        result = expr_converter.expr_to_python(expr)
        assert result == "-x"

    def test_function_call(self):
        """Test function call conversion."""
        expr = ("FUNCALL", ("sin", [("VAR", "x")]))
        result = expr_converter.expr_to_python(expr)
        assert result == "np.sin(x)"

    def test_function_call_multiple_args(self):
        """Test function call with multiple arguments."""
        expr = ("FUNCALL", ("pow", [("VAR", "x"), ("NUM", 2)]))
        result = expr_converter.expr_to_python(expr)
        assert result == "np.power(x, 2)"

    def test_if_then_else(self):
        """Test if-then-else conversion."""
        expr = ("IF",
                ("RELOP", "<", ("VAR", "x"), ("NUM", 0)),
                ("NUM", 1),
                ("NUM", 0))
        result = expr_converter.expr_to_python(expr)
        assert "(1 if (x < 0) else 0)" in result

    def test_relational_equals(self):
        """Test relational equals conversion."""
        expr = ("RELOP", "=", ("VAR", "x"), ("NUM", 1))
        result = expr_converter.expr_to_python(expr)
        assert result == "(x == 1)"

    def test_relational_not_equals(self):
        """Test relational not-equals conversion."""
        expr = ("RELOP", "<>", ("VAR", "x"), ("NUM", 1))
        result = expr_converter.expr_to_python(expr)
        assert result == "(x != 1)"

    def test_nested_expression(self):
        """Test nested expression."""
        # (x + 1) * 2
        expr = ("BINOP", "*",
                ("GROUP", ("BINOP", "+", ("VAR", "x"), ("NUM", 1))),
                ("NUM", 2))
        result = expr_converter.expr_to_python(expr)
        assert "((x + 1))" in result
        assert "* 2" in result

    def test_parameter_substitution(self):
        """Test parameter value substitution."""
        expr = ("BINOP", "*", ("VAR", "a"), ("VAR", "x"))
        result = expr_converter.expr_to_python(expr, {"a": 2.5})
        assert result == "(2.5 * x)"


class TestFunctionToLambda:
    """Test function_to_lambda function."""

    def test_simple_function(self):
        """Test simple function conversion."""
        func = ("DEFUN", "f", ["x"], ("BINOP", "*", ("VAR", "x"), ("NUM", 2)))
        name, lam = expr_converter.function_to_lambda(func)

        assert name == "f"
        assert lam(5) == 10
        assert lam(3) == 6

    def test_function_with_addition(self):
        """Test function with addition."""
        func = ("DEFUN", "g", ["x"], ("BINOP", "+", ("VAR", "x"), ("NUM", 1)))
        name, lam = expr_converter.function_to_lambda(func)

        assert name == "g"
        assert lam(5) == 6

    def test_function_with_power(self):
        """Test function with power."""
        func = ("DEFUN", "square", ["x"], ("BINOP", "^", ("VAR", "x"), ("NUM", 2)))
        name, lam = expr_converter.function_to_lambda(func)

        assert name == "square"
        assert lam(3) == 9
        assert lam(4) == 16

    def test_function_with_numpy(self):
        """Test function using numpy functions."""
        func = ("DEFUN", "sigmoid", ["x"],
                ("BINOP", "/",
                 ("NUM", 1),
                 ("BINOP", "+",
                  ("NUM", 1),
                  ("FUNCALL", ("exp", [("UNARY", "-", ("VAR", "x"))])))))
        name, lam = expr_converter.function_to_lambda(func)

        assert name == "sigmoid"
        result = lam(0)
        assert abs(result - 0.5) < 0.001  # sigmoid(0) ≈ 0.5

    def test_multiple_arguments(self):
        """Test function with multiple arguments."""
        func = ("DEFUN", "add", ["x", "y"], ("BINOP", "+", ("VAR", "x"), ("VAR", "y")))
        name, lam = expr_converter.function_to_lambda(func)

        assert name == "add"
        assert lam(3, 5) == 8
        assert lam(10, -2) == 8

    def test_function_with_parameters(self):
        """Test function with parameter substitution."""
        func = ("DEFUN", "scale", ["x"], ("BINOP", "*", ("VAR", "a"), ("VAR", "x")))
        name, lam = expr_converter.function_to_lambda(func, {"a": 3})

        assert name == "scale"
        assert lam(5) == 15


class TestExtractFunctions:
    """Test extract_functions function."""

    def test_extract_single_function(self):
        """Test extracting single function."""
        syntax = [
            ("PAR", ("ASSIGN", "a", ("NUM", 1))),
            ("DEFUN", "f", ["x"], ("BINOP", "*", ("VAR", "x"), ("NUM", 2))),
        ]
        funcs = expr_converter.extract_functions(syntax)

        assert "f" in funcs
        assert funcs["f"](5) == 10

    def test_extract_multiple_functions(self):
        """Test extracting multiple functions."""
        syntax = [
            ("DEFUN", "f", ["x"], ("BINOP", "*", ("VAR", "x"), ("NUM", 2))),
            ("DEFUN", "g", ["x"], ("BINOP", "+", ("VAR", "x"), ("NUM", 1))),
        ]
        funcs = expr_converter.extract_functions(syntax)

        assert "f" in funcs
        assert "g" in funcs
        assert funcs["f"](5) == 10
        assert funcs["g"](5) == 6

    def test_extract_no_functions(self):
        """Test extracting from syntax with no functions."""
        syntax = [
            ("PAR", ("ASSIGN", "a", ("NUM", 1))),
            ("ODE", "x", ("UNARY", "-", ("VAR", "x"))),
        ]
        funcs = expr_converter.extract_functions(syntax)

        assert len(funcs) == 0


class TestReadFunctions:
    """Test read_functions function."""

    def test_read_functions_from_file(self):
        """Test reading functions from XPP file."""
        import os
        filepath = os.path.join(os.path.dirname(__file__), "fixtures", "functions.ode")

        funcs = expr_converter.read_functions(filepath)

        # Should have extracted 3 functions from the test file
        assert "f" in funcs
        assert "g" in funcs
        assert "sigmoid" in funcs

        # Test the functions work
        assert funcs["f"](5) == 10
        assert funcs["g"](3, 7) == 10

    def test_read_functions_with_numpy_calls(self):
        """Test functions using numpy work correctly."""
        import os
        import tempfile

        # Create a test file with numpy functions
        content = """
par a=1.0

minf(v)=0.5*(1+tanh(v))

dv/dt=-v
init v=0

done
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ode', delete=False) as f:
            f.write(content)
            filepath = f.name

        try:
            funcs = expr_converter.read_functions(filepath)

            assert "minf" in funcs

            # Test that tanh is working
            result = funcs["minf"](0)
            assert abs(result - 0.5) < 0.001

        finally:
            os.unlink(filepath)


class TestXPPFunctionMapping:
    """Test XPP to Python function name mapping."""

    def test_trig_functions(self):
        """Test trigonometric function mapping."""
        funcs = [
            ("sin", "np.sin"),
            ("cos", "np.cos"),
            ("tan", "np.tan"),
            ("tanh", "np.tanh"),
        ]

        for xpp_func, py_func in funcs:
            expr = ("FUNCALL", (xpp_func, [("NUM", 0)]))
            result = expr_converter.expr_to_python(expr)
            assert py_func in result

    def test_exp_log_functions(self):
        """Test exponential and logarithm functions."""
        funcs = [
            ("exp", "np.exp"),
            ("log", "np.log"),
            ("sqrt", "np.sqrt"),
        ]

        for xpp_func, py_func in funcs:
            expr = ("FUNCALL", (xpp_func, [("NUM", 1)]))
            result = expr_converter.expr_to_python(expr)
            assert py_func in result


class TestComplexExpressions:
    """Test complex mathematical expressions."""

    def test_morris_lecar_minf(self):
        """Test Morris-Lecar minf function."""
        # minf(v) = 0.5*(1+tanh((v-VA)/VB))
        func = ("DEFUN", "minf", ["v"],
                ("BINOP", "*",
                 ("NUM", 0.5),
                 ("BINOP", "+",
                  ("NUM", 1),
                  ("FUNCALL", ("tanh",
                               [("BINOP", "/",
                                 ("BINOP", "-", ("VAR", "v"), ("VAR", "va")),
                                 ("VAR", "vb"))])))))

        name, lam = expr_converter.function_to_lambda(func, {"va": 1, "vb": 14.5})

        assert name == "minf"

        # Test some values
        result = lam(0)
        assert 0 <= result <= 1  # Should be between 0 and 1

        result = lam(15)
        assert 0 <= result <= 1
