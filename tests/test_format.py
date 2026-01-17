
from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex

from cases.utils import *

from nodes.tnodes import Var
from objects.func import Function
from nodes.func_expr import setNativeFunc
from nodes.structs import *

from context import Context
from tree import *
from eval import rootContext

from bases.strformat import *

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
        # print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        # dprint('tt>>', rvar)
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
        # print('res = ', res)
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

    def test_fstr_opt_parser(self):
        ''' {x:s}, {x:d}, {x:05d}, {x:+07.3f} {x:x} '''
        data = [
            # (src, exp, val)
            # ('{}', '{}', 123),
            ('{x}', '4058', 0xfda),
            ('{x}', 'abc', 'abc'),
            ('{x:s}', 'abc', 'abc'),
            ('{x:10s}', '       abc', 'abc'),
            ('{x:<10s}', 'abc       ', 'abc'),
            ('{x:b}', '111111011010', 0b111111011010),
            ('{x:o}', '7732', 0o7732),
            ('{x:d}', '1234', 1234),
            ('{x:6d}', '  1234', 1234),
            ('{x:06d}', '001234', 1234),
            ('{x:+06d}', '+01234', 1234),
            ('{x:+6d}', ' +1234', 1234),
            ('{x:-06d}', '001234', 1234),
            ('{x:-06d}', '-01234', -1234),
            ('{x:f}', '12.34567', 12.34567),
            ('{x:.3f}', '12.345', 12.34567),
            ('{x:+6.3f}', '+12.345', 12.34567),
            ('{x:-6.3f}', '12.345', 12.34567),
            ('{x:-6.3f}', '-12.345', -12.34567),
            ('{x:7.3f}', ' 12.345', 12.34567),
            ('{x:07.2f}', '0012.34', 12.34567),
            ('{x:07.2f}', '-012.34', -12.34567),
            ('{x:+7.3f}', '+12.345', 12.34567),
            ('{x:>+8.3f}', ' -12.345', -12.34567),
            ('{x:+07.3f}', '+12.345', 12.34567),
            ('{x:+07.3f}', '-12.345', -12.34567),
            ('{x:<08.3f}', '12.345  ', 12.34567),
            ('{x:>08.3f}', '0012.345', 12.34567),
            ('{x:^012.3f}', '   12.345   ', 12.34567),
            
            ('{x:x}', 'fda', 0xfda),
            ('{x:6x}', '   fda', 0xfda),
            ('{x:06x}', '000fda', 0xfda),
            ('{x:+06x}', '+00fda', 0xfda),
            ('{x:-06x}', '000fda', 0xfda),
            # ('{x:<+06x}', '+fda  ', 0xfda), # BUG: 1 space more
            ('{x:>+06x}', '+00fda', 0xfda),
            ('{x:>+6x}', '  +fda', 0xfda),
            # ('{x:^05x}', ' fda  ', 0xfda), # BUG: No zeros
            ('{x:^06x}', ' fda  ', 0xfda),
            # ('{x:^06x}', ' -fda ', -0xfda), # BUG: No zeros
            ('{x:^02x}', '-fda', -0xfda),
            # 
            # :e - Need fix
            # ('{x:e}', '5.12345e+03', 5.12345e+03), 
            # ('{x:e}', '', 5.12345e-03),
            # ('{x:16e}', '', 5.12345e+03),
            # ('{x:016e}', '', 5.12345e-03),
            
            ('{x:b}', '10101', 0b10101),
            ('{x:10b}', '     10101', 0b10101),
            ('{x:+010b}', '+000010101', 0b10101),
            ('{x:10o}', '   1234567', 0o1234567),
            ('{x:010o}', '0001234567', 0o1234567),
            ('{x:+010o}', '+001234567', 0o1234567),
            ('{x:+010o}', '-001234567', -0o1234567),
            # ('{x}', '', 0xfda),
        ]
        
        fop = FmtOptParser()
        fp = FormatParser()
        fm = Formatter()
        for tt in data:
            src, exp, val = tt
            parts = fp.parse(src)
            slex:subLex = parts[1]
            opt = fop.parseSuff(slex.options)
            # dprint('tt2', opt)
            res = fm.format(val, opt)
            # dprint('tt3', slex.options, '>>>', '`%s`' % res)
            self.assertEqual(exp, res)

    def test_fstr_split(self):
        ''' StrFormatter.parse '''
        data = [
            'ss {aa} dd',
            'ss1 {aa1} bb2 {cc2} dd3 {ee3:0.2f} end',
            'ss1 {aa1[1]} bb2 {cc2["key-2"]} dd3 {ee3.foo(1,2,3):0.2f} end',
            'ss1 {"str value"} 222 {dd.ddd.dddd.ddd[123].foo(1,2,3).ddd["123"].dd.ddd.bar(ddd.baz(vazz(ddd)))} end',
            '{aa_start_line} bb2 {cc2} dd3 {ee3:0.2f} zerolead-int: {a:0d} bin: {a:b} pair: {1}{2}',
            '{} s1 {} s2 {{}} s3 {{aaa}} s4 {{{bbb}}} s5 {{{{ccc}}}} end',
            'ss {} {{abc}} dd',
        ]
        # sf = StrFormatter()
        fp = FormatParser()
        for s in data:
            # dprint('t>', s)
            parts = fp.parse(s)
            # dprint('>>', parts)

    def test_str_formatting(self):
        ''' percent-pattern for string format '''
        code = r'''
        
        r1 = 'hello int:%d, float:%f, str:%s ' << (123, 12.5, 'Lalang')
        r2 = 'example2 hex1:%x, hex2:%x, oct:%o ' << (0b101100111000, 0xfedcba90, 0o12345670)
        res  = [r1, r2]
        # print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
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
