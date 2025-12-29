'''
Function cases:
definition, call, args, results, etc.
'''

from unittest import TestCase, main
from tests.utils import *
import sys

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from cases.utils import *
from tree import *
from eval import *



class TestFunc(TestCase):



    def test_func_named_args(self):
        ''' '''
        code = r'''
        res = []
        
        func f1(aaa, bbb)
            (aaa, bbb)
        
        # f1('a1', 'b1')
        # all args passed by name
        res <- ('f1-1', f1('a1', 'b1'))
        res <- ('f1-2', f1(aaa='a2', bbb='b2'))
        res <- ('f1-3', f1(bbb='b3', aaa='a3'))
        
        func f2(a, b, c=1, d=0)
            (a + b) * c + d
        
        res <- ('f2-1', f2(1,2,3,100))
        # def-val args
        res <- ('f2-2', f2(2,3))
        # named args in the end of list
        res <- ('f2-3', f2(3,4,c=5))
        res <- ('f2-4', f2(5,6,c=7, d=400)) 
        res <- ('f2-4', f2(5,6, d=500,c=8)) 
        
        func f3(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9, j=10, k=11, m=12)
            [a, b, c, d, e, f, g, h, i, j, k, m]
        
        res <- ('f3-1', f3())
        res <- ('f3-2', f3(11,22,33,44,55,66,77,88,99,100,110,120))
        res <- ('f3-3', f3(a=21, b=22, c=23, d=24, e=25, f=26, g=27, h=28, i=29, j=210, k=211, m=212))
        # skipping sonething
        res <- ('f3-4', f3(f=36, g=37, h=38, i=39, j=310, k=311, m=312))
        res <- ('f3-5', f3(41,42,43,44,45, f=46, g=47, h=48, k=411, m=412, a=1000))
        # pass redundant arg by name: no effect here
        res <- ('f3-6', f3(51,52,53,54,55, f=560, g=570, h=580, i=590, m=512, a=1000, b=1001))
        
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
            ('f1-1', ('a1', 'b1')), ('f1-2', ('a2', 'b2')), ('f1-3', ('a3', 'b3')), 
            ('f2-1', 109), ('f2-2', 5), ('f2-3', 35), ('f2-4', 477), ('f2-4', 588), 
            ('f3-1', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]), 
            ('f3-2', [11, 22, 33, 44, 55, 66, 77, 88, 99, 100, 110, 120]), 
            ('f3-3', [21, 22, 23, 24, 25, 26, 27, 28, 29, 210, 211, 212]), 
            ('f3-4', [1, 2, 3, 4, 5, 36, 37, 38, 39, 310, 311, 312]), 
            ('f3-5', [41, 42, 43, 44, 45, 46, 47, 48, 9, 10, 411, 412]), 
            ('f3-6', [51, 52, 53, 54, 55, 560, 570, 580, 590, 10, 11, 512])]
        self.assertEqual(exv, rvar.vals())

    def test_func_default_arg_vals(self):
        ''' '''
        code = r'''
        res = []
        
        func foo(x:int = 0)
            x * 10
        
        res <- ('foo(1)', foo(1))
        res <- ('foo(-1)', foo(-1))
        res <- ('foo(15)', foo(15))
        
        r = foo()
        
        res <- ('foo()', foo())
        
        func strfill(count, str=' ')
            [str ; x <- iter(count)]
        
        res <- (`strfill(3, '=')`, strfill(3, '='))
        res <-  (`strfill(4)`, strfill(4))
        # print('>>', r)
        
        func foo3(a=1, b=10, c=100)
            a + b + c
            
        res <- ('foo3()', foo3())
        res <- ('foo3(2)', foo3(2))
        res <- ('foo3(3, 30)', foo3(3, 30))
        res <- ('foo3(4, 40, 400)', foo3(4, 40, 400))
        
        func fstr3(a="A", b="B", c="C")
            ~"*{a}{b}{c}*"
        
        res <- ('fstr3()', fstr3())
        res <- (`fstr3('Q')`, fstr3('Q'))
        res <- (`fstr3('W', 'E')`, fstr3('W', 'E'))
        res <- (`fstr3('R', 'T', 'Y')`, fstr3('R', 'T', 'Y'))
        
        func fstr3T(a:string="A", b:string="B", c:string="C")
            ~"<{a}{b}{c}>"
        
        res <- ('fstr3T()', fstr3T())
        res <- (`fstr3T('Q')`, fstr3T('Q'))
        res <- (`fstr3T('W', 'E')`, fstr3T('W', 'E'))
        res <- (`fstr3T('R', 'T', 'Y')`, fstr3T('R', 'T', 'Y'))
        
        func defList(x:int, nums=[0])
            [n + x; n <- nums]
        
        res <- ('defList(1)', defList(1))
        res <- ('defList(2, [1,2,3])', defList(2, [1,2,3]))
        
        func defDict(pref:string, options = {'count':0})
            [ ~'{pref}{k}'; k <- options.keys()]
        
        res <- ('defDict:3K', defDict('k_', {'abba':1,'buba':2,'cuba':3,}))
        res <- ('defDict:3K', defDict('!', {}))
        res <- ('defDict:3K', defDict('0_'))
        
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
            ('foo(1)', 10), ('foo(-1)', -10), ('foo(15)', 150), ('foo()', 0), 
            ("strfill(3, '=')", ['=', '=', '=']), ('strfill(4)', [' ', ' ', ' ', ' ']), 
            ('foo3()', 111), ('foo3(2)', 112), ('foo3(3, 30)', 133), ('foo3(4, 40, 400)', 444), 
            ('fstr3()', '*ABC*'), ("fstr3('Q')", '*QBC*'), ("fstr3('W', 'E')", '*WEC*'), ("fstr3('R', 'T', 'Y')", '*RTY*'), 
            ('fstr3T()', '<ABC>'), ("fstr3T('Q')", '<QBC>'), ("fstr3T('W', 'E')", '<WEC>'), ("fstr3T('R', 'T', 'Y')", '<RTY>'), 
            ('defList(1)', [1]), ('defList(2, [1,2,3])', [3, 4, 5]), 
            ('defDict:3K', ['k_abba', 'k_buba', 'k_cuba']), ('defDict:3K', []), ('defDict:3K', ['0_count'])]
        self.assertEqual(exv, rvar.vals())

    def test_naive_extension_of_recursion_limit(self):
        ''' 
        recursion without tail-recursion optimisation.
        pythons recursion limit matters
        '''
        code = r'''
        res = 0
        func f1(x)
            if x <= 0 /: return 7000000
            res += 1
            return 3 + f1(x-1)
        fres = f1(2000)
        # print('res = ', res, fres)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        sys.setrecursionlimit(100000)
        ex.do(ctx)
        sys.setrecursionlimit(1000)
        rvar = ctx.get('res').get()
        fvar = ctx.get('fres').get()
        self.assertEqual(2000, rvar.getVal())
        self.assertEqual(7006000, fvar.getVal())

    def test_builtin_len_fo_string(self):
        ''' test implementation of builtin function len for string type '''
        code = r'''
        nn = [
            '', ' ', '123', 'a b c'
        ]
        nn <- """abc
        def
        """
        res = []
        for s <- nn
            res <- len(s)
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
        self.assertEqual([0, 1, 3, 5, 7], rvar.vals())

    def test_result_of_block_in_brackets(self):
        ''' '''
        code = r'''
        res = []
        
        # last expr in line as result
        func foo(x)
            a = 100; b = x; r = a + b
        
        res <- foo(44)
        
        # result in parenthesis
        func bar(x)
            (200 + x)
        
        res <- bar(55)
        
        # semicolon-separated inline block in lambda
        f1 = x -> (a = 1 + 2; b = x * 2; a * b + 300)
        
        res <- f1(5)
        
        # mulitiline lambda
        f2 = x -> (
            a = 1 + x; 
            b = 2 * 500; # do nothing for result
            x * a + 400)
        
        res <- f2(3)
        
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
        self.assertEqual([144, 255, 330, 412], rvar.vals())

    def test_closure(self):
        ''' 
        Lambdas with closure
        returned lambda uses: 
            argument var passed to function
            var from functions block
            lambda passed to function as an argument
            function defined inside of function
        
        Experimental:
        If def of function f1 was last expression in another function f2 than f1 will be a result of f2. 
        '''
        code = r'''
        res = 0
        
        modVar = 1
        
        func foo(x)
            x + 100
        
        func getLamb(n, ff)
            funVar = foo(n)
            
            func bar(x, y)
                x + 10000 * y
            
            x -> ff(x) + bar(n, funVar)
        
        f1 = getLamb(3, a -> a * 5)
        
        f2 = getLamb(29, b -> b ** 2)
        
        # defined func as a returning value
        func getFuu(n)
            func foo2(x)
                x * n
        
        f3 = getFuu(11)
        
        res = [f1(2), f2(5), f3(4)]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rval = ctx.get('res').get()
        self.assertEqual([1030013, 1290054, 44], rval.vals())

    def test_function_from_function(self):
        ''' Callable expression is a lambda or function from result of function call. '''
        code = r'''
        res = 0
        
        x2 = x -> x * 2
        
        func x1(x)
            x * 10
        
        # defined function
        func foo()
            x1
        
        # lambra from var
        func foo2()
            x2
        
        # new lambda
        func foo3()
            x -> x * 100 
        
        # lambda uses top-level argument
        func foo4(n)
            x -> x * n + 1000 
        
        # lambda uses passed lambda
        func foo5(f)
            x -> f(x) + 5000 
        
        res = []
        
        res <- foo()(3)
        res <- foo2()(7)
        res <- foo3()(22)
        res <- foo4(5)(111)
        res <- foo5(y -> y * 3)(33)

        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rval = ctx.get('res').get()
        self.assertEqual([30, 14, 2200, 1555, 5099], rval.vals())

    def test_lambda_in_collection(self):
        ''' Callable expression is a lambda in list or dict '''
        code = r'''
        res = 0
        
        # lambda in var
        x2 = x -> x * 2
        
        # lambda in list
        ffs = [x2, x -> 5000 + x]
        
        # lambda in dict
        ffd = dict
            'f' : ((a) -> a * 11)
            's' : ((a, b) -> a * b)
        
        res = []
        
        res <- x2(7)
        
        res <- ffs[0](11)
        res <- ffs[-1](31)

        res <- 'next-dict'
        res <- ffd['f'](9)
        res <- ffd['s'](10, 17)
        
        # lambda in brackets
        res <- (x -> [x, x * 2, x * 3])(5)

        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # ctx.print(forsed=1)
        rval = ctx.get('res').get()
        self.assertEqual([14, 22, 5031, 'next-dict', 99, 170, [5, 10, 15]], rval.vals())

    def test_func_as_expr(self):
        ''' '''
        code = r'''
        
        func foo()
            'foo-result'
        
        func bar(arg)
            arg
        
        func inList(arg)
            [arg]
        
        func sum(a, b)
            a + b
        
        ffs = [foo, bar, inList, sum]
        
        ffd = {
            'f' : foo,
            's' : sum
        }
        
        res = []
        
        res <- ffs[0]()
        res <- ffs[1]('bar-arg1')

        res <- 'next-dict'
        res <- ffd['f']()
        res <- ffd['s'](10, 1000)

        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # ctx.print(forsed=1)
        rval = ctx.get('res').get()
        self.assertEqual(['foo-result', 'bar-arg1', 'next-dict', 'foo-result', 1010], rval.vals())

    def test_built_foldl(self):
        ''' '''
        code = r'''
        res = 0
        
        func sum(nums)
            plus = (x, y) -> x + y
            foldl(0, nums, plus)
        
        # args = [1,2,3,4,5]
        s1 = sum([1,2,3,4,5])
        s2 = sum([1..10])
        s3 = sum([x ** 2 ; x <- [2..9]])
        
        res = [s1, s2, s3]
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rval = ctx.get('res').get()
        self.assertEqual([15, 55, 284], rval.vals())

    def test_nesting_blocks(self):
        ''' if/match/for/func/method/ '''
        code = r'''
        # res = 0
        
        func f1(m, k)
            r = 1
            # print(m,k)
            match k - m
                1 !- r += m
                2 !- r = 2 * (k + m)
                _ !- k * 10 + m
            r
        
        func f2(m, k)
            rem = k % m
            if rem > 0
                return rem
            else
                return toint(k / m)
        
        func f3(n)
            r = 0
            for i <- [1..n]
                t = f1(i, n)
                r += t
            r
            
        struct Abc a:int
        
        func abc:Abc f4(x)
            x * abc.a
        
        func test()
            r = []
            aa = Abc{a:5}
            for i <- [1..10]
                r1 = f3(i)
                r2 = f2(i, r1)
                r <- aa.f4(r2)
            r
        
        rr = test()
        # print('res = ', rr)
        '''
        _='''
        
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rr = ctx.get('rr')
        self.assertEqual([5, 5, 20, 10, 20, 25, 5, 10, 15, 20], rr.get().vals())
        # dprint('>>', rr.get().vals())
        # dprint('>>', [n.get() for n in rr.get().elems])

    def test_rerun_list_iter_in_funcs(self):
        ''' src-iter/func/src-iter '''
        code = r'''
        func foo(a:int, b:int)
            a + b
        
        func list3(a, b, c)
            [a, b, c]
        
        func lsum(nums)
            res = 100 * nums[0]
            for n <- nums
                res += n
            res
        
        func bar(a:int)
            bres = []
            for i <- [1..a]
                if i % 2 == 0
                    for n <- iter(i, i+3)
                        sm = foo(n, n % 4)
                        bres <- sm + 100
                else
                    nn = list3(i, i%3, i%7)
                    for n <- nn
                        bres <- n
            bres
        
        rr = {}
        rr2 = []
            
        func test()
            for i <- [2,4,6,3,5,7]
                br = bar(i)
                sb = lsum(br) + 0
                rr <- (i, sb)
                rr2 <- i
        
        test()
        # print('res = ', rr)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rr = ctx.get('rr')
        rr2 = ctx.get('rr2')
        self.assertEqual({2: 417, 4: 741, 6: 1079, 3: 423, 5: 753, 7: 1087}, rr.get().vals())
        # dprint('>>', rr2.get())

    def test_func_in_loop_in_func(self):
        ''' src-iter/func/src-iter '''
        code = r'''
        func foo(a:int, b:int)
            a + b

        
        rr = []
        a = 10
        func test()
            foo(5, 7)
            for b <- [2,4,6,3,5,7]
                br = foo(a, b)
                rr <- br
        
        test()
        # print('res = ', rr)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rr = ctx.get('rr')
        self.assertEqual([12, 14, 16, 13, 15, 17], rr.get().vals())

    def test_func_arg_type(self):
        ''' Auto-define type of args on-the-fly if func definition doesn`t have type of arguments. '''
        code = r'''
        res = 0
        
        func summ(a, b)
            a + b
        
        func concat(str1, str2)
            str1 + str2
        
        struct A a1:int
        
        func aa:A afoo(n)
            aa.a1 += n
        
        avar = A{a1:100}
        
        r1 = summ(10, 2)
        r2 = concat('abc', 'def')
        avar.afoo(11)
        r3 = avar.a1
        
        # print('res = ', r1, r2, r3)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        r1 = ctx.get('r1')
        r2 = ctx.get('r2')
        r3 = ctx.get('r3')
        self.assertEqual(12, r1.getVal())
        self.assertIsInstance(r1.getType(), TypeInt)
        self.assertEqual('abcdef', r2.getVal())
        self.assertIsInstance(r2.getType(), TypeString)
        self.assertEqual(111, r3.getVal())
        self.assertIsInstance(r3.getType(), TypeInt)

    def test_lambda_in_func(self):
        ''' test in function. '''
        code = r'''
        func testLambdas()
            rr = []
            func foo(f, a, b)
                # print('>>==', f, a, b)
                a + f(b)
            
            f1 = x -> x * 10
            n1 = foo(f1, 2, 3)
            rr <- n1
            n2 = foo(x -> x * 100, 4, 5)
            rr <- n2
            n3 = foo(x -> x * 100, 6, 7)
            rr <- n3
            
            # # TODO: 1) append val to list : nums <- 5
            nn = [0,0,0,0,0]
            for i <- [1..5]
                nn[i-1] = foo(x -> x ** 2 , 1, i)
            rr <- nn
            # print('lambda test:', n1, n2, nn)
            rr
            
        res = testLambdas()
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        exv = [32, 504, 706, [2, 5, 10, 17, 26]]
        self.assertEqual(exv, rvar.vals())

    def test_lambda_as_arg(self):
        ''' function object as argument of function. '''
        code = r'''
        func foo(ff, arg)
            ff(arg * 2)
        f1 = x -> x * 3
        n1 = foo(f1, 5)
        n2 = foo( x -> 2 ** x , 5)
        # print('n1,2 = ', n1, n2)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        self.assertEqual(30, ctx.get('n1').getVal())
        self.assertEqual(1024, ctx.get('n2').getVal())

    def test_lambda_match(self):
        ''' Lambda and match-case in one example.
        Resolved conflict between lambdas and preavious syntax of matches. '''
        code = r'''
        c = 5
        res = 0
        match c
            1 !- res = 10
            2 !- res = c * 2
            _ !- res = 100

        f1 = x -> x ** 2
        f2 = (x, y) -> x * y
        n1 = f1(7)
        n2 = f2(res, 111)
        # print('nn = ', n1, n2)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        self.assertEqual(49, ctx.get('n1').getVal())
        self.assertEqual(11100, ctx.get('n2').getVal())

    def test_lambda_def(self):
        ''' simple case - definition and call. '''
        code = r'''
        n1=0
        n2=0
        foo = x -> x ** 2
        n1 = foo(7)
        foo2 = x, y -> x ** 2
        n2 = foo2(5, 2)
        foo3 = (x, y, z) -> (x + y) * z
        n3 = foo3(2, 3, 100)
        # print('n1,2,3 = ', n1, n2, n3)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        self.assertEqual(49, ctx.get('n1').getVal())
        self.assertEqual(25, ctx.get('n2').getVal())
        self.assertEqual(500, ctx.get('n3').getVal())

    def test_local_defined_function(self):
        '''  test usage of function, defined within another function '''
        code = '''
        
        func foo(x:int)

            num1 = 1000
            
            func bar(xx:int, yy:int)
                xx * yy
            
            nums = [bar(a, b) ; a <-[1..x] ; b = x * num1]
            [c + x ; c <- nums]
        
        res = foo(5)
        # print(res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        exp = [5005, 10005, 15005, 20005, 25005]
        resVal = ctx.get('res').get()
        # dprint(resVal)
        self.assertListEqual(exp, resVal.get())


    def test_func_typed_args(self):
        ''' make vars and assign vals from tuple  '''
        code = '''
        func foo(name: string, nn: int, ff: float, arg4 )
            # print('arg4:', arg4)
            div = ' ' * nn
            name + div + '/'
        
        # print('p>>', foo('Brrr', 4, 0.1, '4444'))
        '''
        tt = '''
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_func_method_match(self):
        data = [
            ('func u:User setName(name:string)', CaseMathodDef),
            ('func setName(name:string)', CaseFuncDef),
        ]
        for code, ctype in data:
            # dprint('Code:', code)
            # code = norm(code[1:])
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            cases = getCases()
            for cs in cases:
                if cs.match(elems):
                    # dprint('#tt found cae: ', cs, 'exp:', ctype)
                    self.assertIsInstance(cs, ctype)
                    break


    def test_func_return(self):
        code = '''
        func foo(a)
            res = 0
            for i <- [1,2,3,4,5,6,7,8,9]
                res += i
                if res > a
                    return res
            -1000
        res = foo(10)
        # print('cc res', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        exp.do(ctx)
        res = ctx.get('res').getVal()
        # dprint('#t >>> r:', res)
        self.assertEqual(res, 15)

    def test_call_func(self):
        code = '''
        func foo(a, b, c)
            x = a + b
            y = b + c
            x * y + 1000
        
        arg1 = 8
        
        r1 = foo(2,3,4)
        r2 = foo(arg1, 2, 98)
        # res = [r1, r2]
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        # dprint('$$ run test ------------------')
        exp.do(ctx)
        r1 = ctx.get('r1').getVal()
        r2 = ctx.get('r2').getVal()
        self.assertEqual(r1, 1035)
        self.assertEqual(r2, 2000)

    def test_def_func(self):
        code = '''
        func foo(a, b, c)
            x = a + b
            y = b + c
            x * y
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        # dprint('$$ run test ------------------')
        exp.do(ctx)
        fn:Function = ctx.get('foo')
        # dprint('#tt1>>> ', fn, type(fn))
        args = [value(2, TypeInt()),value(3, TypeInt()),value(4, TypeInt())]
        fn.setArgVals(args)
        ctxCall = Context(None)
        fn.do(ctxCall)
        res = fn.get()
        # dprint('#tt2>>> ', res)



if __name__ == '__main__':
    main()
