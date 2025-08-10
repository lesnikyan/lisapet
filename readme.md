
# LISAPET
 It is was started as a simple and small scripting language.
(Not so small already [facepalm]).
Interpreter builds executable object, actually - tree of actions.
Than this tree can be executed.
Executable tree uses context-object (map of values with nested contexts).
```

```

*
LISAPET:
Line-interpretation scripting as a possibly executable tree.
Linear interpretable script automation project of executable tree.
Linear interpretable script automatic parser of executable tree.
Linear interpretable syntax analyzer and parser of executable tree.
Lexical interpreter of scripting and arithmetical parser of executable tree.
Language interpreter for scrtipt automatic producer of executable tree.
ico: Fox pet on the bicycle

*

Syntax draft:
```
# comment
"string" 'string' `string` '''string'''
var:type
<!any> - start page tag, defines how to interpret text file, optional
<!text-template> - internal templating with including code snippets, not implemented
*.et, *.etml - file extension
```
*
Syntax.
1. no extra thingth, block is defined by line shifting like python or ruby
2. operators are functions, exception: brackets () [] {}, maybe.
3. struct as complex type. struct can have methods.
4. functions have typed args, by default as Any type
5. functions can be overloaded by types (maybe)

exension:
10. mapping and pattern matching
11. functions doesn't needs braces like haskell (for what?)
12. functional elements: lambdas, composition, carrying.
13. interface as list of functions (thinking)
14. functions with ducktype args based on interfaces
15. (), are also functions (for what?)
*

## Usage.
```
# run file
python -m run tests/simple_test.et
...

# run code line
python -m run -c "a=1+2; print(a)"
...

# more complex 1-line example:
# python -m run -c "f1 = (x, y) -> x + y; f2 = x -> x * x;  p = x -> print(x); [p(f1(f2(n), 10000)); n <- [1..10]; n % 2 > 0 && n > 3]"
10025
10049
10081

# python -m run -c "r = [1..5]; print('nums:', tolist(r))"
nums: [1, 2, 3, 4, 5]

# multirun
# json as a data source
py -m run -c "n += a + b; print(':', a, b, n)" -l -j "[{\"a\":1, \"b\":2}, {\"a\":3, \"b\":4}, {\"a\":5, \"b\":6}]" -r n

# print result

py -m run -c "res = 100 + 23" -r res
>> 123

```

## Syntax.

Done parts:

1. Vars, vals, lists, assignment, context of vars
```
x = 1
name = 'Ramzes II'
names = ['Alya', 'Valya', 'Olya']
lastName = names[2]
```

2. numbers, strings
```
hello = "hello somebody!"
nums = [0123, 0b1111, 0o777, 0xfba01, 0.15]
```

3. Sub-block of expressions. 
If statement, comparison operators, bool operators
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
# come sugar
if cond
    code
else if cond
    code
else
    code
```

4. Math operators 
```
y = 5 + x * -3

# unary operators
x = -2

# complex math expressions
b=100 
c=4
d=3
res = 5 + 6 - 7*(b - c * 12 - 15) / 11 + 3 ** d - 0xe * 8
```

```
# operators with assignment
x = 1
x += 2
x *=3
x %= 2
z = 1
z *= (x + y)
```

5. for statement, range-iterator
```
for i=0; i < 5; i = i + 1
    y = y + 2
    for j=-3; j <= 0; j = j + 1
        a = a - j ** 2
        if a % 2 == 0
            b = b + 1
res = y
```

6. Iterator, arrow-assign operator `<-`
```
# by function iter(start[, last+1, step])
arr = [1,2,3]
r = 0
for i <- iter(3)
    r = r + arr[i]

# by array
for n <- [1,2,3]
    r += n

# by generator
for x <- [1..10]
    r += x

# by dict
for k, val <- {'a':1, 'b':2}
    ...
```

7. Function definition, context of functions
```
# definition
func foo(a, b, c)
    x = a + b
    y = b + c
    x * y

# usage
res = foo(1,2,3)

# arg type
func bar(a:int, b:int)
    a + b
```

8. Dict. Linear and block constructor
```
# linear
dd = {'a':1, 'b':2}

# block
ddd = dict
    'a': 'a a a a a a a a a a a a a a a a a'
    'b': 'b b b b b b b b b b b b b b b b b'

# add
dd['c'] = 3

# read
print(dd['a'], ddd['b'])
```

9. arrow-append/set operator `<-`
```
# list: append val
nn = []
nn <- 12

# dict: set val by key 
# dictVar <- (key, val) the same as dictVar[key] = val
dd = {}
dd <- ('a', 123)
```

10. Struct
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

11. Struct method
```
# def
struct A a1:int

# variable after `func` - instance of struct
func a:A plusA1(x:int)
    a.a1 += x

# call
aa = A{} # default is 0
aa.plusA1(5)
```

11. Struct inheritance
```
# parent types
struct Aaaa a1: int, a2: string

func a:Aaaa f1(x:int, y:int)
    a.a1 = x + y

struct Cccc c:int

# child, multiple inheritance
struct B(Aaaa, Cccc) b:int

b1 = B{b:1, a1:12, a2:'aa-2'}
b1.f1(3, 4)
b1.a1 += 10
```

12. List number generator
```
# simple numeric sequence [startVal..endVal]
nums = [1..10] # -->> [1,2,3,4,5,6,7,8,9,10]
```

13. List comprehension / generator
[1) result element expression ; 2) read element; 3) additional exprssion with assignment; 4) filtering condition]
2-4 is a generator-block; generator can have sub-blocks like:

```
[aa + bb + c ; a <- arr1; aa = a * 2; a > 5; b <- arr2; bb = b * b; c <- arr3; c < 10 ]
```

```
# simple
n1 = [x ** 2 ; x <- [1..10]]

# with condition guard
[x ** 2 ; x <- [1..10]; x % 2 > 0]

# several iterators
n2 = [[x, y] ; x <- [5..7]; y <- [1..3]]

# sub-expression
n3 = [(x, y) ; x <- [1..10]; y = x ** 2; y < 50]

# flatten sub-lists
src = [[x, y] ; x <- [5..7]; y <- [1..3]]
# src: [[5, 1], [5, 2], [5, 3], [6, 1], [6, 2], [6, 3], [7, 1], [7, 2], [7, 3]]
nums = [ x ; sub <- src ; x <- sub]
```
```
# generator: multi-expressions, multiline expression
nums = [
    {x:a, y:b, z:c}; # element of result
    x <- [3..7]; # 1-st iterator
    a = x * 10; # sub-expression
    x % 2 > 0; # condition of 1-st part
    y <- [1..10]; # 2-nd iterator
    b = 2 ** y;
    y <= 5;
    z <- [1..3]; # 3-rd iterator
    c = 10 ** z;
    a + b + c < 1000
]
```

```
# list comprehension by converted string
src = "ABCdef123"
res = [s+'|'+s ; s <- tolist(src); !(s ?> '123')]
```

14. Builtin functions:
```
# include python function as an builtin function.
setNativeFunc(ctx, 'print', print, TypeNull)
```
Builtin funcs changed for execute internal functions: added 1-st arg - Context.
```
def built_foldl(ctx:Context, start, elems, fun:Function):
    ...
        ...
        fun.do(ctx)
    ...
```
Actual builtin funcs:
print, len, iter, type, toint, tolist, foldl

15. Lambda functions and high-order functions.
```
# one-arg lambda
x -> x * 10

# several args
(x, y, z) -> (x + y) * z

# high order func
func foo(ff, arg)
    ff(arg * 2)

# lambda arg as var
f1 = x -> x * 3
n1 = foo(f1, 5)

# lambda arg as val
n2 = foo( x -> 2 ** x , 5)
```

16. match-statement.
TODO: types, struct (type, fields, constructor), collections (size, some vals), sub-condition, Maybe-cases
```
# !- is a case-operator: 
# value|template !- expressions
# _ !- expr # default case

a = 4
r1 = 0
b = 3
# just simple values  has been implemented
match a
    1  !- r1 = 100
    10 !- r1 = 200
    b  !-
        b = a * 1000
        r1 = [a, b]
    _  !- r1 = -2
```

17. multi-assignment
```
# simple vals
a,b,c = 1,"2",3.5

# unpack tuple
a, b, c = (1, 2, 3)

# unpack list
a, b, c = [1,2,3]
```

18. ternar operator.
```
# classic ternar oper
x = a < b ? 10 : 20

# shortened case. null-or:  val1 ?: va2
# returns val1 if not null, zero num, empty string, list or tuple; otherwize returns val2
x = val1 ?: va2
```

19. val-in-collection `?>` operator
```
# base usage 
val ?> collection

# val for list|tuple
if val ?> [1,2,3] ...
if val ?> ('a', 'b', 'c') ...

# key for dict
if 'a' ?> {'a':1, 'b':2} ...
```

20. one-line blocks (expr; expr; expr)
```
a = 1; b = 2; c = 3
a = 10 + a; b += 20; c -= 30;
res = [a, b, c]; res <- dd; res <- e
```

21. string formatting
```
# `<<` classic %s-formatting. Uses native python % operator inside with %-templates
'hello int:%d, float:%f, str:%s ' << (123, 12.5, 'Lalang')

# `~`operator for string. Works like f-string in python, with {val:patterns}
a, b, s = (123, 12.5, 'ABC')
~'hello int:{a:05d}, float:{b:.3f}, str: `{s2:<5s}` '
```

22. import
Imports module (file), module in folder (over dots: dirname.dirname2.module ).
Imports all things from module, or named things.
Can use aliases for named things.

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

*

--------------------------------------------------------

Drafts and thoughts:

u = user{"vasya", 16, 1.5}

rx = \[a-z-_]{2,5}\i
text = "Hello somebody here! 123"
res = rx.find(text)

tpl = "found $w"
for w <- res
    print(tpl % w)

// one line
for n <- 0..5 => print "next: %d" << n
if res = rx.match(text); !res.empty() => print " result: %s" << res.first()

// function
// haskell-like. not sure 

foo [int, float] string
foo a,b => "(%d, %.2f)" % a, b

print foo(1,2.222) // "(1, 2.22)"
s = foo 2, 3.333
print s

*

#TODO:
Convert code to Go, Java, Rust
https://github.com/gython/Gython

