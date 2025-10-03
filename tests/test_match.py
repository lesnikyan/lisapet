

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



class TestMatch(TestCase):
    ''' cases of `match` statement '''
    

    def test_match_strings(self):
        ''' '''
        code = r'''
        
        ss = [' ', 'aaa', 'bbb', 'bcd', '123', '']
        res = []
        
        for s <- ss
            match s
                '' !-      res <- [s, 1]
                ' ' !-      res <- [s, 2]
                'aaa' !-   res <- [s, 3]
                'b' !-     res <- [s, 4]
                'bcd' !-   res <- [s, 5]
                '123' !-   res <- [s, 123]
                _ !-
                    res <- [s, 1000]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        # print('..tt>')
        ex.do(ctx)
        exp = [[' ', 2], ['aaa', 3], ['bbb', 1000], ['bcd', 5], ['123', 123], ['', 1]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())
    

    def test_basic_match(self):
        ''' '''
        code = r'''
        
        nn = [1,2,3, 1]
        res = []
        
        for n <- nn
            match n
                1 !- res <- [n,111]
                2 !- res <- [n,222]
                _ !- res <- [n,999]
        
        print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        exp = [[1, 111], [2, 222], [3, 999], [1, 111]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())

    def _test_match_var_case(self):
        '''
        TODO: do we need var as a pattern?
        '''
        code = '''
        a = 4
        r1 = 0
        b = 3
        match a
            1  !- r1 = 100
            10 !- r1 = 200
            b  !- r1 = 300
            _  !- r1 = -2
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        exp.do(ctx)
        r1 = ctx.get('r1').get()
        dprint('#t >>> r:', r1)

    def test_match_for_if_lambda(self):
        ''' TODO: match with for loop, `if` statement in the same case line '''
        code = r'''
        c = 5
        res = 0
        func foo2(ff)
            ff(11)
        rrs = [] # [0 ; x <- [0..11]]
        ff = x -> x * 10
        for i <- [0..8]
            print('i:', i)
            res = 1
            t = i + 10
            match i
                1 !- res = 10
                2 !- 
                    if res > 0 && res < 4
                        print('c2', i, res)
                        res *= 11 * i
                3 !- res = foo2(x -> x ** 2)
                4 !- f = x -> x * 12
                    res = f(i)
                5 !- res = foo2(ff) + i
                6 !- 
                    for j <- [0..5]
                        print('c5', j, res)
                        res += i
                7 !- 
                    for j = 1; j < 6; j = j + 1
                        print('c7', j, res)
                        res *= j
                8 !- 
                    if c= t + 100; c > 110 && t > 4
                        print('c2', i, res)
                        res = c
                _ !- res = 1001
            rrs <- res

        print('rrs = ', rrs)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('rrs').get()
        self.assertEqual([1001, 10, 22, 121, 48, 115, 37, 120, 118], rvar.vals())


    def test_CaseMatchSub_match(self):
        cs = CaseMatchCase()
        rrs = []
        def checkRes(code, exp):
            dprint('$$ run test ------------------')
            dprint('CODE:','\n'+code)
            # code = lines[0]
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            res = cs.match(elems)
            dprint('#tt >>> ', code, res)
            msg = 'Tried use code: %s' % code
            if exp:
                self.assertTrue(res, msg)
            else:
                self.assertFalse(res, msg)
            
        src = ''''
        val !- expr
        123 !- a + b
        234 !- r = 2 + 3
        3 !- res = 4
        user(123) !- res
        '''
        src = norm(src[1:].rstrip())
        data = src.splitlines()
        for code in data:
            if code.strip() == '':
                continue
            checkRes(code, True)
        
        src = ''''
        val 123 -> expr
        1,2,3 -> a + b
        x <- src
        -> expr ...
        user(123) + 0 -> res
        '''
        src = norm(src[1:].rstrip())
        data = src.splitlines()
        for code in data:
            if code.strip() == '':
                continue
            checkRes(code, False)


if __name__ == '__main__':
    main()
