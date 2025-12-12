

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



class TestLibs(TestCase):



    def test_bound_native_methods(self):
        ''' Bound method by native function.
        bind : str_split(_, src, sep)
        as a `stringVal.split(sep)`
        >>
        src = "a,b,c"
        src.split(',') # > ['a', 'b', 'c']
        '''
        code = r'''
        res = []
        
        # list methods
        nums = [1,2,3]
        rnums = nums.reverse()
        res <- rnums
        res <- [1,2,3].join('^')
        
        # dict methods
        kc = 'c'
        dk = {1:11, 2:22, 'a':'aaa', 'b':'bbb', kc: 'ccc'}
        ks = dk.keys()
        res <- ks
        
        res <- dk.items()
        
        
        # split
        str1 = 'aa-bb-cc'
        rsplit = str1.split('-')
        res <- rsplit
        res <- "d,e,f".split(',')
        
        # join
        ss = ['s1', 's2', 's3']
        res <- '-'.join(ss)
        res <- "_".join(['s4','s5','s6'])
        res <- "/".join(['s7','s8', 's9'])
        
        # map
        res <- [1,2,3,4,5].map(x -> x * 11)
        func f1(x)
            ~"({x})"
        res <- "string1".map(f1)
        res <- "l i s t 2".split(' ').map(f1)
        res <- (1,2,3).map(x -> x * 5)
        res <- 't u p l e 3'.split(' ').map(f1)
        
        # combo
        wds = 'Hello dear friend'.split(' ').map(w -> ~"<t>{w}</t>").join(' ')
        res <- wds
        
        struct A a:int
        
        func si:A add(x)
            si.a += x
        
        aa = []
        for i <- [1..5]
            aa <- A(i)
        
        a2 = aa.map(val -> val.add(10))
        
        res <- a2
        
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
        exv = [
            [3, 2, 1], '1^2^3', [1, 2, 'a', 'b', 'c'], 
            [(1, 11), (2, 22), ('a', 'aaa'), ('b', 'bbb'), ('c', 'ccc')], 
            ['aa', 'bb', 'cc'], ['d', 'e', 'f'], 
            's1-s2-s3', 's4_s5_s6', 's7/s8/s9', 
            [11, 22, 33, 44, 55], '(s)(t)(r)(i)(n)(g)(1)', 
            ['(l)', '(i)', '(s)', '(t)', '(2)'], (5, 10, 15), ['(t)', '(u)', '(p)', '(l)', '(e)', '(3)'],
            '<t>Hello</t> <t>dear</t> <t>friend</t>', [11, 12, 13, 14, 15]]
        self.assertEqual(exv, rvar.vals())


    def test_dict_func_ditems(self):
        ''' '''
        code = r'''
        res = []
        src = [
            {}, {1:11}, {2:22, 3:33},
            {'a':'a11'}, {'bb':'b22','cc':'c33','dd':'d44'}, 
            {'nums' : [1,2,3]}, {'names' : ['Adam','Bob','Cindy']}
        ]
        
        for dd <- src
            kvs = ditems(dd)
            res <- (dd, kvs)
        
        
        # print('\n'); for r <- res /: print(r)
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
        exv = [
            ({}, []), ({1: 11}, [(1, 11)]), ({2: 22, 3: 33}, [(2, 22), (3, 33)]), 
            ({'a': 'a11'}, [('a', 'a11')]), ({'bb': 'b22', 'cc': 'c33', 'dd': 'd44'}, [('bb', 'b22'), ('cc', 'c33'), ('dd', 'd44')]), 
            ({'nums': [1, 2, 3]}, [('nums', [1, 2, 3])]), ({'names': ['Adam', 'Bob', 'Cindy']}, [('names', ['Adam', 'Bob', 'Cindy'])])]
        self.assertEqual(exv, rvar.vals())

    def test_dict_func_dkeys(self):
        ''' '''
        code = r'''
        res = []
        src = [
            {}, {1:11}, {2:22, 3:33},
            {'a':'a11'}, {'bb':'b22','cc':'c33','dd':'d44'}, 
        ]
        
        for dd <- src
            kk = dkeys(dd)
            res <- (dd, kk)
        
        
        # print('\n'); for r <- res /: print(r)
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
        exv = [
            ({}, []), ({1: 11}, [1]), ({2: 22, 3: 33}, [2, 3]), 
            ({'a': 'a11'}, ['a']), 
            ({'bb': 'b22', 'cc': 'c33', 'dd': 'd44'}, ['bb', 'cc', 'dd'])]
        self.assertEqual(exv, rvar.vals())

    def test_tostr(self):
        ''' '''
        code = r'''
        
        struct A a:int
        struct B(A) b:string 
        
        func foo(x)
            x + 10
        
        res = []
        src = [
            1, 0, 500, null, true, false,
            "", `\ \n \t \s \d \w \b {} ' " `,
            'abc', ' "a" ', " 'b' ", 
            [], [1,2,3], (1,2,3), {1:2, 'a':'b'},
            [1,2,3,4,5], [(x, 10*x) ; x <- [10..20]],
            [{('k'+tostr(x)) : x * 101} ; x <- [21..29]],
            ['a', 'b'], ['"a b c"', '"'], ["'d e f'", "'", "'\"'"],
            A(11), A{}, B{a:22,b:"barro"},
            [A(33)], (B{a:44, b:"55"},), {'aa':A(66), 'bb':B(0,'b77')},
        ]
        delems = {}
        for i <- [5..16]
            delems <- ('p'+tostr(i), i * 202)
        src <- delems
        
        for s <- src
            res <- tostr(s)
        
        # print('\n'); for r <- res /: print(r)
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
        # for r in rvar.vals():
        #     print('', r, ',')
        exv = [
            '1', '0', '500', 'null', 'true', 'false', '', '\\ \\n \\t \\s \\d \\w \\b {} \' " ', 
            'abc', ' "a" ', " 'b' ", '[]', '[1,2,3]', '(1,2,3)', "{'1':2,'a':'b'}", '[1,2,3,4,5]', 
            '[(10,100),(11,110),(12,120),(13,130),(14,140),(15,150),(16,160),(17,170),(18,180),(19,190),(20,200)]', 
            "[{'k21':2121},{'k22':2222},{'k23':2323},{'k24':2424},{'k25':2525},{'k26':2626},{'k27':2727},{'k28':2828},{'k29':2929}]", 
            "['a','b']", '[\'"a b c"\',\'"\']', '["\'d e f\'","\'","\'\\"\'"]', 
            'st@A{a: 11}', 'st@A{a: 0}', 'st@B{a: 22,b: barro}', "['st@A{a: 33}']", 
            "('st@B{a: 44,b: 55}')", "{'aa':'st@A{a: 66}','bb':'st@B{a: 0,b: b77}'}", 
            "{'p5':1010,'p6':1212,'p7':1414,'p8':1616,'p9':1818,'p10':2020,'p11':2222,'p12':2424,'p13':2626,'p14':2828,'p15':3030,'p16':3232}"]
        self.assertEqual(exv, rvar.vals())

    def test_builtin_split_join_replace(self):
        ''' '''
        code = r'''
        res = []
        
        src1 = "red,green,blue"
        
        res <- split(src1, ',')
        
        src2 = ['hello','dear','string']
        
        res <- join(src2, '_')
        
        src3 = "<div>Hello replace</div>"
        
        res <- replace(src3, 'div', 'span')
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # rvar = ctx.get('res')
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        exp = [['red', 'green', 'blue'], 'hello_dear_string', '<span>Hello replace</span>']
        self.assertEqual(exp, rvar.vals())



if __name__ == '__main__':
    main()
