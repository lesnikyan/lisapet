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



# TODO: add asserts to each test

class TestFunc(TestCase):
    

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
        resVal = ctx.get('res')
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
        res = ctx.get('res').get()
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
        r1 = ctx.get('r1').get()
        r2 = ctx.get('r2').get()
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
