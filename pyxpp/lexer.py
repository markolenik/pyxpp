# An XPP lexer based on PLY.
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


import ply.lex


tokens = [
    "APOSTROPHE",
    "ARRAYSLICE",
    "AUX",
    "DIVIDE",
    "COMMA",
    "ELSE",
    "EQUALS",
    "FLOAT",
    "GE",
    "GLOBAL",
    "GT",
    "ID",
    "IF",
    "INIT",
    "INTEGER",
    "LBRACE",
    "LBRACKET",
    "LE",
    "LPAREN",
    "LT",
    "MINUS",
    "NE",
    "NEWLINE",
    "OF",
    "OPT",
    "PAR",
    "POWER",
    "PLUS",
    "RBRACE",
    "RBRACKET",
    "RPAREN",
    "SEMI",
    "SUM",
    "THEN",
    "TIMES",
]

# We ignore whitespace.
t_ignore = " \t"

# Simple token definitions.
t_EQUALS = r"="
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_POWER = r"(\^|\*\*)"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LT = r"<"
t_LE = r"<="
t_GT = r">"
t_GE = r">="
t_NE = r"<>"
t_COMMA = r"\,"
t_SEMI = r";"
t_APOSTROPHE = r"\'"


# Ignore comments and "active comments".
def t_COMMENT(t):
    r"(?m)^(\#|\").*"
    pass


# For we also ignore the following:
# table, bdry, volt, markov, wiener, solv, special, set,
# derived parameters, numbers, int, block pseudo-arrays.
def t_NOTUSED(t):
    r"(?m)^(table|bdry|volt|markov|wiener|solv|special|set|!|number|int|\%(.|\n)*?\%).*"  # noqa: E501
    pass


# Token definitions for keywords etc.


def t_OF(t):
    r"of"
    return t


def t_ARRAYSLICE(t):
    r"\[\d+\s*\.\.\s*\d+\]"
    return t


def t_IF(t):
    r"if"
    return t


def t_THEN(t):
    r"then"
    return t


def t_ELSE(t):
    r"else"
    return t


def t_INIT(t):
    r"(?m)^init"
    return t


def t_PAR(t):
    r"(?m)^p\w*"
    return t


def t_AUX(t):
    r"(?m)^aux"
    return t


def t_OPT(t):
    r"(?m)^\@"
    return t


def t_GLOBAL(t):
    r"global"
    return t


def t_SUM(t):
    r"sum"
    return t


def t_DONE(t):
    r"done"
    pass


# General identifier for variables.
def t_ID(t):
    r"([a-zA-Z]+\w*|\w*[a-zA-Z]+)"
    # Turn to lowercase since XPP is not case sensitive.
    t.value = str.lower(t.value)
    return t


def t_NEWLINE(t):
    r"\n"
    t.lexer.lineno += 1
    return t


def t_FLOAT(t):
    r"(\d+\.\d*|\d*\.\d+)"
    t.value = float(t.value)
    return t


def t_INTEGER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_error(t):
    print("Illegal character %s" % t.value[0])
    t.lexer.skip(1)


lexer = ply.lex.lex()
