import pytest
from pyxpp import parser
from pyxpp.parser import *


# Here we also test most expressions.
fixed_var_tests = [
    ('x=2', FixedVar([Assignment(Name('x'), Number(2))])),
    ('_yd=.3', FixedVar([Assignment(Name('_yd'), Number(0.3))])),
    ('number x=3,y=0.4', FixedVar([Assignment(Name('x'), Number(3)),
                                   (Assignment(Name('y'), Number(0.4)))])),
    ('k=(1+x)*2',
     FixedVar([
         Assignment(
             Name('k'),
             BinOp(Group(BinOp(Number(1), '+', Name('x'))), '*', Number(2)))])),
]


@pytest.mark.parametrize('test, expected', fixed_var_tests)
def test_fixed_var(test, expected):
    assert parse(test+'\n') == expected


binop_tests = [
    ('x=1+3', FixedVar([
        Assignment(Name('x'), BinOp(Number(1), '+', Number(3)))])),
    ('c=x-3', FixedVar([
        Assignment(Name('c'), BinOp(Name('x'), '-', Number(3)))])),
    ('c=0.33*3', FixedVar([
        Assignment(Name('c'), BinOp(Number(0.33), '*', Number(3)))])),
    ('c=0.33/3', FixedVar([
        Assignment(Name('c'), BinOp(Number(0.33), '/', Number(3)))])),
    ('c=0.33**3', FixedVar([
        Assignment(Name('c'), BinOp(Number(0.33), '**', Number(3)))])),
]


@pytest.mark.parametrize('test, expected', binop_tests)
def test_bionp(test, expected):
    assert parse(test+'\n') == expected


def test_unaryop():
    expected = FixedVar([Assignment(Name('x'), UnaryOp('-', Number(3)))])
    assert parse('x=-3\n') == expected


fun_def_tests = [
    ('f(x)=1', FunDef(Name('f'), [Name('x')], Number(1))),
    ('f(x) = x**2',
     FunDef(Name('f'), [Name('x')], BinOp(Name('x'), '**', Number(2)))),
    ('test(x,y)=2',
     FunDef(Name('test'), [Name('x'), Name('y')], Number(2)))
]

@pytest.mark.parametrize('test, expected', fun_def_tests)
def test_fun_def(test, expected):
    assert parse(test+'\n') == expected


# Test all commands
par_tests = [
    ('par G=0.6',
     Par([Assignment(Name('g'), Number(0.6))])),

    ('par GL=.15,GCA=0.3,GK=-0.6',
     Par([Assignment(Name('gl'), Number(0.15)),
          Assignment(Name('gca'), Number(0.3)),
          Assignment(Name('gk'), UnaryOp('-', Number(0.6)))])),
]


@pytest.mark.parametrize('test, expected', par_tests)
def test_par(test, expected):
    assert parse(test+'\n') == expected


init_tests = [
    ('init v=0.5\n',
     Init([Assignment(Name('v'), Number(0.5))])),

    ('i v=0.5,w=0.1\n',
     Init([Assignment(Name('v'), Number(0.5)),
           Assignment(Name('w'), Number(0.1))])),
]


@pytest.mark.parametrize('test, expected', init_tests)
def test_init(test, expected):
    assert parse(test) == expected


aux_tests = [
    ('aux xx=2*y',
     Aux([Assignment(Name('xx'), BinOp(Number(2), '*', Name('y')))]))
]


@pytest.mark.parametrize('test, expected', aux_tests)
def test_aux(test, expected):
    assert parse(test+'\n') == expected


option_tests = [
    ('@ TOTAL=5000,DT=.5',
     Option([Assignment(Name('total'), Number(5000)),
             Assignment(Name('dt'), Number(0.5))]))
]


@pytest.mark.parametrize('test, expected', option_tests)
def test_option(test, expected):
    assert parse(test+'\n') == expected


global_tests = [
    ('global -1 {u-0.2} {m=0.5*m}',
     Global(UnaryOp('-', Number(1)),
            BinOp(Name('u'), '-', Number(0.2)),
            [Assignment(Name('m'), BinOp(Number(0.5), '*', Name('m')))]))
]


@pytest.mark.parametrize('test, expected', global_tests)
def test_option(test, expected):
    assert parse(test+'\n') == expected


def test_done():
    test = 'done'
    expected = Done()
    assert parse(test+'\n') == expected


fun_call_tests = [
    ('test_var=f(y)',
     FixedVar([Assignment(Name('test_var'),
                          FunCall(Name('f'), [Name('y')]))])),
    ('x=f(y, 2*z)',
     FixedVar([Assignment(Name('x'),
                          FunCall(Name('f'),
                                  [Name('y'),
                                   BinOp(Number(2),
                                         '*',
                                         Name('z'))]))])),
]

@pytest.mark.parametrize('test, expected', fun_call_tests)
def test_fun_call(test, expected):
    assert parse(test+'\n') == expected


ode_tests = [
    ('dv1/dt=-v1',
     ODE(Assignment(Name('v1'),
                    UnaryOp('-', Name('v1'))))),
    ("v1\'=f(v1)",
     ODE(Assignment(Name('v1'),
                    FunCall(Name('f'),
                            [Name('v1')]))))
]


@pytest.mark.parametrize('test, expected', ode_tests)
def test_p_command_ode(test, expected):
    assert parse(test+'\n') == expected

