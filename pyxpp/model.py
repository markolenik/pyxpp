# A convenience model class to store ODE parameters.

from typing import NamedTuple
import scipy as sp

from . import pyxpp.pyxpp as xpp


class Model(NamedTuple):
    """XPP model."""

    ode: str                    # XPP ODE file.
    statevars: sp.ndarray       # State variables.
    inits: sp.ndarray           # Initial conditions.
    opts: sp.ndarray            # Numerical options.
    pars: sp.ndarray            # Parameters.



def new_model(ode):
    """Create new model from XPP ODE file."""
    statevars = xpp.read_state_vars(ode)
    inits = xpp.read_inits(ode)
    opts = xpp.read_opts(ode)
    pars = xpp.read_pars(ode)
    return Model(ode, statevars, inits, opts, pars)


def run(net, **kwargs):
    """Integrate network."""
    sol = xpp.run(net.ode, **kwargs)
    return sol


def nullclines(net, **kwargs):
    """Compute nullclines."""
    ns = xpp.nullclines(net.ode, **kwargs)
    return ns
