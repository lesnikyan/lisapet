


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



class TestControl(TestCase):


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

    def test_for_if_for_case(self):
        ''' '''
        code = r'''
        
        res = 1
        
        func sumInter(a, b)
            r = 0
            for n <- [a..b]
                r += n
            r
        
        func sum(nn)
            r = 0
            # print([i; i <-nn])
            for n <- nn
                # print('n:', n)
                r += n
            r
        
        fres = []
        
        for n <- [-2..10]
            nums = [n .. (-2 * n)]
            res = sum(nums)
            if n > 0 && n < 5
                b = n ** 2
                res = sumInter(n, b)
            else if n % 5 == 0
                res = 5 * n
            else if n ?> [5, 6, 7]
                res = 100 + n
            else if n < 0
                nums = [n .. (-2 * n)]
                res = sum(nums)
            else
                res = 1000
                for k <- [10 + n .. 20 + n]
                    res += k
            fres <- res
            # print('~', n, res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('fres').get()
        dprint('T>>', rvar.vals())
        exp = [7, 2, 0, 1, 9, 42, 130, 25, 106, 107, 1253, 1264, 50]
        self.assertEqual(exp, rvar.vals())

    def test_else_if_nested_if(self):
        ''' '''
        code = r'''
        
        res = 1
        
        if a == 2
            res = 2
        if a == 2
            res = 2
        else if b == 15
            res = 15
        else if a > 2
            res = 8
            if b == 1
                res = 101
            else if b == 2
                res = 102
            else if b == 3
                res = 103
            else if b == 4 || b == 5 || b == 6
                res = 105
            else if b == 7 && a == 3
                res = 110 
            else if b >= 8 && b <= 12 
                res = 108
                if a == 3
                    res = 123
                    if b == 10
                        res = 130
                    else
                        res = 133
                    if b == 12
                        res = 122
                else if a == 4 && b == 9
                    res = 124
                else if a == 5 && b == 9
                    res = 125
                else
                    if b > 8
                        res = 129
            else if b < 20
                if b != 13
                    res = 199
        else if a < 0
            res = 1001
        else
            res = 7

        #print(a, b, ' : res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        data = [
            (2, 0, 2),
            (0, 15, 15),
            (0, 1, 7),
            (11, 13, 8),
            (11, 14, 199),
            (3, 1, 101),
            (3, 2, 102),
            (3, 3, 103),
            (3, 4, 105),
            (3, 5, 105),
            (3, 6, 105),
            (4, 6, 105),
            (3, 7, 110),
            (4, 7, 199),
            (4, 8, 108),
            (4, 10, 129),
            (3, 8, 133),
            (3, 10, 130),
            (3, 12, 122),
            (4, 9, 124),
            (5, 9, 125),
            (5, 10, 129),
            (10, 7, 199),
            (-10, 10, 1001),
            (1, 1, 7),
            (0, 100, 7),
        ]
        for nn in data:
            a, b, exp = nn
            dprint('>>>', a, b, exp)
            vals = {'a': ivar('a', a), 'b': ivar('b', b)}
            ctx.addSet(vals)
            ex.do(ctx)
            rvar = ctx.get('res')
            self.assertEqual(exp, rvar.getVal())

    def test_else_if(self):
        ''' '''
        code = r'''
        
        res = 1
        
        if a == 2
            res = 2
        else if b == 5
            res = 5
        else if a > 2 &&  a == b
            res = 8
        else
            res = 7

        #print(a, b, ' : res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        data = [
            (2, 0, 2),
            (0, 5, 5),
            (0, 1, 7),
            (11, 11, 8)
        ]
        for nn in data:
            a, b, exp = nn
            dprint('>>>', a, b, exp)
            vals = {'a': ivar('a', a), 'b': ivar('b', b)}
            ctx.addSet(vals)
            ex.do(ctx)
            rvar = ctx.get('res')
            self.assertEqual(exp, rvar.getVal())

    def test_if_preset(self):
        ''' '''
        code = r'''
        
        res = []
        for i <- [1..4]
            if n = 10 * i ; n < 30
                res <- n
            else
                res <- i * 3
        
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
        rvar = ctx.get('res').get()
        self.assertEqual([10, 20, 9, 12], rvar.vals())  

    def test_match_val(self):
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

    def test_if_else(self):
        # code = '''
        # res = 100
        # if x >= 10 | x < 2 && x != 0
        #     res = 2000 + x * -10 - 700
        # else
        #     x = x ** 2
        #     res = 1000 + x - 500
        #     # if res < 500
        #     #     res = res + 10000
        # '''
        code = '''
        res = 100
        # y = 0
        if x >= 30 | (x < 2 && x != 0)
            res = 11
        else
            # x = x ** 2
            res = 22
            if res + x > 30
                res = res + x
                res = 33
                @debug 1
                # y = 1
                y = x + res
                res = y
        '''
        # code = ''.join([s[8:] for s in code.splitlines()])
        code = norm(code[1:])
        data = [0, 1, 4, 5, 10, 20, 30, 40, 100, 200]
        # data = [10, 20]
        # lang.FullPrint = 1
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for x in data:
            ctx =rootContext()
            vv = Var('x', TypeInt)
            vv.set(Val(x, TypeInt))
            ctx.addSet({'x': vv})
            print('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            ress.append(ctx.get('res').get())
            dprint('##################t-IF1:', ctx.get('res').get())
        dprint('all:', ress)

    def test_for_iter(self):
        src = [
        '''
        res = 0
        for i <- iter(10)
            res += i
        print('res: ', res)
        ''',
        '''
        res = 0
        for i <- [1,2,3,4,5,6,7,8,9]
            res += i
        print('res: ', res)
        '''
        ]
        for code in src:
            code = norm(code[1:])
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            ex = lex2tree(clines)
            ctx = rootContext()
            ex.do(ctx)
            res = ctx.get('res').get()
            dprint('##################t-IF1:', )
            # self.assertEqual(res, 45)

    def test_for_expr(self):
        code = '''
        y = 0
        a = 100
        b = 0
        @debug 1
        for i=0; i < 5; i = i + 1
            y = y + 2
            for j=-3; j <= 0; j = j + 1
                a = a - j ** 2
                if a % 2 == 0
                    b = b + 1
        res = y
        '''
        code = norm(code[1:])
        # data = [0, 1, 4, 5, 10, 20, 30, 40, 100, 200]
        data = [6]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for x in data:
            ctx = Context(None)
            vv = Var('x', TypeInt)
            vv.set(x)
            ctx.addSet({'x': vv})
            dprint('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            rr = [ctx.get('res').get(), ctx.get('a').get() , ctx.get('b').get()]
            ress.append(rr)
            # ress.append(ctx.get('a').get())
            dprint('##################t-IF1:', ctx.get('res').get())
        dprint('all:', ress)

    def test_while_expr(self):
        code = '''
        y = 0
        z = 2
        a = 0
        @debug 1
        while y < x
            z = z + z
            y = y + 1
            if y % 2 == 0
                a = a + 1
        res = y
        '''
        code = norm(code[1:])
        # dprint('!!')
        # dprint(code)
        # data = [0, 1, 4, 5, 10, 20, 30, 40, 100, 200]
        data = [6]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for x in data:
            ctx = rootContext()
            vv = Var('x', TypeInt())
            vv.set(Val(x, TypeInt()))
            ctx.addSet({'x': vv})
            dprint('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            ress.append(ctx.get('res').get())
            ress.append(ctx.get('a').get())
            dprint('##################t-IF1:', ctx.get('res').get())
        dprint('all:', ress)



if __name__ == '__main__':
    main()
