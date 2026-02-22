
'''
Tests of features of functional programming.

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
from objects.func import Function
from nodes.func_expr import setNativeFunc
from nodes.func_expr import setNativeFunc
from cases.utils import *
from tree import *
from eval import *


class TestFuncs(TestCase):
    

    def test_apply_operator(self):
        ''' foo $ arg '''
        code = r'''
        res = []
        
        func foo(x)
            x + 10
        
        res <- foo $ 1
        res <- foo $ 2 + 3
        res <- foo $ 3 * 5
        res <- foo $ foo(1)
        res <- foo $ 2 ** 3
        res <- [foo $ 11, foo $ 12]
        
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
        exv = [11, 15, 25, 21, 18, [21, 22]]
        self.assertEqual(exv, resv)

    def test_composition_of_function_no_apply(self):
        '''
        composed = foo * bar * baz
        composed(arg)
        # is equal to
        foo(bar(baz(arg)))
        
        no `applay` operator here
        '''
        
        code = r'''
        res = []
        
        func foo(x)
            x * 10
        
        func bar(x)
            x + 5
        
        func baz(x)
            x * 3
        
        
        f0 = foo * bar
        res <- (f0(1), f0(2), f0(5))

        
        # foo * bar * baz
        com1 = foo * bar * baz
        
        res <- com1(1)
        r1 = [-13]
        for n <- [2, 3, 5, 10, 11, 20]
            r1 <- com1(n)
        res <- r1
        
        # baz * bar * foo
        com2 = baz * bar * foo
        
        res <- com2(1)
        r2 = [-14]
        for n <- [2, 3, 5, 10, 11, 20]
            r2 <- com2(n)
        res <- r2
        
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
        exv = [(60, 70, 100), 80, [-13, 110, 140, 200, 350, 380, 650], 45, [-14, 75, 105, 165, 315, 345, 615]]
        self.assertEqual(exv, resv)

    def test_composition_builtin(self):
        '''
        composed = compose(foo, bar, baz)
        composed(arg)
        # is equal to
        foo(bar(baz(arg)))
        '''
        
        code = r'''
        res = []
        
        func foo(x)
            x * 10
        
        func bar(x)
            x + 5
        
        func baz(x)
            x * 3
        
        # foo, bar, baz
        com1 = compose(foo, bar, baz)
        
        res <- com1(1)
        
        r1 = [-11]
        for n <- [2, 3, 5, 10, 11, 20]
            r1 <- com1(n)
        res <- r1
        
        # baz, bar, foo
        com2 = compose(baz, bar, foo)
        
        res <- com2(1)
        
        r2 = [-12]
        for n <- [2, 3, 5, 10, 11, 20]
            r2 <- com2(n)
        res <- r2
        
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
        exv = [80, [-11, 110, 140, 200, 350, 380, 650], 45, [-12, 75, 105, 165, 315, 345, 615]]
        
        self.assertEqual(exv, resv)

    def runComposed(self, ctx, comps:ComposedFunc, argSet:list):
        rr = []
        for i in argSet:
            x = Val(i, TypeInt())
            comps.setArgVals([x])
            comps.do(ctx)
            cres = comps.get()
            rr.append(cres.getVal())
        return rr

    def test_composition_object(self):
        '''
        ComposedFunc object.
        '''
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        
        def f1(_, x:Val):
            v = var2val(x).getVal()
            return Val(v * 2, TypeInt())
        
        def f2(_,x):
            v = var2val(x).getVal()
            return Val(v + 10, TypeInt())
        
        def f3(_, x):
            v = var2val(x).getVal()
            return Val(v * 100, TypeInt())
        
        fn1 = (defineFunc(ctx, 'f1', f1))
        fn2 = defineFunc(ctx, 'f2', f2)
        fn3 = defineFunc(ctx, 'f3', f3)
        
        # test f1 * f2 *  f3

        comps123 = ComposedFunc()
        comps123.add(fn1)
        comps123.add(fn2)
        comps123.add(fn3)
        comps123.setDefContext(ctx)
        
        rr1 = self.runComposed(ctx, comps123, [1, 2, 5, 10, 11, 12])
        self.assertEqual([220, 420, 1020, 2020, 2220, 2420], rr1)
        
        # test f1 * f3 *  f2

        comps132 = ComposedFunc()
        comps132.add(fn1)
        comps132.add(fn3)
        comps132.add(fn2)
        comps132.setDefContext(ctx)
        
        rr2 = self.runComposed(ctx, comps132, [1, 2, 5, 10, 11, 12])
        self.assertEqual([2200, 2400, 3000, 4000, 4200, 4400], rr2)
        
        # test f1 * f2 *  f3

        comps321 = ComposedFunc()
        comps321.add(fn3)
        comps321.add(fn2)
        comps321.add(fn1)
        comps321.setDefContext(ctx)
        
        rr3 = self.runComposed(ctx, comps321, [1, 2, 5, 10, 11, 12])
        self.assertEqual([1200, 1400, 2000, 3000, 3200, 3400], rr3)

    def test_curry_operator(self):
        code = r'''
        res = [-557]
        
        func foo(a,b)
            a + b
        
        func bar(a, b, c)
            a * b + c
        
        func fu5(a1, a2, a3, a4, a5)
            ('fu5>', a1, a2, a3, a4, a5)
        
        # 2 args
        res <- 'foo'
        f01 = foo~>
        res <- f01(100)(23)
        res <- foo~>(200)(13)
        
        f02 = f01(1000)
        f03 = f01(2000)
        res <- f02(31)
        res <- f02(32)
        res <- f03(31)
        res <- f03(32)
        # in format-string
        res <- ~'foo(50)(7)={foo~>(50)(7)}'
        
        # from brackets
        res <- ('(f~>)', (foo~>)(60)(7))
        
        # 3 args
        res <- 'bar'
        
        b01 = bar~>
        res <- b01(3)(100)(1)
        res <- b01(3)(110)(2)
        
        b02 = b01(4)
        b22 = b02(200)
        b03 = b01(5)
        b04 = bar~>(6)
        
        res <- b02(100)(11)
        res <- b02(110)(2)
        res <- b22(3)
        res <- b03(100)(11)
        res <- b03(110)(12)
        
        # 5 args
        
        fu51 = fu5~>
        fu52 = fu51(1)
        fu511 = fu5~>(11)
        
        res <- fu51(22)(2)(3)(4)(5)
        res <- fu52(22)(33)(44)(55)
        res <- fu511(32)(33)(34)(35)
        
        # func from func
        func getFoo()
            foo
        
        res <- getFoo()~>(700)(13)
        
        ff1 = [foo~>, bar~>(14), fu5~>(51)(52)(53)]
        
        for i <- iter(len(ff1))
            fn = ff1[i]
            res <- [~'{i}:', fn(10)(7)]
        
        # from array
        ffs = [foo, (x, y)-> x * y]
        
        res <- '[]~>'
        
        af0 = ffs[0]~>
        
        res <- af0(7700)(1)
        res <- ffs[1]~>(78)(100)
        
        
        # func from struct member
        # f~>(1).n 
        # m.n~>(1)
        
        struct A a:int, f:function
        
        func getA(n)
            f = (x,y) -> [x, y]
            A(n, f)
        
        res <- 'A.foo'
        
        a1 = A(120, foo)
        res <- ('a1', a1.f~>(10)(2))
        
        res <- ('a_2', (getA(2)).f~>(2)(4))
        
        a3 = (getA(3))
        res <- a3.f~>(3)(6)
        
        
        # struct method
        struct B b:int
        
        func st:B bum(x, y)
            ('B.bum', st.b, x, y)
        
        b1 = B(15)
        res <- b1.bum~>(901)(902)
        b8000 = b1.bum~>(8000)
        res <- b8000(16)
        
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
        exv = [-557, 
            'foo', 123, 213, 1031, 1032, 2031, 2032, 'foo(50)(7)=57', ('(f~>)', 67),
            'bar', 301, 332, 411, 442, 803, 511, 562, 
            ('fu5>', 22, 2, 3, 4, 5), ('fu5>', 1, 22, 33, 44, 55), ('fu5>', 11, 32, 33, 34, 35), 713, 
            ['0:', 17], ['1:', 147], ['2:', ('fu5>', 51, 52, 53, 10, 7)], 
            '[]~>', 7701, 7800,
            'A.foo', ('a1', 12), ('a_2', [2, 4]), [3, 6], 
            ('B.bum', 15, 901, 902), ('B.bum', 15, 8000, 16)]
        self.assertEqual(exv, resv)

    def test_dev_currying_function(self):
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        
        code = r'''
        res = []
        
        # 2 args
        func foo(a, b)
            a + b
        
        res <- '@N2'
        f01 = curry(foo)
        res <- f01(1000)(21)
        
        f0k2 = f01(2000)
        f0k3 = f01(3000)
        
        res <- f0k2(22)
        res <- f0k3(33)
        res <- f0k2(44)
        res <- f0k3(55)
        res <- curry(foo)(5000)(51)
        
        # 3 args 
        func foo2(a, b, c)
            [a, b, c]
        
        res <- '@N3'
        f2 = curry(foo2)
        res <- f2(11)(22)(33)
        res <- f2(12)(24)(36)
        
        f2_1 = f2(100)
        f2_2 = f2(110)(220)
        
        res <- f2_1(201)(301)
        res <- f2_2(321)
        
        f3 = curry(foo2)
        
        f31 = f3(1)
        f32 = f3(2)
        
        res <- f31(22)(33)
        res <- f32(122)(133)
        
        # 5 args
        func bar(a, b, c, d, e)
            [a * b + i ; i <- [c, d, e]]
        
        res <- '@N5'
        res <- bar(40, 500, 111, 222, 333)
        
        b1 = curry(bar)
        res <- b1(70)(100)(133)(144)(155)
        
        # 7 args
        func bar7(q, w, e, r, t, y, u)
            [(q,1),(w,2),(e,3),(r,4),(t,5),(y,6),(u,7)]
        
        res <- '@N7'
        fb7 = curry(bar7)
        res <- fb7(1)(2)(3)(4)(5)(6)(7)
        res <- fb7('a')('b')('c')('d')('e')('f')('g')
        
        # 1 arg, strange case
        func fone(a)
            a

        res <- '@N1'
        one1 = curry(fone)
        
        res <- one1(100001)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        trydo(ex, ctx)

        exv = [
            '@N2', 1021, 2022, 3033, 2044, 3055, 5051, 
            '@N3', [11, 22, 33], [12, 24, 36], [100, 201, 301], [110, 220, 321], [1, 22, 33], [2, 122, 133], 
            '@N5', [20111, 20222, 20333], [7133, 7144, 7155], 
            '@N7', [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)], 
            [('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5), ('f', 6), ('g', 7)], 
            '@N1', 100001]
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        self.assertEqual(exv, resv)

    def test_minimal_lambda(self):
        '''
        x -> x
        _ -> 2
        '''
        code = r'''
        res = []
        
        func foo(fn, x)
            fn(x)
        
        f1 = x -> x
        res <- foo(f1, 11)
        
        f2 = x -> 2
        res <- foo(f2, 1)
        
        res <- foo(x -> x, 3)
        
        res <- foo(x -> 5, 2)
        
        f3 = _ -> 10
        res <- foo(f3, 7)
        
        res <- foo(_ -> 100, 6)
        
        func g(a)
            _ -> a
        
        f4 = g(20)
        res <- f4(1)
        
        res <- foo(f4, 11) + 1000
        
        res <- foo(g(30), 22)
        
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [11, 2, 3, 5, 10, 100, 20, 1020, 30]
        self.assertEqual(exv, rvar.vals())

    def test_tail_recursion(self):
        ''' '''
        _ = '''
        # code of 10-million depth of tail recursion
        
        func foo(a, b)
            if a == 0
                return b
            foo(a - 1, b + 1)

        res <- foo(10**7, 0)
        '''
        code = r'''
        res = []
        
        func foo(a, b)
            if a == 0
                return b
            foo(a - 1, b * 2)
        
        res <- foo(10, 1)
        
        func f2(a, b)
            if a == 0
                return b
            f2(a - 1, b + 1)
        
        res <- f2(5000, 0)
        
        # tail recursion for a method
        struct A a:int
        
        func st:A ff(a, b)
            if a == 0
                return b
            st.ff(a - 1, b + st.a)
        
        a1 = A(3)
        res <- a1.ff(101, 0)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        sys.setrecursionlimit(100)
        trydo(ex, ctx)
        sys.setrecursionlimit(1000)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        self.assertEqual([1024, 5000, 303], rvar.vals())

    def test_carrying_cascade(self):
        ''' '''
        code = r'''
        res = []
        func foo(x)
            func plus(y)
                func f3(z)
                    x * 100 + y * 10 + z
        
        func argsToList(n1,n2,n3,n4,n5)
            [n1,n2,n3,n4,n5]
        
        func bar(a)
            func f2(b)
                func f3(c)
                    func f4(d)
                        func f5(e)
                            argsToList(a, b, c, d, e)

        # carrying in method
        struct B b:string
        
        func bin:B triple(x)
            func f2(y)
                func f3(q)
                    t = x * 100
                    ~"{bin.b}_{t + y * 10 + q}"
        
        res <- foo(3)(4)(5)
        res <- bar(11)(22)(33)(44)(55)
        b1 = B('B')
        res <- b1.triple(1)(2)(3)
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        self.assertEqual([345, [11, 22, 33, 44, 55], 'B_123'], rvar.vals())

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
        ffd = {}
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
        Resolved conflict between lambdas and previous syntax of matches. '''
        code = r'''
        c = 5
        res = 0
        match c
            1 /: res = 10
            2 /: res = c * 2
            _ /: res = 100

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




if __name__ == '__main__':
    main()
