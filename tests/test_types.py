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



    def test_assign_compatible_struct_fields(self):
        ''' assign compatible vals to struct fields '''

        code = r'''
        res = []
        
        struct D d:int, dd:string
        struct E(D) e:string
        
        struct A
            a:int
            b:float
            c:bool
            d:D
        
        a1 = A{}
        # A.a
        a1.a = true
        stAbool1 = a1.a
        
        a1.a = false
        stAbool0 = a1.a
        
        a1.a = null
        stAnull = a1.a
        
        # A.b
        a1.b = 22
        stBint = a1.b
        
        a1.b = false
        stBbool0 = a1.b
        
        a1.b = true
        stBbool1 = a1.b
        
        a1.b = null
        stBnull = a1.b
        
        # # A.c
        a1.c = null
        stCnull = a1.c
        
        a1.d = null
        stDnull = a1.d
        
        a2 = A{}
        d2 = D(12345, "D2string")
        a2.d = d2
        st2DD = a2.d
        
        a3 = A{}
        e3 = E(34567, "D3string", "E3string")
        a3.d = e3
        st3DE = a3.d
        
        # print('res = ', 1)
        '''
        
        code = norm(code[1:])
        ctx:Context = doCode(code)
        
        tdata = [
            ('stAbool1', 1, TypeInt), 
            ('stAbool0', 0, TypeInt), 
            ('stAnull', 0, TypeInt), 
            
            ('stBint', 22.0, TypeFloat), 
            ('stBbool1', 1.0, TypeFloat), 
            ('stBbool0', 0.0, TypeFloat), 
            ('stBnull', 0.0, TypeFloat), 
            
            ('stCnull', 0.0, TypeBool), 
            
            ('stDnull', Null(), TypeNull), 
            ('st2DD', ('struct',{'d':12345, 'dd':'D2string'}, 'D'), StructDef), 
            ('st3DE', ('struct',{'d':34567, 'dd':'D3string', 'e':'E3string'}, 'E'), StructDef), 
        ]
        
        types= ['A', 'D', 'E']
        tvals = {}
        for tname in types:
            tval = ctx.getType(tname)
            # print('ttv:', tval.get(), type(tval.get()))
            tvals[tname] = tval.get()
        
        for tcase in tdata:
            name, xval, xtype = tcase
            
            var = ctx.get(name)
            # print('tt>', f'{name}, {xval}, {xtype}', var)
            varT = var.getType()
            valT = var2val(var).getType()
            rval = var2val(var).getVal()
            self.assertIsInstance(varT, xtype)
            self.assertIsInstance(valT, xtype)
            if not (isinstance(xval, tuple)):
                self.assertEqual(xval, rval)
            else:
                # print('3>>', rval)
                obj = var.get()
                xtype = tvals[xval[2]]
                # print('tp>', xtype, obj.getType())
                self.assertTrue(xtype == obj.getType())
                for skey, xfval in xval[1].items():
                    fval = obj.get(skey).get()
                    # print('4>>', fval)
                    self.assertEqual(xfval, fval)
        
        a1 = ctx.get('a1').get()
        typeD = ctx.getType('D').get()
        self.assertTrue(a1.vtype.ntypes['d'] == typeD)
        

    def test_assign_compatible_struct(self):
        '''
        test assign structs:
        base:Super = Child{}
        '''
        code = r'''
        
        struct A a:int
        struct B(A) b:float
        struct C(B) c:string
        struct D d:int
        struct E(C, D) e:bool
        
        aa:A = A(1)
        bb:B = B(11, 1.1)
        cc:C = C(111, 1.11, 'c1')
        dd:D = D(3)
        
        ab:A = B{}
        ac:A = C{}
        bc:B = C{}
        de:D = E{}
        ae:A = E{}
        be:B = E{}
        ce:C = E{}
        de:D = E{}
        
        an:A = null
        # an = A{}
        
        '''
        code = norm(code[1:])
        ctx:Context = doCode(code)

        tdata = [
            # varName, varType, valType 
            ('ab', 'A', 'B'), 
            ('bb', 'B', 'B'), 
            ('ac', 'A', 'C'), 
            ('bc', 'B', 'C'), 
            ('de', 'D', 'E'), 
            ('ae', 'A', 'E'), 
            ('be', 'B', 'E'), 
            ('ce', 'C', 'E'), 
            ('de', 'D', 'E'), 
            ('an', 'A', TypeNull()), 
            
        ]
        types= ['A', 'B', 'C', 'D', 'E']
        tvals = {}
        for tname in types:
            tval = ctx.getType(tname)
            # print('ttv:', tval.get(), type(tval.get()))
            tvals[tname] = tval.get()
        
        for tcase in tdata:
            name, xVarT, xValT = tcase
            var = ctx.get(name)
            val = var.get()
            vrtype = tvals.get(xVarT)
            vltype = xValT
            if isinstance(xValT, str): 
                vltype = tvals.get(xValT)
            # print('tt>', name, var, val, vrtype, vltype)
            
            # check if variable type wasn't changed
            self.assertTrue(vrtype == var.getType(), f'{vrtype} == {var.getType()}')
            # check type of val
            self.assertTrue(vltype == val.getType(), f'{vltype} == {val.getType()}')
        
    def test_assign_compatible_types(self):
        '''
        convert val to destination var type in case with compatible types
        a:int = bool, null
        b:float = int, bool, null
        d:bool = null
        # next
        c:list|dict|tuple = null
        '''

        code = r'''
        res = []
        # single vars
        xIntF:int = false
        xIntT:int = true
        xIntN:int = null
        
        xFloatI:float = 11
        xFloatF:float = false
        xFloatT:float = true
        xFloatN:float = null
        
        xBoolN:bool = null
        
        
        # print('res = ', 1)
        '''
        code = norm(code[1:])
        ctx:Context = doCode(code)

        tdata = [
            ('xIntF', 0, TypeInt), 
            ('xIntT', 1, TypeInt), 
            ('xIntN', 0, TypeInt), 
            
            ('xFloatI', 11.0, TypeFloat),
            ('xFloatF', 0.0, TypeFloat),
            ('xFloatT', 1.0, TypeFloat),
            ('xFloatN', 0.0, TypeFloat),
            
            ('xBoolN', False, TypeBool),
        ]
        for tcase in tdata:
            name, xval, xtype = tcase
            
            var = ctx.get(name)
            # print('tt>', f'{name}, {xval}, {xtype}', var)
            varT = var.getType()
            valT = var2val(var).getType()
            rval = var2val(var).getVal()
            self.assertIsInstance(varT, xtype)
            self.assertIsInstance(valT, xtype)
            self.assertEqual(xval, rval)
        

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
                res = typeCompat(dest(), ntype())
                # if exp != res:
                #     print('tt!>', f"dest:{dest} != src: {ntype}", exp, res)
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

