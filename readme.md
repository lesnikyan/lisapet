
# LISAPET
Linear Interpreter of Scripting And Processing Expression Tree.  
(LP, this code, miniscript)

ico: Fox pet on the bicycle

It was started as a simple and small scripting language.  
(Not so small already [facepalm]).  
Interpreter builds executable object, actually - tree of actions (expressions).  
Than this object can be executed with some data.  
Executable tree uses context-object (map/dict of data values with nested contexts).  

*
Content:  
- [Status](#status)
- [Syntax](#syntax)
1. [Basic things: vars, vals](#1-vars-vals-lists-assignment-context-of-vars)
2. [Basic types](#2-numbers-strings-bool-types)
3. [Block. If-statement](#3-sub-block-of-expressions-if)
4. [Math and other operators](#4-math-operators-unary-operators)
5. [Collections `[1,2]`, `{'b':2}`, `(1, 2, 3)`](#5-collections-list-array-tuple-dict-map)
6. [For-statement: `for i <- [1..5]`](#6-for-statement---operator)
7. [Functions:`func foo()`](#7-function-definition-context-of-functions)
8. [Dicts](#8-dict-linear-and-block-constructor)
9. 
    1. [Collection: append `nums <- 15`](#91-arrow-appendset-operator--)
    2. [Collection: minus `- [key]`](#92-minus-key---key-delete-operator)
10. [Struct: definition, constructor](#10-struct)
11. [Struct: methods](#111-struct-method)
12. List:
    1. [Slice, iteration generator: `[ : ]`, `[ .. ]`](#121-list-features-slice-iteration-generator-tolist)
    1. [Sequence generator `[ ; ; ]`](#122-list-comprehension--sequence-generator)
13. [Multiline esxpressions](#13-multiline-expressions-if-for-math-expr)
14. [Builtin/native functions (print, iter,..)](#14-builtin-functions)
15. [Lambdas and high-order functions `x -> x ** 2`](#15-lambda-functions-and-high-order-functions-right-arrow--)
16. [Match-statement](#16-match-statement)
17. [Multi-assignment `a, b = c, d`](#17-multi-assignment)
18. [Ternary `?:` operator](#18-ternary-operator-)
19. [In `?>`, not in `!?>` operators](#19-bool-operator-val-in--and-val-not-in--operators)
20. [Inline block `a=1; b=2`](#20-one-line-blocks-expr-expr-expr)
21. [String formatting `<<`, `~" "` operators](#21-string-formatting)
22. [Import modules](#22-import-modules)
23. [Function as object](#23-function-as-an-object)
24. [Closures](#24-closures)

*
## Status.
Actually it is on-dev. Most basic features and needed things is done.  
Details see next, in `syntax` section.  

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
```
# run file
python -m run tests/simple_test.et
...

# run code line
python -m run -c "a = 2; b = a + 1"

# with print
python -m run -c "r = [1..5]; print('nums:', tolist(r))"
nums: [1, 2, 3, 4, 5]
...

# more complex 1-line example:
python -m run -c "f1 = (x, y) -> x + y; f2 = x -> x * x;  p = x -> print(x); [p(f1(f2(n), 10000)); n <- [1..10]; n % 2 > 0 && n > 3]"
10025
10049
10081

# print result
py -m run -c "res = 100 + 23" -r res
>> 123

# multirun - build once and run multiple times by dataset
# json as a data source
# data: [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}]
py -m run -c "n = a + b; print(':', a, b, n)" -l -j "[{\"a\":1, \"b\":2}, {\"a\":3, \"b\":4}, {\"a\":5, \"b\":6}]" -r n
: 1 2 3
: 3 4 7
: 5 6 11
>> 11

```
See code of run.py, build.py, eval.py for understanding how to use LISAPET as an imbedded engine, add custom python functions for using in LP code, etc.  

## Syntax.

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
```
x = 1
name = 'Ramzes II'
names = ['Alya', 'Valya', 'Olya']
lastName = names[2]

# multiple assignment
a, b, c = 10, 20, 30
```

### 2. Numbers, strings, bool. Types.
```
hello = "hello somebody!"
'unary-quotes'
'''multiline
string'''

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
```
res = 100
if x >= 10 | x < 2 && x != 0
    res = 2000 + x * -10 - 700
else
    x = x ** 2
    res = 1000 + x - 500
```

```
# if with sub-expressions: if sub-expr; condition ...
if a = foo(); x < bar(a)
    ...
```

```
# some sugar: else-if
if cond
    code
else if cond
    code
else
    code
```

### 4. Math operators, unary operators
```
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
```
x = 1
x += 2
```
Bitwise:   
`&` `|` `^` `<<` `>>` `~`
Compare:  
`==` `!=` `>` `<` `>=` `<` `<=`
Logical:
`&&` `||` `!` 
Other:  
`?>` `!?>` `?:` `<-` `->` `!-`



### 5. Collections: list (array), tuple, dict (map)
```
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
```
nums = [1,2,3,4,5]
print(nums[-2])
>> 4
```
Tuples: `(val, val, val)`.  

Tuple. Few values in the brackets over comma.  
Tuple is immutable.
```
vals = (1, 100, 'More numbers')

# read value by index
print(vals[2])
```
Unpack values from list or tuple.
```
names = ['Anatol', 'Basilev', 'Cardamon']
n1, n2, n3 = names

vals = (1, 22, 33,3)
a, b, c = vals
```

### 6. `for` statement, `<-` operator
- Range-iterator
```
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
```
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
```
# One arg iter(last+1)
iter(3) # >> 0,1,2

# more args iter(start, last+1 [, step])
iter(1, 5) # >> 1,2,3,4

iter(1,7,2) # >> 1,3,5

```

Keywords `continue`, `break`.  

```
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
```
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
```
callIndex = 0

func foo(x, y)
    res = [x, y, callIndex]
    callIndex += 1
    res

```
See more about functions in sections: 14, 15, 23.

### 8. Dict. Linear and block constructor
```
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
```
# list:
nn = []
nn <- 12

# dict:
# 

dd = {'b': 444}
dd <- ('a', 123)
dd <- ('b', 555)

>> {'b': 555, 'a': 123}
```
```
dict <- (key, val) 
# the same as 
dict[key] = val
```
For dicts we can set multiple pairs of key-value by the dict in the right operand: `dict <- dict`
```
res = {'a':11, 'b':22} # new dict

res <- {'c': 44, 'b':33} # add / update vals

>> {'a':11, 'b':33, 'c': 44}
```

### 9.2 Minus key `- [key]` (delete) operator
Minus operator for collections.  
Operator removes element by index | key and returns value of element.  
For list:
```
a1 = [1,2,3]
r1 = a1 - [1] # returns 2
>> [1,3]
```
For dict:
```
d2 = {'a':11, 'b':22}
r2 = d2 - ['a'] # returns 11
>> {'b': 22}
```

### 10. Struct.  
Struct is a basic complex datatype.  
Struct can have inner fields aka inner variable with name and type.  
Keyword for declaration struct as custom type is a `struct`.  
Struct can be defined by inline syntax or block syntax.  
Block-definition is more useful for big struct or fields type-name.  
Struct constructor uses camel-brackets, instead of no-brackets syntax in definition.  
```
# definition.  linear
struct B bb: int

struct A a:int, b:B, c:string

# definition. block
struct A
    a: int
    b: B
    c: string

# constructor and usage
b1 = B{bb:123}
aa = A{a:1, b:b1, c:'abc'}

aa.a += 2
r1 = aa.c
r2 = aa.b.b1
```
Struct fields have default values.
numeric = 0, string = "", bool = false.

### 11.1 Struct method.  

Struct can have methods.  
Method can be declared after declaration of struct type.  
```
# def
struct A a1:int

# variable after `func` is instance of struct
func a:A plusA1(x:int)
    a.a1 += x

# call
aa = A{} # default val of A.a1 is 0
aa.plusA1(5)
```

### 11.2 Struct inheritance. Multiple inheritance is allowed.
```
# parent types
struct Aaaa a1: int, a2: string

func a:Aaaa f1(x:int, y:int)
    a.a1 = x + y

struct Cccc c:int

# child struct, multiple inheritance
# parent types in brackets after child type

struct B(Aaaa, Cccc) b:int

b1 = B{b:1, a1:12, a2:'aa-2'}
# call A-struct method from B-instance
b1.f1(3, 4)
# access to A-field from B-instance
b1.a1 += 10
```

### 12.1 List features: slice, iteration generator, `tolist()`.
```
# Slice
# syntax: [firstIndex : IdexAfterLast]
nums = [1,2,3,4,5]
sliced = nums[2:4]

# Iteration generator is a simple sequence of integers.
# syntax: [startVal .. endVal]
nums = [1..5] # -->> [1,2,3,4,5]

# tolist() - explicit cast to list of other sequences or generators (comprehantion, string)
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
```
[elem; src-expr ;...]
```
Expressions in the generator is divided by `;`.   
Generator has such segments / expressions:  
Second expression is a loop-iterator with arrow-assignment like `for` statement.  
```
for x <- src
    ...
# the same as
[...; x <- src]
```
First expression is an element of result.  
```
res = []
for x <- src
    res <- x

# the same as
res = [x; x <- src]
```
Generator can have more expressions:
```
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
```
[n; n <- values]
```
Full syntax of 1 iterator:
```
src = [1..5]
[   n + s;          # resulting element
    s <- src;       # reading source and assignment to local var
    n = s * 100;    # additional (intermidiate) expression
    s % 2 == 0      # filtering condition
]
>> [101, 303, 505]
```
Generator can have sub-iterations, ie 2-4 is a repeatable part, like:
```
arr1, arr2, arr3 # source lists
[aa + bb + c ; 
    a <- arr1; aa = a * 2; a > 5; 
    b <- arr2; bb = b * b; 
    c <- arr3; c < 10 ]
```
Next gen-blocks can use values from previous.
```
[x ; a <- [1..3] ; b <- [10,20]; c <-[400, 500]; 
    x = a + b + c; x % 7 == 0]
>> [511, 413]
```
Result-expr can see all values from all gen-blocks.

```
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
```
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
```
# list comprehension by converted string
src = "ABCdef123"
res = [s+'|'+s ; s <- tolist(src); !(s ?> '123')]
```

### 13. Multiline expressions: `if`, `for`, math expr.  
Normally code lines in LP are short enough, but in some cases we need longer expressions, even in control statements.
The main way to split long line to shorten parts is use brackets.
For comprehantion expressions it works with its square brackets (see examples).
For function call, `if`, `for` or math expressions we can use round brackets as usual.
```
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
Include python function as an builtin function.  
It needs some preparation of data and returning results.  
```
# commot way to add function
setNativeFunc(context, 'func_name', python_function, ResultType)

# example:
setNativeFunc(ctx, 'print', buit_print, TypeNull)
```
Builtin funcs was changed for call functions passed as argument (lambdas, atc) inside python function: added 1-st arg - Context.
```
# if builtin func receives function / lambda, 
# context is needed

def built_foldl(ctx:Context, start, elems, fun:Function):
    ...
        ...
        fun.do(ctx)
    ...

# if context not needed just use `_`
def built_somefunc(_, args)
    ...
```

Actual builtin funcs:  
`print`, `len`, `iter`, `type`, `toint`,  
`tolist`, `foldl`, `join`  
TODO: split, int2char, [int] to string, char_code

### 15. Lambda functions and high-order functions. Right-arrow `->`.
Right-arrow is an operator for define lambda-function.  
Arrow separates arguments and body of function.  

```
# one-arg lambda
x -> x * 10

# several args
(x, y, z) -> (x + y) * z

# high order func: func which can accept or return another (maybe lambda) function

# high-order func (will use lambdas)
func foo(ff, arg)
    ff(arg * 2)

# lambda arg as var
f1 = x -> x * 3
n1 = foo(f1, 5)

# lambda arg as local val / arg
n2 = foo( x -> 2 ** x , 5)
```
We can put inline-block in brackets and use as a lambdas body.  
```
ff = x -> (a = 100; b = x * 10; a + (b * x))
r = ff(3)
>> 190
```
The same as a multiline expression.  
```
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
```
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
```
# simple vals
a,b,c = 1,"2",3.5

# unpack tuple
a, b, c = (1, 2, 3)

# unpack list
a, b, c = [1,2,3]
```

### 18. Ternary operator `?:`. 
classic ternary oper `condition ? valIfTrue : elseVal`  
```
x = a < b ? 10 : 20

```
shortened case. null-or:  `val1 ?: va2 `  
returns val1 if not null (zero num, empty string, list or tuple); otherwize returns val2  
```
x = val1 ?: va2
```

### 19. Bool operator val-in `?>` and val-not-in `!?>` operators.  

`a ?> vals` : If collection `vals` contains value `a`  
```
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
```
!(val ?> nums)

# the same as

val !?> nums
```
Examples:
```
if 5 !?> [1,2,3] ... # True
if 'c' !?> {'a':1, 'b':2} ...
```

### 20. one-line blocks (expr; expr; expr)
Shortened syntax for those who like long lines and hates tall columns :)  
```
a = 1; b = 2; c = 3
a = 10 + a; b += 20; c -= 30;
res = [a, b, c]; res <- dd; res <- e
```

### 21. String formatting  
There are two syntax implementations.  
1) `%` - formatting with binary operator `<<`.  
It's classic `%s`-formatting. Uses native `%` operator inside with %-formatting syntax of native language (python here).
```
'hello int:%d, float:%f, str:%s ' << (123, 12.5, 'Lalang')
```

2) `~`strings / var-embedding syntax.  
Uses `~` unary operator before string and stringify expressions into `{}` brackets (includes).  
Includes can be simple var-name, or be more complex expression with template-modifier over `:`.  
Any expression returning stringify value is allowed: `var`, `struct.field`, `list`/`dict` element, `function` call.  
Be accurate with `"'``quotes``'"` inside includes.  
```
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

Cases:  
- Imports module (file), submodule in folder (over dots: dirname.dirname2.module ).
- Imports all things from module, or named things.
- Aliases usage for named things.
- TODO: auto-import modules from file-tree for CI `run`.

```
# pure import, just module name
import some_module
some_module.foo()
inst = some_module.MyType{a:1}
inst.bar()

# import all 
import some_module.*
some_module.foo(123)

# import names
import some_module > foo, bar, MyType
foo(123)
bar(321)
mt = MyType{a:1, b:2}

# import aliases
import some_module > foo f1, bar f2
f1(123)
f2(321)
```

### 23. Function as an object. 
We can use a function not only as a predefined name, but also as a value, place it in collections, take it from an expression, and call it.  
Typical cases:  
- functions in list
```
func foo()
    ...
func bar(arg)
    ...
func inList(arg)
    ...
func sum(a, b)
    ...

funcs = [foo, bar, inList, sum]

# call them
ffs[0]()
ffs[1]('arg-val')
```
- function in dict
```
ffd = dict
    'f' : foo,
    's' : sum

ffd['f']()
```
- lambdas in collection
```
x2 = x -> x * 2
ffs = [x2, x -> 5000 + x]

ffs[0](11)
ffs[-1](11)

ffd = {'f' : ((a) -> a * 11)}

ffd['f'](2)
```
- lambda in parentheses with immediate call
```
res = (x -> x + 10)(5)
```
- Also we can call function which has been returned from another function.
```
func foo3()
    x -> x * 100

res = foo()(3)
```
- Use passed argument in lambda.
```
func foo4(n)
    x -> x * n + 1000 

res = foo4(5)(111)
```
- Call passed lambda in returning lambda.
```
func foo5(f)
    x -> f(x) + 5000 

res = foo5(y -> y * 3)(33)
```
### 24. `Closures`.  
Lambdas can use things defined in the function where lambda was defined,  
including another lambdas passed into parent function.
```
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
```
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

