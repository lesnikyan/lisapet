'''

'''


from unittest import TestCase, main

from tests.utils import *

import pdb


class TestMaybe(TestCase):
    ''' '''


    def test_maybe_is_some(self):
        ''' '''
        code = r'''
        res = []
        
        ss = [
            0, 1, null, none, [],
            some(1), some(null), some(none),
            some(some(1)), some([]), some('a')
        ]
        
        for n <- ss
            res <- n
            res <- isNone(n)
            res <- isSome(n)
        
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
            0, False, False, 
            1, False, False, 
            null, False, False, 
            none, True, False, 
            [], False, False, 
            some(1), False, True, 
            some(null), False, True, 
            some(none), False, True, 
            some(some(1)), False, True, 
            some([]), False, True, 
            some('a'), False, True]
        self.assertEqual(exv, resv)

    def test_maybe_fold(self):
        ''' functional feature: fold for maybe type '''
        code = r'''
        res = []
        
        # some(int)
        func sum(a, b)
            a + b
        
        res <- some(5).fold(2, sum)
        res <- none.fold(3, sum)
        
        # some(string)
        
        func pref(acc:string, val:string)
            ~'{acc}{val}'
        
        res <- some('fit').fold('pro', pref)
        res <- none.fold('arc', pref)
        
        # some(list)
        func listSum(base, nn)
            nn.fold(base, sum)
        
        res <- some([1,2,3]).fold(10, listSum)
        res <- none.fold(5, listSum)
        
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
        exv = [7, 3, 'profit', 'arc', 16, 5]
        self.assertEqual(exv, resv)

    def test_maybe_maybe(self):
        ''' '''
        code = r'''
        res = []
        
        f1 = \x -> [x]
        res <- some(1).maybe([], f1)
        res <- none.maybe([], f1)
        
        f1 = \ x -> 101 * x
        
        func f2(x)
            match x
                ::int /: 200 + x
                ::glif /: ~'/{x}/'
                re`^_.+` /: x.map(f2)
                :: string /: ~'<{x}>'
                [::int, ::int] /: x.map(f1)
                :: list /: x.map(f2)
                none /: none # need to fix
                :: maybe /: x.map(f2)
                {*} /: dict(x.items().map(\kv -> (f2(kv[0]), f2(kv[1]+5000))))
                _ /: ('_', x)
            
        ss = [
            some(0), none, 
            some(17), some(null), some('Hello!'), some('128'), 
            some([3,4,5]), some([16,27]), some(4.4), some({'ax':11, 'bx':22}),
            some(none), some(some('ich bin')), some('_yellow_')
        ]
        
        k = len(res)
        for s, i <- ss, iter(len(ss))
            res <- (i + k, s.maybe((null,), f2))
        
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
            [1], [], 
            (2, 200), (3, (null,)), (4, 217), (5, ('_', null)), (6, '<Hello!>'), (7, '<128>'), 
            (8, [203, 204, 205]), (9, [1616, 2727]), (10, ('_', 4.4)), (11, {'<ax>': 5211, '<bx>': 5222}), 
            (12, none), (13, some('<ich bin>')), (14, '<_><y><e><l><l><o><w><_>')]
        self.assertEqual(exv, resv)

    def test_maybe_map(self):
        ''' '''
        code = r'''
        res = []
        
        m1 = some(1)
        m0 = none
        f1 = \ x -> 101 * x
        
        res <- (0, m0.map(f1))
        res <- (1, m1.map(f1))
        
        func f2(x)
            match x
                ::int /: 200 + x
                ::glif /: ~'/{x}/'
                re`^_.+` /: x.map(f2)
                :: string /: ~'<{x}>'
                [::int, ::int] /: x.map(f1)
                :: list /: x.map(f2)
                none /: none # need to fix
                :: maybe /: x.map(f2)
                {*} /: dict(x.items().map(\kv -> (f2(kv[0]), f2(kv[1]+5000))))
                _ /: ('_', x)
            
        ss = [
            some(0), none, 
            some(5), some(null), some('Hello!'), some('128'), 
            some([3,4,5]), some([6,7]), some(3.2), some({'ax':11, 'bx':22}),
            some(none), some(some('ich bin')), some('_green_')
        ]
        
        k = len(res)
        for s, i <- ss, iter(len(ss))
            res <- (i + k, s.map(f2))
        
        
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
            (0, none), (1, some(101)), (2, some(200)), (3, none), (4, some(205)), 
            (5, some(('_', null))), (6, some('<Hello!>')), (7, some('<128>')), 
            (8, some([203, 204, 205])), (9, some([606, 707])), (10, some(('_', 3.2))), 
            (11, some({'<ax>': 5211, '<bx>': 5222})), (12, some(none)), 
            (13, some(some('<ich bin>'))), (14, some('<_><g><r><e><e><n><_>'))]
        self.assertEqual(exv, resv)

    def test_maybe_as_agrument(self):
        ''' '''
        code = r'''
        res = []
        
        struct A a: int
        struct N n:any
        
        func someMap(x:maybe, fn:function)
            if isNone(x)
                return null
            fn(x.get())
        
        ss = [
            none, some(1), some(2.5), 
            some([1,2,3]), some((4,5,6)), 
            some(A(7)), some(some(8)), some([some(11), some(12)])
        ]
        
        for i, s <- iter(len(ss)), ss
            res <- (i, someMap(s, \x -> [x]))
        
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
        exv = [(0, null), (1, [1]), (2, [2.5]), (3, [[1, 2, 3]]), (4, [(4, 5, 6)]), (5, ['st@A{a: 7}']), (6, [some(8)]), (7, [[some(11), some(12)]])]
        self.assertEqual(exv, resv)

    def test_maybe_isNone(self):
        ''' '''
        code = r'''
        res = []
        
        struct A s:string
        
        sm234 = some((2,3,4))
        ss = [some(11), none, some('abc'), some(A{s:'Amba'}), some(sm234), none]
        # ss = [some(11), none, some(sm234)]
        
        for s <- ss
            if isNone(s)
                res <- ('is none', s)
            else
                # res <- s
                res <- ('some of', s, s.get())
        
        pp = (some(1), some('PPpp'), A('AAA'))
        ppr = []
        ppr <- pp
        
        # print('pp::', ppr)
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print('vals', rvar.vals())
        # print('pp', ctx.get('ppr').get(), ' >>> ', ctx.get('ppr').get().vals())
        # print('$$', resv)
        exv = [
            ('some of', some(11), 11), ('is none', none), ('some of', some('abc'), 'abc'), 
            ('some of', some("st@A{s: 'Amba'}"), "st@A{s: 'Amba'}"), 
            ('some of', some(some((2, 3, 4))), some((2, 3, 4))), ('is none', none)]
        self.assertEqual(exv, resv)

    def test_maybe_get(self):
        ''' '''
        code = r'''
        res = []
        
        struct A s:string
        
        ss = [1, 2.5, 'halat', (1,2, 'Omm'), [4,5,'zoom'], {7:77, 8:88}]
        
        mm = []
        for n <- ss
            mm <- some(n)
        
        for m <- mm
            res <- m
            res <- m.get()
        
        # print('>>1', mb3)
        
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
        exv = [some(1), 1, some(2.5), 2.5, some('halat'), 'halat', 
               some((1, 2, 'Omm')), (1, 2, 'Omm'), some([4, 5, 'zoom']), [4, 5, 'zoom'], some({7: 77, 8: 88}), {7: 77, 8: 88}]
        self.assertEqual(exv, resv)

    def test_maybe_type(self):
        ''' '''
        code = r'''
        res = []
        
        struct A s:string
        
        mb1 = some(1)
        mb2:maybe = some(2.5)
        mb3 = some('Hello maybe!')
        
        # m = {?2}
        res <- mb1
        res <- mb2
        res <- mb3
        res <- some(4)
        res <- none
        res <- some([1,2,3])
        res <- some(['aa', 'bb'])
        
        rr = some([1,2,'Abc'])
        
        res <- some(A('abc'))
        
        # print('>>1', mb3)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        
        rr = ctx.get('rr').get()
        # print('rr>', rr)
        self.assertEqual(some([1, 2, 'Abc']), reprElem(rr))
        rvar = ctx.get('res').get()
        
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [some(1), some(2.5), some('Hello maybe!'), some(4), none, some([1, 2, 3]), some(['aa', 'bb']), some("st@A{s: 'abc'}")]
        self.assertEqual(exv, resv)


if __name__ == '__main__':
    main()

