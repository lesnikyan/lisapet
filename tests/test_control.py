


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
from eval import rootContext, moduleContext

from bases.strformat import *


from tests.utils import *



class TestControl(TestCase):


    def test_for_multisource_gen(self):
        ''' test fix for iter-gen and list-expression in for-loop '''
        code = r'''
        res = []
        
        
        # iter-gen, list-expr
        
        r1 = []
        # aa = [11,22,33,44]
        for a, b <- [101..104], [11,22,33,44]
            r1 <- (a,b)
        res <- r1
        
        # index-gen, iter-gen
        r2 = []
        for a, b <- iter(5), [21..25]
            r2 <- (a, b)
        res <- r2
        
        # iter-gen, list-get
        r3 = []
        for a, b <- [1..5], [x ; x <- [11..15]]
            r3 <- (a, b)
        res <- r3
        
        # function results
        func foo(n)
            [1 .. n]
        
        func bar(s, sep)
            s.split(sep)
        
        r4 = []
        for a, b <- foo(3), bar('aa, bb, cc,', ' ')
            r4 <- (a, b)
        res <- r4
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            [(101, 11), (102, 22), (103, 33), (104, 44)], 
            [(0, 21), (1, 22), (2, 23), (3, 24), (4, 25)], 
            [(1, 11), (2, 12), (3, 13), (4, 14), (5, 15)],
            [(1, 'aa,'), (2, 'bb,'), (3, 'cc,')]]
        self.assertEqual(exv, resv)
        
    def test_for_loop_multisource(self):
        ''' Iterating by several collection sources.
            for a, b, c <- s1, s2, s3  '''
        code = r'''
        res = []
        
        # 2 lists
        nn = [1,2,3,4,5]
        mm = [10, 20, 30, 40, 50]
        
        rr = []
        for x, y <- nn, mm
            rr <- (~'{x}+{y}', x + y)
        res <- rr
        
        # 3 lists
        
        aa = [1,2,3]
        bb = [4,5,6]
        cc = [7,8,9]
        r2 = []
        for x, y, z <- aa, bb, cc
            r2 <- (x, y, z)
        res <- r2
        
        # 5 lists
        a1 = [1,2,3,4]
        a2 = [11,22,33,44]
        a3 = [5,6,7,8]
        a4 = [55,66,77,88]
        a5 = [10, 20, 30, 40]
        r3 = []
        for q, w, e, r, t <- a1, a2, a3, a4, a5
            r3 <- (q,w,e,r,t)
        res <- r3
        
        # list, tuple
        
        aa = [1,2,3,4,5]
        tt = ('a','b','c','d','e')
        r4 = []
        for a, t <- aa, tt
            r4 <- (a, t)
        res <- r4
        
        # list, dict
        
        aa = [1,2,3,4,5]
        dd = {'a':'aaa', 'b':'bbb', 'c':'ccc', 'd':'ddd', 'e':'eee'}
        r5 = []
        for x, k, v <- aa, dd
            r5 <- (x, k, v)
        res <- r5
        
        # list, tuple, dict
        aa = [1,2,3]
        tt = ('A','B','C')
        dd = {'aa':111, 'bb':222, 'cc':333}
        r6 = []
        for a, t, k, v <- aa, tt, dd
            r6 <- (a, t, k, v)
        res <- r6
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            [('1+10', 11), ('2+20', 22), ('3+30', 33), ('4+40', 44), ('5+50', 55)], 
            [(1, 4, 7), (2, 5, 8), (3, 6, 9)], 
            [(1, 11, 5, 55, 10), (2, 22, 6, 66, 20), (3, 33, 7, 77, 30), (4, 44, 8, 88, 40)], 
            [(1, 'a'), (2, 'b'), (3, 'c'), (4, 'd'), (5, 'e')], 
            [(1, 'a', 'aaa'), (2, 'b', 'bbb'), (3, 'c', 'ccc'), (4, 'd', 'ddd'), (5, 'e', 'eee')], 
            [(1, 'A', 'aa', 111), (2, 'B', 'bb', 222), (3, 'C', 'cc', 333)]]
        self.assertEqual(exv, resv)

    def test_match_result(self):
        ''' match-statement return result in the end of function '''
        code = r'''
        res = []
        
        func foo(x)
            match x
                1 /: 101
                2 /: 202
                :: int /: (300, x)
                :: float /: (400, x)
                [*] /: (500, len(x), x)
                s::string /: ('string', s)
                _ /: -11111
        
        ss = [0, 1, 1.2, [], [1,2,3], (1,2), {}, 's1']
        
        res <- 'foo'
        res <- foo(2)
        
        for n <- ss
            res <- foo(n)
        
        # nested control-tails
        
        # match-other
        func foo2(x, y)
            match x
                1
                    if y == 1
                        101
                    else if y  == 2
                        102
                    else
                        103
                2
                    match y
                        1 /: 201
                        2 /: 202
                        :: int /: ('m-int', x, y)
                        :: float /: ('m-float', x, y)
                        _ /: ('_', x, y)
                _
                    if x == y
                        (301, x, y)
                    else
                        (302, x, y)
        
        res <- 'foo2'
        res <- foo2(1,1)
        
        ss2 = [
            (1,2), (1,6), 
            (2,1), (2,2), (2,5), (2, 3.5), (2, [12,34]), 
            (3,1), (3,3), 
            (0,1), (0,0)]
        
        for a, b <- ss2
            res <- foo2(a, b)
        
        # if-other
        
        func foo3(x, y)
            if x == 1
                match y
                    1 /: (101, x, y)
                    2 /: (102, x, y)
                    _ /: (104, x, y)
            else if x > 5
                match y
                    :: int /: ('6-int', x, y)
                    :: float /: ('6-float', x, y)
                    :: list /: ('6-list', x, y)
                    _ /: ('_', x, y)
            else if x  < 0
                match y
                    :: tuple /: ('/tuple', x, y)
                    :: dict /: ('/dict', x, y)
            else
                match y
                    1 /: (401, x, y)
                    :: int /: (402, x, y)
                    _ /: (403, x, y)
            # end of func
        
        res <- 'foo3'
        ss3 = [
            (1,1), (1,2), (1,5),
            (6,1), (7, 2.5), (8, []), (9, [1,2]), (10, {1:1}), 
            (-1, 1), (-2, (,)), (-3, (1,2)), (-4, {}), (-5, {2:22}), 
            (0, 1), (2, 2), (3, 3), (3, null), (3, true), (3, {}), 
        ]
        for a, b <- ss3
            res <- foo3(a, b)
        
        # deep match
        
        func foo4(a, b, c, d, e, f)
            match a
                1 /: 101
                _ 
                    match b
                        1 /: 201
                        _
                            match c
                                1 /: 301
                                _
                                    match d
                                        1 /: 401
                                        _
                                            match e
                                                1 /: 501
                                                _
                                                    match f
                                                        1 /: 601
                                                        2 /: 602
                                                        _ /: ('f', f)
            #...
        
        ss4 = [
            (1,1,1,1,1,1),
            (2,1,1,1,1,1),
            (2,2,1,1,1,1),
            (2,2,2,1,1,1),
            (2,2,2,2,1,1),
            (2,2,2,2,2,1),
            (2,2,2,2,2,2),
            (2,2,2,2,2,3),
        ]
        
        res <- 'foo4'
        for args <- ss4
            res <- foo4(args...)
        
        # not last control
        
        func foo5(x)
            if x == 1
                return 1001
            else 
                2
            3003
        
        res <- foo5(1)
        res <- foo5(2)
        res <- foo5(100)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            'foo', 202, (300, 0), 101, (400, 1.2), (500, 0, []), (500, 3, [1, 2, 3]), 
            -11111, -11111, ('string', 's1'), 
            'foo2', 101, 102, 103, 201, 202, ('m-int', 2, 5), ('m-float', 2, 3.5), 
            ('_', 2, [12, 34]), (302, 3, 1), (301, 3, 3), (302, 0, 1), (301, 0, 0), 
            'foo3', (101, 1, 1), (102, 1, 2), (104, 1, 5), 
            ('6-int', 6, 1), ('6-float', 7, 2.5), 
            ('6-list', 8, []), ('6-list', 9, [1, 2]), ('_', 10, {1: 1}), null, 
            ('/tuple', -2, ()), ('/tuple', -3, (1, 2)), ('/dict', -4, {}), ('/dict', -5, {2: 22}), 
            (401, 0, 1), (402, 2, 2), (402, 3, 3), (403, 3, null), (403, 3, True), (403, 3, {}),
            'foo4', 101, 201, 301, 401, 501, 601, 602, ('f', 3),
            1001, 3003, 3003]
        self.assertEqual(exv, resv)
    
    def test_if_result(self):
        ''' `if` as a last expression of function returns result '''
        code = r'''
        res = []
        
        func foo(x)
            if x == 1
                n = 8
                n + 2
            else if x == 2
                20
            else
                3 * 10
        
        r1 = foo(1)
        res <- r1
        
        res <- foo(2)
        res <- foo(5)
        
        # nested if
        
        func foo2(x, y)
            if x == 1
                if y == 1
                    11
                else
                    12
            else if x == 2
                if y  == 1
                    21
                else if y == 2
                    22
                else
                    23
            else if x == 3
                30
            else
                50

        res <- 'foo2'
        res <- foo2(1,1)
        res <- foo2(1,3)
        res <- foo2(2,1)
        res <- foo2(2,2)
        res <- foo2(2,6)
        res <- foo2(3,100)
        res <- foo2(4,200)
        
        # deep nesting
        
        func foo3(x)
            if x > 1
                if x > 2
                    if x > 3
                        if x > 4
                            if x > 5
                                10
                            else
                                5
                        else
                            4
                    else
                        3
                else
                    2
            else
                1
            # end of function
        
        res <- 'foo3'
        res <- foo3(1)
        res <- foo3(2)
        res <- foo3(3)
        res <- foo3(4)
        res <- foo3(5)
        res <- foo3(6)

        # in method
        
        struct A a:int
        
        func n:A f()
            if n.a == 1
                11
            else if n.a == 2
                22
            else
                33
        
        res <- 'A.f'
        
        a1 = A(1)
        res <- a1.f()
        
        a2 = A(2)
        res <- a2.f()
        
        a3 = A(12)
        res <- a3.f()
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [10, 20, 30, 'foo2', 11, 12, 21, 22, 23, 30, 50, 'foo3', 1, 2, 3, 4, 5, 10, 'A.f', 11, 22, 33]
        self.assertEqual(exv, resv)

    def test_for_arrow_multival(self):
        ''' test arrow-assign `a <- b` 
            unpack and multiassign if several vars in left: a,b,c <- data
            no unpack if 1 var: n <- data
        '''
        code = r'''
        res = []
        
        # nn = [(1,2,3), (4,5,6)]
        nnT = [(x, x+2, x+3); i <- [2..5]; x = i * 4]
        
        # @debug !123
        
        # unpack tuple to vars
        for a,b,c <- nnT
            s = ~'{a:02d}:{b:02d}:{c:02d}'
            res <- s
        
        # list of tuples, no unpack
        for elem <- nnT
            res <- elem
        
        nnL = [[x, x+3, x+5]; i <- [2..5]; x = i * 10]
        # unpack list to vars
        for a,b,c <- nnL
            s = ~'{a:02d}:{b:02d}:{c:02d}'
            res <- s
        
        # list of lists, no unpack
        for elem <- nnL
            res <- elem
        
        nn2 = [1,2,3,4,5]
        # iter by list
        for n <- nn2
            res <- 'nn2_%d' <<n
        
        dd = {1:11, 2:22}
        
        # iter by dict, assigning key, val
        for k, v <- dd
            res <- ~'dd_{k},{v}'
        
        # iter by dict, assigning pair of (key, val)
        for elem <- dd
            res <- 'dd_(%d,%d)' << elem
        
        # unpack list in generator
        src = [[1,2], [3,4]]
        nums = [ x ; sub <- src ; x <- sub]
        res <- ('nums', nums)
        
        # iter by tuple
        tt = (1,2,3,4,5)
        for n <- tt
            res <- ~'tt_{n}'
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            '08:10:11', '12:14:15', '16:18:19', '20:22:23', 
            (8, 10, 11), (12, 14, 15), (16, 18, 19), (20, 22, 23), 
            '20:23:25', '30:33:35', '40:43:45', '50:53:55', 
            [20, 23, 25], [30, 33, 35], [40, 43, 45], [50, 53, 55], 
            'nn2_1', 'nn2_2', 'nn2_3', 'nn2_4', 'nn2_5', 
            'dd_1,11', 'dd_2,22', 'dd_(1,11)', 'dd_(2,22)', 
            ('nums', [1, 2, 3, 4]), 'tt_1', 'tt_2', 'tt_3', 'tt_4', 'tt_5']
        self.assertEqual(exv, rvar.vals())

    def test_inline_controls(self):
        ''' for /: if /: '''
        code = r'''
        res = []
        
        # simple for
        for i <- [11,22,33] /: res <- i
        
        # with subs in ()
        for i <- [1..10] /: x = i * 5; (if i > 5 /:  res <- x); (if y = i * 3; y < 12 /:  res <- y * 100)
        
        # print('len res=', len(res))
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
            self.assertEqual(45, res.getVal())

    def test_for_expr(self):
        code = '''
        y = 0
        a = 100
        b = 0
        # @debug 1
        dd1 = 1000
        for i=0; i < x; i = i + 1
            y = y + 2
            for j=-3; j <= 0; j = j + 1
                a = a - j ** 2
                if a % 2 == 0
                    b += 1
                    dd1 -= (a + b)
        res = y
        '''
        code = norm(code[1:])
        data = [0, 1, 4, 5, 10, 200]
        expd = [1000, 825, 444, 365, 330, 443600]
        # data = [6]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for i in range(len(data)):
            x = data[i]
            ctx = Context(None)
            vv = Var('x', TypeInt())
            vv.set(Val(x, TypeInt()))
            ctx.addSet({'x': vv})
            ex.do(ctx)
            rr = [ctx.get('res').get(), ctx.get('a').get() , ctx.get('b').get()]
            ress.append(rr)
            # rval = ctx.get('res').get()
            rdd = ctx.get('dd1').get()
            self.assertEqual(expd[i], rdd.getVal())

    def test_while_expr(self):
        code = '''
        y = 0
        z = 2
        a = 0
        # @debug 1
        while y < x
            z += 1
            y += 2
            if y % 2 == 0
                a += 3
        res = y + a + z
        '''
        code = norm(code[1:])
        data = [0, 1, 4, 200]
        exx = [2, 8, 14, 602]
        # data = [6]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        for i in range(4):
            x = data[i]
            exv = exx[i]
            ctx = rootContext()
            vv = Var('x', TypeInt())
            vv.set(Val(x, TypeInt()))
            ctx.addSet({'x': vv})
            ex.do(ctx)
            ress.append(ctx.get('res').get())
            self.assertEqual(exv, ctx.get('res').get().getVal())
            # print('##################t-IF1:', ctx.get('res').get())


if __name__ == '__main__':
    main()
