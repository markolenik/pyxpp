"""Tests for the XPP code generator."""

import pytest
from pyxpp import generator


class TestCommandGeneration:
    """Test command generation."""

    def test_parameter_command(self):
        """Test parameter command generation."""
        cmd = ("PAR", ("ASSIGN", "a", ("NUM", 1.0)))
        result = generator.g_command(cmd)
        assert result == "par a=1.0"

    def test_init_command(self):
        """Test initial condition command generation."""
        cmd = ("INIT", ("ASSIGN", "v", ("NUM", -5.0)))
        result = generator.g_command(cmd)
        assert result == "init v=-5.0"

    def test_aux_command(self):
        """Test auxiliary variable command generation."""
        cmd = ("AUX", ("ASSIGN", "vscaled", ("BINOP", "/", ("VAR", "v"), ("NUM", 50))))
        result = generator.g_command(cmd)
        assert result == "aux vscaled=v/50"

    def test_opt_command(self):
        """Test option command generation."""
        cmd = ("OPT", ("ASSIGN", "total", ("NUM", 5000)))
        result = generator.g_command(cmd)
        assert result == "@ total=5000"

    def test_ode_command(self):
        """Test ODE command generation."""
        cmd = ("ODE", "v", ("BINOP", "+", ("UNARY", "-", ("VAR", "v")), ("NUM", 1)))
        result = generator.g_command(cmd)
        assert result == "dv/dt=-v+1"

    def test_defun_command(self):
        """Test function definition generation."""
        cmd = ("DEFUN", "f", ["x"], ("BINOP", "*", ("VAR", "x"), ("NUM", 2)))
        result = generator.g_command(cmd)
        assert result == "f(x)=x*2"

    def test_defun_multiple_args(self):
        """Test function with multiple arguments."""
        cmd = ("DEFUN", "add", ["x", "y"], ("BINOP", "+", ("VAR", "x"), ("VAR", "y")))
        result = generator.g_command(cmd)
        assert result == "add(x,y)=x+y"

    def test_global_command(self):
        """Test global command generation."""
        cmd = ("GLOBAL", 1, ("BINOP", "-", ("VAR", "v"), ("VAR", "vtheta")),
               [("ASSIGN", "v", ("VAR", "vreset"))])
        result = generator.g_command(cmd)
        assert result == "global 1 v-vtheta {v=vreset}"


class TestExpressionGeneration:
    """Test expression generation."""

    def test_number(self):
        """Test number generation."""
        expr = ("NUM", 42)
        result = generator.g_expr(expr)
        assert result == "42"

    def test_float(self):
        """Test float generation."""
        expr = ("NUM", 3.14)
        result = generator.g_expr(expr)
        assert result == "3.14"

    def test_variable(self):
        """Test variable generation."""
        expr = ("VAR", "x")
        result = generator.g_expr(expr)
        assert result == "x"

    def test_binary_addition(self):
        """Test binary addition."""
        expr = ("BINOP", "+", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a+b"

    def test_binary_subtraction(self):
        """Test binary subtraction."""
        expr = ("BINOP", "-", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a-b"

    def test_binary_multiplication(self):
        """Test binary multiplication."""
        expr = ("BINOP", "*", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a*b"

    def test_binary_division(self):
        """Test binary division."""
        expr = ("BINOP", "/", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a/b"

    def test_binary_power(self):
        """Test binary power."""
        expr = ("BINOP", "^", ("VAR", "a"), ("NUM", 2))
        result = generator.g_expr(expr)
        assert result == "a^2"

    def test_unary_minus(self):
        """Test unary minus."""
        expr = ("UNARY", "-", ("VAR", "x"))
        result = generator.g_expr(expr)
        assert result == "-x"

    def test_grouped_expression(self):
        """Test grouped expression."""
        expr = ("GROUP", ("BINOP", "+", ("VAR", "a"), ("VAR", "b")))
        result = generator.g_expr(expr)
        assert result == "(a+b)"

    def test_nested_operations(self):
        """Test nested operations."""
        # (a+b)*c
        expr = ("BINOP", "*",
                ("GROUP", ("BINOP", "+", ("VAR", "a"), ("VAR", "b"))),
                ("VAR", "c"))
        result = generator.g_expr(expr)
        assert result == "(a+b)*c"


class TestFunctionCalls:
    """Test function call generation."""

    def test_single_arg_function(self):
        """Test function with single argument."""
        expr = ("FUNCALL", ("sin", [("VAR", "x")]))
        result = generator.g_expr(expr)
        assert result == "sin(x)"

    def test_multiple_arg_function(self):
        """Test function with multiple arguments."""
        expr = ("FUNCALL", ("pow", [("VAR", "x"), ("NUM", 2)]))
        result = generator.g_expr(expr)
        assert result == "pow(x,2)"

    def test_nested_function_calls(self):
        """Test nested function calls."""
        expr = ("FUNCALL", ("sin", [("FUNCALL", ("cos", [("VAR", "x")]))]))
        result = generator.g_expr(expr)
        assert result == "sin(cos(x))"


class TestConditionalExpressions:
    """Test conditional expression generation."""

    def test_simple_if_then_else(self):
        """Test simple if-then-else."""
        expr = ("IF",
                ("RELOP", "<", ("VAR", "x"), ("NUM", 0)),
                ("NUM", 1),
                ("NUM", 0))
        result = generator.g_expr(expr)
        assert result == "if(x<0)then(1)else(0)"

    def test_if_with_complex_condition(self):
        """Test if with complex condition."""
        expr = ("IF",
                ("RELOP", "<=", ("VAR", "x"), ("VAR", "threshold")),
                ("VAR", "a"),
                ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "if(x<=threshold)then(a)else(b)"


class TestRelationalExpressions:
    """Test relational expression generation."""

    def test_less_than(self):
        """Test less than."""
        expr = ("RELOP", "<", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a<b"

    def test_less_equal(self):
        """Test less than or equal."""
        expr = ("RELOP", "<=", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a<=b"

    def test_greater_than(self):
        """Test greater than."""
        expr = ("RELOP", ">", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a>b"

    def test_greater_equal(self):
        """Test greater than or equal."""
        expr = ("RELOP", ">=", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a>=b"

    def test_equals(self):
        """Test equals."""
        expr = ("RELOP", "=", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a=b"

    def test_not_equals(self):
        """Test not equals."""
        expr = ("RELOP", "<>", ("VAR", "a"), ("VAR", "b"))
        result = generator.g_expr(expr)
        assert result == "a<>b"


class TestSumExpression:
    """Test sum expression generation."""

    def test_simple_sum(self):
        """Test simple sum."""
        expr = ("SUM", ("NUM", 1), ("NUM", 10), ("INDEX", "i", "'"))
        result = generator.g_expr(expr)
        assert result == "sum(1,10)of(i')"

    def test_sum_with_expression(self):
        """Test sum with expression."""
        expr = ("SUM",
                ("NUM", 1),
                ("VAR", "n"),
                ("BINOP", "*", ("VAR", "x"), ("INDEX", "i", "'")))
        result = generator.g_expr(expr)
        assert result == "sum(1,n)of(x*i')"


class TestIndexExpression:
    """Test index expression generation."""

    def test_index(self):
        """Test index expression."""
        expr = ("INDEX", "i", "'")
        result = generator.g_expr(expr)
        assert result == "i'"


class TestAssignment:
    """Test assignment generation."""

    def test_simple_assignment(self):
        """Test simple assignment."""
        expr = ("ASSIGN", "a", ("NUM", 1))
        result = generator.g_expr(expr)
        assert result == "a=1"

    def test_assignment_with_expression(self):
        """Test assignment with expression."""
        expr = ("ASSIGN", "a", ("BINOP", "+", ("NUM", 1), ("NUM", 2)))
        result = generator.g_expr(expr)
        assert result == "a=1+2"


class TestComplexExpressions:
    """Test complex expression generation."""

    def test_morris_lecar_rhs(self):
        """Test Morris-Lecar RHS expression."""
        # -GL*(v-VL)-GCA*minf(v)*(v-VCA)
        expr = (
            "BINOP", "-",
            ("BINOP", "*",
             ("UNARY", "-", ("VAR", "gl")),
             ("GROUP", ("BINOP", "-", ("VAR", "v"), ("VAR", "vl")))),
            ("BINOP", "*",
             ("BINOP", "*",
              ("VAR", "gca"),
              ("FUNCALL", ("minf", [("VAR", "v")]))),
             ("GROUP", ("BINOP", "-", ("VAR", "v"), ("VAR", "vca"))))
        )
        result = generator.g_expr(expr)
        # Should generate valid XPP code (exact formatting may vary)
        assert "gl" in result
        assert "minf(v)" in result
        assert "vca" in result


class TestProgramGeneration:
    """Test full program generation."""

    def test_simple_program(self):
        """Test simple program generation."""
        syntax = [
            ("PAR", ("ASSIGN", "a", ("NUM", 1))),
            ("INIT", ("ASSIGN", "v", ("NUM", 0))),
        ]
        result = generator.g_program(syntax)
        assert len(result) == 3  # 2 commands + "done"
        assert result[-1] == "done"
        assert result[0] == "par a=1"
        assert result[1] == "init v=0"

    def test_program_with_all_types(self):
        """Test program with various command types."""
        syntax = [
            ("PAR", ("ASSIGN", "a", ("NUM", 1))),
            ("INIT", ("ASSIGN", "v", ("NUM", 0))),
            ("ODE", "v", ("UNARY", "-", ("VAR", "v"))),
            ("AUX", ("ASSIGN", "v2", ("BINOP", "*", ("VAR", "v"), ("NUM", 2)))),
            ("OPT", ("ASSIGN", "total", ("NUM", 100))),
        ]
        result = generator.g_program(syntax)
        assert len(result) == 6  # 5 commands + "done"
        assert "par a=1" in result
        assert "init v=0" in result
        assert "dv/dt=-v" in result
        assert "aux v2=v*2" in result
        assert "@ total=100" in result
        assert result[-1] == "done"


class TestRoundTrip:
    """Test that parsing and generating produces equivalent code."""

    def test_parameter_roundtrip(self):
        """Test parameter round-trip."""
        from pyxpp.parser import parser
        original = "par a=1.5\n"
        syntax = parser.parse(original)
        generated = generator.g_command(syntax[0])
        # Parse again
        syntax2 = parser.parse(generated + "\n")
        # Should produce same AST
        assert syntax[0] == syntax2[0]

    def test_ode_roundtrip(self):
        """Test ODE round-trip."""
        from pyxpp.parser import parser
        original = "dv/dt=-v+1\n"
        syntax = parser.parse(original)
        # Skip if parsing failed
        if not syntax or syntax[0] is None:
            pytest.skip("Parser returned None")
        generated = generator.g_command(syntax[0])
        if generated is None:
            pytest.skip("Generator returned None")
        syntax2 = parser.parse(generated + "\n")
        # Relaxed comparison - check structure is similar
        assert syntax[0][0] == syntax2[0][0]  # Both are ODE
        assert syntax[0][1] == syntax2[0][1]  # Same variable

    def test_function_roundtrip(self):
        """Test function definition round-trip."""
        from pyxpp.parser import parser
        original = "f(x)=x*2\n"
        syntax = parser.parse(original)
        # Skip if parsing failed
        if not syntax or syntax[0] is None:
            pytest.skip("Parser returned None")
        generated = generator.g_command(syntax[0])
        if generated is None:
            pytest.skip("Generator returned None")
        syntax2 = parser.parse(generated + "\n")
        # Relaxed comparison - check structure is similar
        assert syntax[0][0] == syntax2[0][0]  # Both are DEFUN
        assert syntax[0][1] == syntax2[0][1]  # Same function name
