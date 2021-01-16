import pytest

from pyxpp.parser import parse

# Test all commands

par_tests = [
    ('par G=0.6\n', [('PAR', ('ASSIGN', 'g', 0.6))]),
    ('par GL=.15,GCA=0.3,GK=-0.6\n', [('PAR', ('ASSIGN', 'gl', 0.15)),
                                      ('PAR', ('ASSIGN', 'gca', (0.3))),
                                      ('PAR', ('ASSIGN', 'gk',
                                               ('UMINUS', 0.6)))]),
    ('p x[1..2]=0.1\n', [('PAR', ('ASSIGN', 'x1', 0.1)),
                         ('PAR', ('ASSIGN', 'x2', 0.1))])
]


@pytest.mark.parametrize('syntax, expected', par_tests)
def test_p_command_par(syntax, expected):
    assert parse(syntax) == expected


init_tests = [
    ('initialize v=0.5\n', [('INIT', ('ASSIGN', 'v', 0.5))]),
    ('i v=0.5,w=0.1\n', [('INIT', ('ASSIGN', 'v', 0.5)),
                         ('INIT', ('ASSIGN', 'w', 0.1))]),
    ('init v[1..2]=0.12\n', [('INIT', ('ASSIGN', 'v1', 0.12)),
                             ('INIT', ('ASSIGN', 'v2', 0.12))]),
    ('v[1..2](0.12)=0.11\n', [('INIT', ('ASSIGN', 'v1', 0.11)),
                              ('INIT', ('ASSIGN', 'v2', 0.11))]),
]


@pytest.mark.parametrize('syntax, expected', init_tests)
def test_p_command_init(syntax, expected):
    assert parse(syntax) == expected


# TODO: Not sure if this will work
# aux r[1..10]=sqrt(x[j]^2+y[j]^2)
aux_tests = [
    ('aux xx=2*y\n',
     [('AUX', ('ASSIGN', 'xx', ('BINOP', '*', 2, ('VAR', 'y'))))]),
    ('aux x[1..3]=0.1', [('AUX', ('ASSING', 'x1', 0.1)),
                         ('AUX', ('ASSING', 'x2', 0.1)),
                         ('AUX', ('ASSING', 'x3', 0.1))]),
    ('aux x=v1,y=v1*w1', [('AUX', ('ASSIGN', 'x', 'v1'))])
]


@pytest.mark.parametrize('syntax, expected', aux_tests)
def test_p_command_aux(syntax, expected):
    assert parse(syntax) == expected

# def test_p_command_opt():
#     pass


# def test_p_command_global():
#     pass


# def test_p_command_defun():
#     pass


# def test_p_command_ode():
#     pass


# def test_command_ode_array():
#     pass


# def test_command_expr_if():
#     pass
