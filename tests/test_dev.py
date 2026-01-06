


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
from nodes import setNativeFunc, Function
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
        
        TODO?: Null() -> Null(Val)
        
        TODO: declaration of var:type without assignment: check and fix.
        
        TODO: check type of operand for all operators
        
        TODO: overload: test methods with compatiple types
            add overloaded constructors, custom and default (at least empty)
            test overload for imported functions, 
            struct type args in overloaded func, 
            overloaded methods of imported structs
        TODO: partial call. def foo(a, b, c):  1) foo(x, _, _); 2) foo(x) _ _  
        # not sure, partial usage of operator - make lambda:
                    (2 +) =>> x -> 2 + x
                    (-(2)) =>> x -> x - 2, or -1 # problem here
                    underscore here looks better
                    looks mostly as a shorten syntax of lambdas
                    (2 + _) =>> x -> 2 + x
                    (_ - 2) =>> x -> x - 2
        TODO: carrying: func foo(1,b,c); 1) curry(foo); 2) @cur foo 3) ~foo $)  
            =>> curried_foo(1)(2)(3)
        TODO: composition foo * bar (x)
        TODO: prevent overloading of func with default/named args or variadic list args...
        
        TODO bug: Sequence  match and split if brackets in quotes: (1, '[', ']')

        TODO: test overloading with type function, as function and any.
    '''


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

    def _test_TypeHash(self):
        ''''''
        TH.base = 0xff001
        print('th>>', TH.mk())

    def _test_func_signHash(self):
        ''''''
        htt = [
            [TypeInt(), TypeFloat(),], 
            [TypeFloat(), TypeBool(),], 
            [TypeInt(), TypeFloat(), TypeBool(),], 
            [TypeString(), TypeString(), TypeString(), TypeInt()], 
            [TypeBool(), StructDef('A')],
            [StructDef('A'), StructDef('B')],
            [TypeInt(), TypeFloat(), TypeBool(), StructDef('A'), StructDef('B'), StructDef('C')],
        ]
        for ht in htt:
            hash = FuncInst.sigHash(ht)
            print('hh>>', hash)


    def _test_1(self):
        ''''''
        # hh = TH.mk()
        # for i in range(9999):
            # hh = TH.mk()
        #     if i > 1000:
        #         print(hh)
        #         if i > 1005:
        #             break

        tt = [TypeInt(), TypeFloat(), TypeBool(), StructDef('A'), StructDef('B'), StructDef('C'), ]
        # for t in tt:
        #     
        htt = [
            [TypeInt(), TypeFloat(),], 
            [TypeFloat(), TypeBool(),], 
            [TypeInt(), TypeFloat(), TypeBool(),], 
            [TypeString(), TypeString(), TypeString(), TypeInt()], 
            [TypeBool(), StructDef('A')],
            [StructDef('A'), StructDef('B')],
            [TypeInt(), TypeFloat(), TypeBool(), StructDef('A'), StructDef('B'), StructDef('C')],
        ]
        for ht in htt:
            hash = FuncInst.sigHash(ht)
            print('hh>>', hash)



    def _test_code(self):
        ''' '''
        code = r'''
        res = []
        func foo(s:string)
            {'a':s}

        func foo(x:int)
            x * 10

        func foo(x)
            [x]

        res <- foo(1) #//        [1]
        res <- foo(1.5) #//      [1.5]
        # res <- foo(true) #//     [true]
        res <- foo('hello') #//  {'a': 'hello'}
        print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
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
