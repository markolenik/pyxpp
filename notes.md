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

What's the big goal?
-------------------------
- Store xpp file as sytnax
- Convert xpp-syntax to python objects


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

