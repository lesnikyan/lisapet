


from unittest import TestCase, main

import lang
import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
# import context
from context import Context
from bases.strformat import *
# from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

from cases.utils import *
from nodes.tnodes import Var
from objects.func import Function
from nodes.func_expr import setNativeFunc
from bases.over_ctx import FuncOverSet
from tests.utils import *
from libs.regexp import *
from nodes.func_features import *


import pdb


            
class TestDev(TestCase):


    '''
  _<-od
 (+a)(-b)
        
        
        DONE: list... unpack list/tuple into function 
        nums = [1,2,3]
        1) insert to list
        nn2 = [10, 11, nums...] # >> [10,11,1,2,3]
        2) insert to tuple
        tt2 = (nums...) # >> (1,2,3)
        3) func args
        foo(nums...)
        
        DONE: add bytes.
        bytes - sequence of bytes, mutable (instead of string)
            # implementstion:
                1) pythons `bytearray` inside
            # declarations:
            bb = [00 01 fa d8]
            # usage:
            bb = [f0 01 05 21]
            b = bb[0] # >> get first byte
            bb[-1] = 22 # set last byte
        
        DONE: bytes: add other num bases: bin 0b[10], oct 0o[17], dec 0d[19]
        
        DONE: bytes features
        -- string-related
            # bb.string(encoding='UTF8') # convert bytes to string, enc = 'UTF8', code.UTF8
            #string.bytes(encoding) # string to bytes
            
        DONE: bytes methods:
            # .map(x -> x & 0xf0) # apply function to each byte in sequence and return result
            # .each() # apply function to each byte
            # .fold()
            # .reverse()
            # .replace() # simple val to val
        
        DONE: bytes: splitting methods 
            # .blocks / .nsplit(size:int) # split byte set (from right) on block with size.
                fill last left to size by 0 
            # .nums(int) # list of int numbers, arg = 1-8, split to numbers by byte-size
            # .bits() # list of bits
        
        DONE: .split(sep=bytes) # like string do
        
        DONE: bytes operators
            #ok bb[a:b] # get slice - copy part of bytes
            #ok bitwize: | & ^ ; 0x[01 02 03] & 0x[00 01 f0]
        
        DONE:
            # done: struct type args in overloaded func, 
            # done: test methods with compatiple types
        
        DONE: curry as builtin function
        
        DONE: currying operator:
            func foo(a, b, c)
            foo~>(1)(2)(3)
        
        DONE: tests: curry func from var, from list, from func-call(), curry method, curry 2-3 args lambda.
        
        DONE: func composition operator:
            foo * bar * baz $ (x)
            
        DONE: operator of applying function to argument
            foo $ arg
            equal to
            foo(arg)
        
        DONE: composition / apply with methods
        
        DONE: add base type constructors: int(), string(), float(), bool(), list(), tuple(), dict(), 
            // byte(int), 
            bytes(list[int]|string|glif|int|byte), glif(int|byte|bytes)
            # dont,  string(bytes(), encoding='utf8') # string from bytes / 0x[].string() for that
        DONE: bytes constructor - add len arg for fill by 0
            0x[len=10] # 10 bytes
            0x[] * 10 # 10 bytes
            0x(12) (?)
            bytes(12) # future type-constructors

    # features for for `enum` - not sure
        TODO: Enum.name(11)
        TODO: Enum.value(name)
        TODO: Enum methods .names(), .values(), .items() > (name, val), .todict()
        TODO: 22 ?> Enum # after methods

        TODO:? add shorten alias for the struct: stru A a:int
            shorten of string: name:strn
        
        TODO:? to think about things that is not obvious:
            - instance of function inside function itself
            - additional properties of function as an object
        
        TODO: (?) add byte: int/4, unsigned
            x:byte = 1 # 0-255
            x:byte = 0xff ; auto casting
            x:byte= intVal % 0x100
            #  optional: explicit byte value
            x = &01; 8xff; 8b100; &0xff; |xf0; 8d255
            0xff; 0b10000001
        
        TODO: (?) bytes oper shift: bb << 4; bb >> 8 # no extend size
        
        TODO:? class Null() -> class Null(Val)
        
        TODO (?):  # partially called, make function with remined args; can't be applyed to func with arg...
            foo(1,2, ...>)
            foo(1,2, ->)
            foo(1,2, _...)
            foo(1,2, :...)
            foo(1,2, |...)
            foo(1,2, /...)
        
        TODO: 
            think about escapes in triple-backticks strings
            unary backtick tested in test_parsing_string_backtiks
            mres = ``` \\n \\t \\ \\s \\w ```
        
        TODO: type() for user defined types
            struct ABC a: int, b: int
            abc = ABC{a:1, b:2}
            res <- type(abc)
        
        TODO: inspect and resolve MatchPtrCase to avoid use tree.raw2done if not needed anymore
        
        TODO: check type of operand for all operators
        
        TODO: overload: 
            test overloading for imported functions, 
                should we disallow overloading function in another module?
                looks like overloading is a feature within one module
            (? do we need) overloaded methods of imported structs
            
        TODO: override of overload:
                Think about case with same name func in a child is overloaded for another args in parent
                    1) child method will override all overloaded or
                    2) child method will add and shoud find func by signature in all parent tree or
                    3) disallow override overloaded func name
        
        TODO: error if try to curry func with overloading, variadic args. question: how to do with default args.
        
        TODO: tail recursion:
        1) tail optimization by func name, during interpretation (before add to ctx)
        2) extend tail-recur case for earlier returns - not sure 
        
        TODO:? var type in for-loop 
            for n:int <- nn

        TODO: think about type casting by colon; type in left
            x:int = int: true

        TODO: 21.1 Multi-reading in loop:
            put at right part one more collections, so assign more var in left: 
            aa = [1,2,3]
            dd = {11:1, 22:2, 33:3}
            for i, x, key, val <- iter(3), aa, dd
        
        TODO: group - static block for set of const vals and functions. 
            Like extended enum and struct
                print(i, x, key, val)
        
        TODO: add type `glif` - 1 multibyte symbol
        
        BUG: Sequence  match and split if brackets in quotes: (1, '[', ']')
        
        TODO: add assertion to cases in test_lists
        
        TODO: refactor case-loops to pattern-tree
        1) find common cases:
            solid -> in-brackets, dot.name, solid(brackets), solid-rUnar, control-keywords, var, val, 
            no-solid -> definitions, control-statements, bin-opers, 
        2) dive into sub-cases
        
        TODO: refactor list-like expressions to avoid multiple check items in []-brackets
            first check solid []-case, then find case in []-cases:
            list, slice, iter-gen, list-gen, bytes
        
        TODO: bytes generator: 0x[(n << 2) % 0xff ; n <- iter(32)]
        
        TODO: root, square root operator
            |/ _/ -/ */
            -/4 # 2;  3-/ 8 # 2
            */4 # 2;  3*/ 8 # 2
        
        
        TODO: add glif type
            glif represents one char with any byte-size
            constr: glif('a'),  glif(41), 
            'Hello'.glifs() -> list of glifs
        
        TODO: bytes.replace({old:new,...}) # replace by table in dict, overloading replace
        TODO: string.replace({dict}) # check, implement if not
        
        TODO: fix print(bool): should be false, true, instead of False, True
        
        TODO: add builtin compare() for base type: string, tuple, bytes.
        
        TODO: dict: filter (filter by key, val)
        
        DONE: list|tuple methods: sort, filter; 
        
        DONE: string methods: upper, lower
    '''

    _ = r"""
# guides


"""



    def _test_2(self):
        ''' TODO: in-arguments lambda with slash-leading syntax 
            idea: lambda with one more args without brackets, basically it conficts with comma separator in more complex expression:
            func call, collections, etc.
            leading slash can resolve this issue, commas between slash and r-arrow are definition-args of lambda
        '''
        code = r'''
        res = []
        
        ff = [x -> x, \ a, b -> a + b, y -> 2 * y]
        res <- ff[1](1, 200)
        
        dd2 = {'a':'1', 'b':'2', 'c':'3', 'qqq':'4', 'xxx':'5', 'abc':'6'}
        res <- dd2.filter(\ k , v -> k ?> 'abcd')
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        print(resv)
        exv = []
        # self.assertEqual(exv, resv)

    def _test_code(self):
        ''' '''
        code = r'''
        res = []
        
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        print(resv)
        exv = []
        # self.assertEqual(exv, resv)


    def _test_match_last_expr_of_case_as_result(self):
        ''' if `match` is a last expression in function. 
            each sub-case of match will return result of their last expression'''
        code = r'''
        res = []
        
        func fsubRes(n)
            # Last expression is a result
            match n
                # indent block
                ::int # some comment
                    x  = 1
                    x
                
                # inline block
                ::bool /: x = 2; x
                
                # /: but indent (it's ok)
                {_:_} /:
                    y = 3
                    y
                
                # block with sub control
                p::(tuple|list)
                    r4 = []
                    for x <- p
                        r4 <- x
                        if len(r4) >= 3
                        # in if/else must use `return`
                            return (4, r4, p)
                    -1000
                # default
                _ /: 5
            # end of function
            
        nn = [1, true, [1,2,3], (3,4,5), {4:44}, 1.5, [100,200]]
        
        for k <- nn
            res <- fbase(k)
            
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        # rvar = ctx.get('res').get()
        # exv = [1, 2, (4, [1, 2, 3], [1, 2, 3]), (4, [3, 4, 5], (3, 4, 5)), 3, 5, -2000]
        # self.assertEqual(exv, rvar.vals())


    def _test_barr(self):
        ''' '''
        code = r'''
        res = 0
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res')
        self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        self.assertEqual([], rvar.vals())


    def _test_print_struct(self):
        ''' '''
        code = r'''
        struct A a:int
        struct B(A) b:string
        
        
        a = 11
        b = 12.5
        c = false
        d = null
        e = 'str-abc'
        aa = A{a:1}
        bb = B{a:111, b:'B-b-b'}
        
        print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res')
        self.assertEqual(0, rvar.getVal())



if __name__ == '__main__':
    main()

