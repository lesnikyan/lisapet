'''
tests of types
'''

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

# import pdb


class TestTypes(TestCase):


    def test_resolveVal(self):
        ''' resolving of value for autocasting during assignment '''

        code = r'''
        res = {}
        x1:int = 0 # false
        x2:int = 0 # true
        x3:int = 0 # null
        y1:float = 0.0
        y2:float = 0.0
        y3:float = 0.0
        t:bool = false
        
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        tdata = [
            # Var(), Val(), expVal
            # to int
            (ctx.get('x1'), Val(True, TypeBool()), Val(1, TypeInt())),
            (ctx.get('x2'), Val(False, TypeBool()), Val(0, TypeInt())),
            (ctx.get('x3'), Val(Null(), TypeNull()), Val(0, TypeInt())),
            # to float
            (ctx.get('y1'), Val(True, TypeBool()), Val(1.0, TypeFloat())),
            (ctx.get('y2'), Val(False, TypeBool()), Val(0.0, TypeFloat())),
            (ctx.get('y2'), Val(Null(), TypeNull()), Val(0.0, TypeFloat())),
            # to bool
            (ctx.get('t'), Val(Null(), TypeNull()), Val(False, TypeBool())),
        ]
        for tcase in tdata:
            tvar, val, exv = tcase
            dtype = tvar.getType()
            res = converVal(dtype, val)
            # print('', tvar, val, exv, res)
            self.assertEqual(exv.getVal(), res.getVal())
            self.assertEqual(exv.getType().__class__, res.getType().__class__)

    def test_structTypeCompat(self):
        ''' compatibility check of struct values '''

        code = r'''
        
        struct A a:int
        struct B(A) b:float
        struct C(B) c:string
        struct D d:int
        struct E e:string
        struct F(D, E) f:string
        struct G g: float
        
        aa:A = A(1)
        bb:B = B(11, 1.1)
        cc:C = C(111, 1.11, 'c1')
        dd:D = D(3)
        ee:E = E('e5')
        ff:F = F(7, 'fd7', 'f7')
        gg:G = G(9.01)
        
        std = dict
            # []
            'a': [A(2)]
            'b': [B(22, 2.2)]
            'c': [C(222, 2.22, 'c2')]
            'd': [D(4)]
            'e': [E('e6')]
            'f': [F(8, 'fd8', 'f8')]
            'g': [G(9.02)]
        
        # print('res = ', 1)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        
        keys = {
            'a':['b','c'],
            'b':['c'],
            'c':[],
            'd':['f'],
            'e':['f'],
            'f':[],
            'g':[]
        }
        vars = {}
        varnm = ['aa','bb','cc','dd','ee','ff','gg']
        for vnm in varnm:
            v = ctx.get(vnm)
            vars[vnm[0]] = v
        # print('vnm:',vars )
        std = ctx.get('std').get().data
        for k, cpk in keys.items():
            obDest = vars[k]
            tkeys = [k]+cpk
            # null = Val(Null(), TypeNull())
            nres = structTypeCompat(obDest.getType(), TypeNull())
            self.assertTrue(nres, f"{obDest} !:: null")
            for sk in keys.keys():
                obSrc = std[sk].elems[0]
                res = structTypeCompat(obDest.getType(), obSrc.getType())
                exp = sk in tkeys
                # print('tt>', f"{obDest} :: {obSrc}", exp, res)
                self.assertEqual(exp, res, f"{obDest} !:: {obSrc}")
        
    def test_typeCompat(self):
        ''' compatibility check of base types '''
        btypes = [TypeAny, TypeBool, TypeInt, TypeFloat, TypeComplex, 
            TypeString, TypeList, TypeDict, TypeTuple, TypeFunc]
        # TypeAny, TypeBool, TypeInt, TypeFloat, TypeComplex, TypeString, TypeList, TypeDict, TypeTuple, TypeFunc
        tmap = {
            TypeAny : [TypeAny, TypeBool, TypeInt, TypeFloat, TypeComplex, TypeString, TypeList, TypeDict, TypeTuple, TypeFunc], 
            TypeBool : [TypeBool], 
            TypeInt : [TypeBool, TypeInt, TypeNull], 
            TypeFloat : [TypeBool, TypeInt, TypeFloat, TypeNull], 
            TypeComplex : [TypeBool, TypeInt, TypeFloat, TypeComplex, TypeNull], 
            TypeString : [TypeString], 
            TypeList : [TypeList, TypeNull], 
            TypeDict : [TypeDict, TypeNull], 
            TypeTuple : [TypeTuple, TypeNull], 
            TypeFunc : [TypeFunc, TypeNull],
        }
        
        for dest, ok_types in tmap.items():
            for ntype in btypes:
                exp = ntype in ok_types # ok in type in map
                res = typeCompat(dest, ntype)
                # if exp != res:
                    # print('tt!>', f"dest:{dest} != src: {ntype}", exp, res)
                self.assertEqual(exp, res, f"dest:{dest} != src: {ntype}")
    
    def test_structTypeEqual(self):
        stypes = [
            StructDef('aaa'), StructDef('bbb'), 
            # same name like struct from another module
            StructDef('aaa')]
        for i in range(len(stypes)):
            # left operand
            a = stypes[i]
            for j in range(len(stypes)):
                # right operand
                b = stypes[j]
                res = a == b
                exv = i == j
                # print('tt>', f'equation {a} == {b} = {res}')
                self.assertEqual(exv, res, f'unexpected result of type equation {a} == {b} = {res}')
                res = a != b
                exv = i != j
                self.assertEqual(exv, res, f'unexpected result of type unequation {a} != {b} = {res}')

    def test_typeEqual(self):
        left = [TypeAny(), TypeBool(), TypeInt(), TypeFloat(), TypeComplex(), TypeString(), TypeList(), TypeDict(), TypeTuple(), TypeFunc()]
        right = [TypeAny(), TypeBool(), TypeInt(), TypeFloat(), TypeComplex(), TypeString(), TypeList(), TypeDict(), TypeTuple(), TypeFunc(), StructDef('test_struct', [])]
        for i in range(len(left)):
            # left operand
            a = left[i]
            for j in range(len(right)):
                # right operand
                b = right[j]
                res = a == b
                exv = i == j
                # print('tt>', f'equation {a} == {b} = {res}')
                self.assertEqual(exv, res, f'unexpected result of type equation {a} == {b} = {res}')
                res = a != b
                exv = i != j
                self.assertEqual(exv, res, f'unexpected result of type unequation {a} != {b} = {res}')

