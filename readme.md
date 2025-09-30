
# LISAPET
Linear Interpreter of Scripting And Processing Expression Tree.  
(LP, this code, miniscript)

ico: Fox pet on the bicycle

LISAPET is an interpretable language like python, written with python, but not a python :D  
It was started as a pet-project - simple and small scripting language  (not so small already [facepalm]) for short scripts which could be run for the python project but without direct execution of scripts on the python interpreter (bad and unsafe way).  
Instead of line-by-line execution, interpreter builds executable object, actually - tree of actions (expressions).  
Than this object can be executed with some data. One or many times if need.  
Executable tree uses context-container with working data (variables, values, types, etc).  
Utility `run.py` can run LP code from file or string in console with the set of arguments (see Usage section).  
Another way - call parser and interpreter manually from your code and run built object with context. It's way to embed Lisapet into your own project (no examples here, see `run.py`).  

--------------------------------------------------------
--------------------------------------------------------

Content:  
- [Status](#status)
- [Usage](#usage)
- [Syntax](#syntax)
1. [Basic things: vars, vals](#1-vars-vals-lists-assignment-context-of-vars)
2. [Basic types](#2-numbers-strings-bool-types)
3. [Block. If-statement](#3-sub-block-of-expressions-if)
4. [Math and other operators](#4-math-operators-unary-operators)
5. [Collections `[1,2]`, `{'b':2}`, `(1, 2, 3)`](#5-collections-list-array-tuple-dict-map)
6. [For-statement: `for i <- [1..5]`](#6-for-statement---operator)
7. [Functions:`func foo()`](#7-function-definition-context-of-functions)
8. [Dict](#8-dict-linear-and-block-constructor)
9. Collection features:
    1. [append operator `nums <- 15`](#91-arrow-appendset-operator--)
    2. [deletion operator `data - [key]`](#92-minus-key---key-delete-operator)
    3. [plus for lists `[] + []`](#93-list-plus---)
10. Struct: 
    1. [Definition, constructor, fields](#101-struct)
    2. [Callable constructor](#102-constructor-function-typename)
11. Struct, OOP:
    1. [Methods](#111-struct-method)
    2. [Inheritance](#112-struct-inheritance-multiple-inheritance-is-allowed)
12. List features:
    1. [Slice, iteration generator: `[ : ]`, `[ .. ]`](#121-list-features-slice-iteration-generator-tolist)
    2. [Sequence generator `[ ; ; ]`](#122-list-comprehension--sequence-generator)
13. [Multiline expressions](#13-multiline-expressions-if-for-math-expr)
14. [Builtin/native functions (print, iter,..)](#14-builtin-functions)
15. [Lambdas and high-order functions `x -> x ** 2`](#15-lambda-functions-and-high-order-functions-right-arrow--)
16. [Match-statement](#16-match-statement)
17. [Multi-assignment `a, b = c, d`](#17-multi-assignment)
18. [Ternary `?:` operator](#18-ternary-operator-)
19. [In `?>`, not in `!?>` operators](#19-val-in--and-val-not-in--operators)
20. [Inline block `a=1; b=2`](#20-one-line-block---operators)
21. [String formatting `<<`, `~" "` operators](#21-string-formatting)
22. [Import modules](#22-import-modules)
23. [Function as object](#23-function-as-an-object)
24. [Closures](#24-closures)

*
## Status.
Actually it is on-dev. Most basic features and needed things is done.  
Details see next, in `syntax` section.  
As an one-hands made project all updates are committed into dev and almost immediately merged into main branch, without version numeration. Tests covers all the changes as possible.  

*
Basic principles.
1. no extra thingth, block is defined by line shifting like python or ruby
2. basic collections: list, dict, tuple
3. arithmetic expressions - like python syntax: (a + 1/2) * b - c ** 2 .
4. control structs: `if-else`, `match`, `for`, `while`.
5. functions: function is an object, value of last expression is a returning result. Explicit `return` works too.
6. `struct` as a complex type. struct can have methods. Inheritance works too.
7. functions have typed args, by default as Any type.
8. Import modules.
9. Some syntax sugar: list slice, list generator, `<-`, `?>`, `?:` operators, multiple assignment.

*

## Usage.
Note: `python run` command is one line, splitted in examples just for better readability. 
run file  
```console
$ python -m run tests/simple_test.et
...
```
```console
## run code line
## -c --codeline
$ python -m run -c "a = 2; b = a + 1"

## with print function
$ python -m run -c "r = [1..5]; print('nums:', tolist(r))"
nums: [1, 2, 3, 4, 5]
...

## more complex 1-line example:
$ python -m run \
    -c "f1 = (x, y) -> x + y; f2 = x -> x * x;  p = x -> print(x); \
        [p(f1(f2(n), 10000)); n <- [1..10]; n % 2 > 0 && n > 3]"
10025
10049
10081
```
Features of `run`.  
```console
## show result
## -r --result : name of resulting variable
$ py -m run -c "res = 100 + 23" -r res
>> 123
```

```console
## multirun - build once and run multiple times by dataset
## json as a data source
## -l --multirun
## -s --datasource : LP-code produsing data
## -f --json-file : file with data
## -j --json-source : string with json

## data: [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}]
$ py -m run \
    -c "n = a + b; print(':', a, b, n)" \
    -l -j "[{\"a\":1, \"b\":2}, {\"a\":3, \"b\":4}, {\"a\":5, \ \"b\":6}]" \ 
    -r n
: 1 2 3
: 3 4 7
: 5 6 11
>> 11

```
Impoting and root path.
```console
## -p --pathroot
## -i --import
$ py -m run -p "tests" \
    -i "tdata.st1 > Point2, f1"  \
    -c "pp = Point2{x:2, y:3}; a = pp.sum(); p = (f1(a))" \
    -r p
```
Show error.  
For some debug needs we can ask print native Traceback of error.  
```console
## -e --show-error

$ py -m run -c "1/0" -e
Error handling:  division by zero
Traceback (most recent call last):
...
  File "...\nodes\oper_nodes.py", line 277, in div
    return a / b
           ~~^~~
ZeroDivisionError: division by zero
```

See code of run.py, loader.py, eval.py for understanding how to use LISAPET as an imbedded engine, add custom python functions for using in LP code, etc.  

## Syntax.
The Syntax section has been updated as new features have been added to the code, so it looks a bit chaotic.  
Done parts:  

### 0. Comments.
```
# one-line comment

#@
multiline comment
#@

#@ in-line comment @#
```

### 1. Vars, vals, lists, assignment, context of vars
Assigments of values of vars.  
I common case w euse `=` operator for assignment value to new of already defined variable.  
Default types of falues is: numeric types, string, list, dict, tuple.
```python
x = 1
name = 'Ramzes II'
names = ['Alya', 'Valya', 'Olya']
lastName = names[2]

# multiple assignment
a, b, c = 10, 20, 30
```

### 2. Numbers, strings, bool. Types.
```python
hello = "hello somebody!"
'unary-quotes'
'''multiline
string'''python

nums = [
    0123, # int, leading 0 will be irnored 
    0b1111, # int, binary
    0o777, # int octa
    0xfba01, # int hex
    0.15]   # float

#types
name:string = "Vasya"
age:int = 25
weight:float = 70

yes:bool = true
no:bool = false

```
Types such as a collections, structs, functions, etc will be explaned next sections.

### 3. Sub-block of expressions. If.
Control structures have inner place with internal expressions, here we call it as an expression block.  
Block separated by indent with one or more whitespaces. All indents should be equal.  
If statement, comparison operators, bool operators.
```python
res = 100
if x >= 10 | x < 2 && x != 0
    res = 2000 + x * -10 - 700
else
    x = x ** 2
    res = 1000 + x - 500
```

```python
# if with sub-expressions: if sub-expr; condition ...
if a = foo(); x < bar(a)
    ...
```

```python
# some sugar: else-if
if cond
    code
else if cond
    code
else
    code
```

### 4. Math operators, unary operators
```python
y = 5 + x * -3

# unary operator minus
x = -2

# pow
5 ** 2 # >> 25

# more complex math expressions
b=100 
c=4
d=3
res = 5 + 6 - 7*(b - c * 12 - 15) / 11 + 3 ** d - 0xe * 8
```
Other unary operators.  
`!` logical NOT  
`~` bitwise NOT  

Operators with assignment   
`+=` `-=` `*=` `/=` `%=` 
```python
x = 1
x += 2
```
Classic c-like operators.   
Bitwise:  
`&` `|` `^` `<<` `>>` `~`  
Compare:  
`==` `!=` `>` `<` `>=` `<` `<=`  
Logical:  
`&&` `||` `!`  
Others, have specific behaviour, will be explained further:  
`?>` `!?>` `?:` `<-` `->` `!-` `/:`  

Table of priority order:
```
() [] {} 
. 
-x !x ~x 
** 
* / % 
+ - 
<< >> 
< <= > >= !> ?> !?>
== != 
&
^
|
&&
||
?: 
: 
? 
,
<- 
->
= += -= *= /= %=  
; 
/:
!-
```


### 5. Collections: list (array), tuple, dict (map)
```python
# List, inline constructor

nums = ['One', 'Two', 'Three']

# List, block constructor (for long elements)

names = list
    'Anna'
    'Barbi'
    'Cindy'
    'Muxtar'

# change value
names[3] = 'Vaxtang'

# read value
firstName = names[0]
```
Negative indexes are allowed.  
It accesses to the element by position from the end of list.  
`[-1]` is a last element.  
```python
nums = [1,2,3,4,5]
print(nums[-2])
>> 4
```
Tuples: `(val, val, val)`.  

Tuple. Few values in the brackets over comma.  
Tuple is immutable.
```python
vals = (1, 100, 'More numbers')

# read value by index
print(vals[2])
```
Unpack values from list or tuple.
```python
names = ['Anatol', 'Basilev', 'Cardamon']
n1, n2, n3 = names

vals = (1, 22, 33,3)
a, b, c = vals
```

### 6. `for` statement, `<-` operator
- Range-iterator
```python
for i=0; i < 5; i = i + 1
    y = y + 2
    for j=-3; j <= 0; j = j + 1
        a = a - j ** 2
        if a % 2 == 0
            b = b + 1
res = y
```

- Iterator, arrow-assign operator `<-`  
Left-arrow `<-` operator has several options.  
Here we use left-arrow as an iterative assignment in `for` statement.  
It looks, like we pick the element from the sequence one-by-one.
```python
# by function iter
arr = [1,2,3]
r = 0
for i <- iter(3)
    r = r + arr[i]

# by array
for n <- [1,2,3]
    r += n

# by number-generator
# Generator [start .. last]
for x <- [1..10]
    r += x

# by dict
for k, val <- {'a':1, 'b':2}
    ...
```
Function `iter()`  
```python
# One arg iter(last+1)
iter(3) # >> 0,1,2

# more args iter(start, last+1 [, step])
iter(1, 5) # >> 1,2,3,4

iter(1,7,2) # >> 1,3,5

```

Keywords `continue`, `break`.  

```python
r = []
for i <- [1..10]
    if i < 5
        # stop current iteration and go to next
        continue
    if i > 8
        # exit from the loop immediately
        break
    r <- i

>> [5,6,7,8]
```

### 7. Function definition, context of functions.

Keyword `func`.  
Last expression is a returning result.  
Keyword `return` allowed to. 
```python
# definition
func foo(a, b, c)
    x = a - b
    if x <= 0
        return x # result
    y = b + c
    x * y # result

# function call
res = foo(1,2,3)

# arg type (optional)
func bar(a:int, b:int)
    a + b
```
Function can use nearest declaration context (actually all top-level things in module where func was declared).
```python
callIndex = 0

func foo(x, y)
    res = [x, y, callIndex]
    callIndex += 1
    res

```
See more about functions in sections: 14, 15, 23.

### 8. Dict. Linear and block constructor
```python
# linear constr
dd = {'a':1, 'b':2}

# block constr
ddd = dict
    'a': 'a a a a a a a a a a a a a a a a a'
    'b': 'b b b b b b b b b b b b b b b b b'

# set val by key
dd['c'] = 3

# read
print(dd['a'], ddd['b'])
```

### 9.1 arrow-append/set operator `<-`
Left-arrow with list or dict in the right operand  puts value into collection.  
(not in `for` statement or sequence generator)  
For list it appends new value; `list <- val`  
For dict it sets or updates value by key from passed tuple with `dict <- (val, key)`.  
```python
# list:
nn = [5]
nn <- 12

>> [5, 12]

# dict:
dd = {'b': 444}
dd <- ('a', 123)
dd <- ('b', 555)

>> {'b': 555, 'a': 123}
```
```python
mydict <- (key, val) 
# the same as 
mydict[key] = val
```
For dicts we can set multiple pairs of key-value by the dict in the right operand: `dict <- dict`
```python
res = {'a':11, 'b':22} # new dict

res <- {'c': 44, 'b':33} # add / update vals

>> {'a':11, 'b':33, 'c': 44}
```

### 9.2 Minus key `- [key]` (delete) operator
Minus operator for collections.  
Operator removes element by index | key and returns value of element.  
For list:
```python
a1 = [1,2,3]
r1 = a1 - [1] # returns 2
>> [1,3]
```
For dict:
```python
d2 = {'a':11, 'b':22}
r2 = d2 - ['a'] # returns 11
>> {'b': 22}
```

### 9.3 List plus `[] += []`
We can use plus and plus-assign operators for two lists.  
```python
a = [3,4]
b = [5,6]
nums = [1,2] + a
nums += b
nums += [7,8,9]

>> [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### 10.1 Struct.  
Struct is a basic complex datatype.  
Struct can have inner fields aka inner variable with name and type.  
Keyword for declaration struct as custom type is a `struct`.  
Struct can be defined by inline syntax or block syntax.  
Block-definition is more useful for big struct or fields type-name.  
Struct constructor uses camel-brackets, instead of no-brackets syntax in definition.  
```golang
#// definition.  linear
struct B bb: int

struct A a:int, b:B, c:string

#// definition. block
struct A
    a: int
    b: B
    c: string

#// constructor and usage
b1 = B{bb:123}
aa = A{a:1, b:b1, c:'abc'}

aa.a += 2
r1 = aa.c
r2 = aa.b.b1
```
Struct fields have default values.
numeric = 0, string = "", bool = false.


### 10.2 Constructor-function `TypeName()`.  
We can use function-like constructor instead of direct set of name:values in the curvy brackets.  
There are two cases of such way.  
1. Magic default constructor. It takes passed arguments in the amount of fields that struct type has, and makes instance using passed args in the same order as struct was defined. We have nothing to do before usage, just define the struct type.  
```golang

struct User
    name: string
    age: int

user = User('Olgerd', 25)
print(user.name)

>> Olgerd

```
2. User-defined constructor. It's a regular function with the same name as struct type has. It should return the instance of the struct.  
Usage in code the same as a magic default.  
```golang

struct User
    name: string
    age: int

func User(uname:string, age:float)
    valName = ~"mr.{uname}"
    User{name: valName, age: toint(age)}

user = User('Olgerd', 18 + 3 / 2)
print(user.name, user.age)

>> mr.Olgerd 19

```

### 11.1 Struct method.  

Struct can have methods.  
Method can be declared after declaration of struct type.  
```golang
#// def
struct A a1:int

#// variable after `func` is instance of struct
func a:A plusA1(x:int)
    a.a1 += x

#// call
aa = A{} # default val of A.a1 is 0
aa.plusA1(5)
```

### 11.2 Struct inheritance. Multiple inheritance is allowed.
```golang
#// parent types
struct Aaaa a1: int, a2: string

func a:Aaaa f1(x:int, y:int)
    a.a1 = x + y

struct Cccc c:int

#// child struct, multiple inheritance
#// parent types in brackets after child type

struct B(Aaaa, Cccc) b:int

b1 = B{b:1, a1:12, a2:'aa-2'}
#// call A-struct method from B-instance
b1.f1(3, 4)
# access to A-field from B-instance
b1.a1 += 10
```


### 12.1 List features: slice, iteration generator, `tolist()`.
```python
# Slice
# syntax: [firstIndex : IdexAfterLast]
nums = [1,2,3,4,5]
sliced = nums[2:4]

# Iteration generator is a simple sequence of integers.
# syntax: [startVal .. endVal]
nums = [1..5] # -->> [1,2,3,4,5]

# tolist() - explicit cast to list of other sequences 
# or generators (comprehantion, string)
nums = tolist([1..5])

# Slice following by sequence expression:

# list slice
sliced = [1,2,3,4,5][2:4]

# Iter-gen + slice with explicit convertion to list
sliced = tolist(nums)[2:4]

# iter-get slice
sliced = [1..100][3:10]

# Sequence-gen slice
sliced = [x ; x <- src][2:5]
```

### 12.2 List comprehension / sequence generator
Sequence generator (aka list comprehansion) is a shortened syntax (sugar) for making lists by another list or any sourec of sequence.  
Basic syntax:  
```python
[elem; src-expr ;...]
```
Expressions in the generator is divided by `;`.   
Generator has such segments / expressions:  
Second expression is a loop-iterator with arrow-assignment like `for` statement.  
```python
for x <- src
    ...
# the same as
[...; x <- src]
```
First expression is an element of result.  
```python
res = []
for x <- src
    res <- x

# the same as
res = [x; x <- src]
```
Generator can have more expressions:
```python
[  
    elem-expr;       # 1) result element expression ;  
    assign-expr;     # 2) read element and assign to local var;  
    additional-expr; # 3) additional expression with assignment;  
    condition-expr  # 4) filtering condition (aka guard)
]  
# 2-4 is a generator-block.  
# 3-4 are optional  
```
Generator should contain at least 2 segments:  
```python
[n; n <- values]
```
Full syntax of 1 iterator:
```python
src = [1..5]
[   n + s;          # resulting element
    s <- src;       # reading source and assignment to local var
    n = s * 100;    # additional (intermidiate) expression
    s % 2 == 0      # filtering condition
]
>> [101, 303, 505]
```
Generator can have sub-iterations, ie 2-4 is a repeatable part, like:
```python
arr1, arr2, arr3 # source lists
[aa + bb + c ; 
    a <- arr1; aa = a * 2; a > 5; 
    b <- arr2; bb = b * b; 
    c <- arr3; c < 10 ]
```
Next gen-blocks can use values from previous.
```python
[x ; a <- [1..3] ; b <- [10,20]; c <-[400, 500]; 
    x = a + b + c; x % 7 == 0]
>> [511, 413]
```
Result-expr can see all values from all gen-blocks.

```python
# simple
n1 = [x ** 2 ; x <- [1..10]]

# with condition guard
[x ** 2 ; x <- [1..10]; x % 2 > 0]

# several iterators
n2 = [[x, y] ; x <- [5..7]; y <- [1..3]]

# sub-expression (make local var `y`)
n3 = [(x, y) ; x <- [1..10]; y = x ** 2; y < 50]

# flatten sub-lists
# make list of lists
src = [[x, y] ; x <- [5..7]; y <- [1..3]]
# src: [[5, 1], [5, 2], [5, 3], [6, 1], [6, 2], [6, 3], [7, 1], [7, 2], [7, 3]]

# flatten source, make plane list
nums = [ x ; sub <- src ; x <- sub]
```
Too long expression can be formatted into multiple lines.
```python
# generator: multi-expressions, multiline expression
nums = [
    {x:a, y:b, z:c}; # element of result
    # 1)
    x <- [3..7]; # 1-st iterator
    a = x * 10; # sub-expression
    x % 2 > 0; # condition of 1-st part
    # 2)
    y <- [1..10]; # 2-nd iterator
    b = 2 ** y;
    y <= 5;
    # 3)
    z <- [1..3]; # 3-rd iterator
    c = 10 ** z;
    a + b + c < 1000
]
```
Now strings are not a valid native source for comprehansions. But it can be resolve by `tolist()` function.
```python
# list comprehension by converted string
src = "ABCdef123"
res = [s+'|'+s ; s <- tolist(src); !(s ?> '123')]
```

Here just syntax joke :)  
But it works, it returns list of lambdas which return generators.  
```python
[ x -> [x .. y] ; y <- [1 .. 10]]
```

### 13. Multiline expressions: `if`, `for`, math expr.  
Normally code lines in LP are short enough, but in some cases we need longer expressions, even in control statements.  
The main way to split long line to shorten parts is use brackets.
For comprehantion expressions it works with its square brackets (see examples).  
For function call, `if`, `for` or math expressions we can use round brackets as usual.  
Indents in multiline case makes code more readable.
```python
# func
val = foo(a,
    'b b b b b b b b b', bar(c) )

# if
if ( cond1
    && cond2
    && cond3)
    expr...

# for loop
for ( n <-
    [y; x <- [1..5];
        y = x * 100 - x])
    result <- n

# math
res = ( (a + b) * 15
    - c * d + a ** 5
    + e / 111)
```

### 14. Builtin functions:  
Include native (python) function as an builtin function.  
It needs some preparation of data and returning results.  
```python
# common way to add function by imported `setNativeFunc`

setNativeFunc(context, 'func_name', python_function, ResultType)
```
Example:  
```python
from nodes.func_expr import setNativeFunc

setNativeFunc(ctx, 'print', buit_print, TypeNull)
```
Update for function objects, lambdas.  
Builtin funcs was changed for call functions passed as an argument (lambdas, atc) inside python function: added 1-st arg - Context.
```python
# if builtin func receives function / lambda, 
# context is needed

def built_foldl(ctx:Context, start, elems, fun:Function):
    r = start
    elems = built_list(0, elems).rawVals()
    for n in elems:
        fun.setArgVals([r, n])
        fun.do(ctx)
        r = fun.get()
    return r
```
```python
# if context not needed just use `_`
def built_somefunc(_, args)
    ...
```

Actual builtin funcs:  
`print`, `iter`, `type`, `tolist`, `toint`  
list: `len`, `foldl`,  
strings: `join(srcList, delim)`, `split(src, sep)`, `replace(src, old, new)`  

TODO: int2char, [int] to string, char_code  

### 15. Lambda functions and high-order functions. Right-arrow `->`.
Right-arrow is an operator for definition lambda-function.  
Arrow separates arguments and body of function.  

```python
# one-arg lambda
x -> x * 10

# several args
(x, y, z) -> (x + y) * z

# high order func: func which can accept or return another 
# (maybe lambda) function

# high-order func (will use lambdas)
func foo(ff, arg)
    ff(arg * 2)

# lambda arg as var
f1 = x -> x * 3
n1 = foo(f1, 5)

# lambda as a local expression in argument
n2 = foo( x -> 2 ** x , 5)
```
We can put inline-block in brackets and use as a lambdas body.  
```python
ff = x -> (a = 100; b = x * 10; a + (b * x))
r = ff(3)
>> 190
```
The same as a multiline expression.  
```python
ff = x -> (
    a = 100; # can use comments here
    b = x * 10; 
    a + (b * x))
```

See more about function-as-object in section 23.  

### 16. match-statement.  
`match` keyword  
`!-` case-operator  
Each case starts a new block.
Case-block can be in the same line (not for control statements).  
Now:  
Just simple case with value-equal has been implemented  
Control statements (`if`, `for`, `match`, `while` ) should be started in next line (with indent).
```python
# value|template !- expressions
# _ !- expr # default case

a, b, r1 = 4, 3, 0

match a
    1  !- r1 = 100 # one-line case block
    10 !- r1 = 200
    b  !- b = a * 1000
        r1 = [a, b]
    20 !-
        if a > b
            r1 = 5
    _  !- r1 = -2
```
TODO: types, struct (type, fields, constructor), collections (size, some vals), sub-condition, Maybe-cases


### 17. multi-assignment
```python
# simple vals
a,b,c = 1,"2",3.5

# unpack tuple
a, b, c = (1, 2, 3)

# unpack list
a, b, c = [1,2,3]
```

### 18. Ternary operator `?:`
classic ternary oper `condition ? valIfTrue : elseVal`  
```python
x = a < b ? 10 : 20
```
shortened case. null-or:  `val1 ?: va2 `  
returns val1 if not null (zero num, empty string, list or tuple); otherwize returns val2  
```python
x = val1 ?: va2
```

### 19. Val-in `?>` and val-not-in `!?>` operators.  
Boolean operators for check value or key in collection.  
`a ?> vals` : If collection `vals` contains value `a`  
```python
# base usage 
val ?> collection

# val for list|tuple
if val ?> [1,2,3] ...
if val ?> ('a', 'b', 'c') ...

# key for dict
if 'a' ?> {'a':1, 'b':2} ...
```
If collection doesn't have value `!?>`  
`val !?> collection`
```python
!(val ?> nums)

# the same as

val !?> nums
```
Examples:
```python
if 5 !?> [1,2,3] ... # True
if 'c' !?> {'a':1, 'b':2} ...
```

### 20. One-line block `;` `/:` operators
Shortened syntax for those who like long lines and hate tall columns :)  
```python
a = 1; b = 2; c = 3
a = 10 + a; b += 20; c -= 30;
res = [a, b, c]; res <- dd; res <- e
```
`/:` operator.  
One-line control expressions are possible.  
`if`
```python
if x < 10 /: print(x)
```
`for`
```python
for i <- names /: print(name)
```
Complex examples.  
```python
# multiexpression over `;`
res = []
for i <- [1..5] /: x = i * 10; y = i + 100; res <- (x + y) 
```
Every next inline sub after `/:` is childe of previous block.  
So here no way for several inline sub-blocks like if-else.  
```python
# `if` in `for`
for i <- [1..10] /: if i % 2 != 0 /: print(i)

# the same:
for i <- [1..10]
    if i % 2 != 0
        print(i)

```
But you can use parenthesis.  
```python
for i <- [1..10] /: (if i % 2 != 0 /: print('odd', i)) ; (if i %2 == 0 /: print('even', i))
```


### 21. String formatting  
There are two syntax implementations.  
1) `%` - formatting with binary operator `<<`.  
It's classic `%s`-formatting. Uses native `%` operator inside with %-formatting syntax of native language (python here).
```python
'hello int:%d, float:%f, str:%s ' << (123, 12.5, 'Lalang')
```

2) `~`strings / var-embedding syntax.  
Uses `~` unary operator before string and stringify expressions into `{}` brackets (includes).  
Includes can be simple var-name, or be more complex expression with template-modifier over `:`.  
Any expression returning stringify value is allowed: `var`, `struct.field`, `list`/`dict` element, `function` call.  
Be accurate with `"'``quotes``'"` inside includes.  
```python
a, b, s = (123, 12.5, 'ABC')
name = 'Bob'

# simple tpl
hey = ~' Hello {name}!'

# with {val:patterns}
hello1 = ~'hello int:{a:05d}, float:{b:.3f}, str: `{s2:<5s}`.'

# with function call
func fHello(s)
    'hello, ' + s

~'Some prefix, {fHello(`Formatter`)} '
```
See more examples in `tests/test_format.py`.

### 22. Import modules.  
We can use things from another module by using `import` command.  
Module is a file. Module name is a filename withot extension.  
So file `test.et` contains module `test`  
File `lib/util.et` contains module `lib.util`  
Cases of import:  
- Import module (file) or submodule in folder 
(over dots: `dir.subdir.file` ).
- Import all things from module, or named things.
- Alias for named things.

Pure import, just module name
```python
import mymodule
mymodule.foo()
inst = mymodule.MyType{a:1}
inst.bar()
```
Import names from module after `>` over comma.  
`module > name, name2`
```python
import mymodule > foo, bar, MyType
foo(123)
bar(321)
mt = MyType{a:1, b:2}
```
Import all things from module `> *`  
```python
# function `foo` in mymodule

import mymodule > *
foo(123)
```
Import with aliases.  
`module > orig_name alias, ..`
```python
import mymodule > foo f1, bar f2
f1(123)
f2(321)
```
### 22.1 Module preload. 
`import` command looks for modules in the execution root context. So we have to preload modues into context before run code with imports.  
For `run.py` util we have 2 options how to preload modules.  
1) Module can be imported by console arg `-i` or `--import`.  
    Modules will be preloaded into root context and `import` lines will be added to the head of code. Actual for `run -c` mode.  
```console
$ py -m run -i "module1; module2..." -c "code"
```
Example:  
File to import: `./tests/tdata/st1.et`  
```console
$ py -m run \
    -i "tests.tdata.st1 > Point2, f1" \
    -c "pp = Point2{x:2, y:3}; p = f1(pp.sum())" -r p \
>> [5, 10, 15]
```

2) Auto-import modules from file-tree for CI `run file`.  
For case with the the source file (if contains `import`), importing modules will be preloaded before execution of script automatically.  
Root path is taken from current console position.  
```console
$ py -m run tests/tmods.et
test-import1: 12
test-import2: st=B 17
```
Pathroot.  
We can use custom root path for impoting.  
Arg for pathroot: `-p` `--pathroot`. Useful for run script from any location.  
```console
$ py -m run -p "tests" \
    -i "tdata.st1 > Point2, f1"  \
    -c "pp = Point2{x:2, y:3}; a = pp.sum(); tt = (f1(a))" \
    -r tt
```

### 23. Function as an object. 
We can use a function not only as a predefined name for call, but also as a value, place it in collections, take it from an expression, and use.  
Typical cases:  
- functions in list
```golang
func foo()
    ...
func bar(arg)
    ...
func sum(a, b)
    ...
ffs = [foo, bar, sum]

# call them
ffs[0]()
ffs[1]('arg-val')
```
- function in dict
```golang
ffd = dict
    'f' : foo,
    's' : sum

ffd['f']()
```
- lambdas in collection
```golang
x2 = x -> x * 2
ffs = [x2, x -> 5000 + x]

ffs[0](11)
ffs[-1](11)

ffd = {'f' : ((a) -> a * 11)}

ffd['f'](2)
```
- lambda in parentheses with immediate call
```golang
res = (x -> x + 10)(5)
```
- Also we can call function which has been returned from another function.
```golang
func foo3()
    x -> x * 100

res = foo()(3)
```
- Use passed argument in lambda.
```golang
func foo4(n)
    x -> x * n + 1000 

res = foo4(5)(111)
```
- Call passed lambda in returning lambda.
```golang
func foo5(f)
    x -> f(x) + 5000 

res = foo5(y -> y * 3)(33)
```
### 24. Closures.  
Lambdas can use things defined in the function where lambda was defined,  
including another lambdas passed into parent function.
```golang
func getLamb(n, ff)
    funVar = 100 + n
    
    func bar(x, y)
        x + 10000 * y
    
    x -> ff(x) + bar(n, funVar)

lamb = getLamb(3, a -> a * 5)

res = lamb(2)
>> 1030013
```
Experimental:  
If def of function f1 was last expression in another function f2 than f1 will be a result of f2.  
```golang
func getFuu(n)
    func mult(x)
        x * n

f3 = getFuu(11)
res = f3(4) # here `mult` is called
>> 44
```


--------------------------------------------------------
--------------------------------------------------------
--------------------------------------------------------

Drafts and thoughts:

*.et, *.etml - file extension
etml - possible extension of html/xml template.

*

Possible exension (thoughts):
01. functions can be overloaded by types (maybe)
02. operators are functions, exception: brackets () [] {}, maybe.
10. mapping and pattern matching
11. functions doesn't needs braces like haskell (for what?)
12. functional elements: lambdas(done!), composition, carrying.
13. interface as list of functions (thinking)
14. functions with ducktype args based on interfaces

```
u = user{"vasya", 16, 1.5}

rx = \[a-z-_]{2,5}\i
text = "Hello somebody here! 123"
res = rx.find(text)


// one line
for n <- 0..5 => print "next: %d" << n
if res = rx.match(text); !res.empty() => print " result: %s" << res.first()

```
*
#TODO:
Convert / rewrite code to Go, Java, Rust.  
Looks like its not a simplest task ))

