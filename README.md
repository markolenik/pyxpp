### Introduction

[XPP](http://www.math.pitt.edu/%7Ebard/xpp/xpp.html) is a software by Bard Ermentrout for the analysis of systems of ODEs. **PyXPP** is a Python wrapper around XPP that allows you to conveniently query information from the ODE file, run integrations, and compute nullclines. The main strength of PyXPP lies in its the usage of [PLY](https://github.com/dabeaz/ply), a Python Lex-Yacc implementation, to build a full-fledged XPP lexer, parser, and code generator. This provides easy customisability, and differentiates PyXPP from other XPP Python wrappers such as [Py_XPPCALL](https://github.com/iprokin/Py_XPPCALL) and [xppy](https://github.com/jsnowacki/xppy).

A demonstration can be viewed through [nbviewer](https://nbviewer.jupyter.org/gitlab/molenik/PyXPP/blob/master/demo.ipynb).

### Features
- Read paramters, initial conditions, auxiliary variables, state variables, RHS of ODEs, and functions.
- Run numerical integrations.
- Compute nullclines (unique to PyXPP)
- Modify parameters, nullcline options, initial conditions ...

### Dependencies
- Python 3
- [PLY](https://github.com/dabeaz/ply)
- [SciPy](https://www.scipy.org/)
- [XPP](http://www.math.pitt.edu/%7Ebard/xpp/xpp.html). The latest XPP Ubuntu binary provided as `xppaut`. You may need to change permissions to executable. Many distros also provide the binaries in their repos, e.g. Debian, Ubuntu, Arch (AUR).

### TODO
- Convert functions to actual Python lambda expressions.
- Directional fields.
- Add some other commands. The following commands are not yet supported but could be easily implemented: `table, bdry, volt, markov, wiener, solv, special, set, derived parameters, numbers, int, block pseudo-arrays`

### How to Cite PyXPP

If referencing PyXPP in a paper, please use

`Olenik, M. PyXPP. 2018. Available at: https://gitlab.com/molenik/PyXPP.`

And as BibTeX:

```
@software{pyxpp,
  author = {Olenik, Mark},
  title = {PyXPP},
  url = {https://gitlab.com/molenik/PyXPP},
  version = {0.1.0}
  date = {2018-07-10}
}
```
