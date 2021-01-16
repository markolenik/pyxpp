from collections import OrderedDict
import subprocess
import os
import re

import numpy as np

from pyxpp.parser import parse
from pyxpp import generator


def parse_file(xpp_file):
    """
    Read state variables from XPP file.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.

    Returns
    -------
    syntax: list of tuples
        Syntax tree from XPP file.

    """
    with open(xpp_file, "r") as file:
        data = file.read()
    syntax = parser.parser.parse(data)
    return syntax


def write_syntax(syntax, out_file):
    """
    Generate code from syntax tree and write to file.

    Parameters
    ----------
    syntax: list
        Abstract Syntax Tree generated from parser.
    out_file: str
        File to save the generated code to.

    """
    commands = generator.g_program(syntax)

    with open(out_file, "w") as file:
        file.writelines([command + "\n" for command in commands])


def find_key_index(syntax, key):
    """
    Find index of key in syntax tree.

    Parameters
    ----------
    syntax: list
        Abstract Syntax Tree generated from parser.
    key: str
        Key type can be of type parameter, initial condition,
        auxilliary variable, or numeric option.

    Returns
    -------
    out: int
        Index of entry with key in syntax table.

    """
    keytypes = ["PAR", "INIT", "AUX", "OPT"]
    index = -1
    for index, command in enumerate(syntax):
        if command[0] in keytypes and command[1][1] == key:
            return index
    return index


def version(xpp_file):
    """
    Find version of installed XPP.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.

    Returns
    -------
    out: float
        Version number.

    """
    out_pipe = subprocess.PIPE
    process = subprocess.run(
        "xppaut %s -version" % xpp_file, shell=True,
        stdout=out_pipe, stderr=out_pipe, check=True
    )
    out_string = process.stdout.decode("utf-8")
    return float(re.search(r"(\d+\.\d*|\d*\.\d+)", out_string).group(0))


def dry_run(xpp_file, out_file="output.dat", cleanup=True):
    """
    Perform a dry run of XPP to check file syntax.  Print standard output.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.
    out_file: str, optional
        Name of temporary file.
    quiet: bool, optional
        Print verbose log messages.
    cleanup: bool, optional
        Delete temporary file after reading.

    """
    out_pipe = subprocess.PIPE
    process = subprocess.run(
        "xppaut %s -qics -outfile %s " % (xpp_file, out_file),
        shell=True, stdout=out_pipe, stderr=out_pipe, check=True
    )

    if os.path.isfile(out_file) and cleanup:
        os.remove(out_file)

    if process == 0:
        print(process.stdout.decode("utf-8"))
    else:
        print(process.stderr.decode("utf-8"))

    return process


def _query_info(xpp_file, info, out_file="output.dat", quiet=True,
                cleanup=True):
    """
    Query information by writing it to and from a temporary file.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.
    info: str
        Type of information to read. One of:
        - qsets: Query internal sets.
        - qpars: Query parameters.
        - qics: Query ICs.
    out_file: str, optional
        Name of temporary file.
    quiet: bool, optional
        Print verbose log messages.
    cleanup: bool, optional
        Delete temporary file after reading.

    Returns
    -------
    OrderedDict
        Information dictionary.

    """
    subprocess.check_call(
        "xppaut %s %s -outfile %s -quiet %s" % (
            xpp_file, info, out_file, int(quiet)), shell=True,
    )
    if os.path.isfile(out_file):  # success
        _dat = np.genfromtxt(out_file, dtype=[("f0", list), ("f1", float)])
        # Convert variable names from bytes to strings.
        dat = [(str.lower(x[0].decode("utf-8")), x[1]) for x in _dat]
        if cleanup:
            os.remove(out_file)
        odict = OrderedDict(dat)
        return odict

    print("Error in querying info.")


def read_state_variables(xpp_file):
    """
    Read state variables from XPP file.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.

    Returns
    -------
    array_like of str
        State variables.

    """
    syntax = parse_file(xpp_file)
    state_variables = [command[1] for command
                       in syntax if command[0] == "ODE"]
    return state_variables


def read_aux_variables(xpp_file):
    """
    Read auxilliary variable from XPP file.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.

    Returns
    -------
    array_like of str
        Auxilliary variables.

    """
    syntax = parse_file(xpp_file)
    return [command[1][1] for command in syntax if command[0] == "AUX"]


def read_variables(xppfile):
    """
    Read state and auxilliary variables from XPP file.

    Parameters
    ----------
    xppfile: str
        XPP file with system definition.

    Returns
    -------
    array_like of str
        All variables.

    """
    state_vars = read_state_variables(xppfile)
    aux_vars = read_aux_variables(xppfile)
    return np.concatenate((state_vars, aux_vars))


def read_parameters(xpp_file):
    """
    Read parameters from XPP file.

    Parameters
    ----------
    xppfile: str
        XPP file with system definition.

    Returns
    -------
    OrderedDict
        Parameters.

    """
    syntax = parse_file(xpp_file)
    parameters = [
        (command[1][1], float(generator.g_expr(command[1][2])))
        for command in syntax
        if command[0] == "PAR"
    ]
    return OrderedDict(parameters)


def read_ics(xpp_file):
    """
    Return IC and aux values from XPP file.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.

    Returns
    -------
    array_like
        Array with IC and aux values ordered according to
        associated variables.

    """
    variables = read_state_variables(xpp_file)
    aux_variables = read_aux_variables(xpp_file)

    syntax = parse_file(xpp_file)
    # Get touples of ICs in form of (variable, value).
    inits = OrderedDict(
        [
            (command[1][1], float(generator.g_expr(command[1][2])))
            for command in syntax
            if command[0] == "INIT"
        ]
    )
    # Make sure order is correct.
    inits_ord = OrderedDict((variable, inits[variable])
                            for variable in variables)
    ics = np.array(list(inits_ord.values()))
    # XPP initialises of aux at 0.
    auxs = np.zeros(len(aux_variables))

    return np.concatenate((ics, auxs))


def read_numeric_options(xpp_file):
    """
    Read numeric options from XPP file.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition

    Returns
    -------
    OrderedDict
        Options

    """
    syntax = parse_file(xpp_file)
    options = [command for command in syntax if command[0] == "OPT"]
    option_tuples = []
    for option in options:
        # TODO: This should be solved much more elegantly.
        # Need to implement a generator-like module which returns
        # Python objects instead.
        option_key = option[1][1]
        option_type = option[1][-1][0]
        option_string = generator.g_expr(option[1][-1])
        if option_type == 'NUM':
            option_value = float(option_string)
        # In case of 'VAR' type options
        option_value = option_string
        option_tuples.append((option_key, option_value))
    return OrderedDict(option_tuples)


def _append_uid(fname, uid):
    """
    Append UID to file.

    Parameters
    ----------
    fname: str
        File name
    uid: int
        Unique identifier to append to file

    Returns
    -------
    str
        New file name with uid appended.

    """
    parts = fname.split(".")
    if len(parts) > 1:  # File name with suffix.
        return parts[0] + "-" + str(uid) + "." + parts[1]
    # No suffix.
    return parts[0] + "-" + str(uid)


def run(xpp_file, ics=None, out_file="output.dat", ic_file="ics.dat",
        par_file=None, uid=None, cleanup=True, **kwargs):
    """
    Run XPP simulation in silent mode and return result.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.
    ics: array_like, optional
        ICs.
    out_file: str, optional
        Name of temporary output file.
    ic_file: str, optional
        Load ICs from the named file.
    par_file: str, optional
        Load parameters from the named file.
    uid: int, optional
        Unique identifier to append to all stored files.  Useful for
        parallel simulations.
    cleanup: bool, optional
        Delete temporary file after reading.
    **kwargs: keyword arguments, optional
        Allows setting additional options such as parameters or
        numerical setttings directly.

    Returns
    -------
    ndarray
        Simulation results.

    """
    # Read optional arguments.
    optional_arguments = ""
    for key, value in kwargs.items():
        optional_arguments += key + "=" + str(value) + ";"
    # Remove trailing semicolon.
    optional_arguments = optional_arguments[:-1]

    # Append unique identifier.
    if uid is not None:
        out_file = _append_uid(out_file, uid)
        ic_file = _append_uid(ic_file, uid)

    # Write initial conditions to file.
    if ics is not None:
        np.savetxt(ic_file, list(ics))
    else:
        ics = read_ics(xpp_file)
        np.savetxt(ic_file, ics)

    # Prepare XPP command.
    command = (
        f"xppaut {xpp_file} -silent -with '{optional_arguments}' -runnow "
        f"-outfile {out_file} -icfile {ic_file}"
    )

    if par_file is not None:
        command += " -parfile " + par_file

    out_pipe = subprocess.PIPE
    # Run command and read result.
    process = subprocess.run(command, stdout=out_pipe, stderr=out_pipe,
                             shell=True, check=True)
    if process.returncode != 0:
        return out_pipe.stderr

    outdat = np.genfromtxt(out_file, delimiter=" ")

    # Cleanup if necessary.
    if cleanup and os.path.isfile(out_file) and os.path.isfile(ic_file):
        os.remove(out_file)
        os.remove(ic_file)

    return outdat


def nullclines(xpp_file, xplot=None, yplot=None, xlo=None, xhi=None, ylo=None,
               yhi=None, cleanup=True, out_file="out.ode", **kwargs):
    """
    Compute nullclines.

    Parameters
    ----------
    xpp_file: str
        XPP file with system definition.
    xplot: str, optional
        State variable to plot on X-axis.
    yplot: str, optional
        State variable to plot on y-axis.
    xlo: float, optional
        X-axis lower limit.
    xhi: float, optional
        X-axis higher limit.
    ylo: float, optional
        Y-axis lower limit.
    yhi: float, optional
        Y-axis higher limit.
    cleanup: bool, optional
        Delete temporary file after reading.
    out_file: str, optional
        File name of temporary output file.
    **kwargs: keyword arguments, optional
        Allows setting additional options such as parameters or
        numerical setttings directly.

    Returns
    -------
    ndarray
        Nullclines.

    """
    # Nullclines output file is hard-coded in XPP to 'nullclines.dat'.
    nullclines_file = "nullclines.dat"

    # Read optional arguments.
    optional_arguments = ""
    for key, value in kwargs.items():
        optional_arguments += key + "=" + str(value) + ";"
    # Remove trailing semicolon.
    optional_arguments = optional_arguments[:-1]

    # XPP computes nullclines only on the specified axis limits "xlo", "xhi",
    # and "ylo", "yhi", and for variables specifies in "xplot" and "yplot".
    # We therefore need to create a temporary XPP file and update the limits
    # accordingly if they were provided.

    syntax = parse_file(xpp_file)
    keys = ["xlo", "xhi", "ylo", "yhi", "xplot", "yplot"]
    values = [xlo, xhi, ylo, yhi, xplot, yplot]
    for key, value in zip(keys, values):
        if value is not None:
            key_index = find_key_index(syntax, key)
            command = "@ %s=%s\n" % (key, value)
            syntax[key_index] = parser.parser.parse(command)[0]

    # Generate temporary XPP file.
    write_syntax(syntax, out_file)

    # Run with nullcline command line option.
    out_pipe = subprocess.PIPE
    process = subprocess.run(
        "xppaut %s -silent -with '%s' -ncdraw 2 -noout" % (
            out_file, optional_arguments),
        stdout=out_pipe, stderr=out_pipe, shell=True, check=True
    )
    if process.returncode != 0:
        return out_pipe.stderr

    # Read nullclines from file.
    nullcline_data = np.genfromtxt(nullclines_file, delimiter=" ")

    # Separate the two nullclines, nullc_dat[:,2] is either 1 or 2.
    nullcline1 = nullcline_data[nullcline_data[:, 2] == 1, :2]
    nullcline2 = nullcline_data[nullcline_data[:, 2] == 2, :2]

    # Sort data along first variable for easier plotting.
    indices1 = np.argsort(nullcline1[:, 0])
    indices2 = np.argsort(nullcline2[:, 0])
    nullcline1_sorted = nullcline1[indices1, :2]
    nullcline2_sorted = nullcline2[indices2, :2]

    if cleanup and os.path.isfile(nullclines_file):
        os.remove(nullclines_file)
        os.remove(out_file)

    return nullcline1_sorted, nullcline2_sorted
