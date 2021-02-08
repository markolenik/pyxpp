# Allow forward references for types
from __future__ import annotations

import typing
import ply.yacc as yacc
from pyxpp.lexer import tokens



# Commands
Command = typing.Union[FixedVar, Par, Aux, Init, Option,
                       Global, FunDef, ODE, Done]

# FixedVar = namedtuple("FixedVar", ["assignments"])
class FixedVar(typing.NamedTuple):
    assignments: typing.List[Assignment]

class Par(typing.NamedTuple):
    assignments: typing.List[Assignment]

# NOTE: Maybe combine command classes since identical?
class Aux(typing.NamedTuple):
    assignments: typing.List[Assignment]

class Init(typing.NamedTuple):
    assignments: typing.List[Assignment]

class Option(typing.NamedTuple):
    assignments: typing.List[Assignment]

class Global(typing.NamedTuple):
    # TODO: Sign is in [-1, 1, 0], make that more explicit?
    sign: int
    condition: BinOp
    body: typing.List[Assignment]


class FunDef(typing.NamedTuple):
    name: Name
    arguments: typing.List[Name]
    body: Expression

class ODE(typing.NamedTuple):
    assignment: Assignment

# ['assignment'])
class Done: pass


# Expressions
Expression = typing.Union[Number, Name, BinOp, UnaryOp, FunCall]

class Number(typing.NamedTuple):
    value: typing.Union[float, int]

class Name(typing.NamedTuple):
    id: str

class BinOp(typing.NamedTuple):
    # Not sure if the type quote is correct here
    left: Expression
    operator: str
    right: Expression

class UnaryOp(typing.NamedTuple):
    operator: str
    operand: Number


class FunCall(typing.NamedTuple):
    name: Name
    arguments: typing.List[Expression]

class Assignment(typing.NamedTuple):
    left: Expression
    right: Expression


precedence = (  # Operator precedence.
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("left", "POWER"),
    ("right", "UMINUS"),
)


# An XPP program is a series of stmts.  We represent the program as
# a list of tuples.

# I tried to mimick the python AST grammar
# https://docs.python.org/3/library/ast.html


def p_program(p):
    """ program : program stmt
                | stmt """
    if len(p) == 3:
        if type(p[2]) == list:
            p[0] = p[1] + p[2]

        else:
            p[0] = p[1] + [p[2]]

    elif len(p) == 2:
        p[0] = p[1]


# This catch-all rule is used for any catastrophic errors.  In this case,
# we simply return nothing.
def p_program_error(p):
    """ program : error """
    p[0] = []
    p.parser.error = 1


# Statements

# Format of all XPP statements
def p_stmt(p):
    """ stmt : command NEWLINE """
    p[0] = p[1]


# Blank line.
def p_stmt_newline(p):
    """ stmt : NEWLINE """
    p[0] = []


# A command is any single line statement.
# TODO: Add wiener, bndry, number, table,
def p_command(p):
    """ command : fixed_var
                | fun_def
                | par
                | init
                | aux
                | option
                | global
                | done
                | ode
    """
    p[0] = p[1]


def p_fixed_var(p):
    """ fixed_var : NUMBERCMD assignments
                  | assignment
    """
    if len(p) == 3:
        p[0] = FixedVar(p[2])
    else:
        p[0] = FixedVar([p[1]])


def p_fun_def(p):
    """ fun_def : name LPAREN names RPAREN EQUALS expression """
    p[0] = FunDef(p[1], p[3], p[6])


def p_par(p):
    """ par : PAR assignments """
    p[0] = Par(p[2])


def p_init(p):
    """ init : INIT assignments """
    p[0] = Init(p[2])


def p_aux(p):
    """ aux : AUX assignments """
    p[0] = Aux(p[2])


def p_option(p):
    """ option : OPTION assignments """
    p[0] = Option(p[2])


def p_global(p):
    """ global : GLOBAL global_sign LBRACE binop RBRACE LBRACE assignments RBRACE """
    p[0] = Global(p[2], p[4], p[7])


def p_global_sign(p):
    """ global_sign : number
                    | unaryop
    """
    p[0] = p[1]


def p_done(p):
    """ done : DONE """
    p[0] = Done()


def p_ode(p):
    """ ode : DIFF_LEIBNIZ EQUALS expression
            | DIFF_EULER EQUALS expression
    """
    # Euler notation
    if p[1][-1] == "\'":
        state_var = p[1][:-1]
    # Leibniz notation
    else:
        state_var = p[1].split('/')[0][1:]
    p[0] = ODE(Assignment(Name(state_var), p[3]))


# An expression is anything on the RHS of assignment
def p_expression(p):
    """ expression : number
                   | name
                   | binop
                   | unaryop
                   | fun_call
    """
    p[0] = p[1]


def p_number(p):
    """ number : INTEGER
               | FLOAT
    """
    p[0] = Number(p[1])


# variable or function name
def p_name(p):
    """ name : ID """
    p[0] = Name(p[1])


# Comma separated names.
def p_names(p):
    """ names : names COMMA name
              | name
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_binop(p):
    """ binop : expression PLUS expression
              | expression MINUS expression
              | expression TIMES expression
              | expression DIVIDE expression
              | expression POWER expression
    """
    p[0] = BinOp(p[1], p[2], p[3])


# Unary expression like -x.
# NOTE: Might need to change that to include negation.
def p_unaryop(p):
    """ unaryop : MINUS expression %prec UMINUS """
    p[0] = UnaryOp(p[1], p[2])


def p_fun_call(p):
    """ fun_call : name LPAREN arguments RPAREN """
    p[0] = FunCall(p[1], p[3])


# Function arguments are comma sepparated expressions.
def p_arguments(p):
    """ arguments : arguments COMMA expression
                  | expression
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_assignment(p):
    """ assignment : name EQUALS expression """
    p[0] = Assignment(p[1], p[3])


def p_assignments(p):
    """ assignments : assignments COMMA assignment
                    | assignment
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


# Catastrophic error handler.
def p_error(p):
    if not p:
        print("SYNTAX ERROR AT EOF")


# # Write tables into current directory.
# parser = yacc.yacc(outputdir=".")

# Write tables into current directory.
# NOTE: Not sure if it's a good idea to write into working dir
# parser = yacc.yacc(outputdir=".", debug=False, write_tables=False)


def parse(parse_string, **kwargs):
    # parser = yacc.yacc(**kwargs)
    # TODO: Combine kwargs
    parser = yacc.yacc(outputdir=".", debug=False, write_tables=False)
    return parser.parse(parse_string)
