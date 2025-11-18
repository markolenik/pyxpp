# Convert XPP expressions to Python lambda functions.
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

import numpy as np


# Map XPP function names to Python/NumPy equivalents
XPP_FUNCTION_MAP = {
    "sin": "np.sin",
    "cos": "np.cos",
    "tan": "np.tan",
    "tanh": "np.tanh",
    "sinh": "np.sinh",
    "cosh": "np.cosh",
    "exp": "np.exp",
    "log": "np.log",
    "log10": "np.log10",
    "sqrt": "np.sqrt",
    "abs": "np.abs",
    "sign": "np.sign",
    "floor": "np.floor",
    "ceil": "np.ceil",
    "max": "np.maximum",
    "min": "np.minimum",
    "pow": "np.power",
    "mod": "np.mod",
    "atan": "np.arctan",
    "atan2": "np.arctan2",
    "asin": "np.arcsin",
    "acos": "np.arccos",
}


def expr_to_python(expr, param_dict=None):
    """
    Convert XPP expression AST to Python expression string.

    Parameters
    ----------
    expr : tuple
        XPP expression AST (from parser).
    param_dict : dict, optional
        Dictionary of parameter values to substitute.

    Returns
    -------
    str
        Python expression string.

    Examples
    --------
    >>> expr = ("BINOP", "+", ("VAR", "x"), ("NUM", 1))
    >>> expr_to_python(expr)
    'x + 1'
    """
    if param_dict is None:
        param_dict = {}

    if not isinstance(expr, tuple):
        return str(expr)

    uid = expr[0]

    if uid == "NUM":
        return str(expr[1])

    elif uid == "VAR":
        var_name = expr[1]
        # Substitute parameter values if available
        if var_name in param_dict:
            return str(param_dict[var_name])
        return var_name

    elif uid == "BINOP":
        op = expr[1]
        left = expr_to_python(expr[2], param_dict)
        right = expr_to_python(expr[3], param_dict)

        # Handle power operator
        if op == "^":
            return f"({left} ** {right})"
        else:
            return f"({left} {op} {right})"

    elif uid == "UNARY":
        op = expr[1]
        operand = expr_to_python(expr[2], param_dict)
        return f"{op}{operand}"

    elif uid == "GROUP":
        return f"({expr_to_python(expr[1], param_dict)})"

    elif uid == "FUNCALL":
        func_info = expr[1]
        func_name = func_info[0]
        args = func_info[1]

        # Map XPP function names to Python equivalents
        py_func = XPP_FUNCTION_MAP.get(func_name, func_name)

        # Convert arguments
        py_args = [expr_to_python(arg, param_dict) for arg in args]
        args_str = ", ".join(py_args)

        return f"{py_func}({args_str})"

    elif uid == "IF":
        condition = expr_to_python(expr[1], param_dict)
        then_expr = expr_to_python(expr[2], param_dict)
        else_expr = expr_to_python(expr[3], param_dict)
        return f"({then_expr} if {condition} else {else_expr})"

    elif uid == "RELOP":
        op = expr[1]
        left = expr_to_python(expr[2], param_dict)
        right = expr_to_python(expr[3], param_dict)

        # Convert XPP operators to Python
        py_op = op
        if op == "=":
            py_op = "=="
        elif op == "<>":
            py_op = "!="

        return f"({left} {py_op} {right})"

    elif uid == "SUM":
        # sum(start, end)of(expr) - convert to Python sum
        start = expr_to_python(expr[1], param_dict)
        end = expr_to_python(expr[2], param_dict)
        body = expr_to_python(expr[3], param_dict)
        # This is tricky - would need to analyze the body to find the index variable
        # For now, return a descriptive string
        return f"sum({body} for i in range({start}, {end}+1))"

    elif uid == "INDEX":
        # Index variable like i'
        return expr[1]

    elif uid == "ARRAY_SELECT":
        # Array indexing - for now, just return the array name
        arr_info = expr[1]
        if isinstance(arr_info, tuple):
            return arr_info[0]
        return str(arr_info)

    else:
        # Fallback for unknown types
        return str(expr)


def function_to_lambda(func_cmd, param_dict=None):
    """
    Convert XPP function definition to Python lambda.

    Parameters
    ----------
    func_cmd : tuple
        Function command from parser: ("DEFUN", name, args, expr).
    param_dict : dict, optional
        Dictionary of parameter values to substitute.

    Returns
    -------
    tuple
        (function_name, lambda_function)

    Examples
    --------
    >>> func = ("DEFUN", "f", ["x"], ("BINOP", "*", ("VAR", "x"), ("NUM", 2)))
    >>> name, lam = function_to_lambda(func)
    >>> name
    'f'
    >>> lam(5)
    10
    """
    if func_cmd[0] != "DEFUN":
        raise ValueError(f"Expected DEFUN command, got {func_cmd[0]}")

    func_name = func_cmd[1]
    arg_names = func_cmd[2]
    expr = func_cmd[3]

    # Convert expression to Python string
    py_expr = expr_to_python(expr, param_dict)

    # Build lambda string
    args_str = ", ".join(arg_names)
    lambda_str = f"lambda {args_str}: {py_expr}"

    # Create lambda function with numpy in scope
    lambda_func = eval(lambda_str, {"np": np, "__builtins__": {}})

    return func_name, lambda_func


def extract_functions(syntax, param_dict=None):
    """
    Extract all function definitions from XPP syntax tree.

    Parameters
    ----------
    syntax : list
        XPP syntax tree from parser.
    param_dict : dict, optional
        Dictionary of parameter values to substitute.

    Returns
    -------
    dict
        Dictionary mapping function names to lambda functions.

    Examples
    --------
    >>> syntax = [("DEFUN", "f", ["x"], ("BINOP", "*", ("VAR", "x"), ("NUM", 2)))]
    >>> funcs = extract_functions(syntax)
    >>> funcs["f"](5)
    10
    """
    functions = {}

    for cmd in syntax:
        if isinstance(cmd, tuple) and cmd[0] == "DEFUN":
            try:
                name, func = function_to_lambda(cmd, param_dict)
                functions[name] = func
            except Exception as e:
                # Log error but continue processing
                print(f"Warning: Could not convert function {cmd[1]}: {e}")

    return functions


def read_functions(xppfile, param_dict=None):
    """
    Read function definitions from XPP file and return as Python lambdas.

    Parameters
    ----------
    xppfile : str
        Path to XPP file.
    param_dict : dict, optional
        Dictionary of parameter values to substitute.

    Returns
    -------
    dict
        Dictionary mapping function names to lambda functions.

    Examples
    --------
    >>> funcs = read_functions("model.ode")
    >>> result = funcs["minf"](0.5)
    """
    from . import pyxpp

    syntax = pyxpp.parse_file(xppfile)
    if syntax is None:
        return {}

    return extract_functions(syntax, param_dict)
