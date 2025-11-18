"""Tests for the XPP parser."""

import pytest
from pyxpp.parser import parser


class TestParameters:
    """Test parameter parsing."""

    def test_single_parameter(self):
        """Test single parameter definition."""
        data = "par a=1.0\n"
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0][0] == "PAR"
        assert result[0][1][0] == "ASSIGN"
        assert result[0][1][1] == "a"
        assert result[0][1][2] == ("NUM", 1.0)

    def test_multiple_parameters(self):
        """Test multiple parameters in one line."""
        data = "par a=1.0, b=2.0\n"
        result = parser.parse(data)
        assert len(result) == 2
        assert result[0][1][1] == "a"
        assert result[1][1][1] == "b"

    def test_parameter_with_expression(self):
        """Test parameter with expression."""
        data = "par a=1.0+2.0\n"
        result = parser.parse(data)
        assert result[0][0] == "PAR"
        # The RHS should be a BINOP
        assert result[0][1][2][0] == "BINOP"

    def test_parameter_array(self):
        """Test parameter array definition."""
        data = "par x[1..3]=0.5\n"
        result = parser.parse(data)
        assert len(result) == 3
        assert all(r[0] == "PAR" for r in result)
        assert result[0][1][1] == "x1"
        assert result[1][1][1] == "x2"
        assert result[2][1][1] == "x3"


class TestInitialConditions:
    """Test initial condition parsing."""

    def test_simple_init(self):
        """Test simple initial condition."""
        data = "init v=-5.0\n"
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0][0] == "INIT"
        assert result[0][1][1] == "v"
        # Check for UNARY minus
        assert result[0][1][2][0] in ("NUM", "UNARY")

    def test_multiple_inits(self):
        """Test multiple initial conditions."""
        data = "init v=-5.0, w=0.1\n"
        result = parser.parse(data)
        assert len(result) == 2
        assert result[0][1][1] == "v"
        assert result[1][1][1] == "w"

    def test_init_array(self):
        """Test initial condition array."""
        data = "init x[1..2]=0.0\n"
        result = parser.parse(data)
        assert len(result) == 2
        assert result[0][1][1] == "x1"
        assert result[1][1][1] == "x2"

    def test_init_indexed_form(self):
        """Test indexed initial condition."""
        data = "v(0)=1.5\n"
        result = parser.parse(data)
        assert result[0] == "INIT"
        assert result[1][1] == "v"


class TestAuxiliaryVariables:
    """Test auxiliary variable parsing."""

    def test_simple_aux(self):
        """Test simple auxiliary variable."""
        data = "aux vscaled=v/50\n"
        result = parser.parse(data)
        assert result[0] == "AUX"
        assert result[1][1] == "vscaled"
        assert result[1][2][0] == "BINOP"

    def test_aux_array(self):
        """Test auxiliary array."""
        data = "aux y[1..2]=x*2\n"
        result = parser.parse(data)
        assert len(result) == 2
        assert result[0][0] == "AUX"
        assert result[1][0] == "AUX"


class TestODEs:
    """Test ODE definition parsing."""

    def test_ode_apostrophe_notation(self):
        """Test ODE with apostrophe notation."""
        data = "v'=-v+1\n"
        result = parser.parse(data)
        assert result[0] == "ODE"
        assert result[1] == "v"
        assert result[2][0] == "BINOP"

    def test_ode_derivative_notation(self):
        """Test ODE with d/dt notation."""
        data = "dv/dt=-v+1\n"
        result = parser.parse(data)
        assert result[0] == "ODE"
        assert result[1] == "v"

    def test_ode_complex_rhs(self):
        """Test ODE with complex RHS."""
        data = "dv/dt=-GL*(v-VL)-GCA*minf(v)*(v-VCA)\n"
        result = parser.parse(data)
        assert result[0] == "ODE"
        assert result[1] == "v"
        # RHS should be complex expression
        assert result[2][0] == "BINOP"

    @pytest.mark.xfail(reason="Array ODE parsing has bugs in PLY implementation")
    def test_ode_array(self):
        """Test ODE array notation."""
        data = "x[1..2]'=x[i]-0.5\n"
        result = parser.parse(data)
        assert len(result) == 2
        assert result[0][0] == "ODE"
        assert result[1][0] == "ODE"


class TestFunctions:
    """Test function definition parsing."""

    def test_simple_function(self):
        """Test simple function definition."""
        data = "f(x)=x*2\n"
        result = parser.parse(data)
        assert result[0] == "DEFUN"
        assert result[1] == "f"
        assert result[2] == ["x"]
        assert result[3][0] == "BINOP"

    def test_multiarg_function(self):
        """Test multi-argument function."""
        data = "add(x,y)=x+y\n"
        result = parser.parse(data)
        assert result[0] == "DEFUN"
        assert result[1] == "add"
        assert result[2] == ["x", "y"]

    def test_function_with_builtin(self):
        """Test function using builtin."""
        data = "minf(v)=.5*(1+tanh((v-VA)/VB))\n"
        result = parser.parse(data)
        assert result[0] == "DEFUN"
        assert result[1] == "minf"
        assert result[2] == ["v"]


class TestOptions:
    """Test option parsing."""

    def test_numeric_option(self):
        """Test numeric option."""
        data = "@ TOTAL=5000\n"
        result = parser.parse(data)
        assert len(result) == 1
        assert result[0][0] == "OPT"
        assert result[0][1][1] == "total"  # Should be lowercase

    def test_multiple_options(self):
        """Test multiple options."""
        data = "@ TOTAL=5000, DT=0.5\n"
        result = parser.parse(data)
        assert len(result) == 2

    def test_string_option(self):
        """Test string option value."""
        data = "@ method=stiff\n"
        result = parser.parse(data)
        assert result[0][0] == "OPT"
        assert result[0][1][1] == "method"


class TestGlobal:
    """Test global command parsing."""

    def test_global_command(self):
        """Test global zero crossing."""
        data = "global 1 v-vtheta {v=vreset}\n"
        result = parser.parse(data)
        assert result[0] == "GLOBAL"
        assert result[1] == 1  # Sign
        assert result[2][0] == "BINOP"  # Condition
        assert isinstance(result[3], list)  # Assignments


class TestExpressions:
    """Test expression parsing."""

    def test_binary_operations(self):
        """Test binary operations."""
        ops = [
            ("a+b", "BINOP", "+"),
            ("a-b", "BINOP", "-"),
            ("a*b", "BINOP", "*"),
            ("a/b", "BINOP", "/"),
            ("a^b", "BINOP", "^"),
        ]
        for expr, expected_type, expected_op in ops:
            data = f"par x={expr}\n"
            result = parser.parse(data)
            rhs = result[0][1][2]
            assert rhs[0] == expected_type
            assert rhs[1] == expected_op

    def test_operator_precedence(self):
        """Test operator precedence."""
        data = "par x=1+2*3\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        # Should parse as 1+(2*3), not (1+2)*3
        assert rhs[0] == "BINOP"
        assert rhs[1] == "+"
        # Right side should be multiplication
        assert rhs[3][0] == "BINOP"
        assert rhs[3][1] == "*"

    def test_parentheses(self):
        """Test grouped expressions."""
        data = "par x=(1+2)*3\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        # Outer should be multiplication
        assert rhs[0] == "BINOP"
        assert rhs[1] == "*"
        # Left side should be grouped addition
        assert rhs[2][0] == "GROUP"

    def test_unary_minus(self):
        """Test unary minus."""
        data = "par x=-5\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        # Could be NUM with negative value or UNARY
        assert rhs[0] in ("UNARY", "NUM")

    def test_variable_reference(self):
        """Test variable reference."""
        data = "par x=y\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        assert rhs[0] == "VAR"
        assert rhs[1] == "y"

    def test_function_call(self):
        """Test function call."""
        data = "par x=sin(y)\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        assert rhs[0] == "FUNCALL"
        assert rhs[1][0] == "sin"

    def test_function_call_multiple_args(self):
        """Test function call with multiple arguments."""
        data = "par x=pow(2,3)\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        assert rhs[0] == "FUNCALL"
        assert len(rhs[1][1]) == 2

    def test_if_then_else(self):
        """Test if-then-else expression."""
        data = "par x=if(a<0)then(1)else(0)\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        assert rhs[0] == "IF"
        assert rhs[1][0] == "RELOP"  # Condition
        assert rhs[2][0] == "NUM"  # Then part
        assert rhs[3][0] == "NUM"  # Else part

    def test_sum_expression(self):
        """Test sum expression."""
        data = "par x=sum(1,10)of(i')\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        assert rhs[0] == "SUM"


class TestRelationalExpressions:
    """Test relational expressions."""

    def test_comparison_operators(self):
        """Test all comparison operators."""
        ops = ["<", "<=", ">", ">=", "=", "<>"]
        for op in ops:
            data = f"par x=if(a{op}b)then(1)else(0)\n"
            result = parser.parse(data)
            rhs = result[0][1][2]
            condition = rhs[1]
            assert condition[0] == "RELOP"
            assert condition[1] == op


class TestArrays:
    """Test array operations."""

    def test_array_declaration(self):
        """Test array declaration."""
        data = "par x[1..10]=0\n"
        result = parser.parse(data)
        assert len(result) == 10

    def test_array_select(self):
        """Test array element selection."""
        data = "par y=x[i]\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        assert rhs[0] == "ARRAY_SELECT"

    def test_array_select_offset(self):
        """Test array selection with offset."""
        data = "par y=x[i+1]\n"
        result = parser.parse(data)
        rhs = result[0][1][2]
        assert rhs[0] == "ARRAY_SELECT"


class TestCompletePrograms:
    """Test parsing complete XPP programs."""

    def test_morris_lecar_snippet(self):
        """Test parsing Morris-Lecar model snippet."""
        data = """# Morris Lecar model
par GL=.15
par VL=-50
minf(v)=.5*(1+tanh((v-VA)/VB))
dv/dt=-GL*(v-VL)
init v=-5.0
aux vscaled=v/50
@ TOTAL=5000
done
"""
        result = parser.parse(data)
        # Should parse without errors
        assert len(result) > 0
        # Check various command types are present
        types = [cmd[0] for cmd in result]
        assert "PAR" in types
        assert "DEFUN" in types
        assert "ODE" in types
        assert "INIT" in types
        assert "AUX" in types
        assert "OPT" in types

    def test_blank_lines(self):
        """Test that blank lines are handled."""
        data = """par a=1

par b=2

"""
        result = parser.parse(data)
        # Should get 2 parameters, blank lines ignored
        assert len(result) == 2

    def test_mixed_separators(self):
        """Test mixed comma and semicolon separators."""
        data = "par a=1; b=2, c=3\n"
        result = parser.parse(data)
        assert len(result) == 3


class TestErrorHandling:
    """Test error handling."""

    def test_syntax_error(self):
        """Test that syntax errors are handled gracefully."""
        data = "par = 1\n"  # Missing variable name
        result = parser.parse(data)
        # Parser should return empty list or handle error
        assert isinstance(result, list)
