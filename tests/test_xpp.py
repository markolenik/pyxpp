import textwrap

import pytest
from pyxpp import xpp


# TODO
def test_check_syntax_pass():
    test_pass = textwrap.dedent("""
    # nnet1.ode
    da/dt = (-a+w*f(a)+i)/tau
    f(a)=1/(1+exp(-beta*(a-theta)))
    par beta=2,theta=1,i=0,tau=1,w=1
    done""")
    assert xpp.check_syntax()

# TODO
def test_check_syntax_fail():
    test_fail = textwrap.dedent("""
    # nnet1.ode
    da/dt = (-a+w*f(a)+i)/tau
    f(a)=1/(1+exp(-beta*(a-theta)))'
    par beta=2,theta=1,i=0,tau=1,w=1
    done""")
