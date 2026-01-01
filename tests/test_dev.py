


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
# from nodes.structs import *
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
        
        TODO: check TypeMString if need. If not then Convert to TypeString
        # print(type(""" """))
        # print((""" a s d""").split(' '))
        
        TODO?: Null() -> Null(Val)
        
        TODO: declaration of var:type without assignment: check and fix.
        
        TODO: check type of operand for all operators
    '''


    def test_func_overload(self):
        ''' func overload 
            can't be overloaded (at least one such case):
            1. if has var... argument
            2. if has default values
        '''

    def _test_overload_by_args_type(self):
        ''' func overload by type of args '''
        code = r'''
        res = []
            
        func foo(x:int)
            x * 10
            
        func foo(x:float)
            x / 100 + 5000
            
        func foo(x:string)
            ~'<x>'
            
        func foo(x:list)
            len(x) + 3000
            
        func foo(x:dict)
            x.keys()
            
        func foo(x:tuple)
            len(x) + 2000
        
        struct A a:int
        
        func foo(a:A)
            a.a + 1000
        
        res <- foo(1)
        
        
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        # self.assertEqual([], rvar.vals())


    def _test_new_collection_constr(self):
        ''' constr-like brackets with colon - []:, {}:, (): '''
        code = r'''
        res = []
        
        varList = []:
            111,
            222,
            333
        
        # varDict = {}:
        #     1:1111
        #     2:2222
        #     3:3333
        
        # Vd2= {}:
        #     'a': 'AAAAAAAAAAAAAAAAAAAA'
        #     'b': 'BBBBBBBBBBBBBBBBBBB'
        #     'c': 'CCCCCCCCCCCCCCCCCC'
        
        # varTuple = ():
        #     'aaaaa'
        #     'bbbbb'
        
        print(f1(200))
        # print('res = ', 1)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # print('>>', dd.values())
        # self.assertEqual(0, rvar.getVal())
        # rvar = ctx.get('res').get()
        # self.assertEqual([], rvar.vals())

    def _test_1(self):
        ''''''

    def _test_new_collection_constr(self):
        ''' constr-like brackets with colon - []:, {}:, (): '''
        code = r'''
        res = []
        
        varList = []:
            111,
            222,
            333
        
        # varDict = {}:
        #     1:1111
        #     2:2222
        #     3:3333
        
        # Vd2= {}:
        #     'a': 'AAAAAAAAAAAAAAAAAAAA'
        #     'b': 'BBBBBBBBBBBBBBBBBBB'
        #     'c': 'CCCCCCCCCCCCCCCCCC'
        
        # varTuple = ():
        #     'aaaaa'
        #     'bbbbb'
        
        print(f1(200))
        # print('res = ', 1)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # print('>>', dd.values())
        # self.assertEqual(0, rvar.getVal())
        # rvar = ctx.get('res').get()
        # self.assertEqual([], rvar.vals())


    def _test_code(self):
        ''' '''
        code = r'''
        res = []

        print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
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
