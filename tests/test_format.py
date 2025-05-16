
from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex

from cases.utils import *

from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from nodes.structs import *

from context import Context
from tree import *
from eval import rootContext

from strformat import *

import pdb


class TestFormat(TestCase):



    def test_sformat_vars(self):
        ''' string formatting: different includes: 
        collection elem, struct fields, func/method call, operators and their conbinations '''
        code = r'''
        
        func intfoo()
            1234
        
        func f100(x)
            x * 100
        
        func floatfoo()
            12.345
        
        func strfoo()
            'abc!!@@'
        
        func foo(a, b)
            a + b
        
        struct A aa1:int, aa2:float, aa3:string
        
        struct B bb1:A, bb2:int
        
        nums = [10, 20, 30]
        dd = {'ka': 11, 'kb':22, 'kc':33}
        sta = A{aa1:4455, aa2:55.68, aa3:'Lulaby'}
        stb = B{bb1:sta, bb2:789}
        # ['q', 'w', 'e']
        
        r1 = ~' Prefix1: {intfoo()} {floatfoo():.3f} {strfoo()} {foo(10, 5)} {foo(200, 33)} '
        r2 = ~' Prefix2: {sta.aa1} {sta.aa2} {sta.aa1:08x} {stb.bb1.aa3} {nums[1]} {dd["kb"]} '
        r3 = (~" Prefix3: {f100(sta.aa1 - 4400)} {f100(dd['kc'])} {foo(stb.bb1.aa1, stb.bb2)} "
            + ~"[{-(nums[1] + dd['kc'] * 2 - foo(sta.aa1, nums[2])):010d}] ")
        # r4 = ~''
        
        res  = [r1, r2, r3]
        print('res = ', res)
        '''
        code = norm(code[1:])
        # print('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        print('tt>>', rvar)
        exp = [' Prefix1: 1234 12.345 abc!!@@ 15 233 ',
               ' Prefix2: 4455 55.68 00001167 Lulaby 20 22 ',
               ' Prefix3: 5500 3300 5244 [0000004399] '
               ]
        self.assertEqual(exp, rvar.vals())

    def test_sformat_types(self):
        ''' string formatting by including expressions into {} '''
        code = r'''
        
        a, b, s, s2 = (123, 12.5, 'ABCabc-$%&', "'#'")
        aa, bb, cc = (0b101100111000, 0xfedcba90, 0o12345670)
        
        r1 = ~'hello int:{a:05d}, float:{b:.3f}, str: {s} `{s2:<6s}` '
        r2 = ~'example2 hex1:{aa:b}, hex2:{bb:x}, oct:{cc:o} '
        res  = [r1, r2]
        print('res = ', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = ["hello int:00123, float:12.500, str: ABCabc-$%& `'#'   ` ", 
               'example2 hex1:101100111000, hex2:fedcba90, oct:12345670 ']
        self.assertEqual(exp, rvar.vals())

    def test_str_formatting(self):
        ''' percent-pattern for string format '''
        code = r'''
        
        r1 = 'hello int:%d, float:%f, str:%s ' << (123, 12.5, 'Lalang')
        r2 = 'example2 hex1:%x, hex2:%x, oct:%o ' << (0b101100111000, 0xfedcba90, 0o12345670)
        res  = [r1, r2]
        print('res = ', res)
        '''
        code = norm(code[1:])
        # print('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exp = ['hello int:123, float:12.500000, str:Lalang ', 
               'example2 hex1:b38, hex2:fedcba90, oct:12345670 ']
        self.assertEqual(exp, rvar.vals())


if __name__ == '__main__':
    main()
