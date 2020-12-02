# An XPP code generator.
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
#
# Author: Mark Olenik, mark.olenik@gmail.com



def g_program(syntax):
    """
    Read full syntax tree and return generated commands.
    
    Parameters
    ----------
    syntax : list
        Abstract Syntax Tree generated from parser.
    
    Returns
    -------
    out : list
        List of generated code commands.

    """
    cmds = [g_command(cmd) for cmd in syntax]
    return cmds + ['done']


# COMMANDS.

def g_command(cmd):
    """ Generate a command. """
    uid = cmd[0]
    if uid == 'PAR':
        return g_command_par(cmd)
    elif uid == 'INIT':
        return g_command_init(cmd)
    elif uid == 'AUX':
        return g_command_aux(cmd)
    elif uid == 'OPT':
        return g_command_opt(cmd)
    elif uid == 'GLOBAL':
        return g_command_global(cmd)
    elif uid == 'DEFUN':
        return g_command_defun(cmd)
    elif uid == 'ODE':
        return g_command_ode(cmd)


# Parameter definition.
def g_command_par(cmd):
    """ Generate a parameter command. """
    assign = cmd[1]
    var = assign[1]
    rhs = g_expr(assign[2])
    return 'par %s=%s' % (var, rhs)
        

def g_command_init(cmd):
    """ Generate an initial value command. """
    assign = cmd[1]
    var = assign[1]
    rhs = g_expr(assign[2])
    return 'init %s=%s' % (var, rhs)
        

def g_command_aux(cmd):
    """ Generate an auxilliary variable command. """
    var = cmd[1][1]
    rhs = g_expr(cmd[1][2])
    return 'aux %s=%s' % (var, rhs)
        

def g_command_opt(cmd):
    """ Generate a numerical option command. """
    assignment = g_expr(cmd[1])
    return '@ ' + assignment


def g_command_global(cmd):
    """ Generate a 'global' command. """
    sign = str(cmd[1])
    condition = g_expr(cmd[2])
    assignments = [g_expr(assignment) for assignment in cmd[3]]
    return 'global %s %s {%s}' % \
        (sign, condition, ';'.join(assignments))


def g_command_defun(cmd):
    """ Generate a function definition command. """
    fname = cmd[1]
    arguments = cmd[2]
    rhs = g_expr(cmd[3])
    return '%s(%s)=%s' % (fname, ','.join(arguments), rhs)


def g_command_ode(cmd):
    """ Generate an ODE definition command. """
    var = cmd[1]
    rhs = g_expr(cmd[2])
    return 'd%s/dt=%s' % (var, rhs)


# EXPRESSIONS

def g_expr(expr):
    """ Generate an expression. """
    uid = expr[0]
    if uid == 'RELOP':
        return g_expr_rel(expr)
    if uid == 'ASSIGN':
        return g_expr_assignment(expr)
    elif uid == 'INDEX':
        return g_expr_index(expr)
    elif uid == 'UNARY':
        return g_expr_unary(expr)
    elif uid == 'GROUP':
        return g_expr_group(expr)
    elif uid == 'VAR':
        return g_expr_variable(expr)
    elif uid == 'FUNCALL':
        return g_expr_funcall(expr)
    elif uid == 'NUM':
        return g_expr_num(expr)
    elif uid == 'BINOP':
        return g_expr_binary(expr)
    elif uid == 'SUM':
        return g_expr_sum(expr)
    elif uid == 'IF':
        return g_expr_if(expr)


def g_expr_if(expr):
    """ Generate an if-expression. """
    expr1 = g_expr(expr[1])
    expr2 = g_expr(expr[2])
    expr3 = g_expr(expr[3])
    return 'if(%s)then(%s)else(%s)' % (expr1, expr2, expr3)


def g_expr_sum(expr):
    """ Generate a sum expression. """
    expr1 = g_expr(expr[1])
    expr2 = g_expr(expr[2])
    expr3 = g_expr(expr[3])
    return 'sum(%s,%s)of(%s)' % (expr1, expr2, expr3)


def g_expr_binary(expr):
    """ Generate a binary operation expression. """
    operator = expr[1]
    expr1 = g_expr(expr[2])
    expr2 = g_expr(expr[3])
    return expr1 + operator + expr2


def g_expr_num(expr):
    """ Generate a number expression. """
    return str(expr[1])


def g_expr_variable(expr):
    """ Generate a variable expression. """
    var = expr[1]
    return var


def g_expr_funcall(expr):
    """ Generete a function call expression. """
    var = expr[1][0]
    term = expr[1][1]

    # Function call with one argument.
    if len(term) == 1:
        # Recursive call on single argument.
        rterm = g_expr(term[0])
        return '%s(%s)' % (var, rterm)

    # Function call with multiple arguments.
    else:
        # Recursive calls on all arguments.
        rterms = [g_expr(x) for x in term]
        rterms_comma = ','.join(rterms)
        return '%s(%s)' % (var, rterms_comma)


def g_expr_group(expr):
    """ Generate a paranthesis-group expression. """
    return '(%s)' % g_expr(expr[1])


def g_expr_unary(expr):
    """ Generate a unary minus expression. """
    return expr[1] + g_expr(expr[2])


def g_expr_index(expr):
    """ Generate an index expression. """
    return expr[1] + '\''


def g_expr_rel(expr):
    """ Generate a relation expression. """
    operator = expr[1]
    expr1 = g_expr(expr[2])
    expr2 = g_expr(expr[3])
    return expr1 + operator + expr2


def g_expr_assignment(expr):
    """ Generate an assignment expression. """
    var = expr[1]
    rhs = expr[2]
    return '%s=%s' % (var, g_expr(rhs))
