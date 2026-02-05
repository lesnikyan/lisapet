


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


import pdb


class TestDev(TestCase):


    '''
        
    
        DONE: test and fix string + string, string += string << val
        
        DONE: unified multi-assignment in for-loop
            nn = [(1,2,3), ...]
            for a,b,c <-nn 

        TODO:? add shorten alias for the struct: stru A a:int
            shorten of string: name:strn
        
        TODO:? to think about things that is not obvious:
            - instance of function inside function itself
            - additional properties of function as an object
        
        TODO:? class Null() -> class Null(Val)
        
        TODO: 
            think about escapes in triple-backticks strings
            unary backtick tested in test_parsing_string_backtiks
            mres = ``` \\n \\t \\ \\s \\w ```
        
        TODO:  user defined types
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
            
            override of overload:
                Think about case with same name func in a child is overloaded for another args in parent
                    1) child method will override all overloaded or
                    2) child method will add and shoud find func by signature in all parent tree or
                    3) disallow override overloaded func name
            # done: struct type args in overloaded func, 
            # done: test methods with compatiple types
        
        BUG: Sequence  match and split if brackets in quotes: (1, '[', ']')
        
        TODO: tail recursion:
        1) tail optimization by func name, during interpretation (before add to ctx)
        2) extend tail-recur case for earlier returns - not sure 
        
        TODO:? var type in for-loop 
            for n:int <- nn
        
        TODO: string methods: upper, lower
        TODO: list|tuple methods: sort, filter
        TODO: minimal lambda:
            x -> x
            x -> 0
        
        DONE: enum as a static set of named values
            enum Color  Red, Green, Blue # >> 0,1,2
            enum Color:int  Red 5, Green 10, Blue # >> 5, 10, 11
            enum Alphabet a:1, b, c, d, e, f
            # block
            enum Color: int
                Red: 0xf00
                Green: 0x0f0
                Blue: 0x00f
            thoughts:
                enum (enumerable) is just static numeric set, but not a set of any other data types
                we need additional static/const type set: conset, valset, const, etc. (?)

        TODO: match n / case: Enum.val1 /: print('val1', n)
        TODO: 22 ?> Enum
        TODO: Enum.name(11)
        TODO: Enum.value(name)
        TODO: Enum .names(), .values(), .items() > (name, val), .todict()
    '''

    def test_enum_block_definition(self):
        ''' '''
        code = r'''
        res = []
        
        enum Nums 
            one=1 
            two
            three 
            four 
            five 
            six
            seven
            nineteen = 19
            x20
        
        gnums = [Nums.two .. Nums.five]
        res <- ('n..n', tolist(gnums))
        
        nn = [0, 1, 2, 3, 4, 5, 6, 7, 8, 19, 20]
        
        dn = {}
            Nums.six : '|6|'
            Nums.seven : '|7|'
        
        tt = (Nums.nineteen, Nums.x20)
        
        for n <- nn
            if n == Nums.one
                res <- ('one', n)
            else if n ?> [Nums.four, Nums.two]
                res <- ('in [4, 2]', n)
            else if n < Nums.three
                res <- ('n < 3', n)
            else if n == Nums.three
                res <- ('three', n)
            else if n ?> tt
                res <- ('in (19, 20)', n)
            else if n ?> dn
                res <- ('in dict', n, dn[n])
            else
                res <- ('other', n)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [('n..n', [2, 3, 4, 5]), 
               ('n < 3', 0), ('one', 1), ('in [4, 2]', 2), ('three', 3), ('in [4, 2]', 4), 
               ('other', 5), ('in dict', 6, '|6|'), ('in dict', 7, '|7|'), ('other', 8), 
               ('in (19, 20)', 19), ('in (19, 20)', 20)]
        self.assertEqual(exv, rvar.vals())

    def test_enum_linear_definition(self):
        ''' '''
        code = r'''
        res = []
        
        # default vals
        
        enum Abc a,b,c,d,e,f,g
        
        res <- [-111, Abc.a, Abc.b, Abc.c, Abc.d, Abc.e, Abc.f, Abc.g ]
        
        # all assigned vals
        enum Colors red = 0xff0000, green = 0xff00, blue = 0xff
        
        res <- ~"{Colors.red:06x}"
        res <- ~"{Colors.green:06x}"
        res <- ~"{Colors.blue:06x}"
        
        # initiated first
        enum Nums one=1, two, three, four, five, six
        
        # just assign
        x = Nums.one
        res <- ('x', x)
        
        # if conditions test
        nn = [0, 1, 2, 3, 4, 5, 6]
        
        dn = {}
            Nums.six : '|6|'
        
        for n <- nn
            if n == Nums.one
                res <- ('one', n)
            else if n ?> [Nums.four, Nums.two]
                res <- ('in [4, 2]', n)
            else if n < Nums.three
                res <- ('n < 3', n)
            else if n == Nums.three
                res <- ('three', n)
            else if n ?> dn
                res <- ('in dict', n, dn[n])
            else
                res <- ('other', n)
        
        # init vals in random positions
        enum B a, b=10, c, d, e=20, f, g
        
        res <- [-333, B.a, B.b, B.c, B.d, B.e, B.f, B.g]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            [-111, 0, 1, 2, 3, 4, 5, 6],
            'ff0000', '00ff00', '0000ff', ('x', 1),
            ('n < 3', 0), ('one', 1), ('in [4, 2]', 2), ('three', 3), ('in [4, 2]', 4), ('other', 5), ('in dict', 6, '|6|'),
            [-333, 0, 10, 11, 12, 20, 21, 22]]
        self.assertEqual(exv, rvar.vals())


    def _test_enum_matching(self):
        ''' '''
        code = r'''
        res = []
        
        enum Nums one=1, two, tree
        x = Nums.one
        print(Nums.one, x)
        
        nn = [0, 1, 2, 3, 4]
        for n <- nn
            match n
                # concreate elem from enum
                Nums.one /: res <- ('one', n)
                Nums.two /: res <- ('two', n)
                # any elem from enum
                Nums /: res <- ('enum Nums', n)
        
        print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        # rvar = ctx.get('res').get()
        # exv = []
        # self.assertEqual(exv, rvar.vals())


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
        # rvar = ctx.get('res').get()
        # exv = []
        # self.assertEqual(exv, rvar.vals())


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
