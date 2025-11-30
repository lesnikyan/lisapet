

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
            [A(33)], (B{a:44, b:"55"},), {'aa':A(66), 'bb':B('b77')},
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
        exv = ['1', '0', '500', 'null', 'true', 'false', 
               '', '\\ \\n \\t \\s \\d \\w \\b {} \' " ', 'abc', ' "a" ', " 'b' ", 
               '[]', '[1,2,3]', '(1,2,3)', "{'1':2,'a':'b'}", '[1,2,3,4,5]', 
               "[(10,100),(11,110),(12,120),(13,130),(14,140),(15,150),(16,160),(17,170),(18,180),(19,190),(20,200)]", 
               "[{'k21':2121},{'k22':2222},{'k23':2323},{'k24':2424},{'k25':2525},{'k26':2626},{'k27':2727},{'k28':2828},{'k29':2929}]", 
               "['a','b']", '[\'"a b c"\',\'"\']', '["\'d e f\'","\'","\'\\"\'"]', 
               'st@A{a: 11}', 'st@A{a: 0}', 'st@B{b: barro}', "['st@A{a: 33}']", 
               "('st@B{b: 55}')", "{'aa':'st@A{a: 66}','bb':'st@B{b: b77}'}", 
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
