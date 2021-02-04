import pytest
from pyxpp.parser import *
from pyxpp.generator import *


def test_generate_name():
    test = Name('x')
    expected = 'x'
    assert generate_name(test) == expected


def test_generate_assignment():
    test = Assignment(Name('x'), Number(3))
    expected = 'x=3'
    assert generate_assignment(test) == expected


def test_generate_unaryop():
    test = UnaryOp('-', Number(32.2))
    expected = '-32.2'
    assert generate_unaryop(test) == expected


# def test_generate_group():
#     test = Group(BinOp(Number(2), '+', Name('v')))
#     expected =


def test_generate_fun_call():
    test = FunCall(Name('f'), [Name('x'), BinOp(Name('x'), '+', Number(42))])
    expected = 'f(x, x+42)'
    assert generate_fun_call(test) == expected
