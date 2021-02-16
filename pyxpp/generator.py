""" Code generator
Generates code from parser output.
"""
import typing

from pyxpp import parser


def generate_program(syntax: typing.List[parser.Command]) -> typing.List[str]:
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
    return cmds


# COMMANDS.

def generate_command(command: parser.Command) -> str:
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
        return generate_done()
    else:
        return "error"


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
    assignments = generate_assignments(glob.body, separator=';')
    return f'global {sign} {{{condition}}} {{{assignments}}}'


def generate_fun_def(fun_def: parser.FunDef) -> str:
    """ Generate a function definition command. """
    fname = generate_name(fun_def.name)
    arguments = ','.join(generate_name(name) for name in fun_def.arguments)
    body = generate_expression(fun_def.body)
    return f'{fname}({arguments})={body}'


def generate_ode(ode: parser.ODE) -> str:
    """ Generate an ODE definition command. """
    var = generate_name(ode.assignment.left)
    rhs = generate_expression(ode.assignment.right)
    return "%s\'=%s" % (var, rhs)


def generate_done() -> str:
    """ Generate simple done command. """
    return 'done'


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


def generate_binop(binop: parser.BinOp):
    """ Generate a binary operation expression. """
    left = generate_expression(binop.left)
    right = generate_expression(binop.right)

    # Put brackets around string when necessary.
    if isinstance(binop.left, parser.BinOp):
        left_full = f'({left})'
    else:
        left_full = left
    if isinstance(binop.right, parser.BinOp):
        right_full = f'({right})'
    else:
        right_full = right
    return left_full + binop.operator + right_full


def generate_unaryop(unaryop: parser.UnaryOp) -> str:
    """ Generate a unary minus string. """
    return unaryop.operator + generate_expression(unaryop.operand)


# TODO: Add compare generator

def generate_fun_call(fun_call: parser.FunCall) -> str:
    """ Generete a function call string. """

    # Recursive calls on all arguments.
    fun_name = generate_name(fun_call.name)
    arguments = [generate_expression(x) for x in fun_call.arguments]
    arguments_comma = ",".join(arguments)
    return "%s(%s)" % (fun_name, arguments_comma)


def generate_assignment(assignment: parser.Assignment) -> str:
    """ Generate an assignment string. """
    left = generate_expression(assignment.left)
    right = generate_expression(assignment.right)
    return "%s=%s" % (left, right)


def generate_assignments(assignments: typing.List[parser.Assignment],
                         separator: str = ',') -> str:
    assignment_strings = [generate_assignment(assignment)
                          for assignment in assignments]
    return separator.join(assignment_strings)
