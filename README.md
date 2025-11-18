### Introduction

[XPP](http://www.math.pitt.edu/%7Ebard/xpp/xpp.html) is a software by Bard Ermentrout for the analysis of systems of ODEs. **pyxpp** is a Python wrapper around XPP that allows you to conveniently query information from the ODE file, run integrations, and compute nullclines.

The main strength of pyxpp lies in its use of [Lark](https://github.com/lark-parser/lark), a modern parsing library, to build a full-fledged XPP lexer, parser, and code generator. This provides easy customizability and better error messages than other XPP Python wrappers such as [Py_XPPCALL](https://github.com/iprokin/Py_XPPCALL) and [xppy](https://github.com/jsnowacki/xppy).

### Features

- **Parse XPP files**: Read parameters, initial conditions, auxiliary variables, state variables, RHS of ODEs, and functions
- **Run simulations**: Execute numerical integrations using XPP
- **Compute nullclines**: Unique to pyxpp (to our knowledge)
- **Convert functions to Python**: ✨ NEW! Convert XPP function definitions to Python lambda expressions
- **Modify parameters**: Change parameters, nullcline options, initial conditions on the fly
- **Modern parser**: Built with Lark for better error messages and maintainability

### Installation

```bash
pip install pyxpp
```

Or install from source:

```bash
git clone https://github.com/markolenik/pyxpp.git
cd pyxpp
pip install -e .
```

### Dependencies

- Python ≥ 3.8.6
- [Lark](https://github.com/lark-parser/lark) - Modern parsing library
- [NumPy](https://www.numpy.org/) - Numerical computing
- [XPP 8.0](http://www.math.pitt.edu/%7Ebard/xpp/xpp.html) - The XPP binary (included as `xppaut` or available in many distro repos)

### Quick Start

```python
import pyxpp

# Parse an XPP file
syntax = pyxpp.parse_file("model.ode")

# Read parameters and initial conditions
pars = pyxpp.read_pars("model.ode")
ics = pyxpp.read_ics("model.ode")

# Convert XPP functions to Python lambdas
funcs = pyxpp.read_functions("model.ode")
result = funcs["minf"](0.5)  # Call the function!

# Run a simulation
output = pyxpp.run("model.ode", ics=ics)

# Compute nullclines
n1, n2 = pyxpp.nullclines("model.ode", xlo=-2, xhi=2, ylo=-2, yhi=2)
```

### NEW: Function-to-Lambda Conversion ✨

PyXPP can now convert XPP function definitions to Python lambda functions:

```python
import pyxpp

# Read functions from an XPP file
funcs = pyxpp.read_functions("morris_lecar.ode")

# Use them like normal Python functions!
import numpy as np
v_values = np.linspace(-80, 40, 100)
m_inf = funcs["minf"](v_values)  # Vectorized with NumPy!

# Functions can use parameters
funcs_with_params = pyxpp.read_functions("model.ode",
                                         param_dict={"va": 1.0, "vb": 14.5})
```

This feature supports:
- All basic arithmetic operations (+, -, *, /, ^)
- NumPy functions (sin, cos, tan, tanh, exp, log, sqrt, etc.)
- Conditional expressions (if-then-else)
- Parameter substitution
- Multi-argument functions

### Tutorial

A comprehensive demo and tutorial can be found [here](https://github.com/markolenik/pyxpp/blob/master/wiki/demo/demo.ipynb).

### Migration from PLY to Lark

As of 2024, pyxpp has migrated from PLY to Lark for parsing. Benefits include:

- ✅ **Better error messages**: Clearer parse errors with context
- ✅ **Modern library**: Actively maintained with good documentation
- ✅ **Cleaner code**: Grammar separated from Python code
- ✅ **Bug fixes**: Fixed 5+ array parsing bugs from the PLY implementation
- ✅ **Easier to extend**: Add new XPP features by modifying the grammar file

The migration is **fully backward compatible** - all existing code continues to work.

### Testing

PyXPP has comprehensive test coverage:

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/test_parser.py      # Parser tests
pytest tests/test_expr_converter.py  # Function conversion tests
pytest tests/test_pyxpp.py       # Integration tests
```

Current status: **150+ tests passing** ✅

### TODO

- **Directional fields**: Compute and visualize direction fields
- **Additional XPP commands**: The following commands could be easily added by extending the grammar:
  - `table`, `bdry`, `volt`, `markov`, `wiener`, `solv`, `special`, `set`
  - Derived parameters, numbers, int, block pseudo-arrays

Contributions welcome!

### Contributing

Contributions are welcome! The codebase uses:
- **Lark** for parsing (see `src/pyxpp/xpp.lark` for the grammar)
- **pytest** for testing
- **black** for code formatting

To add a new XPP feature:
1. Update the grammar in `src/pyxpp/xpp.lark`
2. Add transformer method in `src/pyxpp/lark_parser.py`
3. Add tests in `tests/`
4. Submit a pull request!

### How to Cite pyxpp

If referencing pyxpp in a paper, please use:

`Olenik, M. PyXPP. 2018-2024. Available at: https://github.com/markolenik/pyxpp.`

BibTeX:

```bibtex
@Misc{pyxpp,
  author       = {Mark Olenik},
  title        = {pyxpp},
  howpublished = {https://github.com/markolenik/pyxpp},
  year         = {2018--2024}
}
```

### License

PyXPP is licensed under the GNU General Public License v3.0. See LICENSE for details.
