
from unittest import TestCase, main

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
from bases.strformat import *
from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

from cases.utils import *
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from tests.utils import *



from tests.utils import *



class TestKeywords(TestCase):
    ''' Operators defined by word '''

    def test_break_continue(self):
        ''' Loop in loop with break and continue '''
        code = r'''
        res = 0
        
        func foo(x)
            x * 10
            
        func bar(x, y)
            x + y
        
        func baz(a, b)
            r = []
            for i <- [1..5]
                for j <- [2..5]
                    n = foo(i)
                    m = bar(i, j)
                    # print('::', i,j,' ->', n,m)
                    if n < a
                        continue
                    if m < a
                        continue
                    if m > b
                        break
                    r <- n + m
            r
        
        res = baz(5, 9)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = [15, 16, 25, 26, 27, 35, 36, 37, 38, 46, 47, 48, 49, 57, 58, 59]
        self.assertEqual(exp, rvar.vals())

    def test_continue(self):
        ''' '''
        code = r'''
        res = []
        
        r = 0
        for i <- [1..10]
            # print(i, r)
            if i % 2 == 0
                continue
            r += i
        res <- r
        
        r = 0
        for i = 0; i < 12; i += 1
            # print(i, r)
            if i % 2 == 0
                continue
            r += i
        res <- r
        
        a, b = 3, 1
        while a < 7
            a += 1
            if a % 2 != 0
                continue
            b *= a
        
        res <- b
        
        func foo(a, b)
            r = 0
            for i <- [1..25]
                c = i * 3
                # print('foo:', i, c)
                if c < a || c > b
                    continue
                r += c
            r
        
        res <- foo(5, 15)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        self.assertEqual([25, 36, 24, 42], rvar.vals())

    def test_break(self):
        ''' '''
        code = r'''
        res = []
        
        # `for` by iterator
        r = 0
        for i <- [1..5]
            r += i
            # print(i, r)
            if i == 3
                break
        res <- r
        
        # `for` by counter
        r = 0
        for i = 0; i < 10; i += 1
            r += i
            # print(i, r)
            if i == 5
                break
        res <- r
        
        # `while`
        a, b = 0, 1
        while a < 10
            a += 1
            if a > 5
                break
            b *= a
            # print('w3:', a, b)
        
        res <- b
        
        # `for` in function
        func foo(a, b)
            r = 0
            for i <- [1..25]
                c = a * i
                # print('foo:', i, c)
                if c > b
                    break
                r += c
            r
        
        res <- foo(3, 20)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        self.assertEqual([6, 15, 120, 63], rvar.vals())


if __name__ == '__main__':
    main()
