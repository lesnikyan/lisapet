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
from objects.func import Function
from nodes.func_expr import setNativeFunc
from nodes.func_expr import setNativeFunc
from cases.utils import *
from tree import *
from eval import *



class TestFuncs(TestCase):



    def test_tail_recursion(self):
        ''' '''
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

    def test_func_args_typed_by_list_dict(self):
        ''' '''
        code = r'''
        res = []
        
        func key_intersect(nn:list, dd:dict)
            r = []
            for n <- nn
                if n ?> dd
                    r <- dd[n]
            r
        
        keys = [11, 22, 'a', 'b']
        data = {22:220022, 'a':'Aloha!'}
        r1 = key_intersect(keys, data)
        res <- r1
        
        keys2 = [50, 17, 'abc']
        data2 = {17:'seventeen', 'abc':'Bonjour', 'qwerty':'asdfg'}
        res <- key_intersect(keys2, data2)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        exv = [[220022, 'Aloha!'], ['seventeen', 'Bonjour']]
        self.assertEqual(exv, rvar.vals())

    def test_func_from_method(self):
        ''' test when func is returned from method and immediately called 
            obj.foo(a)(b)
        '''
        
        code = r'''
        res = []
        
        struct A a:int
        struct R r:list
        struct B(A) b:string
        
        func st:A foo(a)
            x -> x + a
        
        func st:B bInfo(y)
            x -> ~"{st.a},{st.b} ({x}, {y})"
        
        func bin:B triple(x)
            func f2(y)
                t = x * 100
                (q, post) -> ~"{bin.b}_{t + y * 10 + q}{post}"
        
        aa = A{}
        res <-  aa.foo(2)(5)
        
        r1 = R([[1,2,3]])
        res <-  r1.r[0][1]
        
        b1 = B(11, 'B-1')
        
        res <- b1.foo(3)(7)
        res <- b1.bInfo(9)(8)
        res <- b1.triple(3)(5)(7, '_Yo')
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [7, 2, 10, '11,B-1 (8, 9)', 'B-1_357_Yo']
        self.assertEqual(exv, rvar.vals())

    def test_overload_func_as_arg(self):
        ''' func overload with func as argument
        '''
        
        code = r'''
        res = []
        
        
        # over no args
        func foo()
            1
            
        # over 1 arg by type
        func foo(x:bool)
            x ? 'dark' : 'light'
            
        func foo(f:function)
            f()
        
        func ret(f:function)
            f
        
        func ret(a:float)
            x -> x * a
        
            
        func foo(x:string)
            ~'~`{x}`:str'
        
            
        # overload 2 args, by type
        func foo(a:float,b:float)
            a + b
        
        func foo(f:function, b)
            f(b)
        
        func foo(f:function, b:list)
            b.map(f)
        
        struct A a:int
        
        func st:A foo()
            st.a
        
        func st:A foo(a:int, b:int)
            a + b
        
        func st:A foo(f:function, x:int)
            f(x) + 1000
        
        func st:A boo(x, f:function)
            y -> y + f(x)
        
        # call
        
        func f0()
            'func-0'
        
        func f1(x)
            x + 300
        
        res <- '#1'
        res <- foo()
        res <- foo(true)
        res <- foo('hello')
        res <- foo(f0)
        res <- ret(f1)(12)
        res <- ret(1.1)(5)
        
        
        res <- '#2'
        
        func x100(x)
            x * 100
        
        res <- foo(1, 2)
        res <- foo(x100, 1.25)
        res <- foo(x100, [1,2,3])
        
        res <- '# struct'
        
        a1 = A(17)
        res <- a1.foo()
        res <- a1.foo(10, 4)
        res <- a1.foo(x100, 2)
        
        fa = a1.boo(3, x100)
        res <- fa(41)
        res <- a1.boo(3, x100)(52)        
        res <- a1.boo(4, x100)(1.5)
        
        # for n <- res /: print('> ', n)
        # print('res', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = ['#1', 1, 'dark', '~`hello`:str', 'func-0', 312, 5.5, '#2', 3.0, 125.0, [100, 200, 300], 
               '# struct', 17, 14, 1200, 341, 352, 401.5]
        self.assertEqual(exv, rvar.vals())

    def test_overload_methods(self):
        ''' test overload for methods '''
        code = r'''
        res = []
        
        struct A a:int
        struct B(A) b:int
        struct Caramba(B) c:int
        
        struct D d:float
        
        struct Utype u: int
        
        func  u:Utype foo()
            d = 10
            if d > 0
                c = 20
            else if d < 15
                c = 30
            else
                c = 7
            -1
        
        func u:Utype foo(x:int)
            x * 10
        
        
        func u:Utype foo(x:string)
            ~'u-string<{x}>'
        
        func u:Utype bar()
            -2
        
        func u:Utype bar(x:float)
            x / 10 + 1000
        
        func u:Utype bar(x:string)
            ~'bar<{x}>'
        
        
        struct types
        
        func u:Utype bar(aaa:A)
            aaa.a + 4400
        
        func u:Utype bar(ss:Caramba)
            ss.c + 7700
        
        func u:Utype bar(xa:A, xd:D)
            r = xa.a * xd.d
            ~"barAD:{xa.a} * {xd.d} = {r}"
        
        func u:Utype baz(x:bool)
            ('baz', x ? 'yep' : 'nop')
            
        func u:Utype baz(x:string)
            'baz(%s)' << x
            
        func u:Utype baz(x)
            ('baz-any', x)
        
        # 2 args
        
        func u:Utype foo(a:int, b:int)
            a * b
        
        func u:Utype foo(a:float, b:float)
            a / b
        
        func u:Utype foo(a:string, b:string)
            '%s||%s' << (a, b)
        
        # 3 arg 
        func u:Utype foo(a,b,c)
            [-3, a, b, c]
            
        func u:Utype foo(a:bool,b:float,c:float)
            [-30, a,b,c]
        
        # 4 args
        func u:Utype foo(a,b,c,d)
            [-4, a,b,c,d]
            
        u1 = Utype{}
        
        # 0
        res <- u1.foo()
        res <- u1.bar()
        
        
        # 1
        res <- u1.foo('hello!')
        
        res <- u1.bar(1)
        
        # # structs
        a1 = A(1)
        res <- u1.bar(a1)
        
        b1 = B(10, 2)
        res <- u1.bar(b1)
        
        c1 = Caramba(33, 11, 22)
        res <- u1.bar(c1)
        
        # # 2
        res <- u1.foo(11, 13)
        
        a2 = A(3)
        d2 = D(2.12)
        res <- u1.bar(a2, d2)
        
        b3 = B(5, 10)
        d3 = D(1.5)
        res <- u1.bar(b3, d3)
        
        
        func int1()
            1
        
        val5 = 5
        
        # 3
        res <- u1.foo(2, 1.5, 2.5)
        res <- u1.foo(int1(), val5, 3)
        res <- u1.foo(true, 11.1, 22.2)
        res <- u1.foo(false, 11,22,33)
        res <- u1.foo(false, 1.1,2.2,3.3)
        res <- u1.foo(false, val5, 2.5, true)
        
        # over with basic type any
        res <- u1.baz(true)
        res <- u1.baz(false)
        res <- u1.baz('-str-')
        res <- u1.baz(10)
        res <- u1.baz(2.5)
        res <- u1.baz([1,2,3])
        res <- u1.baz(A(115))
        res <- u1.baz({1:11})
        res <- u1.baz((2, 23))
        
        # for n <- res /: print('> ', n)
        # print('res', res)
        
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            -1, -2, 'u-string<hello!>', 1000.1, 4401, 4410, 7722, 143, 
            'barAD:3 * 2.12 = 6.36', 'barAD:5 * 1.5 = 7.5', 
            [-3, 2, 1.5, 2.5], [-3, 1, 5, 3], 
            [-30, True, 11.1, 22.2], [-4, False, 11, 22, 33], 
            [-4, False, 1.1, 2.2, 3.3], [-4, False, 5, 2.5, True], 
            ('baz', 'yep'), ('baz', 'nop'), 'baz(-str-)', 
            ('baz-any', 10), ('baz-any', 2.5), ('baz-any', [1, 2, 3]), 
            ('baz-any', 'st@A{a: 115}'), ('baz-any', {1: 11}), ('baz-any', (2, 23))]
        self.assertEqual(exv, rvar.vals())

    def test_func_all_variative_cases(self):
        ''' func overload 
            can't be overloaded (at least one such case):
            1. if has var... argument
            2. if has default values
            3. overloaded func can't be assigned by name, 
                [possible by future feature `func type` (: arg-types)
                    name(types) like f = foo(: int, int)
                    name(count) like f = foo(: _, _)      ]
        '''
        
        code = r'''
        res = []
        
        struct A a:int
        struct AA(A) aa: string
        struct B b:int
        struct B2 b2:string
        struct C(A, B2) c:string
        struct D(B) d:string
        
        # over no args
        func foo()
            1
            
        # over 1 arg by type
        func foo(x:int)
            x * 10
            
        func foo(x:float)
            x / 10.
            
        func foo(x:string)
            ~'foo `{x}`:str'
        
        func foo(a:A)
            a.a
        
        func foo(b:B)
            b.b
            
        # overload 2 args, by type
        func foo(a:float,b:float)
            a + b
        
        func foo(a:string, b:string)
            if b :: null
                b = 'null'
            ~'{a}:>{b}'
        
        func foo(a,b,c,d)
            [a,b,c,d]
        
        func foo(a,b,c,d,e)
            {'k1':a, 'k2':b, 'k3':c, 'k4':d, 'k5':e}
        
        # over 2 args, by type with any
        
        func bar(a:string, b:float)
            ~'a::{b * 1000}'
        
        func bar(a,b)
            [a,b]
        
        # variadic args...
        
        func makeDict(args...)
            pairLen = toint(len(args) / 2)
            dr = {}
            for i <- iter(pairLen)
                k, v = args[i*2], args[i*2+1]
                dr <- (k, v)
            dr

        # named default
        
        func tag(s, inner='', open='<', close='>')
            if len(inner) > 0
                inner = ' ' + inner
            ~'{open}{s}{inner}{close}'

        # call
        
        a1 = A(101)
        aa2 = AA{a:102, aa:'aa-2'}
        b1 = (202)
        c1 = C(103, 'b2-33', 'c-33')
        d1 = D(404, 'dd-44')
        
        res <- '<foo obj>'
        res <- foo(a1)
        res <- foo(aa2)
        res <- foo(b1)
        res <- foo(c1)
        res <- foo(d1)
        
        res <-'<foo #0>'
        res <- foo()
        # # 1
        res <-'<foo #1>'
        res <- foo(1)
        res <- foo(1.5)
        res <- foo('hello!')
        
        res <-'<foo #2>'
        res <- foo(500, 2)
        res <- foo(510, 2.5)
        res <- foo('Yaa', 'Xoo')
        res <- foo('nil', null)
        
        
        res <-'<foo #4>'
        res <- foo(1,2,3,4)
        res <- foo('foo','4','args','case')
        
        res <-'<foo #5>'
        res <- foo(11,22,33,44,55)
        res <- foo('foo','5','args','case','done')
        
        res <-'<bar #2>'        
        res <- bar('a',2.0)
        res <- bar(1,2.5)
        res <- bar(2,2)
        res <- bar(3,[3,4,5])
        res <- bar(4,{5:55, 6:77})
        
        
        res <-'<makeDict(n...)>'
        res <- makeDict('a', 111, 'b', 222, 'c', 333 )
        res <- makeDict(1, 11, 2, 22, 3, 33, 4, 44)
        res <-'<tag>'
        res <- tag('div')
        res <- tag('div', 'id="11"')
        res <- tag('div', open='</')
        res <- tag('div', open='<=', close='=>')
        
        # for n <- res /: print('> ', n)
        # print('res', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            '<foo obj>', 101, 102, 2020, 103, 404, '<foo #0>', 1, '<foo #1>', 10, 0.15, 'foo `hello!`:str', '<foo #2>', 
            502.0, 512.5, 'Yaa:>Xoo', 'nil:>null', '<foo #4>', [1, 2, 3, 4], ['foo', '4', 'args', 'case'], '<foo #5>', 
            {'k1': 11, 'k2': 22, 'k3': 33, 'k4': 44, 'k5': 55}, {'k1': 'foo', 'k2': '5', 'k3': 'args', 'k4': 'case', 'k5': 'done'}, 
            '<bar #2>', 'a::2000.0', [1, 2.5], [2, 2], [3, [3, 4, 5]], [4, {5: 55, 6: 77}], '<makeDict(n...)>', 
            {'a': 111, 'b': 222, 'c': 333}, {1: 11, 2: 22, 3: 33, 4: 44}, '<tag>', '<div>', '<div id="11">', '</div>', '<=div=>']
        self.assertEqual(exv, rvar.vals())

    def test_overload_by_args_type_compatible(self):
        ''' more complex case, for overload by type
            if called expr don't have equal types of existed funcs, but have compatible
            def: func foo(float, float); call: foo(1,2)
            '''
        code = r'''
        res = []
            
        func foo()
            1
            
        func foo(x:int)
            x * 10
            
        func foo(x:string)
            ~'foo<{x}>'
            
        # func foo(x)
        #     ('any', x)
            
        func bar(x:float)
            x / 10 + 1000
            
        func bar(x:string)
            ~'bar<{x}>'
        
            
        # TODO: complete after refactoring of collection constructors
        
        # func foo(x:list)
        #     len(x) + 3000
            
        # func foo(x:dict)
        #     x.keys()
            
        # func foo(x:tuple)
        #     len(x) + 2000
        
        # struct types
        
        struct A a:int
        struct B(A) b:int
        struct Caramba(B) c:int
        
        func bar(a:A)
            a.a + 4400
        
        func bar(ss:Caramba)
            ss.c + 7700
        
        
        # 2 args
        
        func foo(a:int, b:int)
            a * b
        
        func foo(a:float, b:float)
            (a + b) / 10 + 100
        
        func bar(a:bool, b:float)
            a ? b + 500: -1000.0
        
        # 3 args
        
        func foo(a:int, b:float, c:float)
            [b * c + i * 100; i <- iter(a)]
            
        func foo(a:int, b:string, c:string)
            r = -100
            match a
                0 /: r = ~'-{b}'
                1 /: r = ~'{b}:{c}'
                _ /: r = [b]+[c ; i <- iter(a)]
            r
        
        # 4 args
        
        func foo(a:float, b:float, c:float, d:float)
            ~"{a:.3f}/{b:.3f}/{c:.3f}/{d:.3f}"
        
        func foo(a:string, b:float, c:float, d:float)
            ~"{a:s}/{b:.3f}/{c:.3f}/{d:.3f}"
        
        func foo(a:string, b:string, c:float, d:float)
            ~"{a:s}/{b:s}/{c:.3f}/{d:.3f}"
        
        func foo(a:string, b:string, c:string, d:float)
            ~"{a:s}/{b:s}/{c:s}/{d:.3f}"
        
        # 1
        res <- foo()
        res <- foo('hello!')
        res <- foo(1)
        res <- foo(true)
        res <- foo(false)
        
        res <- bar(0)
        res <- bar(false)
        res <- bar(true)
        res <- bar(2)
        res <- bar(3.5)
        
        # structs
        a1 = A(1)
        res <- bar(a1)
        
        b1 = B(10, 2)
        res <- bar(b1)
        
        c1 = Caramba(33, 11, 22)
        res <- bar(c1)
        
        # 2
        res <- foo(11, 13)
        res <- foo(11.0, 13)
        res <- foo(11.0, true)
        res <- foo(true, 13.)
        res <- bar(true, 11)
        res <- bar(true, 13.0)
        res <- bar(true, true)
        
        func int1()
            1
        
        # 3
        res <- foo(2, 1.5, 2.5)
        res <- foo(2, 2, 3)
        res <- foo(2, true, true)
        res <- foo(0, '1-', 'w11')
        res <- foo(false, '2-', 'w22')
        res <- foo(null, '3-', 'w33')
        res <- foo(1, '11-', 'z11')
        res <- foo(true, '22-', 'z12')
        res <- foo(int1(), '33-', 'z13')
        
        res <- foo(2, '44-', 'z21')
        res <- foo(3, '55-', 'z22')
        res <- foo(4, '66-', 'z23')
        
        # 4
        res <- foo(1., 2., 3., 4.)
        res <- foo(1.0, 2.0, 3.0, 4.0)
        res <- foo(1.1, 2.1, 3.1, 4.1)
        res <- foo(1.05, 2.05, 3.05, 4.05)
        res <- foo(1, 2, 3, 4)
        res <- foo(true, false, null, int1())
        
        # 4 num-str
        res <- foo('aa', 2, 3, 4)
        res <- foo('bb', '-', 3, 4)
        res <- foo('cc', '=', '!', 4)
        res <- foo('ff', '@', '^', false)
        
        # for n <- res /: print('> ', n)
        # print('res', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            1, 'foo<hello!>', 10, 10, 0, 1000.0, 1000.0, 1000.1, 1000.2, 1000.35, 
            4401, 4410, 7722, 143, 102.4, 101.2, 101.4, 511.0, 513.0, 501.0, 
            [3.75, 103.75], [6.0, 106.0], [1.0, 101.0], 
            '-1-', '-2-', '-3-', '11-:z11', '22-:z12', '33-:z13', 
            ['44-', 'z21', 'z21'], ['55-', 'z22', 'z22', 'z22'], ['66-', 'z23', 'z23', 'z23', 'z23'], 
            '1.000/2.000/3.000/4.000', '1.000/2.000/3.000/4.000', '1.100/2.100/3.100/4.100', 
            '1.050/2.050/3.050/4.050', '1.000/2.000/3.000/4.000', '1.000/0.000/0.000/1.000', 
            'aa/2.000/3.000/4.000', 'bb/-/3.000/4.000', 'cc/=/!/4.000', 'ff/@/^/0.000']
        self.assertEqual(exv, rvar.vals())


    def test_overload_by_args_type_strict(self):
        ''' func overload by type of args '''
        code = r'''
        res = []
            
        func foo()
            1
            
        func foo(x:int)
            x * 10
            
        func foo(x:float)
            x / 100 + 5000
            
        func foo(x:string)
            ~'<x>'
        
        struct A a:int
        struct B b:int
        struct SuperLongNamedStructType c:int
        
        func foo(a:A)
            a.a + 2200
        
        func foo(b:B)
            b.b + 5205
        
        func foo(ss:SuperLongNamedStructType)
            ss.c + 9200
            
        # TODO: complete after refactoring of collection constructors
        
        # func foo(x:list)
        #     len(x) + 3000
            
        # func foo(x:dict)
        #     x.keys()
            
        # func foo(x:tuple)
        #     len(x) + 2000
        
        res <- foo()
        res <- foo(1)
        res <- foo(100.0)
        res <- foo('hello!')
        
        a1 = A(1)
        res <- foo(a1)
        
        b1 = B(10)
        res <- foo(b1)
        
        c1 = SuperLongNamedStructType(33)
        res <- foo(c1)
        

        # 2 args
        
        func foo(a:int, b:int)
            a * b
        
        func foo(a:float, b:float)
            (a + b) / 10 + 100
        
        func foo(a:bool, b:float)
            a ? b + 500: -1000.0
        
        func foo(a:string, b:int)
            [~'{_a}' ; i <- iter(b)]
        
        func foo(a:int, b:string)
            [~'{b_}' ; i <- iter(a)]
        
        
        res <- foo(11, 20)
        res <- foo(11, 20)
        res <- foo(11, 20)
        res <- foo(11, 20)
        
        # print('res', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [1, 10, 5001.0, '<x>', 2201, 5215, 9233, 220, 220, 220, 220]
        self.assertEqual(exv, rvar.vals())

    def test_overload_by_args_count_methods(self):
        ''' func overload by count of args '''
        code = r'''
        res = []
        
        struct A a:int
        
        func st:A foo()
            1
            
        func st:A foo(x)
            x * 10
        
        func st:A foo(x, y)
            x * y
        
        func st:A foo(x, y, z)
            x * y + z
        
        func st:A foo(a,b,c,d)
            (a+b) * (c + d)
        
        func st:A foo(a,b,c,d,e)
            ~' < {a} {b} {c} {d} {e} > '
        
        func st:A foo(a,b,c,d,e,f)
            [a,b,c,d,e,f].map(x -> x * 10)
        
        func st:A foo(fff, a,b,c,d,e,f,g,h,i,j,k,l,m,n,,o,p,q,r,s,t,u,v,w,x,y,z)
            nn = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,,o,p,q,r,s,t,u,v,w,x,y,z]
            nn.map(fff)
        
        a1 = A{}
        
        res <- a1.foo()
        
        res <- a1.foo(3)
        
        res <- a1.foo(3, 4)
        
        res <- a1.foo(3, 3, 11)
        res <- a1.foo(2, 3, 4, 6)
        
        res <- a1.foo(1,2,3,4,5)
        res <- a1.foo(1,2,3,4,5,6)
        res <- a1.foo(
            x -> a1.foo(x),
            1,2,3,4,5,6,7,8,9,10,
            11,12,13,14,15,16,17,18,19,20,
            21,22,23,24,25,26
        )
        
        # print('res', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            1, 30, 12, 20, 50, ' < 1 2 3 4 5 > ', [10, 20, 30, 40, 50, 60], 
            [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260]]
        self.assertEqual(exv, rvar.vals())

    def test_overload_by_args_count_only(self):
        ''' func overload by count of args '''
        code = r'''
        res = []
        
        func foo()
            1
            
        func foo(x)
            x * 10
        
        func foo(x, y)
            x * y
        
        func foo(x, y, z)
            x * y + z
        
        func foo(a,b,c,d)
            (a+b) * (c + d)
        
        func foo(a,b,c,d,e)
            ~' < {a} {b} {c} {d} {e} > '
        
        func foo(a,b,c,d,e,f)
            [a,b,c,d,e,f].map(x -> x * 10)
        
        func foo(fff, a,b,c,d,e,f,g,h,i,j,k,l,m,n,,o,p,q,r,s,t,u,v,w,x,y,z)
            nn = [a,b,c,d,e,f,g,h,i,j,k,l,m,n,,o,p,q,r,s,t,u,v,w,x,y,z]
            nn.map(fff)
        
        res <- foo()
        
        res <- foo(2)
        
        res <- foo(2, 4)
        
        res <- foo(3, 3, 11)
        res <- foo(2, 3, 4, 6)
        
        res <- foo(1,2,3,4,5)
        res <- foo(1,2,3,4,5,6)
        res <- foo(
            x -> foo(x),
            1,2,3,4,5,6,7,8,9,10,
            11,12,13,14,15,16,17,18,19,20,
            21,22,23,24,25,26
        )
        
        # print('res', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            1, 20, 8, 20, 50, ' < 1 2 3 4 5 > ', [10, 20, 30, 40, 50, 60], 
            [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260]]
        self.assertEqual(exv, rvar.vals())

    def test_func_variadic_args_in_methods(self):
        ''' def foo(args...) '''
        code = r'''
        res = []
        
        struct A a: int, b: string
        
        func a:A f1(nn...)
            a.a = nn.fold(0, (a, b) -> a + b)
        
        a1 = A{}
        a1.f1()
        res <- ('f1-0', a1.a)
        a1.f1(1)
        res <- ('f1-0', a1.a)
        a1.f1(1,2)
        res <- ('f1-0', a1.a)
        a1.f1(1,2,3)
        res <- ('f1-0', a1.a)
        a1.f1(1,2,3,4,5,6,7,8,7,9)
        res <- ('f1-0', a1.a)
        
        func a:A f2(x, y, nn...)
            k = x + y
            a.a = k * nn.fold(0, (a, b) -> a + b)
        
        a2 = A{}
        a2.f2(3, 7)
        res <- ('f2-2', a2.a)
        a2.f2(3, 7, 2)
        res <- ('f2-2', a2.a)
        a2.f2(3, 7, 2,3)
        res <- ('f2-2', a2.a)
        a2.f2(3, 7, 2,3,4,5,6,7,8,9)
        res <- ('f2-2', a2.a)
        
        # default-args after collector... never will passed by order, only by name
        func a:A f4(x, nn..., pref='', post='')
            tt = [~"{pref}{x}{n}{post}" ; n <- nn]
            n = len(tt)
            a.b = tt.join(' ')
            n
        
        a3 = A{}
        n = a3.f4('A-', 'a')
        res <- (~'f4-1 n={n}', a3.b)
        n = a3.f4('B-', 'b', 'c')
        res <- (~'f4-2 n={n}', a3.b)
        n = a3.f4('C-', 'c', 'd', 'e', pref='<?', post='?>')
        res <- (~'f4-3 n={n}', a3.b)
        n = a3.f4('D-', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', pref='[=', post='=]')
        res <- (~'f4-4 n={n}', a3.b)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            ('f1-0', 0), ('f1-0', 1), ('f1-0', 3), ('f1-0', 6), ('f1-0', 52),
            ('f2-2', 0), ('f2-2', 20), ('f2-2', 50), ('f2-2', 440),
            ('f4-1 n=1', 'A-a'), ('f4-2 n=2', 'B-b B-c'), ('f4-3 n=3', '<?C-c?> <?C-d?> <?C-e?>'),
            ('f4-4 n=8', '[=D-d=] [=D-e=] [=D-f=] [=D-g=] [=D-h=] [=D-i=] [=D-j=] [=D-k=]')
        ]
        self.assertEqual(exv, rvar.vals())

    def test_func_variadic_args(self):
        ''' def foo(args...) '''
        code = r'''
        res = []
        
        func f1(nn...)
            [100 + n; n <- nn]
        
        res <- ('f1-0', f1())
        res <- ('f1-0', f1(1))
        res <- ('f1-0', f1(1,2))
        res <- ('f1-0', f1(1,2,3))
        res <- ('f1-0', f1(1,2,3,4,5,6,7,8,7,9))
        
        func f2(x, y, nn...)
            nn.map(n -> x * y + n)
        
        res <- ('f2-2', f2(3, 7))
        res <- ('f2-3', f2(3, 7, 2))
        res <- ('f2-4', f2(3, 7, 2,3))
        res <- ('f2-10', f2(3, 7, 2,3,4,5,6,7,8,9))
        
        func f3(a, b=2, nn...)
            snn = nn.fold(0, (x, y) -> x+y)
            if snn == 0
                snn = 1
            (a + b) * snn
        
        res <- ('f3-1', f3(1)) # 3
        res <- ('f3-2', f3(1,1)) # 2
        res <- ('f3-2b', f3(1,b=2)) # 3
        res <- ('f3-3', f3(1,1,2)) # 4
        b = 2
        res <- ('f3-3b', f3(1,b,2)) # 6
        res <- ('f3-6', f3(1,1, 1,1,1,1,1)) # 10
        
        # # default-args after collector... never will passed by order, only by name
        func f4(x, nn..., pref='', post='')
            [~"{pref}{x}{n}{post}" ; n <- nn]
        
        res <- ('f4-1', f4('A-', 'a'))
        res <- ('f4-2', f4('B-', 'b', 'c'))
        res <- ('f4-3', f4('C-', 'c', 'd', 'e', pref='<', post='>'))
        res <- ('f4-4', f4('D-', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', pref='(=', post='=)'))
        
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
            ('f1-0', []), ('f1-0', [101]), ('f1-0', [101, 102]), ('f1-0', [101, 102, 103]), ('f1-0', [101, 102, 103, 104, 105, 106, 107, 108, 107, 109]),
            ('f2-2', []), ('f2-3', [23]), ('f2-4', [23, 24]), ('f2-10', [23, 24, 25, 26, 27, 28, 29, 30]), 
            ('f3-1', 3), ('f3-2', 2), ('f3-2b', 3), ('f3-3', 4), ('f3-3b', 6), ('f3-6', 10), 
            ('f4-1', ['A-a']), ('f4-2', ['B-b', 'B-c']), ('f4-3', ['<C-c>', '<C-d>', '<C-e>']), 
            ('f4-4', ['(=D-d=)', '(=D-e=)', '(=D-f=)', '(=D-g=)', '(=D-h=)', '(=D-i=)', '(=D-j=)', '(=D-k=)'])]
        self.assertEqual(exv, rvar.vals())

    def test_func_named_and_default_for_methods(self):
        ''' obj.foo(1, b=2)  '''
        code = r'''
        res = []
        
        struct A a:int, b:string
        
        func inst:A f1(aaa:int=-1, bbb:string=null)
            n = aaa
            if n < 0
                n = inst.a
            s = inst.b
            if bbb::string
                s = bbb
            [s ; n <- iter(n)]
        
        
        a = A(1, 'A')
        res <- ('a.f1-0', a.f1())
        res <- ('a.f1-1', a.f1(2, 'bb'))
        # all args passed by name
        res <- ('a.f1-1', a.f1(3, bbb='cc'))
        res <- ('f1-2', a.f1(aaa=2, bbb='dd'))
        res <- ('f1-3', a.f1(bbb='E', aaa=4))
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            ('a.f1-0', ['A']), ('a.f1-1', ['bb', 'bb']), 
            ('a.f1-1', ['cc', 'cc', 'cc']), ('f1-2', ['dd', 'dd']), 
            ('f1-3', ['E', 'E', 'E', 'E'])]
        self.assertEqual(exv, rvar.vals())
        

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
        
        # use vars and expressions in named arg
        a = 1
        b = 2
        
        func foo(x)
            10 * x
        
        res <- ('f1-11', f1(aaa=a, bbb=b))
        res <- ('f1-12', f1(bbb=b, aaa=a))
        res <- ('f1-13', f1(aaa=1, bbb=foo(5)))
        res <- ('f1-14', f1(aaa=foo(6), bbb=foo(7)))
        
        # use element of collection as a 
        nn = [1,2,3]
        dd = {'a':11, 'b':22}
        
        res <- ('f1-15', f1(nn[1], bbb=nn[0]))
        res <- ('f1-16', f1(dd['a'], bbb=dd['b']))
        
        # use struct fields and methods
        struct A a:int, b:int
        
        func a:A sum()
            a.a + a.b
        
        aa1 = A(12, 13)
        aa2 = A(21, 32)

        res <- ('f1-17', f1(aaa=aa1.a, bbb=aa1.b))
        res <- ('f1-18', f1(bbb=aa1.sum(), aaa=aa2.sum()))
        res <- ('f1-19', f1(bbb=aa1.b + b, aaa=aa2.sum() + aa1.sum()))
        
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
            ('f3-6', [51, 52, 53, 54, 55, 560, 570, 580, 590, 10, 11, 512]), 
            ('f1-11', (1, 2)), ('f1-12', (1, 2)), ('f1-13', (1, 50)), ('f1-14', (60, 70)), 
            ('f1-15', (2, 1)), ('f1-16', (11, 22)), ('f1-17', (12, 13)), ('f1-18', (53, 25)), ('f1-19', (78, 15))]
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
        # self.fail()
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
        def"""
        res = []
        for s <- nn
            res <- len(s)
        # print('res = ', res)
        '''
        code = norm(code[1:])

        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
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
                1 /: r += m
                2 /: r = 2 * (k + m)
                _ /: k * 10 + m
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
        
        func xxist3(a, b, c)
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
                    nn = xxist3(i, i%3, i%7)
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
        
        # print('res1 = ', rr)
        # print('res2 = ', rr2)
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
