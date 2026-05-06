''' '''



from unittest import TestCase, main

from tests.utils import *

import pdb


class TestMatchMaybe(TestCase):
    ''' '''
    



    def test_maybe_match_in_func(self):
        ''' some(sub): some(::int), some(var), some([a, b, s]), some(N{s: var}) '''
        
        code = r'''
        res = ['func: match maybe']
        
        func doSome(x: maybe)
            match x
                none /: 0
                some(null)
                    -100501
                some(a::int)
                    a * 100
                some(a :: float)
                    ~'{a:.2f}'
                some(s :: string)
                    s.map(\c -> ~'{c}!')
                some(nn @ [*])
                    nn.map(\e -> ~'_{e}_').join('; ')
        
        nn = [
            some(8), none,  some(2.54321),
            some(null), some('Abc'), some([1,2,3]), some('blue green red'.split(' ')),
        ]
        
        for n <- nn
            res <- doSome(n)
        
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
        exv = ['func: match maybe', 800, 0, '2.54', -100501, 'A!b!c!', '_1_; _2_; _3_', '_blue_; _green_; _red_']
        self.assertEqual(exv, resv)

    def test_maybe_match_some_sub(self):
        ''' some(sub): some(::int), some(var), some([a, b, s]), some(N{s: var}) '''
        code = r'''
        res = ['match: some(x) 1']
        
        nn1 = [0, 1, null, none, 
            some(3.2), some(1), 
            some('hello'), some([1,2,3]),
            some([4,5]), some((6,7)), some((12, 13, 14, 15)), 
        ]
        
        r1 = []
        for n <- nn1
            match n
                none /: r1 <- (1, n)
                some(::int) /: r1 <- (2, 1000 + n.get())
                some(s :: string) /: r1 <- (3, s)
                some(f::float) /: r1 <- (4, f)
                some([a, b]) /: r1 <- (5, (a,b))
                some(v @ [*]) /: r1 <- (6, v)
                some(v @ (a, b)) /: r1 <- (7, v)
                some(v @ (a, *)) /: r1 <- (8, v, a)
                _ /: r1 <- (-1, n)
        res <- r1
        
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
            'match: some(x) 1', 
            [(-1, 0), (-1, 1), (-1, null), (1, none), 
             (4, 3.2), (2, 1001), (3, 'hello'), (6, [1, 2, 3]), 
             (5, (4, 5)), (7, (6, 7)), (8, (12, 13, 14, 15), 12)]]
        self.assertEqual(exv, resv)

    def test_maybe_match_some_sub_container(self):
        ''' some(sub): some(::int), some(var), some([a, b, s]), some(N{s: var}) '''
        code = r'''
        res = ['match: some(x) 2']
        
        struct A a:int
        struct B b:string
        struct C c:maybe, s:string
        
        nn2 = [
            none, some(none),
            some([[11]]), 
            some(((22,),)), 
            some([({33:333},)]),
            some({12:123}), some({21:111, 22:222, 23:333}), 
            some([]), some((,)), some({}),
            some(A(31)),
            some(B('Bob')),
            some(C(none, '')), some(C(some(41), 'IIII-I')),
            C(some(42), '4-II')
        ]
        
        r2 = []
        for n <- nn2
            match n
                none /: r2 <- (1, n)
                some(none) /: r2 <- (101, n)
                some([[x]]) /: r2 <- (2, '[[x]]', x)
                some(((x,),)) /: r2 <- (201, [((x))], x)
                some([({k:v},)]) /: r2 <- (202, '[({k:v})]', k, v)
                some(dd @ {k: v}) /: r2 <- (3, dd, k, v)
                some(dd @ {_:_,*}) /: r2 <- (4, dd)
                some(cc @ :: (list|tuple|dict)) /: r2 <- (5, cc)
                some(A{a:val}) /: r2 <- (6, 'A', val)
                some(b @ B{}) /: r2 <- (7, 'B', b)
                some(C{c:none}) /: r2 <- (8, '?C-none')
                some(C{c:some(val), s:sval}) /: r2 <- (9, '?C-val', val, sval)
                C{c:some(val), s:sval} /: r2 <- (10, 'C', val, sval)
                _ /: r2 <- (-1, n)
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
        exv = [
            'match: some(x) 2', 
            [
                (1, none), (101, some(none)), (2, '[[x]]', 11), (201, [22], 22), 
                (202, '[({k:v})]', 33, 333), (3, {12: 123}, 12, 123), (4, {21: 111, 22: 222, 23: 333}), 
                (5, []), (5, ()), (5, {}), (6, 'A', 31), (7, 'B', "st@B{b: 'Bob'}"), 
                (8, '?C-none'), (9, '?C-val', 41, 'IIII-I'), (10, 'C', 42, '4-II')]]
        self.assertEqual(exv, resv)

    def test_maybe_match_simple(self):
        ''' none, ::maybe, some(), [none, some(), var@some()], {k: some()} '''
        code = r'''
        res = []
        
        struct A a: maybe
        
        nn1 = [
            0, 1, null, none, some(2), some('hello'), 
            some([1,2,3]), [some(3)], {'kbt': some('session')},
            A(some(5)), A(none), [(A(some(7)), 8)]
        ]
        
        r1 = []
        for n <- nn1
            match n
                null /: r1 <- (0, n)
                none /: r1 <- (1, n)
                some() /: r1 <- (2, n.get())
                [mb @ some()] /: r1 <- (3, 1000 + mb.get())
                {k: mb@some()}
                    r1 <- (4, {k: ~'<{mb.get()}>'})
                A{a:none} /: r1 <- (5, 'A-none')
                A{a: mb@some()} /: r1 <- (6, ~'A-some({mb.get()})')
                [(a @ A{a:some()}, b)] /: r1 <- (7, ~'[(A-some({a.a.get()}), {b})]')
                _ /: r1 <- (-1, n)
        res <- r1
        
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
            [(-1, 0), (-1, 1), (0, null), (1, none), (2, 2), (2, 'hello'), (2, [1, 2, 3]), 
             (3, 1003), (4, {'kbt': '<session>'}), (6, 'A-some(5)'), (5, 'A-none'), (7, '[(A-some(7), 8)]')]]
        self.assertEqual(exv, resv)


if __name__ == '__main__':
    main()
