


from unittest import TestCase, main

import lang
import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
import context
from context import Context
from strformat import *
from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

from cases.utils import *
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from tests.utils import *
from libs.regexp import *


import pdb


class TestDev(TestCase):


    # TODO: type of struct field: list, dict, bool, any

    '''
        # user defined types
        struct ABC a: int, b: int
        abc = ABC{a:1, b:2}
        res <- type(abc)
        
    '''


    def _test_n(self):
        import re
        src = ''' 
        abc 123
        qe 456
        hjk 890
        '''
        pt = re.compile(r'([a-z]+)\s+((\d)\d+)', re.MULTILINE)
        src = 'qwe 123 asd 456 zxc 789'
        pt = re.compile(r'([a-z]+)\s+((\d)\d+)', re.IGNORECASE)
        iter = pt.finditer(src)
        
        for mt in iter:
            print('mt>>', mt.group(0))
            print('ttr>>', mt.groups())


    def _test_code(self):
        ''' '''
        code = r'''
        # dd = {'aa':'11'}
        print(1, "1\n2\t3")
        print(2, `1 \n 2 \t3 \\ \/ \` \' \"`)
        print("Hello there! \n\t Here new line, \\ back-slash and \"Words in quotes.\" ")
        # print('res = ', 1)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # rvar = ctx.get('dd')
        # dd = rvar.get().vals()
        # print('>>', dd.values())
        # self.assertEqual(0, rvar.getVal())
        # rvar = ctx.get('res').get()
        # self.assertEqual([], rvar.vals())


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


    def _test_match_for_if_same_line(self):
        ''' TODO: match with for loop, `if` statement in the same case line
        Note: not sure we need it'''
        code = r'''
        struct ThreeNum a:int, b:int, c:int
        
        func n:ThreeNum sum()
            n.a + n.b + n.c
        
        func n:ThreeNum mult()
            n.a * n.b * n.c
        
        c = 5
        res = 0
        func foo2(ff)
            ff(11)
        rrs = [] # [0 ; x <- [0..11]]
        ff = x -> x * 10
        for i <- [1..7]
            res = 1
            for jj < [1..3]
                match i
                    1 !- n3 = ThreeNum
                        a:jj
                        b:5
                        c:7
                        res = n3.sum() * 1000 + n3.mult()
                    2 !- match ii
                        1 !- res = 121 + ii * 1000
                        2 !- res = 122 + ii * 1000
                        _ !- res = 123 + ii * 1000
                    3 !- if ii > 1 && ii < 4
                            print('c2', i, res)
                            res *= 11 * i + ii * 1000
                    4 !- for j <- [0..5]
                        print('c5', j, res)
                        res += i
                    5 !- for j = 1; j < 6; j = j + 1
                            print('c7', j, res)
                            res *= j
                    _ !- res = 1001
                rrs <- res

        print('rrs = ', rrs)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('rrs').get()
        self.assertEqual([10, 22, 121, 48, 115, 37, 120], rvar.vals())

    def __tt(self):
        '''
        # thoughts about OOP
        
        struct C c:int
        struct D(A,C) d1:int, d2:float
        
        func d:D f1(x, y)
            d.f1(x, y)
            d.a1 = 1
            d.A.f1(x, y) # ??
            d.super().f1(x, y) # ??
            super(d).f1(x, y) # for methods only # ??
        
        #struct D:(A,C) d1:int, d2:float
        
        struct E(A,B)
            A, B
            e1:int
            e2:D
        '''

    def _test_print(self):
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


    def _test_list_gen_by_strings(self):
        ''' thoughts:
            1) [..;..;..] should be a list-generator, not string
            2) [..; s <- "..."] in gen from string we want to get string
            3) ~[s, s <- "..."] solution (1) `~` operator as a list-to-string convertor
            3.1) looks like `join` func can be a good solution
        '''
        code = '''
        strline = 'abcdefg'
        res1 = []
        for s <- strline:
            res1 <- s
        print('res1', res1)
        # src = ['aaa', 'bbb', 'ccc']
        # nums = [x ; ns <- src; x <- ns ; x % 5 > 0]
        # print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_list_gen_comprehention_iter_by_string(self):
        ''' list generator and strings
            case 1: list from string
            case 2: string from string ? 
             -- think about: string is a list of chars, but string is an immutable list
        '''
        code = '''
        src = ['a' .. 'k'] # >> 'abcdef...k' ?? do we need that?
        src = "Hello strings!"
        res = [ [a ; a <- src]
        # print('src = ', src)
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_tuple_assign_left(self):
        ''' make vars and assign vals from tuple
            
            A) tuple as a result of comma-separated expression: var = a, b, c
            Shuold do:
            1. any value-returning sub-expression, like list constructor
            2. think about common case of `x, x, x` expression; not sure.
            tuple as destination of assignment operator, or: result-to-tuple mapping
            Should do:
            1. reuse defined vars.
            2. declare new vars
            3. allow `_` var
            4. allow type declaration (a:int, b:float) = foo()
            Should not:
            1. contain non-var expressions, like func call, collection constuctors (except tuple), const expr like strings or numbers.
            2. contain incorrect var-type
            -- Thoughts:
                a) left-tuple should have extra property like self.isLeft. 
                    In such case tuple can allow call tuple.setVal(args...)
                b) isLeft sould be changable only in assertion operator in .setArgs method.
                c) mapping list to tuple with the same size looks ok.
            '''
        code = '''
        (a, b, s) = 1,2,3
        print('', a, b, c)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_struct_anon(self):
        code = '''
        user = struct {name:'Anod', age:25, sex:male, phone:'123-45-67'}
        # uf = user.fields()
        print(user.name)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_bin_opers_cases(self):
        ''' test all operators in mixed cases: 
            assignment, math | bool expressions, separators (, ; :), brackets. '''


    _ = '''
        TODO features:
        1. generators extra features
    [-10..10]; [..10] >> IterGen(beg, over, step)

        3. tuple
        
        TODO tests:
    test assignment and read 
    global var and local block
    local var and function-block
    
    '''

if __name__ == '__main__':
    main()
