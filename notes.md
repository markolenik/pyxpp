Purpose of this project
-----------------------
The ultimate goal is to have a robust xpp wrapper that can be put on pypi, with CI/CD etc. It's functionality is supposed to include:
- Reading of parameters, variables, auxiliarry stuff and options
- Running of simulations, automatic handling of temporary files etc.
- Arrays should be implemented
- Be able to identify bits that aren't supported and just ignore them
- Compute and plot nullclines

What the project is not:
- Will not modify xpp files or replace model definition: this shit still has to be done through .ode files. No code generation
- A feature complete xpp parser. I won't implement many things, since I don't use them, and they probably aren't too useful for inspection anyway.

Stuff that may be implemented in future and might be useful:
- Reading of RHS of ODEs and custom function definitions

Array troubles
--------------

This whole array thing is fucking up everything. Need to somehow generalise.


Array can occur in:
- par
- init
- aux
- variable def
- function def


Array assignment can only come first


fun_name(x,y) = expr

Array blocks
---------------
This will be hard to implement...

```
%[1..3]
x[j]’=-y[j]
y[j]’=x[j]
init x[j]=1
%
```

Array subscript
-------------------
```
x[1..10]’=-x[j]
```


Abbreviations
----------------
All of the declarations, markov, parameter, wiener,
table, aux, init, bndry, global, **done***, can be abbreviated by their first letter.


Line continuation
---------------------
I'm not sure if that's implemented at all yet. Example
```
x' = y \
 + z + \
```

I'm not sure how the line continuation is even read by ply...


Are maps implemented?
--------------------------
Have this form:

```
x(t+1)=x

```

Reservered words
--------------------
sin cos tan atan atan2 sinh cosh tanh
exp delay ln log log10 t pi if then else
asin acos heav sign ceil flr ran abs del\_shft
max min normal besselj bessely erf erfc
arg1 ... arg9 @ $ + - / * ^ ** shift
| > < == >= <= != not \# int sum of i’

What's `not`?


Wiener parameters
---------------------

```
wiener w[1..5]
```

