


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
        
        DONE: check TypeMString if need. If not then Convert to TypeString
        # print(type(""" """))
        # print((""" a s d""").split(' '))
        
        # think about escapes in triple-backticks strings
        #   unary backtick tested in test_parsing_string_backtiks
            mres = ``` \\n \\t \\ \\s \\w ```

        DONE: test overloading with type function, as function and any.
        
        DONE: fix parsing of struct.field with brackets:
            calling func, returned from method: stru.method()()
            collection in collection in field: stru.field[0][1]

        TODO:? add shoren alias for the struct: stru A a:int
            shorten of string: name:strn
        
        TODO?: class Null() -> class Null(Val)
        
        TODO: declaration of var:type without assignment: check and fix.
        
        TODO: check type of operand for all operators
        
        TODO: overload: 
            add overloaded constructors, custom and default (at least empty)
            test overloading for imported functions, 
            override o overload:
                Think about case with same name func in a child is overloaded for another args
            overloaded methods of imported structs
            # done: struct type args in overloaded func, 
            # done: test methods with compatiple types
        
        TODO bug: Sequence  match and split if brackets in quotes: (1, '[', ']')
        
        TODO: tail recursion:
        1) tail optimization by func name, during interpretation (before add to ctx)
        2) extend tail-recur case for earlier returns - not sure 
   
    '''


    def _test_dev_tail_recursion(self):
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
        
        func foo(a, b)
            if a > 0
                return foo(a - 1, b + 1)
            b + 1
        
        print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        # rvar = ctx.get('res').get()
        # self.assertEqual([220022, 'Aloha!'], rvar.vals())


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
