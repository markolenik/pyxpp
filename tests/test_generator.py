import pytest
from pyxpp.parser import *
from pyxpp.generator import *



def test_generate_name():
    test = Name('x')
    expected = 'x'
    assert generate_name(test) == expected


number_tests = [
    (Number(42), '42'),
    (Number(.4), '0.4'),
    (Number(3.2), '3.2'),
]

@pytest.mark.parametrize('test, expected', number_tests)
def test_generate_number(test, expected):
    assert generate_number(test) == expected


binop_tests = [
    (BinOp(Name('x'), '*', Number(2.)), 'x*2.0'),
    (BinOp(Name('d'), '-', BinOp(Name('x'), '/', Name('s'))),
     'd - (x/s)'),
]

@pytest.mark.parametrize('test, expected', binop_tests)
def test_generate_binop(test, expected):
    assert generate_binop(test) == expected


def test_generate_unaryop():
    test = UnaryOp('-', Name('x_1'))
    expected = '-x_1'
    assert generate_unaryop(test) == expected


funcall_tests = [
    (FunCall('f', [Name('x')]), 'f(x)'),
    (FunCall('tanh', [Name('x'), Name('y')]), 'tanh(x,y)'),
    (FunCall('sin', [FunCall('f', [Name('t')]), Name('y')]),
             'sin(f(t),y)'),
]

@pytest.mark.parametrize('test, expected', funcall_tests)
def test_generate_fun_call(test, expected):
    assert generate_fun_call(test) == expected


def test_generate_assignment():
    test = Assignment(Name('x'), Number(3))
    expected = 'x=3'
    assert generate_assignment(test) == expected


def test_generate_assignments():
    test = [Assignment(Name('x'), Number(2.3)),
            Assignment(Name('method'), ('stiff'))]
    expected = 'x=2.3,method=stiff'
    assert generate_assignments(test) == expected


def test_generate_fixed_var():
    test = FixedVar([Assignment(Name('x'), Number(42.)),
                     Assignment(Name('k'), Number(.1))])
    expected = 'number x=42.0,k=0.1'
    assert generate_fixed_var(test) == expected


def test_generate_par():
    test = Par([Assignment(Name('vv'), Number(2))])
    expected = 'par vv=2'
    assert generate_par(test) == expected


def test_generate_aux():
    test = Aux([Assignment(Name('y'), UnaryOp('-', Number(3.2)))])
    expected = 'aux y=-3.2'
    assert generate_aux(test) == expected


def test_generate_init():
    test = Init([Assignment(Name('v1'), Number(0))])
    expected = 'init v1=0'
    assert generate_init(test) == expected


def test_generate_option():
    test = Option([Assignment(Name('maxstor'), Number(40000000)),
                   Assignment(Name('bounds'), Number(100000)),
                   Assignment(Name('method'), Name('stiff'))])
    expected = '@ maxstor=40000000,bounds=100000,method=stiff'
    assert generate_option(test) == expected


def test_generate_global():
    test = Global(UnaryOp('-', Number(1)),
            BinOp(Name('u'), '-', Number(0.2)),
            [Assignment(Name('m'), BinOp(Number(0.5), '*', Name('m')))])
    expected = 'global -1 {u-0.2} {m=0.5*m}'
    assert generate_global(test) == expected


def test_fun_def():
    test = FunDef(
        Name('minf'),
        [Name('v')], BinOp(Number(.5), '*',
                           BinOp(Number(1), '+',
                                 FunCall(Name('tanh'),
                                         [BinOp(BinOp(Name('v'),
                                                      '-', Name('va')),
                                                '/', Name('vb'))])))
    )
    expected = 'minf(v)=.5*(1+tanh((v-VA)/VB))'
    assert generate_fun_def(test) == expected


def test_ode():
    test = ODE(Assignment(Name('v1'), FunCall(Name('f'), [Name('v1')])))
    expected = "v1\'=f(v1)"
    assert generate_ode(test) == expected


def test_done():
    test = Done()
    expected = 'done'
    assert generate_done(test) == expected
