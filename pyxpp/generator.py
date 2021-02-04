""" Code generator
Generates code from parser output.
"""
from pyxpp import parser

def generate_program(syntax):
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
    cmds = [generate_command(cmd) for cmd in syntax]
    return cmds + ["done"]


# COMMANDS.


def generate_command(cmd):
    """ Generate a command. """
    uid = cmd[0]
    if uid == "PAR":
        return generate_par(cmd)
    elif uid == "INIT":
        return generate_init(cmd)
    elif uid == "AUX":
        return generate_aux(cmd)
    elif uid == "OPT":
        return generate_opt(cmd)
    elif uid == "GLOBAL":
        return generate_global(cmd)
    elif uid == "DEFUN":
        return generate_fun_def(cmd)
    elif uid == "ODE":
        return generate_ode(cmd)


# Parameter definition.
def generate_par(cmd):
    """ Generate a parameter command. """
    assign = cmd[1]
    var = assign[1]
    rhs = generate_expression(assign[2])
    return "par %s=%s" % (var, rhs)


def generate_init(cmd):
    """ Generate an initial value command. """
    assign = cmd[1]
    var = assign[1]
    rhs = generate_expression(assign[2])
    return "init %s=%s" % (var, rhs)


def generate_aux(cmd):
    """ Generate an auxilliary variable command. """
    var = cmd[1][1]
    rhs = generate_expression(cmd[1][2])
    return "aux %s=%s" % (var, rhs)


def generate_opt(cmd):
    """ Generate a numerical option command. """
    assignment = generate_expression(cmd[1])
    return "@ " + assignment


def generate_global(cmd):
    """ Generate a 'global' command. """
    sign = str(cmd[1])
    condition = generate_expression(cmd[2])
    assignments = [generate_expression(assignment) for assignment in cmd[3]]
    return "global %s %s {%s}" % (sign, condition, ";".join(assignments))


def generate_fun_def(cmd):
    """ Generate a function definition command. """
    fname = cmd[1]
    arguments = cmd[2]
    rhs = generate_expression(cmd[3])
    return "%s(%s)=%s" % (fname, ",".join(arguments), rhs)


def generate_ode(cmd):
    """ Generate an ODE definition command. """
    var = cmd[1]
    rhs = generate_expression(cmd[2])
    return "d%s/dt=%s" % (var, rhs)


# EXPRESSIONS


def generate_expression(expr):
    """ Generate an expression. """
    uid = expr[0]
    if uid == "RELOP":
        return g_expr_rel(expr)
    if uid == "ASSIGN":
        return g_expr_assignment(expr)
    elif uid == "INDEX":
        return g_expr_index(expr)
    elif uid == "UNARY":
        return generate_unaryop(expr)
    elif uid == "GROUP":
        return generate_group(expr)
    elif uid == "VAR":
        return generate_name(expr)
    elif uid == "FUNCALL":
        return generate_fun_call(expr)
    elif uid == "NUM":
        return generate_number(expr)
    elif uid == "BINOP":
        return generate_binary(expr)


def generate_binary(expr):
    """ Generate a binary operation expression. """
    operator = expr[1]
    expr1 = generate_expression(expr[2])
    expr2 = generate_expression(expr[3])
    return expr1 + operator + expr2


def generate_number(number: parser.Number):
    """ Generate a number expression. """
    return str(number.value)
    # return str(number[1])


def generate_name(name: parser.Name) -> str:
    """ Generate a name string. """
    var = name.id
    return var


def generate_fun_call(fun_call: parser.FunCall) -> str:
    """ Generete a function call string. """

    # Function call with one argument.
    if len(fun_call.arguments) == 1:
        # Recursive call on single argument.
        argument = generate_expression(fun_call.arguments[0])
        return "%s(%s)" % (fun_call.name, argument)

    # Function call with multiple arguments.
    else:
        # Recursive calls on all arguments.
        arguments = [generate_expression(x) for x in fun_call.arguments]
        arguments_comma = ",".join(arguments)
        return "%s(%s)" % (fun_call.name, arguments_comma)


# Not sure how this should be done
# def generate_group(group):
#     """ Generate a paranthesis-group expression. """
#     return "(%s)" % generate_expression(group[1])


def generate_unaryop(unaryop: parser.UnaryOp) -> str:
    """ Generate a unary minus string. """
    return unaryop.operator + generate_expression(unaryop.operand)


def generate_assignment(assignment):
    """ Generate an assignment string. """
    target = assignment.target
    value = generate_expression(assignment.value)
    return "%s=%s" % (target, value)
