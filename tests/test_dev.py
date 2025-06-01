

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
from eval import rootContext, moduleContext

from strformat import *


from tests.utils import *

import pdb


class TestDev(TestCase):


    # TODO: type of struct field: list, dict, bool, any


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
            # print('tt2', opt)
            res = fm.format(val, opt)
            print('tt3', slex.options, '>>>', '`%s`' % res)
            self.assertEqual(exp, res)
        

    def test_fstr_split(self):
        ''' StrFormetter.parse '''
        data = [
            # 'ss {aa} dd',
            # 'ss1 {aa1} bb2 {cc2} dd3 {ee3:0.2f} end',
            # 'ss1 {aa1[1]} bb2 {cc2["key-2"]} dd3 {ee3.foo(1,2,3):0.2f} end',
            # 'ss1 {"str value"} 222 {dd.ddd.dddd.ddd[123].foo(1,2,3).ddd["123"].dd.ddd.bar(ddd.baz(vazz(ddd)))} end',
            '{aa_start_line} bb2 {cc2} dd3 {ee3:0.2f} zerolead-int: {a:0d} bin: {a:b} pair: {1}{2}',
            '{} s1 {} s2 {{}} s3 {{aaa}} s4 {{{bbb}}} s5 {{{{ccc}}}} end',
            # 'ss {} {{abc}} dd',
        ]
        # sf = StrFormatter()
        fp = FormatParser()
        for s in data:
            print('t>', s)
            parts = fp.parse(s)
            print('>>', parts)

    def _test_barr(self):
        ''' '''
        code = r'''
        res = 0
        
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
        rvar = ctx.get('res')
        self.assertEqual(0, rvar.getVal())

    def __tt(self):
        '''
        # thoughts about OOP
        
        struct C c:int
        struct D(A,C) d1:int, d2:float
        
        func d:D f1(x, y)
            d.f1(x, y)
            d.a1 = 1
            d.A.f1(x, y) # ??
            d.super().f1(x, y) # ??
            super(d).f1(x, y) # for methods only # ??
        
        #struct D:(A,C) d1:int, d2:float
        
        struct E(A,B)
            A, B
            e1:int
            e2:D
        '''

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
        # print('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res')
        self.assertEqual(0, rvar.getVal())

    def _test_match_for_if_lambda(self):
        ''' '''
        code = r'''
        c = 5
        res = 0
        func foo2(ff)
            ff(11)
        rrs = [0 ; x <- [0..11]]
        f = x -> x * 10
        for i <- [1..10]
            match c
                1 !- res = 10
                2 !- if res > 0
                    res *= 10
                3 !- res = foo2(x -> x ** 2)
                4 !- f = x -> x * 100
                5 !- for i=0; i < 5; i += 1
                    res += i
                _ !- res = 1000
            rrs[i] = res

        # foo = (x, y) -> x ** 2
        # nums = foo(5, 2)
        print('rrs = ', rrs)
        '''
        code = norm(code[1:])
        # print('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_list_gen_by_strings(self):
        ''' thoughts:
            1) [..;..;..] should be a list-generato, not string
            2) [..; s <- "..."] in gen from string we want to get string
            3) ~[s, s <- "..."] solutution (1) `~` operator as a list-to-string convertor
        '''
        code = '''
        strline = 'abcdefg'
        res1 = []
        for s <- strline:
            res1 <- s
        print('res1', res1)
        # src = ['aaa', 'bbb', 'ccc']
        # nums = [x ; ns <- src; x <- ns ; x % 5 > 0]
        # print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_list_gen_comprehention_iter_by_string(self):
        ''' list generator and strings
            case 1: list from string
            case 2: string from string ? 
             -- think about: string is a list of chars, but string is an immutable list
        '''
        code = '''
        src = ['a' .. 'k'] # >> 'abcdef...k' ?? do we need that?
        src = "Hello strings!"
        res = [ [a ; a <- src]
        # print('src = ', src)
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_list_gen_empty_end(self):
        ''' list generator. [... expr;] empty last sub-case after semicolon'''
        code = '''
        nums = [[x ** 2] ; x <- [2..5] ;]
        nums = [[x ** 2] ; x <- [2..5] ; ]
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_tuple_assign_left(self):
        ''' make vars and assign vals from tuple
            
            A) tuple as a result of comma-separated expression: var = a, b, c
            Shuold do:
            1. any value-returning sub-expression, like list constructor
            2. think about common case of `x, x, x` expression; not sure.
            tuple as destination of assignment operator, or: result-to-tuple mapping
            Should do:
            1. reuse defined vars.
            2. declare new vars
            3. allow `_` var
            4. allow type declaration (a:int, b:float) = foo()
            Should not:
            1. contain non-var expressions, like func call, collection constuctors (except tuple), const expr like strings or numbers.
            2. contain incorrect var-type
            -- Thoughts:
                a) left-tuple should have extra property like self.isLeft. 
                    In such case tuple can allow call tuple.setVal(args...)
                b) isLeft sould be changable only in assertion operator in .setArgs method.
                c) mapping list to tuple with the same size looks ok.
            '''
        code = '''
        (a, b, s) = 1,2,3
        print('', a, b, c)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_struct_anon(self):
        code = '''
        user = struct {name:'Anod', age:25, sex:male, phone:'123-45-67'}
        # uf = user.fields()
        print(user.name)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_bin_opers_cases(self):
        ''' test all operators in mixed cases: 
            assignment, math | bool expressions, separators (, ; :), brackets. '''


    _ = '''
        TODO features:
        1. generators extra features
    [-10..10]; [..10] >> IterGen(beg, over, step)

        3. tuple
        
        TODO tests:
    test assignment and read 
    global var and local block
    local var and function-block
    
    '''

if __name__ == '__main__':
    main()
