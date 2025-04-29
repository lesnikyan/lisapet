'''
Function cases:
definition, call, args, results, etc.
'''

from unittest import TestCase, main
from tests.utils import *

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
        print('res = ', rr)
        '''
        _='''
        
        rr = []
        rr2 = []
        '''
        code = norm(code[1:])
        # print('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rr = ctx.get('rr')
        rr2 = ctx.get('rr2')
        # self.assertEqual(0, rr.get().data)
        self.assertEqual({2: 417, 4: 741, 6: 1079, 3: 423, 5: 753, 7: 1087}, rr.get().vals())
        # print('>>', rr.get())
        print('>>', rr2.get())

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
        
        print('res = ', r1, r2, r3)
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
            
            func foo(f, a, b)
                # print('>>==', f, a, b)
                a + f(b)
            
            f1 = x -> x * 10
            n1 = foo(f1, 2, 3)
            
            n2 = foo(x -> x * 100, 4, 5)
            n2 = foo(x -> x * 100, 6, 7)
            
            # # TODO: 1) append val to list : nums <- 5
            nn = [0,0,0,0,0]
            for i <- [1..5]
                nn[i-1] = foo(x -> x ** 2 , 1, i)
            
            print('lambda test:', n1, n2, nn)
            
        testLambdas()
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_lambda_as_arg(self):
        ''' function object as argument of function. '''
        code = r'''
        func foo(ff, arg)
            ff(arg * 2)
        f1 = x -> x * 3
        n1 = foo(f1, 5)
        n2 = foo( x -> 2 ** x , 5)
        print('n1,2 = ', n1, n2)
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
        print('nn = ', n1, n2)
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
        print('n1,2,3 = ', n1, n2, n3)
        '''
        code = norm(code[1:])
        # print('>>\n', code)
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
        print(res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        exp = [5005, 10005, 15005, 20005, 25005]
        resVal = ctx.get('res').get()
        print(resVal)
        self.assertListEqual(exp, resVal.get())


    def test_func_typed_args(self):
        ''' make vars and assign vals from tuple  '''
        code = '''
        func foo(name: string, nn: int, ff: float, arg4 )
            print('arg4:', arg4)
            div = ' ' * nn
            name + div + '/'
        
        print('p>>', foo('Brrr', 4, 0.1, '4444'))
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
            print('Code:', code)
            # code = norm(code[1:])
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            elems = clines[0].code
            cases = getCases()
            for cs in cases:
                if cs.match(elems):
                    print('#tt found cae: ', cs, 'exp:', ctype)
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
        print('cc res', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        exp.do(ctx)
        res = ctx.get('res').getVal()
        print('#t >>> r:', res)
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
        # print('$$ run test ------------------')
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
        print('$$ run test ------------------')
        exp.do(ctx)
        fn:Function = ctx.get('foo')
        print('#tt1>>> ', fn, type(fn))
        args = [value(2, TypeInt),value(3, TypeInt),value(4, TypeInt)]
        fn.setArgVals(args)
        ctxCall = Context(None)
        fn.do(ctxCall)
        res = fn.get()
        print('#tt2>>> ', res)



if __name__ == '__main__':
    main()
