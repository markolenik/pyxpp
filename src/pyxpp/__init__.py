# PyXPP - Python wrapper for XPP/XPPAUT
#
# Main exports for pyxpp package

from .pyxpp import (
    parse_file,
    write_syntax,
    read_state_vars,
    read_aux_vars,
    read_vars,
    read_pars,
    read_ics,
    read_opts,
    run,
    nullclines,
)

from .expr_converter import (
    read_functions,
    extract_functions,
    function_to_lambda,
    expr_to_python,
)

__all__ = [
    # Core parsing and file operations
    "parse_file",
    "write_syntax",
    # Data extraction
    "read_state_vars",
    "read_aux_vars",
    "read_vars",
    "read_pars",
    "read_ics",
    "read_opts",
    # Simulation
    "run",
    "nullclines",
    # Function conversion (NEW!)
    "read_functions",
    "extract_functions",
    "function_to_lambda",
    "expr_to_python",
]
