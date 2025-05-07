
Simple and small programming language (not so small already [facepalm]).
*
LISAPET:
Line-interpretation scripting as a possibly executable tree.
Linear interpretable script automation project of executable tree.
Linear interpretable script automatic parser of executable tree.
Linear interpretable syntax analyzer and parser of executable tree.
Lexical interpreter of scripting and arithmetical parser of executable tree.
ico: Fox pet on the bicycle

Syntax draft:
# comment
"string"
<!any> - start page tag, defines how to interpret text file, optional
<!text-template> - internal templating with including code snippets
*.ep, *.pml - file extension

Syntax.
1. no extra thingth, block is defined by line shifting like python
2. operators are functions exception: (),
3. struct as complex type
4. functions are typed, by default as Any type
5. functions can be overloaded by types (?)

exension:
10. mapping and pattern matching
11. fcuntions doesn't needs braces like haskell (for what?)
12. composition of functions are possible, by `.` or another
13. interfase as list of functions
14. functions with ducktype args based on interfaces
15. (), are also functions (for what?)

Done:

1. Vars, vals, lists, assignment, context of vars
x = 1
name = 'Ramzes II'
names = ['Alya', 'Valys', 'Olya']
lastName = names[2]

2. numbers, strings
hello = "hello somebody!"
nums = ['0123', '0b1111', '0o777', '0xfba01', '0.15']

3. Sub-block of expressions. 
If statement, comparison operators, bool operators
res = 100
if x >= 10 | x < 2 && x != 0
    res = 2000 + x * -10 - 700
else
    x = x ** 2
    res = 1000 + x - 500

4. Math operators 
y = 5 + x * -3

# unary operators
x = -2

# complex math expressions
b=100 
c=4
d=3
res = 5 + 6 - 7*(b - c * 12 - 15) / 11 + 3 ** d - 0xe * 8

# operators with assignment
x = 1
x += 2
x *=3
x %= 2
z = 1
z *= (x + y)

5. for statement, range-iterator
for i=0; i < 5; i = i + 1
    y = y + 2
    for j=-3; j <= 0; j = j + 1
        a = a - j ** 2
        if a % 2 == 0
            b = b + 1
res = y
# ---------------

6. Iterator, arrow-assign operator `<-`

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


7. Function definition, context of functions (func call - in dev)

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

8. Dict. Linear and block constructor
# linear
dd = {'a':1, 'b':2}

# block
ddd = dict
    'a': 'a a a a a a a a a a a a a a a a a'
    'b': 'b b b b b b b b b b b b b b b b b'


9. arrow-append/set operator `<-`
# list
nn = []
nn <- 12

# for dict: dictVar <- (key, val) the same as dictVar[key] = val
dd = {}
dd <- ('a', 123)

10. Struct
# definition.  linear:
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


11. Struct method
# def
struct A a1:int

func a:A plusA1(x:int)
    a.a1 += x

# call
aa = A{} # default is 0
aa.plusA1(5)

11. Struct inheritance
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

12. List generator
# [startVal..endVal]
nums = [1..10] # -->> [1,2,3,4,5,6,7,8,9,10]

13. List comprehension
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

# multi-expressions, multiline expression
nums = [
    {x:a, y:b, z:c};
    x <- [3..7];
    a = x * 10;
    x % 2 > 0;
    y <- [1..10];
    b = 2 ** y;
    y <= 5;
    z <- [1..3];
    c = 10 ** z;
    a + b + c < 1000
]

14. Builtin functions:
# include python function as an builtin function.
setNativeFunc(ctx, 'print', print, TypeNull)

15. Lambda functions and high-order functions.

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

16. match-statement. TODO: types, struct (type, fields, constructor), collections (size, some vals), sub-condition, Maybe-cases
# !- is a case-operator: 
# value|template !- expressions
a = 4
r1 = 0
b = 3
# just simple values now
match a
    1  !- r1 = 100
    10 !- r1 = 200
    b  !- r1 = 300
    _  !- r1 = -2


17. multi-assignment
# simple vals
a,b,c = 1,"2",3.5

# unpack tuple
a, b, c = (1, 2, 3)

# umpack list
a, b, c = [1,2,3]

18. ternar operator.
# classic ternar oper
x = a < b ? 10 : 20

# shortened case. null-or:  val1 ?: va2
# returns val1 if not null, zero num, empty string, list or tuple, otherwize returns val2
x = val1 ?: va2

19. val-in-collection `?>` operator

# base usage 
val ?> collection

# val for list|tuple
if val ?> [1,2,3] ...
if val ?> ('a', 'b', 'c') ...

# key for dict
if 'a' ?> {'a':1, 'b':2} ...



NN.Next: 
one-line blocks (expr; expr; expr)


Drafts and thoughts:
// ****************  Version 1 ********************* 
DONE
// ****************  Version 2 ********************* 

import std.*
import std.(reader, writer)
import std.print p, std.open op



print "%d %s %.2f" << a,b,c // position templating with formatting 
print " %($a)d " // varname with formatting

u = user{"vasya", 16, 1.5}
descr = "office manager"
print "user $name $age %($rate).2f \"$descr\" " << user // uncover object

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

#TODO:
Convert code to Go, Java, Rust
https://github.com/gython/Gython

