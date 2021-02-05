""" Code generator
Generates code from parser output.
"""
import typing

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

def generate_command(command):
    """ Generate an expression. """
    if isinstance(command, parser.FixedVar):
        return generate_fixed_var(command)
    elif isinstance(command, parser.Par):
        return generate_par(command)
    elif isinstance(command, parser.Aux):
        return generate_aux(command)
    elif isinstance(command, parser.Init):
        return generate_init(command)
    elif isinstance(command, parser.Option):
        return generate_option(command)
    elif isinstance(command, parser.Global):
        return generate_global(command)
    elif isinstance(command, parser.FunDef):
        return generate_fun_def(command)
    elif isinstance(command, parser.ODE):
        return generate_ode(command)
    elif isinstance(command, parser.Done):
        return generate_done(command)


def generate_fixed_var(fixed_var: parser.FixedVar) -> str:
    """ Generate a fixed variable command"""
    assignments = generate_assignments(fixed_var.assignments)
    return f'number {assignments}'


def generate_par(par: parser.Par) -> str:
    """ Generate a parameter command. """
    assignments = generate_assignments(par.assignments)
    return f'par {assignments}'


def generate_init(init: parser.Init) -> str:
    """ Generate an initial value command. """
    assignments = generate_assignments(init.assignments)
    return f'init {assignments}'


def generate_aux(aux: parser.Aux) -> str:
    """ Generate an auxilliary variable command. """
    assignments = generate_assignments(aux.assignments)
    return f'aux {assignments}'


def generate_option(option: parser.Option) -> str:
    """ Generate a numerical option command. """
    assignments = generate_assignments(option.assignments)
    return f'@ {assignments}'


def generate_global(glob: parser.Global) -> str:
    """ Generate a global command. """
    if isinstance(glob.sign, parser.UnaryOp):
        sign = generate_unaryop(glob.sign)
    else:
        sign = generate_number(glob.sign)
    sign = generate_unaryop(glob.sign)
    condition = generate_expression(glob.condition)
    assignments = generate_assignments(glob.body)
    return f'global {sign} {{{condition}}} {{{assignments}}}'


# NOTE: Continue here
def generate_fun_def(fun_def: parser.FunDef) -> str:
    """ Generate a function definition command. """
    fname = generate_name(fun_def.name)
    arguments = ','.join(generate_name(name) for name in fun_def.names)
    body = generate_expression(fun_def.body)
    return f'{fname}({arguments})={body}'


def generate_ode(cmd):
    """ Generate an ODE definition command. """
    var = cmd[1]
    rhs = generate_expression(cmd[2])
    return "d%s/dt=%s" % (var, rhs)


# EXPRESSIONS


# NOTE: Can this thing be done more elegantly,
# maybe with a different pattern?
def generate_expression(expression) -> str:
    """ Generate an expression. """
    if isinstance(expression, parser.Number):
        return generate_number(expression)
    elif isinstance(expression, parser.Name):
        return generate_name(expression)
    elif isinstance(expression, parser.BinOp):
        return generate_binop(expression)
    elif isinstance(expression, parser.UnaryOp):
        return generate_unaryop(expression)
    elif isinstance(expression, parser.FunCall):
        return generate_fun_call(expression)
    else:
        return 'error'



def generate_number(number: parser.Number) -> str:
    """ Generate a number expression. """
    return str(number.value)


def generate_name(name: parser.Name) -> str:
    """ Generate a name string. """
    return name.id


# TODO: Add brackets here!!!
def generate_binop(binop: parser.BinOp):
    """ Generate a binary operation expression. """
    left = generate_expression(binop.left)
    right = generate_expression(binop.right)
    return left + binop.operator + right


def generate_unaryop(unaryop: parser.UnaryOp) -> str:
    """ Generate a unary minus string. """
    return unaryop.operator + generate_expression(unaryop.operand)

# TODO: Add compare generator

def generate_fun_call(fun_call: parser.FunCall) -> str:
    """ Generete a function call string. """

    # # Function call with one argument.
    # if len(fun_call.arguments) == 1:
    #     # Recursive call on single argument.
    #     argument = generate_expression(fun_call.arguments[0])
    #     return "%s(%s)" % (fun_call.name, argument)

    # Recursive calls on all arguments.
    arguments = [generate_expression(x) for x in fun_call.arguments]
    arguments_comma = ",".join(arguments)
    return "%s(%s)" % (fun_call.name, arguments_comma)


def generate_assignment(assignment: parser.Assignment) -> str:
    """ Generate an assignment string. """
    target = generate_expression(assignment.target)
    value = generate_expression(assignment.value)
    return "%s=%s" % (target, value)


def generate_assignments(assignments: typing.List[parser.Assignment]) -> str:
    assignment_strings = [generate_assignment(assignment)
                          for assignment in assignments]
    return ','.join(assignment_strings)
