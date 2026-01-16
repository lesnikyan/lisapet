


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


    # TODO: type of struct field: list, dict, bool, any

    '''
        # user defined types
        struct ABC a: int, b: int
        abc = ABC{a:1, b:2}
        res <- type(abc)
        
        TODO: check TypeMString if need. If not then Convert to TypeString
        # print(type(""" """))
        # print((""" a s d""").split(' '))

        DONE: test overloading with type function, as function and any.
        
        TODO?: Null() -> Null(Val)
        
        TODO: declaration of var:type without assignment: check and fix.
        
        TODO: check type of operand for all operators
        
        TODO: overload: test methods with compatiple types
            add overloaded constructors, custom and default (at least empty)
            test overload for imported functions, 
            struct type args in overloaded func, 
            overloaded methods of imported structs
        
        TODO bug: Sequence  match and split if brackets in quotes: (1, '[', ']')

        TODO: add shoren alias fo struct: stru A a:int
            shorten of string: name:strn
        
        TODO: fix parsing of struct.field with brackets:
            calling func, returned from method: stru.method()()
            collection in collection in field: stru.field[0][1]
   
    '''


    def test_refactored_dot_and_brackets(self):
        ''' '''
        # True cases
        exam = '''
        a.b
        a.b[0]
        a.b[0].c
        a.b.c[0]
        a.b().c
        a.b()[0].c
        a.b.c[0]()
        a.b()()
        a([f([g('', []())])])
        a.b[0]()()
        a.b[0]()()[0]
        a.b[0]()().c
        a.b[0]()().c[0]
        [][](a+b)
        a[](1,2,3)
        a.b([], 1+2, c[]()[].d).e[f+3-g]
        re`abc`Ui
        [1,2,3]
        {1:11, 2:22, 3:foo(1,2,3)}
        (1,2,3,['a'])
        'hello + 1'
        `hello \s 1 + 2`
        """ hello \n 3 """
        '''
        code = norm(exam[1:])
        tlines = splitLexems(code)
        clines:list[CLine] = elemStream(tlines)
        for cline in clines:
            if not cline.code:
                continue
            # print('', elemStr(cline.code))
            res = isSolidExpr(cline.code)
            # print('', res)
            self.assertTrue(res)
            
        # False cases
        # print(flatOpers())
        exam = '''
        a.b + 1
        a + b[0]
        a; b
        a << 2
        r <- 2
        f() - g()
        a = 123
        a.b : c[0].d
        a.b , c[0]
        '''
        code = norm(exam[1:])
        tlines = splitLexems(code)
        clines:list[CLine] = elemStream(tlines)
        for cline in clines:
            if not cline.code:
                continue
            print('', elemStr(cline.code))
            res = isSolidExpr(cline.code)
            print('', res)
            self.assertFalse(res)
        
        
    def test_multiline_base(self):
        ''' test when func returned from method and call obj.foo()(arg)
        '''
        
        code = r'''
        res = []
        
        '!!!!!!!!!!!!!!!'
        '''
        r'''
        
        '''
        code = r'''
        res = []
        
        
        
        func foo(x)
            x + x
        res <- foo(20)
        
        s = """
        a ' X ' 
        ``` 12 
        ```
        b
        c"""
        
        res <- s
        
        aa = [
            1,2,3,
            foo(
                4 + foo(
                    2
                )
            )
        ]
        res <- aa
        
        b = (10 + (
                2 ** 2 * 5)
                + 4 * 5 *( 5 + 5)) + 1000
        
        res <- b
        
        s0 = 'aaa bbb ccc'
        s1 = """
        111 11 \"\"\"
            222 22 ```
                3333 33\'\'\'"""
        
        res <- s1
        #@
        # comments
        # @#
        
        c = []
            111
            """
            222
            """
            ```
            333
            ```
        
        res <- c
        ``` Q
        in mult
        qwe
        ```
        
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = []
        print('TT>>', rvar.vals())
        # self.assertEqual(exv, rvar.vals())

    def test_blocks(self):
        ''' test when func returned from method and call obj.foo()(arg)
        '''
        
        code = r'''
        res = ['-0']
        
        func foo(x)
            2 * x
        
        r1 = []
        for a <- [1..7]
            if a > 2 && a < 6
                r1 <- foo(a)
        
        
        r2 = []
        for b <- [1..5] /: if b % 2 /: r2 <- b
        
        struct A a:int
        
        func st:A foo2(x)
            st.a + x
            
        func st:A foo3(x, y)
            st.a + (x * y)
        
        a1 = A(12)
        res <- a1.foo2(5)
        res <- a1.foo3(2,3)
        
        res <- r1
        res <- r2
        
        func fooo4(x)
            r = []
            if x == 1
                111
                for n <- [1,2]
                    for m <- [1,2,3]
                        r <- n * m
            else if x == 2
                222
                for n <- [6..8]
                    for m <- [4,5,6]
                        r <- n * m
            else if x == 3
                333
                for n <- [10..13]
                    for m <- [7,8]
                        r <- n * m
                        
            else
                r <- 444
            r
        
        r3 = [fooo4(1), fooo4(2), fooo4(3), fooo4(4)]
        res <- r3
        
        func foo(a:int)
            if a > 5
                return a
            else
                return - a
        1
        res <- foo(2)
        
        r5 = 0
        for i <- [1..10]
            # print(i, r5)
            if i % 2 == 0
                continue
            r5 += i
        res <- r5 
        
        # print('r1', r1, r2, r3)
        # print('res', res)
        '''
        
        # code = r'''
        # res = [-17]
        # '''
        
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        print('tt>>', rvar.vals())
        exv = ['-0', 17, 18, [6, 8, 10], [1, 3, 5], 
               [[1, 2, 3, 2, 4, 6], [24, 30, 36, 28, 35, 42, 32, 40, 48], [70, 80, 77, 88, 84, 96, 91, 104], [444]], -2, 25]
        self.assertEqual(exv, rvar.vals())

    def test_func_from_method(self):
        ''' test when func returned from method and call obj.foo()(arg)
        '''
        
        code = r'''
        res = []
        
        struct A a:int
        struct R r:list
        struct B(A) b:string
        
        func st:A foo(a)
            x -> x + a
        
        func st:B bInfo(y)
            x -> ~"{st.a},{st.b} ({x}, {y})"
        
        aa = A{}
        res <-  aa.foo(2)(5)
        
        r1 = R([[1,2,3]])
        res <-  r1.r[0][1]
        
        b1 = B(11, 'B-1')
        
        res <- b1.foo(3)(7)
        res <- b1.bInfo(9)(8)
        
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [7, 2, 10, '11,B-1 (8, 9)']
        self.assertEqual(exv, rvar.vals())

    def _test_1(self):
        ''''''
        def _foo(n, x, y):
            r = x + y
            if n == 0:
                return r
            n, x, y = n - 1, r, y
            return _foo(n, x, y)
        
        def foo(x, y):
            return _foo(x, x, y)
            
        def _loop(n, x, y):
            # r, n = 0, x
            # dx = x
            while True:
                r = x + y
                if n == 0:
                    return r
                n, x, y = n - 1, r, y
        
        def loop(x, y):
            return _loop(x, x, y)
        
        rfoo = foo(10, 2)
        rloop = loop(10, 2)
        print('tt>>', rfoo, rloop)
        self.assertEqual(rfoo, rloop)

    def _test_code(self):
        ''' '''
        code = r'''
        res = []


        print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
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



if __name__ == '__main__':
    main()
