'''
'''



from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from eval import rootContext, moduleContext
from tree import *
from context import Context

# from cases.utils import *
# from nodes.tnodes import Var
# from objects.func import Function
# from nodes.func_expr import setNativeFunc
# from nodes.structs import *



class TestIter(TestCase):
    ''' iteration cases '''



    def test_fix_str_repeate_in_sub_string_compr_in_gen(self):
        ''' fix of BUG:
        ['1:2-->', '1:3----->', '1:2------->', '1:3---------->', '1:2------------>','''
        code = r'''
        res = []
        
        # g1 = (: (~'1:{d}|' + ~['-'; _ <-iter(d)] + '>', d, [n ; n <- iter(d)]) ; a <-[1,2,3]; b <-[5..7]; c <-['','']; d <-[2,3])
        g1 = (: (~'1:{d}{k}' + '>') ; a <-[1,2,3]; d <-[2,3]; k = ~['-'; _ <-iter(d)])
        res <- [n ; n <- g1]
        
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
        exv = [['1:2-->', '1:3--->', '1:2-->', '1:3--->', '1:2-->', '1:3--->']]
        self.assertEqual(exv, resv)

    def test_multisource_for_iter_gen(self):
        ''' '''
        code = r'''
        res = []
        
        # x3 + bool
        
        nn1 = [1..9]
        ss1 = 'absdefgh'
        aa1 = [1,2,3,4,5,6,7,8,9,0]
        g1 = (: ~'{s}{d+c}' ; s, n, a <- ss1, nn1, aa1; d = n * 10 + a; a > 2 && n % 2 > 0; c <- [100, 200])
        res <- [n ; n <- g1]
        
        # 3 x 3
        
        g2 = (: (g + h + i, (a*100 + b * 10 + c)*1000 + d*10 + e + f);
            a, b, c <- [1..3], [4..6], [7..9];
            d, e, f <- [10,20], [30,40], [5,6];
            g,h,i <- 'ab', 'cd', 'ef'
        )
        
        # gen to string comprehension
        res <- ~[ ~'{s}-{n} ' ; s, n <- g2]
        
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
            ['s133', 's233', 'e155', 'e255', 'g177', 'g277'], 
            'ace-147135 bdf-147135 ace-147246 bdf-147246 ace-258135 bdf-258135 ace-258246 bdf-258246 ace-369135 bdf-369135 ace-369246 bdf-369246 ']
        self.assertEqual(exv, resv)

    def test_code_generator_in_comprh(self):
        ''' [ ; <- (: <- )] '''
        code = r'''
        res = []
        
        # gen to list
        
        g1 = (: x ; x <- [1..10] ; x % 2 == 0 )
        
        res <- [n ; n <- g1]
        
        # 3 loops
        
        g2 = (: ~'{z}{d}';
            x <- [3..5];
            y <- [10,20,30]; d = x + y; d % 3 == 0;
            z <- ['a', 'b', 'c']; true
        )
        
        res <- [n ; n <- g2]
        
        # gen to dict { ; (: )}
        g3 = (: (k, bytes(v).string()); 
            n <- [1..3]; n != 2; 
            m <- [15 .. 17]; k = n * 100 + m; v = [50 + m, 81+n*3+m]; m % 2 > 0)
        res <- {k:v ;  k, v <- g3}
        
        # gen to string
        
        s4 = 'hello here, dude!'.split(re`\b`)
        g4 = (: s ; s <- s4; re`\w+` =~ s)
        res <- ~[~'<{s}>' ; s <- g4]
        
        # bytes
        s5 = 'abc 123'.bytes()
        g5 = (: b ; b <- s5 )
        res <- 0x[t ; t <- g5]
        
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
            [2, 4, 6, 8, 10], 
            ['a33', 'b33', 'c33', 'a24', 'b24', 'c24', 'a15', 'b15', 'c15'], 
            {115: 'Ac', 117: 'Ce', 315: 'Ai', 317: 'Ck'}, 
            '<hello><here><dude>', 
            '0x[61 62 63 20 31 32 33]']
        self.assertEqual(exv, resv)

    def test_generator_in_for(self):
        ''' gen = (: n + 5 ; n <- nn ; n > 0 )
        from 1 up to 5 source-iterators (: <- ; <- ; <- ; <- ; <- ;)'''
        code = r'''
        res = []
        
        # simplest case
        g0 = (: n *100 + n * 2 ; n <- [1 .. 3])
        
        r = []
        for i <- g0
            r <- i
        res <- r
        
        # 2 iterations
        
        g1 = (: n * 100 + m ; n <- [1 .. 3]; m <- [5 , 6, 7])
        
        r1 = []
        for i <- g1
            r1 <- i
        res <- r1
        
        # 1 iter with filter
        
        g2 = (: n + 10 ; n <- [1..7] ; n % 2 != 0 )
        r2 = []
        for i <- g2
            r2 <- i
        res <- r2
        
        # 2 iters with filter
        
        g3 = (: n * 100 + m ; n <- [1 .. 5]; m <- [6 .. 9]; n % 2 != 0 && m % 3 == 0)
        
        r3 = []
        for i <- g3
            r3 <- i
        res <- r3
        
        # 3 iters
        
        g4 = (: n * 1000 + m * 10 + k ; n <- [33 , 44]; m <- [6 .. 7]; k <- [1, 2])
        
        r4 = []
        for i <- g4
            r4 <- i
        res <- r4
        
        # 3 iters + final filter
        
        res <- 'r5'
        
        g5 = (: (z) ; n <- [1 .. 3]; m <- [6 .. 9]; k <- [11 .. 17] ; z = (n,m,k); m > 7 && k % 3 == 0 )
        # n * 1000 + m * 100 + k, 
        r5 = []
        for i <- g5
            r5 <- i
        res <- r5
        
        # 3 iters all with filters
        
        g6 = (: 100*a + b + c; 
            a <- [-1, 1, -2, 2, -3, 3] ; a > 0 ; 
            b <- [-10, 10, -20, 20, -30, 30]; b > 0; 
            c <- [-5, 5, -6, 6, -7, 7]; c > 0 )
        # a * 1000 + b + c , ((a, b, c))
        r6 = []
        for i <- g6
            r6 <- i
        res <- r6
        
        # 4 iters
        
        # res = []
        
        g7 = (: ~'{a}/{b}/{c}/{d}'  ; a <-[1..3]; a !=2; b <-[5..7]; b !=6; c <-['a','b']; d <-['?','!'] )
        r7 = []
        for i <- g7
            r7 <- i
        res <- r7
        
        # 5 iters
        
        # res = []
        
        g8 = (: ~'{a}{b}{c}{d}{e}'  ; a <-[1,2,3]; b <-[5,7]; c <-[11,12]; d <-['a','b']; e <- ['d','e']; a !=2 && c + b ?> [16, 19])
        r8 = []
        for i <- g8
            r8 <- i
        res <- r8
        
        # 5 iters with all filters
        
        # res = []
        
        g9 = (: ~'{a}{b}{c}{d}{e} {t}'  ; 
            a <-[1,2,3,4]; a != 2 && a < 4;
            b <-[5..9]; b %2 != 0;
            c <-[11,12, 13, 14, 15]; c !?>  [13,14,11]; 
            d <-['a','b']; rc = c % 2; rc == 0 && d =='b' || rc != 0 && d == 'a';
            e <- ['d','e']; t = b-a; t > 7 )
        r9 = []
        for i <- g9
            r9 <- i
        res <- r9
        
        
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
            [102, 204, 306], 
            [105, 106, 107, 205, 206, 207, 305, 306, 307], 
            [11, 13, 15, 17], 
            [106, 109, 306, 309, 506, 509], 
            [33061, 33062, 33071, 33072, 44061, 44062, 44071, 44072], 
            'r5', [(1, 8, 12), (1, 8, 15), (1, 9, 12), (1, 9, 15), (2, 8, 12), (2, 8, 15), (2, 9, 12), (2, 9, 15), (3, 8, 12), (3, 8, 15), (3, 9, 12), (3, 9, 15)], 
            [115, 116, 117, 125, 126, 127, 135, 136, 137, 215, 216, 217, 225, 226, 227, 235, 236, 237, 315, 316, 317, 325, 326, 327, 335, 336, 337], 
            ['1/5/a/?', '1/5/a/!', '1/5/b/?', '1/5/b/!', '1/7/a/?', '1/7/a/!', '1/7/b/?', '1/7/b/!', 
             '3/5/a/?', '3/5/a/!', '3/5/b/?', '3/5/b/!', '3/7/a/?', '3/7/a/!', '3/7/b/?', '3/7/b/!'], 
            ['1511ad', '1511ae', '1511bd', '1511be', '1712ad', '1712ae', '1712bd', '1712be', '3511ad', '3511ae', '3511bd', '3511be', '3712ad', '3712ae', '3712bd', '3712be'], 
            ['1912bd 8', '1912be 8', '1915ad 8', '1915ae 8']]
        self.assertEqual(exv, resv)

    def test_slice_iter_gen(self):
        ''' '''
        code = r'''
        res = []
        
        ss1 = [1..9]
        res <- ss1[2:7]
        
        res <- [11..19][2:7]

        res <- [11..19][:]
        
        func nns(a, b)
            return [a..b]
        
        res <- nns(3, 8)[1:-1]
        res <- nns(5,10)[:]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            [3, 4, 5, 6, 7], 
            [13, 14, 15, 16, 17], 
            [11, 12, 13, 14, 15, 16, 17, 18, 19], 
            [4, 5, 6, 7], 
            [5, 6, 7, 8, 9, 10]]
        self.assertEqual(exv, resv)

    def test_iter_negative(self):
        '''back iter with negative step '''
        code = r'''
        res = []
        
        r = []
        for n <- iter(2,8,2)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(5)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(10, 5, -1)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(5, 0, -1)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(5, -1, -1)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(6, -2, -2)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(6, -5, -2)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(5, -2, -3)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(0, 101, 25)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(100, -1, -25)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(-2, -11, -4)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(2**30, 2 **30+5, 1)
            r <- n
        res <- (r)
        
        r = []
        for n <- iter(-1000000, -1000005, -1)
            r <- n
        res <- (r)
        
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
            [2, 4, 6], 
            [0, 1, 2, 3, 4], 
            [10, 9, 8, 7, 6], 
            [5, 4, 3, 2, 1], 
            [5, 4, 3, 2, 1, 0], 
            [6, 4, 2, 0], 
            [6, 4, 2, 0, -2, -4], 
            [5, 2, -1], 
            [0, 25, 50, 75, 100], 
            [100, 75, 50, 25, 0], 
            [-2, -6, -10],
            [1073741824, 1073741825, 1073741826, 1073741827, 1073741828],
            [-1000000, -1000001, -1000002, -1000003, -1000004]]
        self.assertEqual(exv, resv)

    def test_string_comprehension(self):
        ''' '''
        code = r'''
        res = []
        
        
        # List by string

        # list gen from string
        r1 = [ g ; g <- 'abc']
        res <- r1
        
        # list gen mixed source string, list
        a2 = [1,2,3]
        s2 = 'def'
        r2 = [~'{s}{n}' ; s, n <- s2, a2 ; n > 1]
        res <- r2
        
        
        # String from glifs
        
        # from string ~[;  <- '']
        r3 = ~[ s ; s <- 'Hello!']
        res <- r3
        
        # from bytes ~[ ; n <- 0x[]]
        bb4 = 0x[41 42 43 44 21 61 62 63]
        r4 = ~[glif(b) ; b <- bb4]
        res <- r4
        
        # from numbers ~[ ; n <- [41..50]]
        r5 = ~[ glif(n); n <- [80.. 85]]
        res <- r5
        
        
        # String from strings
        
        # from list of sttrings ~[wd ; wd <- ['I', 'am', 'coding']]
        ss6 = ['I', '-', 'am', '-', 'coding']
        r6 = ~[x ; wd <- ss6; x = wd == '-' ? ' ' : wd]
        res <- r6
        
        # from multiline, 2 iterations
        ss7 = """
        Hello!
        What we can do?
        Let's do it!
        """
        r7 = ~[wd + ' ' ; ss <- ss7.split('\n'); wd <- ss.split(re`\b`) ; len(wd) > 0]
        res <- r7
        
        # filtering by string
        pt = '.,?!:;-'
        r8 = ~[ s ; s <- 'Hello, dude!' ; s !?> pt]
        res <- r8
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            ['g(a)', 'g(b)', 'g(c)'], ['e2', 'f3'], 
            'Hello!', 'ABCD!abc', 'PQRSTU', 'I am coding', 
            "Hello ! What   we   can   do ? Let ' s   do   it ! ", 
            'Hello dude']
        self.assertEqual(exv, resv)
        
    def test_iter_by_string(self):
        ''' '''
        code = r'''
        res = []
        
        # simple string
        r1 = []
        ss = "abc+-12"
        for g <- ss
            r1 <- g
        res <- r1
        
        # in the same expr
        r2 = []
        for g <- "Hello!"
            r2 <- g
        res <- r2
        
        # multi string
        ss2 = '123'
        r3 = []
        for a, b <- ss2, "ABC"
            r3 <- (a, b, a + b)
        res <- r3
        
        # mixed sources str, list, tuple, dict
        aa3 = ['aa','bb','cc']
        ss3 = 'QWE'
        dd3 = {'x':'-', 'y':'+', 'z':'='}
        tt3 = (11, 22, 33)
        r3 = []
        for a, k, v, s, t  <- aa3, dd3, ss3, tt3
            r3 <- ~'~ {a} {k}{v} {s}/{t}'
        res <- r3
        
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
            ['g(a)', 'g(b)', 'g(c)', 'g(+)', 'g(-)', 'g(1)', 'g(2)'], ['g(H)', 'g(e)', 'g(l)', 'g(l)', 'g(o)', 'g(!)'], 
            [('g(1)', 'g(A)', '1A'), ('g(2)', 'g(B)', '2B'), ('g(3)', 'g(C)', '3C')], 
            ['~ aa x- Q/11', '~ bb y+ W/22', '~ cc z= E/33']]
        self.assertEqual(exv, resv)
        
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

    def test_gen_arrow_assign(self):
        ''' '''
        code = r'''
        res = []
        
        s = [111]
        ss = [1,2,3]
        
        r1 = [s ; s <- ss]
        
        res <- r1
        res <- s
        
        # local context over upper
        ss = [[1,2], [3,4]]
        s = [5,6,7]
        r2 = [(s, n) ; s <- ss; n <- s]
        res <- 'r2'
        res <- r2
        res <- s
        
        # for loop
        s = [1,2,3]
        ss = [4,5,6]
        r3 = []
        for s <- ss
            r3 <- s
        res <- 'r3'
        res <- r3
        
        # in dict 
        
        s = [111]
        k = [222]
        tt = ('qq','ww','ee')
        ss = [11,22,33]
        
        r4 = {k: s ; k, s <- tt, ss}
        res <- 'r4'
        res <- r4
        
        # `append` huck in gen
        
        rt = []
        func f4(x)
            rt <- x
            
        rp = []
        f5 = \x -> (rp <- x)
        
        s = []
        ss = [21, 22, 23]
        
        r5 = [100 + s ; s <- ss ; _ = f4(s + 200); _= f5(s + 300)]
        res <- 'r5'
        res <- r5
        res <- rt
        res <- rp
        
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
            [1, 2, 3], 3, 
            'r2', [([1, 2], 1), ([1, 2], 2), ([3, 4], 3), ([3, 4], 4)], [3, 4], 
            'r3', [4, 5, 6], 
            'r4', {'qq': 11, 'ww': 22, 'ee': 33}, 
            'r5', [121, 122, 123], [221, 222, 223], [321, 322, 323]]
        self.assertEqual(exv, resv)
        
    def test_dict_generator(self):
        ''' dict generator
            { key: val ; key, val <- src; expr; condition }
        '''
        code = r'''
        res = []
        
        # simplest case
        
        pairs = [('aa', 11), ('bb',22), ('cc',33), ('dd',44)]
        dd = {k:v ; k, v <- pairs}
        res <- dd
        
        # from list, tuple
        
        nn = [1,2,3,4,5]
        tt = ('a', 'b', 'c', 'd', 'e')
        
        d2 = { c : n ; n, c <- nn, tt}
        d3 = { n : c ; n, c <- nn, tt}
        
        res <- d2
        res <- d3
        
        # from slices
        
        ss = [1,2,3,4,5, 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', [0]]
        d4 = { k: v ; v, k <- ss[5:10], ss[:5]}
        res <- d4
        
        # from dict
        
        ds = {'a1':'aaa', 'b1':'bbb', 'c1':'ccc', 'd1':'ddd', }
        d5 = { k:v ; k, v <- ds}
        res <- d5
        d6 = { v:k ; k, v <- ds}
        res <- d6
        
        # + condition
        
        d7 = { c : n ; n, c <- nn, tt; n > 1 && n % 2 > 0}
        res <- d7
        
        # + pre + condition
        
        d8 = { c : s ; n, c <- nn, tt; s = ~'{n:03d}@{c}'; n % 2 > 0}
        res <- d8
        
        # 3 sub levels
        
        n9 = [1,2,3]
        d9 = {
            k: i * 100 + j ; 
            n <- n9; p = [1..n]; 
            i <- p; s = ~'k{i}'; q = [i .. 4]; 
            j <- q; k = ~'{s}-{j}'; i > 1 && j > 2
        }
        res <- d9
        
        # unpack list of lists
        
        s10 = [
            [11, 12, 13],
            [21, 22, 23],
            [31, 32, 33],
        ]
        d10 = {
            ~'{p}.{n}': n ; 
            s1 <- s10; 
            n <- s1; p = s1.fold(n*100, \s, c -> s + c)}
        res <- d10
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            {'aa': 11, 'bb': 22, 'cc': 33, 'dd': 44}, 
            {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}, 
            {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}, 
            {1: 'f', 2: 'g', 3: 'h', 4: 'i', 5: 'j'}, 
            {'a1': 'aaa', 'b1': 'bbb', 'c1': 'ccc', 'd1': 'ddd'}, 
            {'aaa': 'a1', 'bbb': 'b1', 'ccc': 'c1', 'ddd': 'd1'}, 
            {'c': 3, 'e': 5}, {'a': '001@a', 'c': '003@c', 'e': '005@e'}, 
            {'k2-3': 203, 'k2-4': 204, 'k3-3': 303, 'k3-4': 304},
            {'1136.11': 11, '1236.12': 12, '1336.13': 13, '2166.21': 21, '2266.22': 22, '2366.23': 23, '3196.31': 31, '3296.32': 32, '3396.33': 33}]
        self.assertEqual(exv, resv)

    def test__listgen_with_multisource(self):
        '''Multi-source in list-generator
            [expr ; a, b, c <- s1, s2, s3 ] '''
        code = r'''
        res = []
        
        # list, tuple
        aa = [1,2,3]
        bb = [5,6,7]
        tt = ('A', 'B', 'C')
        r1 = []
        r1 = [{c:(a,b)} ; a, b, c <- aa, bb, tt]
        res <- r1
        
        # iter-gen, dict
        dd = {'a':'aaa', 'b':'bbb', 'c':'ccc'}
        r2 = [ ~'{a}:({k},{v})'; a, k, v <- [1 .. len(dd.keys()) ], dd ]
        res <- r2
        
        # index-gen, slice
        aa = [11, 22, 33, 44, 55, 66, 77]
        r3 = [(i + 10, x) ; i, x <- iter(3), aa[1:4]]
        res <- r3
        
        # strings
        s1 = 'RGB'
        s2 = 'red green blue'
        r4 = [ ~'{b}:{c}' ; b, c <- list(s1), s2.split(' ') ]
        res <- r4
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            [{'A': (1, 5)}, {'B': (2, 6)}, {'C': (3, 7)}], 
            ['1:(a,aaa)', '2:(b,bbb)', '3:(c,ccc)'], 
            [(10, 22), (11, 33), (12, 44)],
            ['R:red', 'G:green', 'B:blue']]
        self.assertEqual(exv, resv)

    def test_list_gen_empty_end(self):
        ''' list generator. [... expr;] empty last sub-case after semicolon'''
        code = '''
        nums1 = [[x ** 2] ; x <- [2..5] ; x > 1; ]
        nums2 = [[x ** 2 + 1] ; x <- [2..5] ;]
        res = [nums1, nums2]
        # print('nums = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        exp = [[[4], [9], [16], [25]], [[5], [10], [17], [26]]]
        rvar = ctx.get('res').get()
        self.assertEqual(exp, rvar.vals())



if __name__ == '__main__':
    main()
