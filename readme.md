
Simple and small programming language.
*
LISAPET
Line-interpretation scripting as a possibly executable tree.
Linear interpretable script automation project of executable tree.
Linear interpretable script automatic parser of executable tree.
Linear interpretable syntax analyzer and parser of executable tree.
ico: Fox pet on the bicycle


// comment
# comment
"string"
<!any> - start page tag, defines how to interpret text file, optional
<!text-template> - internal templating with including code snippets
*.sml - file extension

Syntax.
1. no extra thingth, block is defined by line shifting like python
2. operators are functions exception: (),
3. struct as complex type
4. functions are typed, by default as Any type
5. functions can be overloaded by types

exension:
10. mapping and pattern matching
11. fcuntions doesn't needs braces like haskell
12. composition of functions are possible, by `.`
12. interfase as list of functions
13. functions with ducktype args based on interfaces
13. (), are also functions


x = 10 // integer
y = 1.2 // float
z = 2.5j5.0 // complex
zz = complex(2.5, 5,0) // complex

s = "some text" // string
nums = [1,2,3] // list[int]
nums2 = [1,2,3.1] // list[float]
nums3 = [1,2,, 3.3, "4"] // list[string]
operators:
1+2, 2-3, 3*4, 4/5, 5**2, 55%6
x++; y--; x+=2; y-=3; s += " " + "aaa"

bool:
true, false, 
true && false; true || false; !true; 
x1 = 1001b; x2 = 010b;
x1 | x2; x1 & x2; x1 ^ x2;

block = {
    a=1; b=2; c = a + b;
    print(c);
}

do block; // do in current namespace

none ; internal empty block;

if x == 1:
    do print(x)

for i in [1,10]: // 1,10
    do none;

for i in [1..10]: // 1,2,3,4,5,6,7,8,9
    do print(i);

for i in [1..10, n*2+1 | n%3 > 0]:
    do print(i)
// :
t = []
for n in [1..10]:
    i = n * 2 + 1
    if i%3 > 0:
        t[] = i
for i in t:
do print(i)
    
// ****************  Version 2 ********************* 

import std.*
import std.(reader, writer)
import std.print p, std.open op

x = 5
for i to 5
    print i

for i << 1..5
    print i

for a=10,b=3; i << 10..20
    c = a + b + i
    if n=i*2+1; if n != c
        print c
# ? free block - not sure
blockRes = 
    a = 1
    b = 2
    a+b

// struct
type user {
    name "" // string
    age 0 // int
    rate 0. // float
}

// alter struct 
type User
    name string
    age float
    agr1 num
    arg2 int
    arg3 list
    arg4 dict
    arg5 CustomType


u = user{"vasya", 16, 1.5}

nums = list{}
nums = [1,2,3]
nums << 4 // append
n << nums // pop

vals = dict{}
vals = {a:5, b:7}
vals << {c:9} // add key:val

print vals.c

for key:val << vals
    print "$key = ${val}" // $varName, ${varName} - name templating

a,b,c = 1,"2",3.5
print "%d %s %.2f" << a,b,c // position tmplating with formatting 
print " %($a)d " // varname with formatting

u = user{"vasya", 16, 1.5}
descr = "office manager"
print "user $name $age %($rate).2f \"$descr\" " << user // uncover object

rx = \[a-z-_]{2,5}\i
text = "Hello somebody here! 123"
res = rx.find(text)

for w << res
    print "found $w"

tpl = "found $w"
for w << rx
    print tpl << w

// one line
for n << 0..5 => print "next: %d" << n
if res = rx.match(text); !res.empty() => print " result: %s" << res.first()

// function
foo [int, float] string
foo a,b => "(%d, %.2f)" % a, b

print foo(1,2.222) // "(1, 2.22)"
s = foo 2, 3.333
print s

#TODO:
Convert code to Go, Java, Rust
https://github.com/gython/Gython

