'''

'''


from unittest import TestCase, main

from tests.utils import *

import pdb


class TestMaybe(TestCase):
    ''' '''


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

