### Introduction

[XPP](http://www.math.pitt.edu/%7Ebard/xpp/xpp.html) is a software by Bard Ermentrout for the analysis of systems of ODEs. **xply** is a Python wrapper around XPP that allows you to conveniently query information from the ODE file, run integrations, and compute nullclines. The main strength of xply lies in its the usage of [PLY](https://github.com/dabeaz/ply), a Python Lex-Yacc implementation, to build a full-fledged XPP lexer, parser, and code generator. This provides easy customisability and extensability, and differentiates xply from other XPP Python wrappers such as [Py_XPPCALL](https://github.com/iprokin/Py_XPPCALL) and [xppy](https://github.com/jsnowacki/xppy).

A demonstration can be viewed through [nbviewer](https://nbviewer.jupyter.org/github/itsok-dontworry/xply/blob/master/demo.ipynb).

### Features
- Read paramters, initial conditions, auxiliary variables, state variables, RHS of ODEs, and functions.
- Run numerical integrations.
- Compute nullclines (unique to xply)
- Modify parameters, nullcline options, initial conditions ...

### TODO
- Convert functions to actual Python lambda expressions.
- Directional fields.

### How to Cite xply

If referencing xply in a paper, please use

`Olenik, M. xply. 2018. Available at: https://github.com/itsok-dontworry/xply.`

and as BibTeX:

`@misc{xppy, author = {Olenik, Mark}, title = {{xply}}, url = {https://github.com/itsok-dontworry/xply}, year = {2018} }`
