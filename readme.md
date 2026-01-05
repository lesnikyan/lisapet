
# LISAPET
Linear Interpreter of Scripting And Processing Expression Tree.  
(LP, this code, miniscript)

ico: Fox pet on the bicycle

LISAPET is an interpretable language like python, written with python, but not a python :)  
It was started as a pet-project (and still is) - simple and small scripting language  (not so small already [facepalm]) for short scripts which could be run for the python project but without direct execution of scripts on the python interpreter (bad and unsafe way).  
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
1. Basic things.
    1. [vars, vals, assignment](#11-vars-vals-lists-assignment)
    2. [Context](#12-execution-context)
    3. [Basic types](#13-numbers-strings-bool-types)
2. [Code blocks and formatting.](#2-sub-blocks-code-formatting)
3. [`if`-statement](#3-if-statement-else)
4. [Operators. Math, bool, unary, others.](#4-operators-math-unary-others)
5. [Collections, short overview `[,]`, `(,)`](#5-collections-list-array-tuple-dict-map)
6. [Dict `{'key':val}`](#6-dict-linear-and-block-constructor)
7. [For-statement: `for i <- [1..5]`](#7-for-statement---operator)
8. Functions:`func foo()`  
    1 [Base info](#8-function-definition-context-of-functions)  
    2 [Default arguments `func foo(x=1)`](#82-default-value-of-arguments)  
    3 [Named arguments `n = foo(x=2)`](#83-named-arguments)  
    4 [Variadik arguments `func foo(args...)`](#84-variadic-arguments)  
    5 [Overload of functions](#85-function-overload)  
9. Collection features:  
    1. [append operator `nums <- 15`](#91-arrow-appendset-operator--)
    2. [deletion operator `data - [key]`](#92-minus-key---key-delete-operator)
    3. [plus for lists `[] + []`](#93-list-plus---)
10. Struct: 
    1. [Definition, constructor `A{f:val}`, fields, `.` operator](#101-struct)
    2. [Callable constructor `A(val)`](#102-constructor-function-typename)
11. Struct, OOP:
    1. [Methods `x.foo()`](#111-struct-method)
    2. [Inheritance `A(B)`](#112-struct-inheritance-multiple-inheritance-is-allowed)
12. List features:
    1. [Slice, iteration generator: `[ : ]`, `[ .. ]`](#121-list-features-slice-iteration-generator-tolist)
    2. [Sequence generator `[ ; ; ]`](#122-list-comprehension--sequence-generator)
13. [Multiline expressions](#13-multiline-expressions-if-for-math-expr)
14. Builtin (native) functions
    1. [Global functions: print, iter, etc.](#141-global-native-functions)
    2. [Bind native function as a method `[1,2].join(',')`](#142-binding-method-for-type)
    3. [Methods are already bound](#143-methods--are-already-bound-to-types)

15. [Lambdas and high-order functions `x -> x ** 2`](#15-lambda-functions-and-high-order-functions-right-arrow--)
16. Match-statement
    1. [Match, cases, `!-`](#16-match-statement)
    2. [List and tuple `[0,x,_,?,*]` `(_,?,*)`](#162-matching-list-and-tuple)
    3. [Dict pattern `{'a':a, _:_, *}`](#163-matching-dict)
    4. [Struct pattern `N{ }`, `_{ }`](#164-matching-struct)
    5. [Multicase `1 | 2`](#165-multicase-)
    6. [Guard with pattern `[a] :? a > 5`](#166-bool-guard-in-case)
    7. [Mixed patterns: `[]|{}`, `[A{},B{}]`](#167-mixed-nested-patterns)
    8. [Regexp case ```re`abc` ```](#168-regexp-case)
    9. [Type pattern `::`](#169-type-matching-_int)
17. [Multi-assignment `a, b = c, d`](#17-multi-assignment)
18. Operators with bool condition.  
    1. [Ternary `?:` operator](#18-ternary-operator-)
    2. [In `?>`, not in `!?>` operators](#19-val-in--and-val-not-in--operators)
    3. [Check type `::`](#183-check-type-operator-)
19. [optimized place :) ]
20. Inline syntax.  
    [Few-expressions block ` ; `](#20-one-line-block---operators)  
    [Controls (`if`, `for`, etc) `/:`](#20-one-line-block---operators)  
21. [String features](#21-string-features)
    1. [insert `"%s" << x`](#211-percent-formatting)
    2. [include `~"{x}"`](#212-format-by-including-expressions)
    3. [base functions](#213-string-functions)
22. [Import modules](#22-import-modules)
23. [Function as object](#23-function-as-an-object)
24. [Closures](#24-closures)
25. Regular expression:
    1. [Base syntax ```re`[abc]`i```](#251-regular-expressions-re)
    2. [match `=~`](#252-regexp-match-)
    3. [find `?~`](#253-regexp-find-)
    4. [Replace by regexp](#254-regexp-replace)
    5. [Split by regexp](#255-regexp-split)

*
## Status.
Actually it is on-dev. Most basic features and needed things is done.  
Details see next, in `syntax` section.  
As an one-hands made project (withous users) all updates are committed into dev and almost immediately merged into main branch, without version numeration.  
Tests covers all changes whenever possible.  
Therefore, critical changes to previously added things happen extremely rarely.  

*
Basic principles.
1. No extra thingth, block is defined by line shifting without endline operator.
2. Basic collections: list, dict, tuple
3. Arithmetic expressions - python-like syntax: (a + 1/2) * b - c ** 2 .
4. Control structs: `if-else`, `match`, `for`, `while`.
5. Functions: value of last expression is a returning result. Explicit `return` works too.  Function is an object. Lambdas `x -> y`.
6. `struct` is a main complex type. struct can have methods. Inheritance works too.
7. Vars, struct fields, func args have type `x : type`, internal `Any` type by default.
8. Import modules or things from modules.
9. Syntax sugar and useful operators is ok. For example: list slice, list generator, `<-`, `?>`, `?:`, `::` operators, multiple assignment, inline syntax of blocks.
10. Native regexp.

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

See code of tests, run.py, loader.py, eval.py for understanding how to use LISAPET as an imbedded engine, add custom python functions for using in LP code, etc.  

## Syntax.
The Syntax section is updated as new features are added to the code, so it looks a bit chaotic.  
Done parts:  

### 0. Comments.
Operators of comment lines:  
`#` inline, up to end of line.  
`#@`(open)  
multiline (sub-line)  
all text between open and close operators.   
`@#`(close)  
```
# one-line comment

#@
multiline comment
@#

x = #@ in-line comment @# 2 + 5
```

### 1.1 Vars, vals, lists, assignment.  
Assigning values ​​to variables.  
In general, we use the `=` operator to assign a value to a new or already defined variable.  

Basic types of values is:  
numeric types (`int`, `float`),  
`bool` (with values: `true`, `false`).  
Sequence and collection types: `string`, `list`, `dict`, `tuple`.  
Complex types such a `struct` and `function`.  
```python
x = 1 # assignment
x = 2 # reassignment
iAmSuperman = false
name1 = 'Ramzes II'
names = [ name1, 'Alya', 'Valya', 'Olya']
lastName = names[2]

# multiple assignment
a, b, c = 10, 20, 30
```
Alternatives see in next sections: [`<-` operator](#6-for-statement---operator).

### 1.2 Execution context.  
In the mechanics of language, each block of code is executed in specific data-context. Execution context is a dictionary-like object that contains all local things (types, vars, functions) including imported modules and parent context.  
Context-object is responsible of search datatypes, variables, functions etc in current execution context.  
So we can use all local things and any things defined in all levels above: module-level - in the function, function- and module- level - in the control sub-level (for, if, match), and so on.  
See more about visibility of things in sections of functions, closures, structs, importing.  

### 1.3 Numbers, strings, bool. Types.
1. Numeric types.  
```python
nums = [
    true, # bool
    123, # int, decimal
    0123, # decimal, leading 0 will be irnored 
    0b1111, # int, binary
    0o777, # int octa
    0xfba01, # int hex
    0.15]   # float
```

2. Strings.  
Strings can be defined by several type of quotes.  
```golang
hello = "hello somebody!"
us = 'unary-quotes'
```
Classic escape sequences is work.
```golang
print("Hello there! \n\t Here new line, \\ back-slash and \"Words in quotes.\" ")
```
```
Hello there!
         Here new line, \ back-slash and "Words in quotes."
```
Backticks is an yet one type of quotes, designed to create little more ascetic strings.  
In backticks sequences like `\s` doesn't try to be  interpreted as an escape sequence.  
It's very useful for making strings with slashes, quotes, etc, like regexp needs.  
```golang
s = `\s\w\b\d` #// no errors about incorrect escaping
```
In back quotes most escape sequences don't work.  
(``` \` ``` does)  
```golang
print(`\n\t\'\" `)
```
```
>> \n\t\'\" 
```


Multiline strings.
Triple quotes is a main way to create multiline string.  
Triple backticks work too. Thinking about escape sequences. Now it  just works like other, except warnings of wrong sequences like ``` \w \s ```.  
````golang
'''multiline
string'''
""" yet 
one """
```
and more
in b\acktick\s
```
````
String operators:  
Concatenation: `string + string`  
Get sub element (like list): `string[index]`  
Formatting operators see in [`"%s"<<` ](#211-percent-formatting) and 
[`"~{s}"`](#212-format-by-including-expressions) formatting.


3. Data type.  
Type of variable is defined by `:` operator.  
`varName : typeName`  
This syntax means strict typing of variable (or functions arg)
instead of definition without `:` .  
```python
name:string = "Vasya"
age:int = 25
weight:float = 70

yes:bool = true
no:bool = false
```
Types such as collections, structs, functions, etc will be explaned next sections.

4. Type compatibility.  
Variable defined by `:` operator has strict type.  
It prevents setting of new value with an inappropriate type.  
Compatible types are converted automatically.  
In common case value will be compatible if type of variable is more general, like `float` var and `int` value.  
```python
a:float = 0
a = 12 # 12.0

b:int = 0
b = true # 1
```
The same is correct for field of struct instance and functions agrument.  
For a structures, type of value can be a child of type of variable, but not vice versa.  


### 2. Sub-blocks, code-formatting.
Control structures, data-structures, functions, etc. have inner place with internal lines (expressions), here we call it as an expression block, child or sub-block.  
Sub block is separated by indent with one or more whitespaces related to parent.  
All indents should be equal.  
First indent defines all other indents in the file.  
Base block structures: `if`, `for`, `while`, `match-cases`, `function`.  
Data structures can have block version of definition (`struct`) or constructor (`dict` and `list`).  
Some blocks also can have inline version of syntax (controls, sequence of expressions).  
See more about inline syntax [in next sections](#20-one-line-block---operators).  

### 3. `if`-statement, `else`
`if` statement, comparison operators, bool operators. 

`if` is a basic control operator.  
```python
if condition
    sub-expressions
```
As usual we have `else` - pair operator for `if`.  
```python
if condition
    expr1
else
    expr2
```
`else` can be combined with a sub-`if`:  
```python
else
    if cond
        expr

# the same as
else if cond
    expr
```
Condition can contain any expression which returns bool result:  
bool value: `true`, `false`  
`null`, `0` (means `false` in condition)  
Functions that return appropriate value.  
Classic comparison operators `<` `<=` `>` `>=` `==` `!=`  
Check value operators: `?>` `!?>` `::`  
Logic operators `&&` `||` `!`  

```python
if x >= 10 | x < 2 && x != 0
    res = x * 10
else
    y = x ** 2
    res = 10 * y
```
`if` statement can have sub-expression before condition.  
Usually it uses for local assignment or initialization that have relation to condition expression only (and maybe to sub-block).  
Subexpression should be separated by semicolon `;`  
Last of sub-expressions is taken as a condition.  
```python
# if with sub-expressions: if sub-expr; condition ...
if a = foo(); x < bar(a)
    ...
```
Note.
Inline operator `/:` has less priority than `;` so we have to cover whole `if` expression by parentheses in the case with inline `if`-block.  
```python
a = 10; b = 2; (if x = a + 1; x > b /: print(a, b, x))
```
See more about [inline control expressions](#20-one-line-block---operators).  

### 4. Operators: math, unary, others.
1. Arithmetic operators `+` `-` `*` `/` works as usual.  
`%` - mod operator, returns remainder of division.  
`**` - pow operator. `2 ** 3` = 8.
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
2. Other unary operators.  
`!` logical NOT  
`~` bitwise NOT (overloaded for the string as a formatting operator)  

3. Operators with assignment   
`+=` `-=` `*=` `/=` `%=` 
```python
x = 1
x += 2
```
4. Classic c-like operators.   
Bitwise:  
`&` `|` `^` `<<` `>>` `~`  
`<<` overloaded for the string too.  
Comparison:  
`==` `!=` `>` `<` `>=` `<` `<=`  
Logical:  
`&&` `||` `!`  

5. Others, have specific behaviour, and will be explained further:  
`?>` `!?>` `?:` `<-` `->` `!-` `:?` `/:` `::` `=~` `?~`

More details in   
[Bool expressions `?:` `?>` `!?>`](#181-ternary-operator-) , 
[one-line `;` `/:`](#20-one-line-block---operators),   
[append `<-`](#91-arrow-appendset-operator--), 
[`for` `<-` ](#7-for-statement---operator), 
[lambda `->`](#15-lambda-functions-and-high-order-functions-right-arrow--),  
[`match` `!-` `:?` `::`](#16-match-statement),  
[regexp `=~` `?~` ](#252-regexp-match-)
[type check `::`](#183-check-type-operator-)

Table of priority order:
```
() [] {} 
. 
-x !x ~x 
** 
* / % 
+ - 
<< >> 
=~ ?~ /~
< <= > >= !> ?> !?>
::
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
/:
; 
:?
!-
```

### 5. Collections: list (array), tuple, dict (map)
1. List, linear constructor.  
```python

nums = ['One', 'Two', 'Three']
```

List, block constructor (for long elements)
```python
names = list
    'Anna'
    'Barbi'
    'Cindy'
    'Muxtar'
```
Elements of lists.
```python
# set / change element
names[3] = 'Vaxtang'

# read value of element
firstName = names[0]
```
Negative indexes are allowed.  
It accesses to the element by position from the end of list.  
`[-1]` is a last element (1-st from the end).  
```python
nums = [1,2,3,4,5]
print(nums[-2])
>> 4
```

2. Tuples: `(val, val, val)`.  

Tuple. Few values in the parenthesis over comma.  
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

### 6. Dict. Linear and block constructor
```python
# linear constr
dd = {'a':1, 'b':2}

# block constr
ddd = dict
    'a': 'a a a a a a a a a a a a a a a a a'
    'b': 'b b b b b b b b b b b b b b b b b'

# set val by key
dd['c'] = 3
```
```python
# read
u = {'name':'Vasya', 'age':22, weight:60.0}
print('User name:', u['name'])

>> User name: Vasya
```
More feature of collections:
[`<-` operator](#91-arrow-appendset-operator--),
[`list - [key]`](#92-minus-key---key-delete-operator),
[`[]+[]`](#93-list-plus---).


### 7. `for` statement, `<-` operator
1. Range-iterator. It works like classic C-like `for`.  
`for` {init-expression} `;` {condition-check} `;` {post-iteration expression}
```python
for i=0; i < 5; i += 1
    y = y + 2
    for j=-3; j <= 0; j += 1
        a = a - j ** 2
        if a % 2 == 0
            b = b + 1
res = y
```

2. Iterator, arrow-assign operator `<-`  
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
3. Function `iter()`  
```python
# One arg iter(last+1)
iter(3) # >> 0,1,2

# more args iter(start, last+1 [, step])
iter(1, 5) # >> 1,2,3,4

iter(1,7,2) # >> 1,3,5

```

4. Keywords `continue`, `break`.  

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

### 8. Function definition, context of functions.

1. Keyword `func`.  
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

```
2. Definition context.  
Function can use nearest declaration context (actually all top-level things in module where func was declared).
```python
callIndex = 0

func foo(x, y)
    res = [x, y, callIndex]
    callIndex += 1
    res
```
3. Argument type.  
By default arguments have most general type `any`.  
But we can specify more strict type.  
According to type compatibility, we can pass value with more strict type to argument with wider type, like typed vars. 
For example `int` value to `float` argument, or `bool` to `int`.  
```golang

#// arg type (optional)
func bar(a:float, b:float)
    a + b

bar(1.5, 2.8) #// ok
bar(2, 3) #// ok too
bar('a', 'b') #// error
```
### 8.2. Default value of arguments.  
Arguments of functions can have default value.  
Default values is used if function was called without arguments that have default value.  
Default values are possible in the end of arg list in func definition only, they should fill missing args. So it doen't make sense to declare argument without default value after at least one arg with default value.  
```golang

func foo(a:int, b:int=1)
    a * b

foo(3, 4) #// >> 7

foo(5) #// >> 5

```

### 8.3. Named arguments.  
In function call expression named args are allowed.  
Named argument is passed like assignment expression on the argument position in function call, name of argument as a left operand of assignment:  
`foo(name='Bob')`  
If redundant named arg will be passed after the same arg was passed in base order, it will be ignored (now).  
```golang

func foo(a, b)
    a - b

foo(a=1, b=2) #// -1
foo(b=1, a=2) #// 1
foo(a=10, b = foo(3,2)) #// 9
foo(5, 2, a=10) #// 3; 10 is ignored
```

### 8.4 Variadic arguments.  
Variadic arguments is a feature of function that allow pass into function different number of params, but take them in function body as a one list.  
Most used example is a `print()` function from builtins.  
```golang
print(1)
print(1,2,3,4,5)
print('Hello', 'Somebody')
```
In definition of function such argument has special syntax, it's a trple-dots suffix of arg name.  
```golang
func foo(args...)
    for val <- args
        process(val)
```
The main way for usage variadic args is put such argument in definition after necessary arguments in definition and pass as many params in call as we need.  
```golang
func f2(x, y, nn...)
    nn.map(n -> x * y + n)

f2(3, 7, 2) #// [23]
f2(3, 7, 2,3,4,5,6,7,8,9) #// [23, 24, 25, 26, 27, 28, 29, 30]
```
Next, we can use default value in args after variadic arg (in the definition) and pass named args after ordered args in the call.  
```golang
func f4(x, nn..., pref='', post='')
    [~"{pref}{x}{n}{post}" ; n <- nn]

f4('A-', 'a') #// ['A-a']
f4('c=', '1', '2', '3', pref='<', post='>') #// ['<C=1>', '<C=2>', '<C=3>']
```

### 8.5 Function overload.  
C++ like overload means that we can create several functions with the same name but different list of arguments.  

1. Arg count overloading.  
Simples case is overloading function by number of arguments.  

Example:
```golang
func foo()
    0

func foo(x)
    x * 100

func foo(a, b)
    a * b

foo() #// >> 0

foo(3) #// >> 300

foo(2, 6) #// >> 12
```

2. Overload by arg types.  
If overloaded functions have the same number of args, interpreter takes function with such types which was passed in call expression.  
```golang

func foo(x: int, y:int)
    x + y

func foo(x:float, y:float)
    x * y

func foo(s:string, n:int)
    [s ; i <- iter(n)]


foo(2, 3) # // >> 5

foo(2.0, 3.5) # // >> 7.0

foo('hey', 3) # // >> ['hey', 'hey', 'hey']

```
In case if exact arg types wasn't found the function with compatible arg types will be used.  
But if several functions have compatible types interpreter will make error.  

If arguments of one of overloaded cases have type `any` (no type of arg in definition) this case is compatible with any other types, so be accurate to avoid uncertainty.  
```golang
func foo(s:string)
    {'a':s}

func foo(x:int)
    x * 10

func foo(x)
    [x]

foo(1) #//        [1]
foo(1.5) #//      [1.5]
foo('hello') #//  {'a': 'hello'}

#// error because bool is compatible with `int` and `any`
foo(true) #  // Error: More than 1 compatible case found for overload...
```

Warning. Overloading and variadic args (including default vals and named args) are two different approach of function flexibility. So they shouldn't be combine for one name of function. So choose those which more applicable for a specific case.  
The same about functional objects (like lambdas or function in variable).  
Combinations of different approaches wasn't planned, implemented or tested.  


All features: variadic and named args, default vals, overloading (looks like) works for methods too.  

See more about functions in next sections:  
[14 builtins](#14-builtin-functions), 
[15 lambdas](#15-lambda-functions-and-high-order-functions-right-arrow--),
[23 func-object](#23-function-as-an-object), 
[24 closures](#24-closures),  
[11.1 struct methods](#111-struct-method),
[10.2 callable constructor for structs](#102-constructor-function-typename).

## 9 Collections features.  
### 9.1 arrow-append/set operator `<-`
Left-arrow with list or dict in the right operand  puts value into collection.  
(not in `for` statement or sequence generator)  
For list it appends new value; `list <- val`  
For dict it sets or updates value by key from passed tuple with two sub elements  
`dict <- (val, key)`.  
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
Struct have fields (aka inner variable) with name and type.  
Keyword for declaration structs is a `struct`.  
Struct can be defined by inline syntax or block syntax.  
Block-definition is more useful for big structs or fields type-name.  
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
We can use callable constructor instead of direct set of name:values in the curvy brackets.  
There are two cases of such way.  
1. Magic default constructor. It takes passed arguments in the amount of fields that struct type has, and makes instance using passed args in the same order as it was defined in the struct. We have nothing to do before usage, just define the struct type.  
```golang

struct User
    name: string
    age: int

user = User('Olgerd', 25)
print(user.name)

>> Olgerd

```
2. User-defined constructor. It's a regular function with the same name as the struct type. It should return the instance of the struct (remember that last expression in function is a result).  
Usage in code the same as for default callable construct.  
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
3. Constructor of inherited type.  
The default constructor of a child structure has the same arguments as the structure's fields.  
Order of args is the same as fields was defined, from first parent to last child level.  
```golang

struct A a:int
struct B(A) b:float
struct C(B) c:string

c = C(11, 20.05, "Hello!")

#//>> st@C{a: 11, b: 20.05, c: 'Hello!'}
```


### 11.1 Struct method.  

Struct can have methods.  
Method can be declared after declaration of struct type.  
The main attribute of method is a variable typed by struct type, between `func` keyword and name of function:  
`func var:TypeName myMethod({args})`
This variable will be an istance of struct in the body of method.  
```golang
#// definition
struct A a1:int

#// variable after `func` is an instance of struct
func a:A plusA1(x:int)
    a.a1 += x

#// call
aa = A{} #// default val of A.a1 is 0

aa.plusA1(5) #// set aa.a1 to 5
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
#/ access to A-field from B-instance
b1.a1 += 10
```
Same name from multiple parents.  
If several fields from parents have the same name here only first will be taken, in order that was used in the struct definition. 
```golang
struct A a:int
struct B a:string

struct C(A, B) c:list #// C.a is int

struct D(B, A) d:dict #// D.a is string

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
### 14.1 Global native functions
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
`print`, `iter`, `type`,  
list: `len`, `foldl`,  
strings: `join(srcList, delim)`, `split(src, sep)`, `replace(src, old, new)`  
type conversion:  `tolist()`, `toint()`, `tostr()`

TODO: int2char, [int] to string, char_code  

### 14.2 Binding method for type
In case when we want call function like method of base type, like `list` or `string` we can bind function with such type by magic.  
Binding of native functions has been implemented now.  
Special function is useful for binding:  
`bindNativeMethod(ctx:Context, typeName, func, fname, rtype:VType)`  
Binding args:
1) root context
2) type name
3) function for binding
4) name of method
5) returning type (python class)  

Args of bound function:  
1. Context of call (make sense if arg of method is a  function)
2. instance of type (target value/variable)
3. other - args of method  
1 and 2 - is necessary.  

How to:
```python
# native python function
def list_reverse(_, inst:ListVal):
    src = inst.rawVals().copy()
    src.reverse()
    return ListVal(elems=src)
```
```python

# binding method in python code
bindNativeMethod(ctx, 'list', list_reverse, 'reverse', TypeList)
```
Then we can use `reverse` method for `list`-values in LP code:
```python
nums = [1,2,3]
res = nums.reverse() # >> [3,2,1]
```
See `eval.py` for more examples.

### 14.3 Methods  are already bound to types
1. `list`:  
    .map(`function`)  
    .fold(any, `function`)
    .reverse()  
    .join(`string`)  
    .each(`function`)  
2. `tuple`:  
    .map(`function`)  
    .fold(any, `function`)
    .reverse()  
    .each(`function`)  
3. `dict`:  
    .keys()  
    .items()  
4. `string`:  
    .split(`string`|`regexp`)  
    .replace(`string`|`regexr`, `string`)
    .joinn(`list`|`tuple`)  
    .map(`function`)  

Example of usage: 
```python
res = 'Hello dear friend'.split(' ').map(w -> ~"<t>{w}</t>").join('^')
>> '<t>Hello</t>^<t>dear</t>^<t>friend</t>'
```


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

### 16.2 Matching list and tuple.
List or tuple can be matched by special collection-patterns. They look similar to regular collections, but have some special features.  
```python
[?, 12, b, _, *] !- ...
```
In collection patterns we can use several types of sub-expressions. They can be combined.  

1.  Const value in the collection. Pattern matches if element from pattern equals the element of such position in value we check.  
```python
match n
    # list
    [1,2,3] !- expr
    
    # tuple
    (3,4,5) !- expr
```
2. Variable in collection `[a,b]`, `(a,b,c)`, named non-constant element.  
    Var in pattern is matched with any element and will be assigned with the value according to position if pattern will be matched.  
    Assigned var can be used in the sub block of current match-case.  
```python
match n
    [a] !- print(a) # array with 1 element 
        # in case block var `a` will contain value of n[0]
        res = a * 100
    [a,b,c] !- # any array with 3 elements
        #vars a,b,c with values of list elements
        res = a + b + c 
```
3. Wildcard `_` (means - any value), unnamed non-constant element.  
    Wildcard don't assign anything, unlike of var-pattern.  
```python
match n
    [_] !- # any array with 1 element
    [1,_] !- # any arrays with 2 elemnts, and n[0] == 1
    [_,_] !- # any array with 2 elements
    (1,_) !- the same for tuple
```
Combined example:
```python
match n
    (1, _) !- print('tuple with 1')
    (a, b, _) !- sum = a + b
    [a, 22, b, _] !- res = [a, b, a + b]
```

4. `?` - optional element.  
In case when we need match sequence one or more element is not necessary we can use question mark `?` pattern-element.  
Matcher can ignore optional element.  
In common case we can think about optional + non-constant (var, `_`) that it is pattern of min-max optional segment.  
`(a, _, ?,?)` - segment witn 2-4 elements.  
```
nn = [[], [1], [2], [1,2], [1,2,3], [2,4], [5,6,7,8,15], [5,8,15]]

for n in nn
    match n
        [1, ?] !- # match [1], [1,2]
        [?] !- # match [], [2]
        [1,?,3] !- # [1,2,3]
        [?, 4] !- # [2,4]
        [5,?,?,?,a,15] !- # [5,6,7,8,15], [5,8,15]; a = 8
        _ !- 
```
The same applies to cases of a tuple `(a,?,_)`.  
Uncertainty of result with optional subpatterns.  
Optional sub-patterns can work unpredictable with same sub-values of matching data in sequence like `[1, 10, 2, 3, 10]`, matching them as `?` or const. Especially with set of `?`-s before const pattern like `?,?,?,10`.  
Matcher tries to find a const value one-by-one in segment with such length as a whole set of question marks (before it) has + 1, but will take only first one. Then it may cause fail if the value of const pattern will be found in optional segment.  
Keep in mind that `match` is not a full functional query language like regexp, but just simple element-by-element search machine.  

5. Star `*` in list or tuple matches any sub elements with any count from 0 up to size of collection.  
In common case `*` means 'any others' in the and of pattern.  
Or it can be between two const values, meaning 'any but not the same as second one'. Here works the same rule as for `?` subpattern - first matching value (equal to 1-st const pattern after `*`) will close the uncertain subsequence.  
Combinations `*` and any number of `?`-s means the same as just `*`.  
Star as a length-independent subpattern can provoke uncertain behavior near vars or `_` subpattern. Be accurate with it.  
For templates with optional subelements, it is important for predictable behavior to define a relationship between the variable to be assigned and some constant value or collection side (start, end).  
```python

match n
    [1, *] !- # any list starts with 1
    (*, 2) !- # any tuple that ends with 2
    [31, *, 32] !- # list starts with 31 and ends with 32
    [*, 44, *] !- # list has 44

    # list has at least 4 elements,
    # 1-st and two last will be assigned with var `a,b,c`.
    [a, 55, *, b, c] !- ...
    
    # list starts with 60, has at least 3 elements after it, 
    # and the 3rd from the end will be assigned with the var `a`
    [60, *, a,  _, _] !- ...

    [*] !- # any list
    (*) !- # any tuple
```


### 16.3 Matching dict.

Base pattern is similar to regular inline constructor of dict: `{key:val, ...}`.  
Var, value, `_` cases applicable for dicts.  

1. Emplty dict:
```python
{} !- ...
```
2. Dict with 1 element:
```python
match x
    {1:_} !- # numeric key, any val
    {'name':_} !- # string key any val
    {_:100500} !- # any key, but const val
    {k:v} !- # local vars in key and val
    {_:_} !- # wildcard - any key, any val, will never matched here
```

In the key position all `null` instances are equal.  
`0`, `''` and `null` are different cases.  
```python
x = {null:123}
match x
    {0:_} !- ...
    {null:val} !- # will matched
```

3. Dict with many subpatterns. 
Subpatterns are defined like pairs in dict, over comma.  
```python
    !- {'name':nameVal, 'age':25, _:100500, a:b}
    !- {'a':a, 'b':_, c:'ccc'}
```
Var and `_` have the same matching result, so `{k:v}` after `{_:_}` will never matched.  
Order of subpatterns in dict doesn't matter.  
```python
{'a':_, _:b}
# the same as
{_:b, 'a':_}

```
Within one pattern with many parts, subpatterns have priority by predictability of result (const before any, left(key) before right(val)).  
At first pattern looks for keys (left-part of subpattern) with const values, like `{, 'name':_,}`, if failed then tries match sub-cases with const val in right-part `{, _:'Harry',}`.  
If pattern didn't match const cases, it will apply first pattern with key-var or wildcard `{key1:val1}`.  
Notes.   
    Long patterns with right-values `_:'abc'` take more time. Avoid them without necessity.  
    Be accurate using variable for key, because position of key is undefined.  
    It's ok if 1 var key in pattern with constantly defined others.  

4. Star `*`. Means any values with any number of sub-elements including 0.  

In dict pattern `*` star sub-elem matches with all elements that wasn't matched before. 
In general It is used if we need match some elements beyond those previously defined, and with undefined number of those.  
```python
match n
    {'a':b, *}  !- # 'a' key and any more elements
    {_:_, *}    !- # one or more elements
    {*}         !- # empty or any elements == any dict
    _ !-        !- # here any non-dict, because after {*} case
```

5. Question mark `?` as a 'maybe' case.  
Question mark in dict means 1 optional element.  
The position of `?`-elements in the dict doesn't matter. Only number matters.  
So number of q-marks means possible elements from 0 up to number.  
In case {?,?} - 0-2 elements.  
```python
match d
    {?}             !- # empty or 1 key
    {'a':_, ?, ?}   !- # dict has key 'a' and may contain yet 1 or 2
    {_:_, ?, ?}     !- # dict has at least 1 key but not more than 3
    {'b':v, _:_, ?, ?}  !- # dict has from 2 up to 4 keys, one of them is 'b'
    {?,?,?,?}       !- # only dict with 4 keys without 'b'-key will match here, less was matched above
    {?,?,*}         !- # doesn't make sense, because equal to {*}
```

Notes.  
    `*` and `?` doen't make sense for variable in key like `{a:b, ?,?}` because position of key is not predictable.  
    `*` after `?` means the same as a just `*`.  
    For better readability, it makes sense to put `?` or `*` subs in the end of pattern.  


### 16.4 Matching struct
Struct pattern looks like general constructor with curly brackets `Typename{...}`.  
1. Empty brackets means that pattern matches any instances of type.  
Child type will be matched by parent.  
```python
struct A
struct B
struct C(B)

match st
    A{} !- # match any of A
    B{} !- # match B and C (as a child of B)
```
2. Fields in brackets.  
Pattern will try match those field which has in pattern.  
So struct pattern filters instances only by fields has used in pattern, skipping others, instead of how pattern of dict works.  
Names of fields should be just words like in struct constructor, no vars, wilcards, etc.  
Subpattern of fields value can be any pattern of value - const, var, collection-pattern.  
```python
struct A a:int
struct B b: string
struct C(B) c:list

match st
    A{a:val} !- # any A inst, assign value of A.a to var `val`
    B{b:'abc'} !- # B anc C inst, by value of field `b`
    C{b:bval} :? bval ?> ['aaa', 'bbb', 'ccc'] !- # field from parent type (and complex condition)
    B{b:_} !- # wildcard in field-value of struct doesn't make sense, but works
    C{c:[_,*]} !- # C with non-empty list in `c`-field
```
3. Pattern of any-type struct.  
In pattern of struct we can match any instance of struct ignoring type of value.  
Undercore `_{}` lexem instead of type name is used for that.  
```python

A a:int
B name:string
C name:string
...
match nn
    _{a:val} !- # struct with field `a` will be matched: A
    _{name:val} !- # with field `name`: B, C
    _{} !- # any other structs will be matched
    _ !- # non-struct values will reach this point
```


### 16.5 Multicase `|`
Multicase is feature for combine several patterns in one executable case.  
Operator `|` is divider in such complex expression between patterns.  
The case will be executed if one of patterns in set is matched.  
```python
match n
    1 | 2 | 3 !- # one of 1, 2, 3 is matched
    (*) | [*] !- # any tuple or list

    # 1-key dict or dict with 2 keys one of them is 'name' is matched. 
    # a:b will be assigned by matched pattern
    {a:b} | {'name':_, a:b} !- ...
```

### 16.6 Bool guard in case
Case pattern can has additional `guard` - bool condition equal to `if`. 
Guard can be added to case-condition by operator `:?` after pattern.  
Guard will be used after pattern has matched.  
Guard can contain assign-part, equally to `if` statement.  
(Actually, guard is the same object as the `if`, without execution block).  
```python
x = someval()
match n
    [a, *] :? x < a !- # list pattern, val from list in guard
    (1, b) | [2, b] :? b > 10 !- # multipattern before guard
    {'name':name, *} :? name !- 'Alan' && 'address' ?> n !- # complex condition in guard
    (a, b, c) :? d = a + b; c < d !- print(a, b, c, d) # assign sub-expression, var from guard uses in sub-block  
    _ :? n != 17 !- guard with `_`
    _ !- # other
```

### 16.7 Mixed (nested) patterns
Multipattern can contain collections or structs.  
```python
struct A a1: int
struct B(A) b1: int

match n
    [1,2,3] | (1,2,3) | {'a':_, 'b':_, 'c':_} !- # some collections
    A{a1:1} | B{b1:2} | C{c1:'c3'} !- # some structs
    [*] | (*) | {*}  !- # any collections
```
Containers can contain another containers.  
```python
match n
    # dict / list / tuple
    [(), ()] !- # top list
    ([], []) !- # top tuple
    [{}, {}] !- # dict in
    [{1:()}] !- # 3-lvl, tuple is last
    ({2:[]}) !- # 3-lvl, list is last
    [({3:_})] !- #-lvl dict is last
    # with structs
    [(A{}, 11), (B{}, 22)] !- ...
    {'a':A{}, 'b':B{}} !- ...
```


### 16.8 Regexp case
String value can be matched by regular expression.  
```golang
match n
    re`aa|bb|cc` !- #// simple pattern 
    re`^[houpring]{3,6}$` !- #// full string
    re`.+`m !- #// non empty string
    [re`\d+`, *] !- #// regexp can be a sub-element of a container-pattern
```

### 16.9 Type matching `_::int`
Case can be matched by a type.  
Operator `::` is used for that.  
Now basic types have been implemented.  
```python
match x
    ::int !- # all int values
    ::float !- # float values
    :: bool !- ..
    ::string !- ..
```
Collections can be matched by type too.  
```python
match data
    ::list !- ...
    ::dict !- ...
    ::tuple !- ...
```
Var pattern or `_` can be restricted by type.  
```python
match n
    a::int !- print(a)
    a::string !- print(a)
    _::float !- ...
```
Actually `::type` means the same as a pattern `_::type`.
But in dict this two sub-elements can act differently alittle in combination with `?` or `*` sub elements.  

Typed pattern can be the part of collection pattern.  
In dict pattern typed key is found before typed val.  
```python
match data
    [::int, a::int, _::float] !- # in list
    (::string, val::float) !- # in tuple
    {k::string : v::int} !- # in dict
    {::string : _::list} !- # list in dict
```



### 17. multi-assignment
```python
# simple vals
a,b,c = 1,"2",3.5

# unpack tuple
a, b, c = (1, 2, 3)

# unpack list
a, b, c = [1,2,3]
```

### 18.1 Ternary operator `?:`  
classic ternary oper `condition ? valIfTrue : elseVal`  
```python
x = a < b ? 10 : 20
```
shortened case. null-or:  `val1 ?: va2 `  
returns val1 if not null (zero num, empty string, list or tuple); otherwize returns val2  
```python
x = val1 ?: va2
```

### 18.2 Val-in `?>` and val-not-in `!?>` operators.  
Boolean operators for check value or key in collection.  
1. If collection `vals` contains value `a`  
 `a ?> vals`  
```python
# base usage 
val ?> collection

# val for list|tuple
if val ?> [1,2,3] ...
if val ?> ('a', 'b', 'c') ...

# key for dict
if 'a' ?> {'a':1, 'b':2} ...
```
2. If collection doesn't have value `!?>`  
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

### 18.3 Check type operator `::`  
If we need to check type of value we can use operator `::`  
Left oparend is value (var, ect..), right - name of type.  
```python
src = [10, 2.5 , "three", [4]]

for val <- src
    if val :: int
        # 10 
    if val :: float
        # 2.5
    if val :: string
        # "three"
    if val :: list
        # [4]
```
Basic list of types usable in `::` operator:
```
int, float, bool
string, list, tuple, dict,
function
```
Some types can be added in the future.  

### 19. Free place :)  


### 20. One-line block `;` `/:` operators
(Note! there is not a usual code style. Just special tool for specific cases.)  
1. One-line multiespressions.  
"Horisontal" syntax for those who like long lines and hate tall columns :)  
Several simple expressions without sub-lines, like assignment or function call,  
can be separated within the one line by `;` operator.
```python
a = 1; b = 2; c = 3
a = 10 + a; b += 20; c -= 30;
res = [a, b, c]; res <- dd; res <- e
```
2. Inline bloks.  
It's just syntax sugar for some control structures with subexpressions.  
Mostly for usage for 1-line cases, like short code in console-input.  
Inline blocks is defined by `/:` operator that separates control statement and his sub-expressions.  
Implemented for `if`, `for`, `while`.  
```python
if x < 10 /: print(x)
```
```python
for i <- names /: print(name)
```
We can put several expressions into a control.
```python
res = [] ; 
for i <- [1..5] /: x = i * 10 ; y = i + 100; res <- (x + y)
```
Nested controls.  
Every next inline sub control after `/:` is a childe of previous block.  
```python
# `if` in `for`
for i <- [1..10] /: if i % 2 != 0 /: print(i)

# the same:
for i <- [1..10]
    if i % 2 != 0
        print(i)
```
So there no way for several inline sub-blocks like if-else.  
But you can use parenthesis and `;` to combine independent expressions.  
```python
for i <- [1..10] /: (if i % 2 != 0 /: print('odd', i)) ; (if i %2 == 0 /: print('even', i))
```
It's ok to combine multiple nested controls, with child subexpressions separated by a semicolon `;`.  
But be accurate with using `/:` and `;` in one line.  
Remember that `/:` has less priority tnan `;`.  
So all expressions separated by `;` after `/:` will be interpret as a sub-block.  
But `;` before control statement in the same line will cause error.  
Use parenthesis for such case.  
```python
res = []; (for i <- [1..5] /: if n=i*2; n > 4 /: x = i * 10; y = i + 100; res <- (x + y))
```
The same for `while`.  
```python
res = []; c=1; (while c < 5 /: res <- c; c += 1)
```
Full example in console run:  
```python
py -m run -c \
    "res = []; (for i <- [1..5] /: if n=i*2; n > 4 /: x = i * 10; y = i + 100; res <- (x + y)) "\
    -r res
>> [133, 144, 155]
```


### 21 String features  

- String formatting.
There are two syntax implementations.  

### 21.1 Percent formatting
`%` - formatting with binary operator `<<`.  
It's classic `%s`-formatting. Uses native `%` operator inside with %-formatting syntax of native language (python here).
```python
'hello int:%d, float:%f, str:%s ' << (123, 12.5, 'Lalang')
```

### 21.2 Format by including expressions
`~`strings / var-embedding syntax.  
Uses `~` unary operator before string and stringify expressions into `{}` brackets (includes).  
Includes can be simple var-name, or be more complex expression with template-modifier over `:`.  
Any expression returning stringify value is allowed: `var`, `struct.field`, `list`/`dict` element, `function` call.  
Be accurate with `"'``quotes``'"` inside includes.  
```python
a, b, s = (123, 12.5, 'ABC')
name = 'Bob'

# simple template
hey = ~' Hello {name}!'

# with {val:pattern}
hello1 = ~'hello int:{a:05d}, float:{b:.3f}, str: `{s2:<5s}`.'

# with function call
func fHello(s)
    'hello, ' + s

~'Some prefix, {fHello(`Formatter`)} '
```
See more examples in `tests/test_format.py`.

### 21.3 String functions.

1. Split.

```python
split("1,2,3", ',')
>> ['1','2','3']
```
Method-like:
```python
"1,2,3".split(',')
```

2. Join.

```python
join(['a','b','c'], '_')
>> 'a_b_c'
```
Method-like:
```python
# list method
['a','b','c'].join('_')
# string methos 
'_'.join(['a','b','c'])
```

3. Replace.

```python
src = "<div> Hello </div>"
replace(src, 'div', 'span')
>> '<span> Hello </span>'
```
Method-like:
```golang
# string pattern
"a b c".replace(' ', '--')
# regexp pattern
"a b\tc   d".replace(re`\s+`, '--')
>> 'a--b--c'
```

4. tostr
```python
tostr(123)      # '123'
tostr(1 == 1)     # 'true'
tostr([1,2, (3, 4)])  # '[1,2,(3,4)]'
tostr({'a': 123}) # "{'a':123}"
```

5. map
```python
r = 'abc'.map(s -> ~'<{s}>')
>> '<a><b><c>'
```



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

### 25.1 Regular expressions. `re`
1. Regular expression is a native object in lisapet.  
Regexp is created by keyword `re` before string quotes.  
Most usable quotes for regexp is back-quotes, they ignores almost all escape sequences except very needed like ``` \` ```.  
Other quotes works too (triple multiline is not currently, thinking about that).  
```golang
rx1 = re`pattern`
rx2 = re"pattern"
```

3. Syntax of regexp patterns is similar to Python (or Perl).  
```golang
re`\b\d\w\s\t\n` #// escapes
re`[a-z][0-9][^inverted]` #// classes
re`^full string$` #// start and end
re`any-count* one-more+ maybe-one? count{2,5}` #// quantifiers
re`(group) (?:ignored group)` #// groups
#// and so on
```

2. Flags.  
`re`-syntax allows native [(pythons) regexp flags](https://docs.python.org/3/library/re.html#flags): `a,i,L,m,s,u,x`.  
Flag or flags can be added to pattern right after pattern quotes without white spaces or separators.  
Flags set is corresponding to pythons flags of regexp.  
```golang
re`pattern`is
re`pattern`aim
re`pattern`Lux
```
Another way to add flags (mostly if we need generate them programmatically) is take them from string variable.  
Just put variable on the flags position in the curly brackets (it looks similar to string formatting).  
```golang
flags = 'muL'
rx = re`pattern`{flags}
```

Regexp objects have its own set of operators and can be used as a pattern of match-cases (in dev).

### 25.2 Regexp match `=~`
Most basic regexp operator is a matching `=~`  
It can accept regexp as a left operand and the string as a right.  
Result of matching operator is a `bool` value:
```golang
src = "aaa"
if re`\w+`ai =~ src
    print(src, 'has matched')
```

### 25.3 Regexp find `?~`
Finding substrings, operator `?~`  
Operator `?~` searches matches in string and returns list of found matches.  
Flags can make changes in result.  
Result of rx-find operator is a table represented as a list of lists.  
Each row of result is a result of the matching.  
If a pattern don't has groups then we will obtain single subvalue in each row.  
```golang
src = """
Let's get started learning regular expressions.
"""
res = re`[a-z']+`ai ?~ src

# >> [["Let's"], ['get'], ['started'], ['learning'], ['regular'], ['expressions']]
```
In pattern with groups 1-st sub value in each row will be result of matching of full pattern. Other values after first - results of matching groups.  
```golang
src = 'Tom Red, 111-22-33; Bob Green, 444-55-66'
rx = re`([^,;]+),\s*(\d+-\d+-\d+)`
res = rx ?~ src

>> [['Tom Red, 111-22-33', 'Tom Red', '111-22-33'], 
    [' Bob Green, 444-55-66', ' Bob Green', '444-55-66']]
```

Since regexp finding returns list of results, we can use results of `?~` right in the loop statement.  
```golang
src = "h88 i99 j101 k202"

for s <- re`\w(\d+)`m ?~ src
    res <- (s, s[1])
```
Or in the comprehantion expression.
```golang
src = "h88 i99 j101 k202"
res = [s[1:] ; s <- re`(\w)(\d+)`m ?~ src]

>> [['h', '88'], ['i', '99'], ['j', '101'], ['k', '202']]
```
Also regexp can be [used as case of strings](#168-regexp-case) in `match` statement.  


### 25.4 Regexp replace
Function `replace(src, old, repl, count)` can receive regexp as a second arg.  
Backreferences like `\1` work as well according to groups order.  
```golang
src2 = 'a111 b222 c333'
r2 = replace(src2, re`([a-z])(\d+)`i, `<\1:\2:\1>`)

>> '<a:111:a> <b:222:b> <c:333:c>'
```

### 25.5 Regexp split 
Function `split(src, rx)` can use regexp too.  
```golang
src = "h88 i99 /j101;k202--n204"
res = []

for s <- split(src, re`[\s/;-]+`)
    res <- ~'<{s}>'

>> ['<h88>', '<i99>', '<j101>', '<k202>', '<n204>']
```



--------------------------------------------------------
--------------------------------------------------------
--------------------------------------------------------

Drafts and thoughts:

*.et, *.etml - file extension
etml - possible extension of html/xml template.

*

Possible features (thoughts):
01. functions can be overloaded by types (maybe)
02. operators are functions, exception: brackets () [] {}, maybe.
10. mapping and pattern matching (done!)
11. functions doesn't needs braces like haskell (for what?)
12. functional elements: lambdas(done!), composition, carrying.
13. interface as list of functions (thinking)
14. functions with ducktype args based on interfaces (what did that mean? anonimous interface as a list of func-names?)

*
#TODO:
Convert / rewrite code to Go, Java, Rust.  
Looks like its not a simplest task ))

