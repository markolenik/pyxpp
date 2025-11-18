# An XPP parser based on Lark.
#
# This file is part of PyXPP.
#
# PyXPP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyXPP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyXPP.  If not, see <http://www.gnu.org/licenses/>.

import copy
import os
from lark import Lark, Transformer, v_args
from lark.exceptions import ParseError, LarkError


# Load grammar
GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "xpp.lark")
with open(GRAMMAR_PATH) as f:
    XPP_GRAMMAR = f.read()


@v_args(inline=False)
class XPPTransformer(Transformer):
    """Transform Lark parse tree to PLY-compatible AST.

    Note: @v_args(inline=False) means we receive items as a list,
    but Lark only passes non-literal tokens by default.
    """

    # Program structure
    def program(self, items):
        """Flatten program into list of commands."""
        from lark.lexer import Token
        result = []
        for item in items:
            # Skip Token objects (like "done")
            if isinstance(item, Token):
                continue
            if isinstance(item, list):
                result.extend(item)
            elif item is not None:
                result.append(item)
        return result

    def stmt(self, items):
        """Extract command from statement."""
        return items[0]

    def blank_line(self, items):
        """Ignore blank lines."""
        return []

    # Parameter commands
    def par_assign(self, items):
        """Parameter assignments (PAR assignments)."""
        # items[0] = PAR token, items[1] = assignments
        assigns = items[1]
        return [("PAR", assign) for assign in assigns]

    def par_array(self, items):
        """Parameter array definition (PAR array "=" number)."""
        # items[0] = PAR token, items[1] = array, items[2] = number
        arr, num = items[1], items[2]
        statevar, indices = arr
        return [("PAR", ("ASSIGN", statevar + str(x), num)) for x in indices]

    # Initial condition commands
    def init_assign(self, items):
        """Init assignments (INIT assignments)."""
        # items[0] = INIT token, items[1] = assignments
        assigns = items[1]
        return [("INIT", assign) for assign in assigns]

    def init_indexed(self, items):
        """Indexed init (ID "(" INTEGER ")" "=" expr)."""
        # items = [ID, INTEGER_as_NUM_tuple, expr] - no terminals to skip
        var, idx_tuple, expr = items[0], items[1], items[2]
        return ("INIT", ("ASSIGN", var, expr))

    def init_array(self, items):
        """Init array definition (INIT array "=" expr)."""
        # items[0] = INIT token, items[1] = array, items[2] = expr
        arr, expr = items[1], items[2]
        statevar, indices = arr
        return [("INIT", ("ASSIGN", statevar + str(x), expr)) for x in indices]

    def init_array_indexed(self, items):
        """Indexed array init (array "(" INTEGER ")" "=" expr)."""
        # items = [array, INTEGER_as_NUM_tuple, expr]
        arr, idx_tuple, expr = items[0], items[1], items[2]
        statevar, indices = arr
        return [("INIT", ("ASSIGN", statevar + str(x), expr)) for x in indices]

    # Auxiliary variable commands
    def aux_var(self, items):
        """Auxiliary variable (AUX ID "=" expr)."""
        # items = [AUX_token, ID, expr] - skip AUX token
        var, expr = items[1], items[2]
        return ("AUX", ("ASSIGN", var, expr))

    def aux_array(self, items):
        """Auxiliary array (AUX array "=" expr)."""
        # items = [AUX_token, array, expr] - skip AUX token
        arr, expr = items[1], items[2]
        statevar, indices = arr
        return [("AUX", ("ASSIGN", statevar + str(x), expr)) for x in indices]

    # Option commands
    def opt_assign(self, items):
        """Option assignments (OPT assignments)."""
        # items[0] = OPT token, items[1] = assignments
        assigns = items[1]
        return [("OPT", assign) for assign in assigns]

    # Global command
    def global_cmd(self, items):
        """Global zero-crossing command (GLOBAL INTEGER relexpr "{" assignments "}")."""
        # items[0] = GLOBAL token, items[1] = INTEGER_as_NUM_tuple, items[2] = relexpr, items[3] = assignments
        sign_tuple, condition, assigns = items[1], items[2], items[3]
        # Extract integer value from NUM tuple
        sign = sign_tuple[1] if isinstance(sign_tuple, tuple) else sign_tuple
        return ("GLOBAL", sign, condition, assigns)

    # Function definition
    def defun(self, items):
        """Function definition (ID "(" idlist ")" "=" expr)."""
        # items = [ID, idlist, expr] - no command terminal
        fname, args, expr = items[0], items[1], items[2]
        return ("DEFUN", fname, args, expr)

    # ODE commands
    def ode_apostrophe(self, items):
        """ODE with apostrophe notation (ID "'" "=" expr)."""
        # items = [ID, expr] - apostrophe and equals are literals
        var, expr = items[0], items[1]
        return ("ODE", var, expr)

    def ode_derivative(self, items):
        """ODE with d/dt notation (ID "/" ID "=" expr)."""
        # items = [ID, ID, expr] - first ID is like "dv", second is "dt"
        dvar, dt, expr = items[0], items[1], items[2]
        # Extract variable name from dvar (e.g., "dv" -> "v")
        var = dvar[1:] if dvar.startswith('d') else dvar
        return ("ODE", var, expr)

    def ode_array(self, items):
        """ODE array definition."""
        arr, expr = items
        statevar, indices = arr

        def subst(ex, var, idx):
            """Substitute array variables in expression."""
            if not isinstance(ex, tuple):
                return ex
            if ex[0] == "ARRAY_SELECT" and ex[1][0] == var:
                idxfun = ex[1][1]
                if callable(idxfun):
                    newidx = idxfun(idx)
                else:
                    newidx = idx
                return ("VAR", (var + str(newidx), None, None))
            return tuple(subst(x, var, idx) for x in ex)

        return [("ODE", statevar + str(x), subst(expr, statevar, x)) for x in indices]

    # Assignments
    def assignments(self, items):
        """List of assignments."""
        return items

    def assignment(self, items):
        """Single assignment (ID "=" expr)."""
        # items = [ID, expr] - "=" is literal, optional "," or ";" are literals
        var = items[0]
        expr = items[1]
        return ("ASSIGN", var, expr)

    # Arrays
    def array(self, items):
        """Array definition (ID ARRAYSLICE)."""
        # items = [ID, ARRAYSLICE] both after terminal handlers
        var, slice_str = items[0], items[1]
        # Parse slice notation [x..y]
        slice_str = str(slice_str)
        start_idx = slice_str.index('[') + 1
        end_idx = slice_str.index(']')
        slice_part = slice_str[start_idx:end_idx]
        dot_idx = slice_part.index('..')
        x0 = int(slice_part[:dot_idx].strip())
        x1 = int(slice_part[dot_idx+2:].strip())
        return (var, list(range(x0, x1 + 1)))

    # Expression lists
    def exprlist(self, items):
        """Expression list."""
        return items

    def idlist(self, items):
        """ID list."""
        return items

    # Expressions
    def if_expr(self, items):
        """If-then-else expression."""
        condition, then_expr, else_expr = items
        return ("IF", condition, then_expr, else_expr)

    def sum_expr(self, items):
        """Sum expression."""
        start, end, body = items
        return ("SUM", start, end, body)

    # Arithmetic operations
    def add(self, items):
        """Addition."""
        return ("BINOP", "+", items[0], items[1])

    def sub(self, items):
        """Subtraction."""
        return ("BINOP", "-", items[0], items[1])

    def mul(self, items):
        """Multiplication."""
        return ("BINOP", "*", items[0], items[1])

    def div(self, items):
        """Division."""
        return ("BINOP", "/", items[0], items[1])

    def pow(self, items):
        """Power."""
        return ("BINOP", "^", items[0], items[1])

    def neg(self, items):
        """Unary negation."""
        return ("UNARY", "-", items[0])

    def group(self, items):
        """Grouped expression."""
        return ("GROUP", items[0])

    # Function calls
    def funcall(self, items):
        """Function call."""
        fname = items[0]
        args = items[1:]
        return ("FUNCALL", (fname, args))

    # Array selection
    def array_idx(self, items):
        """Array index selection."""
        arr, idx = items
        return ("ARRAY_SELECT", (arr, idx))

    def array_idx_add(self, items):
        """Array index with addition (ID "[" ID "+" INTEGER "]")."""
        # items = [ID, ID, INTEGER_as_NUM_tuple]
        arr, idx, offset_tuple = items[0], items[1], items[2]
        # Extract integer from NUM tuple
        num = copy.deepcopy(offset_tuple[1] if isinstance(offset_tuple, tuple) else offset_tuple)
        return ("ARRAY_SELECT", (arr, lambda x: x + num))

    def array_idx_sub(self, items):
        """Array index with subtraction (ID "[" ID "-" INTEGER "]")."""
        # items = [ID, ID, INTEGER_as_NUM_tuple]
        arr, idx, offset_tuple = items[0], items[1], items[2]
        # Extract integer from NUM tuple
        num = copy.deepcopy(offset_tuple[1] if isinstance(offset_tuple, tuple) else offset_tuple)
        return ("ARRAY_SELECT", (arr, lambda x: x - num))

    def array_idx_mul(self, items):
        """Array index with multiplication (ID "[" ID "*" INTEGER "]")."""
        # items = [ID, ID, INTEGER_as_NUM_tuple]
        arr, idx, offset_tuple = items[0], items[1], items[2]
        # Extract integer from NUM tuple
        num = copy.deepcopy(offset_tuple[1] if isinstance(offset_tuple, tuple) else offset_tuple)
        return ("ARRAY_SELECT", (arr, lambda x: x * num))

    # Variables and literals
    def var(self, items):
        """Variable reference."""
        return ("VAR", items[0])

    def index_var(self, items):
        """Index variable (e.g., i')."""
        return ("INDEX", items[0], "'")

    # Relational operations
    def lt(self, items):
        """Less than."""
        return ("RELOP", "<", items[0], items[1])

    def le(self, items):
        """Less or equal."""
        return ("RELOP", "<=", items[0], items[1])

    def gt(self, items):
        """Greater than."""
        return ("RELOP", ">", items[0], items[1])

    def ge(self, items):
        """Greater or equal."""
        return ("RELOP", ">=", items[0], items[1])

    def eq(self, items):
        """Equals."""
        return ("RELOP", "=", items[0], items[1])

    def ne(self, items):
        """Not equals."""
        return ("RELOP", "<>", items[0], items[1])

    # Terminals
    def ID(self, token):
        """Convert ID to lowercase (XPP is case-insensitive)."""
        return str(token).lower()

    def INTEGER(self, token):
        """Convert to int and wrap in NUM tuple."""
        return ("NUM", int(token))

    def FLOAT(self, token):
        """Convert to float and wrap in NUM tuple."""
        return ("NUM", float(token))

    def ARRAYSLICE(self, token):
        """Keep array slice as string for processing."""
        return str(token)

    # Numbers need to be wrapped in NUM tuple
    def number(self, items):
        """Wrap number in NUM tuple."""
        val = items[0]
        if isinstance(val, tuple) and val[0] == "NUM":
            return val
        return ("NUM", val)


# Create parser instance
_lark_parser = None


def get_parser():
    """Get or create Lark parser instance."""
    global _lark_parser
    if _lark_parser is None:
        _lark_parser = Lark(
            XPP_GRAMMAR,
            parser='lalr',
            transformer=XPPTransformer(),
            # Keep case for case-insensitive matching
            # (transformer handles lowercasing)
        )
    return _lark_parser


class Parser:
    """Parser interface compatible with PLY parser."""

    def parse(self, data, lexer=None, debug=False):
        """Parse XPP code and return AST."""
        try:
            parser_inst = get_parser()
            result = parser_inst.parse(data)
            return result
        except (ParseError, LarkError) as e:
            print(f"SYNTAX ERROR: {e}")
            return None


# Create global parser instance
parser = Parser()
