# An XPP wrapper based on PLY.
#
# This file is part of PyXPP.
#
# PyXPP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyXPP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyXPP.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Mark Olenik, mark.olenik@gmail.com



from collections import OrderedDict
import subprocess
import csv
import os
import re

import scipy as sp
import ply

from . import lexer
from . import parser
from . import generator


def parse_file(xppfile):
    """
    Read state variables from XPP file.

    Parameters
    ----------
    xppfile : str
        XPP file with system definition.

    Returns
    -------
    out : list of tuples
        Syntax tree from XPP file.

    """
    with open(xppfile, 'r') as f:
        data = f.read()
    syntax = parser.parser.parse(data)
    return syntax


def write_syntax(syntax, outfile):
    """
    Generate code from syntax tree and write to file.

    Parameters
    ----------
    syntax : list
        Abstract Syntax Tree generated from parser.
    outfile : str
        File to save the generated code to.

    """
    gen = generator.g_program(syntax)

    with open(outfile, 'w') as f:
        f.writelines([cmd + '\n' for cmd in gen])


def find_key_index(syntax, key):
    """
    Find index of key in syntax tree.  

    Parameters
    ----------
    syntax : list
        Abstract Syntax Tree generated from parser.
    key : str
        Key type can be of type parameter, initial condition, 
        auxilliary variable, or numeric option.
    
    Returns
    -------
    out : int
        Index of entry with key in syntax table.
    
    """
    keytypes = ['PAR', 'INIT', 'AUX', 'OPT']
    for idx, cmd in enumerate(syntax):
        if cmd[0] in keytypes and cmd[1][1]==key:
            return idx
    return idx


def version(xppfile):
    """
    Find version of installed XPP.

    Parameters
    ----------
    xppfile : str
        XPP file with system definition.
    
    Returns
    -------
    out : float
        Version number.
    
    """
    out = subprocess.PIPE
    res = subprocess.run('xppaut %s -version' % xppfile, shell=True,
                         stdout=out, stderr=out)
    outstring = res.stdout.decode('utf-8')
    version = float(re.search(r'(\d+\.\d*|\d*\.\d+)', outstring).group(0))
    return version



def dry_run(xppfile, outfile='output.dat', cleanup=True):
    """
    Perform a dry run of XPP to check file syntax.  Print standard output.

    Parameters
    ----------
    xppfile : str
        XPP file with system definition.
    outfile : str, optional
        Name of temporary file.
    quiet : bool, optional
        Print verbose log messages.
    cleanup : bool, optional
        Delete temporary file after reading.
    
    """
    out = subprocess.PIPE
    res = subprocess.run('xppaut %s -qics -outfile %s ' % (xppfile, outfile),
                         shell=True, stdout=out, stderr=out)
    
    if os.path.isfile(outfile) and cleanup:
        os.remove(outfile)

    if res == 0:
        print(res.stdout.decode('utf-8'))
    else:
        print(res.stderr.decode('utf-8'))

    return res
    

def _query_info(xppfile, info, outfile='output.dat', quiet=True,
                cleanup=True):
    """
    Query information by writing it to and from a temporary file.

    Parameters
    ----------
    xppfile : str
        XPP file with system definition.
    info : str
        Type of information to read. One of: 
        - qsets : Query internal sets.
        - qpars : Query parameters.
        - qics : Query ICs.
    outfile : str, optional
        Name of temporary file.
    quiet : bool, optional
        Print verbose log messages.
    cleanup : bool, optional
        Delete temporary file after reading.
    
    Returns
    -------
    out : OrderedDict
        Information dictionary.

    """
    subprocess.check_call('xppaut %s %s -outfile %s -quiet %s'
                                % (xppfile, info, outfile, int(quiet)),
                                shell=True)
    if os.path.isfile(outfile): # success
        _dat = sp.genfromtxt(outfile, dtype=[('f0', list), ('f1', float)])
        # Convert variable names from bytes to strings.
        dat = [(str.lower(x[0].decode('utf-8')), x[1]) for x in _dat]
        if cleanup:
            os.remove(outfile)
        odict = OrderedDict(dat)
        return odict

    else:
        print('Error in querying info.')


def read_state_vars(xppfile):
    """
    Read state variables from XPP file.

    Parameters
    ----------
    xppfile : str
        XPP file with system definition.

    Returns
    -------
    out : array_like of str
        State variables.

    """
    # Don't query state vars directly to avoid aux variables.
    syntax = parse_file(xppfile)
    opt_tuples = []
    opts = [cmd for cmd in syntax if cmd[0]=='ODE']
    state_vars = sp.array([opt[1] for opt in opts])
    return state_vars


def read_aux_vars(xppfile):
    """
    Read auxilliary variable from XPP file.

    Parameters
    ----------
    xppfile : str
        XPP file with system definition.

    Returns
    -------
    out: array_like of str
        Auxilliary variables.

    """
    syntax = parse_file(xppfile)
    opt_tuples = []
    opts = [cmd for cmd in syntax if cmd[0]=='AUX']
    state_vars = sp.array([opt[1][1] for opt in opts])
    return state_vars


def read_vars(xppfile, **kwargs):
    """
    Read state and auxilliary variables from XPP file.

    Parameters
    ----------
    xppfile : str
        XPP file with system definition.

    Returns
    -------
    out: array_like of str
        All variables.

    """
    state_vars = read_state_vars(xppfile)
    aux_vars = read_aux_vars(xppfile)
    return sp.concatenate((state_vars, aux_vars))


def read_pars(xppfile):
    """
    Read parameters from XPP file.
    
    Parameters
    ----------
    xppfile : str
        XPP file with system definition.

    Returns
    -------
    out : OrderedDict
        Parameters.

    """
    syntax = parse_file(xppfile)
    pars = [(cmd[1][1], float(generator.g_expr(cmd[1][2])))
            for cmd in syntax
            if cmd[0]=='PAR']
    return OrderedDict(pars)


def read_ics(xppfile):
    """
    Return IC and aux vales from XPP file.
    
    Parameters
    ----------
    xppfile : str
        XPP file with system definition.

    Returns
    -------
    out : array_like
        Array with IC and aux values ordered according to 
        associated variables.

    """
    state_vars = read_state_vars(xppfile)
    aux_vars = read_aux_vars(xppfile)

    syntax = parse_file(xppfile)
    # Get touples of ICs in form of (variable, value).
    inits = OrderedDict([(cmd[1][1], float(generator.g_expr(cmd[1][2])))
                         for cmd in syntax
                         if cmd[0]=='INIT'])
    # Make sure order is correct.
    inits_ord = OrderedDict((k, inits[k]) for k in state_vars)
    ics = sp.array(list(inits_ord.values()))
    # XPP initialises of aux at 0.
    auxs = sp.zeros(len(aux_vars))

    return sp.concatenate((ics, auxs))


def read_opts(xppfile):
    """
    Read numeric options from XPP file.
    
    Parameters
    ----------
    xppfile : str
        XPP file with system definition.

    Returns
    -------
    out : OrderedDict
        Options.

    """
    syntax = parse_file(xppfile)
    opt_tuples = []
    opts = [cmd for cmd in syntax if cmd[0]=='OPT']
    for cmd in opts:
        opt = generator.g_expr(cmd[1][-1])
        if opt.isdigit():
            opt = float(opt)
        key = cmd[1][1]
        opt_tuples.append((key, opt))
    return OrderedDict(opt_tuples)
    

def _append_uid(fname, uid):
    """
    Append UID to file.
    
    Parameters
    ----------
    fname : str
        File name.
    uid : int
        Unique identifier to append to file.
    
    Returns
    -------
    out : str
        New file name with uid appended.

    """
    parts = fname.split('.')
    if len(parts) > 1:          # File name with suffix.
        return parts[0]+'-'+str(uid)+'.'+parts[1]
    else:                       # No suffix.
        return parts[0]+'-'+str(uid)


def run(xppfile, ics=None, outfile='output.dat', icfile='ics.dat',
        parfile=None, uid=None, cleanup=True, **kwargs):
    """
    Run XPP simulation in silent mode and return result.
    
    Parameters
    ----------
    xppfile : str
        XPP file with system definition.
    ics : array_like, optional
        ICs.
    outfile : str, optional
        Name of temporary output file.
    icfile : str, optional
        Load ICs from the named file.
    parfile : str, optional
        Load parameters from the named file.
    uid : int, optional
        Unique identifier to append to all stored files.  Useful for
        parallel simulations.
    cleanup : bool, optional
        Delete temporary file after reading.
    **kwargs : keyword arguments, optional
        Allows setting additional options such as parameters or
        numerical setttings directly.
    
    Returns
    -------
    out : ndarray
        Simulation results.

    """
    # Read optional arguments.
    optstr = ''
    for key, value in kwargs.items():
        optstr += key + '=' + str(value) + ';'
    # Remove trailing semicolon.
    optstr = optstr[:-1]

    # Append unique identifier.
    if uid is not None:
        outfile = _append_uid(outfile, uid)
        icfile = _append_uid(icfile, uid)

    # Write initial conditions to file.
    if ics is not None:
        sp.savetxt(icfile, list(ics)) 
    else:
        ics = read_ics(xppfile)
        sp.savetxt(icfile, ics)

    # Prepare XPP command.
    command = (f"xppaut {xppfile} -silent -with '{optstr}' -runnow "
               f"-outfile {outfile} -icfile {icfile}")

    if parfile is not None:
        command += ' -parfile ' + parfile

    out = subprocess.PIPE
    # Run command and read result.
    res = subprocess.run(command, stdout=out, stderr=out, shell=True)
    if res.returncode != 0:
        return out.stderr

    outdat = sp.genfromtxt(outfile, delimiter=' ')

    # Cleanup if necessary.
    if cleanup and os.path.isfile(outfile) and os.path.isfile(icfile):
        os.remove(outfile)
        os.remove(icfile)

    return outdat


def nullclines(xppfile, xplot=None, yplot=None, xlo=None, xhi=None,
               ylo=None, yhi=None, cleanup=True, outfile='out.ode',
               **kwargs):
    """
    Compute nullclines.
    
    Parameters
    ----------
    xppfile : str
        XPP file with system definition.
    xplot : str, optional
        State variable to plot on X-axis.
    yplot : str, optional
        State variable to plot on y-axis.
    xlo : float, optional
        X-axis lower limit.
    xhi : float, optional
        X-axis higher limit.
    ylo : float, optional
        Y-axis lower limit.
    yhi : float, optional
        Y-axis higher limit.
    cleanup : bool, optional
        Delete temporary file after reading.
    outfile : str, optional
        File name of temporary output file.
    **kwargs : keyword arguments, optional
        Allows setting additional options such as parameters or
        numerical setttings directly.
    
    Returns
    -------
    out : ndarray
        Nullclines.

    """
    # Nullclines output file is hard-coded in XPP to 'nullclines.dat'.
    NULLCLINES_FILE = 'nullclines.dat'
    
    # Read optional parameters.
    optstr = ''
    for key, value in kwargs.items():
        optstr += key + '=' + str(value) + ';'
    # Remove trailing semicolon.
    optstr = optstr[:-1]

    # XPP computes nullclines only on the specified axis limits "xlo", "xhi",
    # and "ylo", "yhi", and for variables specifies in "xplot" and "yplot".
    # We therefore need to create a temporary XPP file and update the limits
    # accordingly if they were provided.

    syntax = parse_file(xppfile)
    keys = ['xlo', 'xhi', 'ylo', 'yhi', 'xplot', 'yplot']
    vals = [xlo, xhi, ylo, yhi, xplot, yplot]
    for key, val in zip(keys, vals):
        if val is not None:
            key_idx = find_key_index(syntax, key)
            cmd = '@ %s=%s\n' % (key, val)
            syntax[key_idx] = parser.parser.parse(cmd)[0]

    # Generate temporary XPP file.
    write_syntax(syntax, outfile)

    # Run with nullcline command line option.
    out = subprocess.PIPE
    res = subprocess.run("xppaut %s -silent -with '%s' -ncdraw 2 -noout" 
                         % (outfile, optstr), stdout=out, stderr=out,
                         shell=True)
    if res.returncode != 0:
        return out.stderr

    # Read nullclines from file.
    nullc_dat = sp.genfromtxt(NULLCLINES_FILE, delimiter=' ')

    # Separate the two nullclines, nullc_dat[:,2] is either 1 or 2.
    n1 = nullc_dat[nullc_dat[:, 2]==1, :2]
    n2 = nullc_dat[nullc_dat[:, 2]==2, :2]

    # Sort data along first variable for easier plotting.
    idx1 = sp.argsort(n1[:, 0])
    idx2 = sp.argsort(n2[:, 0])
    n1_sorted = n1[idx1, :2]
    n2_sorted = n2[idx2, :2]

    ret = n1_sorted, n2_sorted

    if cleanup and os.path.isfile(NULLCLINES_FILE):
            os.remove(NULLCLINES_FILE)
            os.remove(outfile)

    return ret

