


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


    def test_inline_controls(self):
        ''' for /: if /: '''
        code = r'''
        res = []
        
        # simple for
        for i <- [11,22,33] /: res <- i
        
        # with subs in ()
        for i <- [1..10] /: x = i * 5; (if i > 5 /:  res <- x); (if y = i * 3; y < 12 /:  res <- y * 100)
        
        # for /: if /:
        r2 = []
        for n <- res /:  if n % 2 > 0 /: k=n; n += 1 ; r2 <- n + 1000
        res += r2
        
        # expression before controls
        r3 = []; (for i <- [1..5] /: if n=i*2; n >5 /: x = i * 10; y = i + 100; r3 <- (x + y))
        res += r3
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        # lang.FullPrint = 1
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx:Context = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # rvar = ctx.get('res')
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        exp = [11, 22, 33, 300, 600, 900, 30, 35, 40, 45, 50, 1012, 1034, 1036, 1046, 133, 144, 155]
        self.assertEqual(exp, rvar.vals())


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
        # dprint('T>>', rvar.vals())
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
        self.assertEqual([10, 20, 9, 12], rvar.vals())  

    def test_if_else(self):
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
                # @debug 1
                # y = 1
                y = x + res
                res = y
        '''
        code = norm(code[1:])
        data = [0, 1, 4, 5, 10, 20, 30, 40]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for x in data:
            ctx =rootContext()
            vv = Var('x', TypeInt())
            vv.set(Val(x, TypeInt()))
            ctx.addSet({'x': vv})
            # print('~~~~ test case: %d ~~~~' % x)
            ex.do(ctx)
            ress.append(ctx.get('res').getVal())
        #     dprint('##################t-IF1:', ctx.get('res').get())
        # print('all:', ress)
        exv = [22, 11, 22, 22, 43, 53, 11, 11]
        self.assertEqual(exv, ress)

    def test_for_iter(self):
        src = [
        '''
        res = 0
        for i <- iter(10)
            res += i
        # print('res: ', res)
        ''',
        '''
        res = 0
        for i <- [1,2,3,4,5,6,7,8,9]
            res += i
        # print('res: ', res)
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
