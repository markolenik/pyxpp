# An XPP parser based on PLY.
#
# This file is part of xply.
#
# xply is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Mark Olenik, mark.olenik@gmail.com



import copy
import ply.yacc as yacc
from . lexer import tokens

 
precedence = (                  # Operator precedence.
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'POWER'),
    ('right', 'UMINUS')
)


# An XPP program is a series of statements.  We represent the program as
# a list of tuples.

def p_program(p):
    """ program : program statement
                | statement """
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

# Statements.

# Format of all XPP statements.
def p_statement(p):
    """ statement : command NEWLINE """
    p[0] = p[1]

# Blank line.
def p_statement_newline(p):
    """ statement : NEWLINE """
    p[0] = []



# Parameter definition.
def p_command_par(p):
    """ command : PAR assignments
                | PAR array EQUALS number
    """
    if len(p) == 3:
        p[0] = [('PAR', x) for x in p[2]]

    elif len(p) == 5:
        statevar = p[2][0]
        p[0] = [('PAR', ('ASSIGN', statevar + str(x), p[4])) for x in p[2][1]]
        

# Initial value command.
def p_command_init(p):
    """ command : INIT assignments
                | ID LPAREN INTEGER RPAREN EQUALS expr
                | INIT array EQUALS expr
                | array LPAREN INTEGER RPAREN EQUALS expr
    """
    if len(p) == 3:
        p[0] = [('INIT', x) for x in p[2]]

    elif (len(p) == 7) and (type(p[1]) is str):
        p[0] = ('INIT', ('ASSIGN', p[1], p[6]))

    elif len(p) == 5:
        statevar = p[2][0]
        p[0]= [('INIT', ('ASSIGN', statevar + str(x), p[4])) for x in p[2][1]]

    else:
        statevar = p[1][0]
        p[0] = [('INIT', ('ASSIGN', statevar + str(x), p[6])) for x in p[1][1]]
        

# Auxilliary variable definition.
def p_command_aux(p):
    """ command : AUX ID EQUALS expr
                | AUX array EQUALS expr
    """
    if type(p[2]) is str:
        p[0] = ('AUX', ('ASSIGN', p[2], p[4]))

    else:
        var = p[2][0]
        p[0] = [('AUX', ('ASSIGN', var + str(x), p[4])) for x in p[2][1]]
        

# Numerical options.
def p_command_opt(p):
    """ command : OPT assignments """
    p[0] = [('OPT', x) for x in p[2]]


# "Global" command for finding zero crossings.
def p_command_global(p):
    """ command : GLOBAL INTEGER expr LBRACE assignments RBRACE """
    p[0] = ('GLOBAL', p[2], p[3], p[5])


# Function definition.
def p_command_defun(p):
    """ command : ID LPAREN idlist RPAREN EQUALS expr """
    p[0] = ('DEFUN', p[1], p[3], p[6])


# Right-hand-side of an ODE.
def p_command_ode(p):
    """ command : ID APOSTROPHE EQUALS expr
                | ID DIVIDE ID EQUALS expr
    """
    if len(p) == 5:
        statevar = p[1]
        p[0] = ('ODE', statevar, p[4])

    else:
        statevar = p[1][1:]
        p[0] = ('ODE', statevar, p[5])


# Right-hand-side of an ODE using pseudo-array notation.
def p_command_ode_array(p):
    """ command : array APOSTROPHE EQUALS expr """

    def subst(expr, var, idx):
        """
        Substitute variable in expression containing "ARRAY_SELECT"
        with corresponding indexed variable.

        Parameters
        ----------
        expr : tuple
            Expression to substitute recursively.
        var : string
            Variable name to search for.
        idx : int
            New index to append to variable.

        Returns
        -------
        out : tuple
            New expression.

        """
        if type(expr) is not tuple:
            return expr

        # Substitute.
        elif (expr[0] == 'ARRAY_SELECT') and (expr[1][0] == var):
            idxfun = expr[1][1]
            newidx = idxfun(idx)
            return tuple(('VAR', (expr[1][0]+str(newidx), None, None)))

        # Recursive call if no match.
        else: 
            return tuple((subst(x, var, idx) for x in expr))

    statevar = p[1][0]
    p[0] = [('ODE', statevar + str(x), subst(p[4], statevar, x))
            for x in p[1][1]]


# Expressions.

def p_expr_if(p):
    """ expr : IF LPAREN relexpr RPAREN THEN LPAREN expr RPAREN ELSE LPAREN expr RPAREN """
    p[0] = ('IF', p[3], p[7], p[11])


def p_expr_sum(p):
    """ expr : SUM LPAREN expr COMMA expr RPAREN OF LPAREN expr RPAREN """
    # sum(<ex1>, <ex2>)of(<ex3>)
    p[0] = ('SUM', p[3], p[5], p[9])


def p_expr_funcall(p):
    """ expr : funcall """
    # f(<ex1> [, <ex2>, ..., <exn>])
    p[0] = ('FUNCALL', p[1])


def p_expr_binary(p):
    """ expr : expr PLUS expr
             | expr MINUS expr
             | expr TIMES expr
             | expr DIVIDE expr
             | expr POWER expr
    """
    p[0] = ('BINOP', p[2], p[1], p[3])


def p_expr_number(p):
    """ expr : INTEGER
             | FLOAT
    """
    p[0] = ('NUM', p[1])


def p_expr_variable(p):
    """ expr : variable """
    p[0] = ('VAR', p[1])


# Selection of array elements, e.g. x[j].
def p_expr_array_select(p):
    """ expr : array_select """
    p[0] = ('ARRAY_SELECT', p[1])


# Grouped arithmetic expression with parantheses.
def p_expr_group(p):
    """ expr : LPAREN expr RPAREN """
    p[0] = ('GROUP', p[2])


# Unary expression like -x.    
def p_expr_unary(p):
    """ expr : MINUS expr %prec UMINUS """
    p[0] = ('UNARY', '-', p[2])


# Expression used for indexing, e.g. sum(1,10)of(i')    
def p_expr_index(p):
    """ expr : ID APOSTROPHE """
    p[0] = ('INDEX', p[1], p[2])


# Relational expressions.
def p_relexpr(p):
    """ relexpr : expr LT expr
                | expr LE expr
                | expr GT expr
                | expr GE expr
                | expr EQUALS expr
                | expr NE expr
    """
    p[0] = ('RELOP', p[2], p[1], p[3])


# Assignments.

def p_assignments(p):
    """ assignments : assignments assignment
                    | assignment
    """
    if len(p) > 2:
        p[0] = p[1] + [p[2]]

    else:
        p[0] = [p[1]]
        
def p_assignment(p):
    """ assignment : ID EQUALS expr
                   | ID EQUALS expr COMMA
                   | ID EQUALS expr SEMI
    """
    p[0] = ('ASSIGN', p[1], p[3])


# Arrays.

# An array such as x[1..10].
def p_array(p):
    """ array : ID ARRAYSLICE """
    x0 = int(p[2][1:p[2].index('.')])
    x1 = int(p[2][p[2].rindex('.')+1:-1])
    p[0] = (p[1], list(range(x0, x1+1)))


# Select from array, e.g. x[j+n].
def p_array_select(p):
    """ array_select : ID LBRACKET ID RBRACKET
                     | ID LBRACKET ID PLUS INTEGER RBRACKET
                     | ID LBRACKET ID MINUS INTEGER RBRACKET
                     | ID LBRACKET ID TIMES INTEGER RBRACKET
    """
    if len(p) == 5:
        p[0] = (p[1], p[3])

    elif len(p) == 7:
        num = copy.deepcopy(p[5])
        if p[4] == '+':
            p[0] = (p[1], lambda x: x + num)

        elif p[4] == '-':
            p[0] = (p[1], lambda x: x - num)

        elif p[4] == '*':
            p[0] = (p[1], lambda x: x * num)
        

def p_funcall(p):
    """ funcall : ID LPAREN expr RPAREN
                | ID LPAREN expr COMMA exprlist RPAREN
    """
    # Function call with one argument.
    if len(p) == 5:
        p[0] = (p[1], [p[3]])

    # Function call with multiple arguments.
    else:                       
        p[0] = (p[1], [p[3]] + p[5])


def p_variable(p):
    """ variable : ID """
    p[0] = p[1]


# Expressions sepparated by comma.
def p_exprlist(p):
    """ exprlist : exprlist COMMA expr
                 | expr
    """
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


# Builds a list of IDs as a Python list.
def p_idlist(p):
    """ idlist : idlist COMMA ID
               | ID
    """
    if len(p) > 2:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


# A number. May be an integer or a float
def p_number(p):
    """ number : INTEGER
               | FLOAT
    """
    p[0] = p[1]


# A signed number.
def p_number_signed(p):
    """ number : MINUS INTEGER
               | MINUS FLOAT
    """
    p[0] = -p[2]


# Catastrophic error handler.
def p_error(p):
    if not p:
        print("SYNTAX ERROR AT EOF")


parser = yacc.yacc(debug=True)
