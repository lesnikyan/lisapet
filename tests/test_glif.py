''' 
'''


from unittest import TestCase, main

from tests.utils import *

import pdb


class TestGLif(TestCase):


    def test_glif_constructor(self):
        ''' '''
        code = r'''
        res = []
        
        res <- glif(g'G') # from glif
        res <- glif(55) # from int
        res <- glif('A') # from str char
        res <- glif(0x[42]) # from bytes
        res <- glif(0x[e7 99 be]) # multibyte
        
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
        exv = ['g(G)', 'g(7)', 'g(A)', 'g(B)', 'g(百)']
        self.assertEqual(exv, resv)

    def test_glif_val(self):
        ''' '''
                
        code = r'''
        res = []
        
        c = g'C'
        
        res <-c
        
        res <- g'+'
        res <- g'0'
        res <- g'9'
        res <- g'A'
        res <- g'a'
        res <- g'Z'
        res <- g'z'
        res <- g'!'
        res <- g'@'
        res <- g'+'
        res <- g'#'
        res <- g'$'
        res <- g'%'
        res <- g'&'
        res <- g'"'
        res <- g'`'
        res <- g`/`
        res <- g`\\`
        res <- g`,`
        res <- g`.`
        res <- g'百'
        res <- g'ج'
        res <- g'छ'
        res <- 'お'
        
        res <- [g'a', g'b', g'c', g'+', g'=', g'/', g'\n', g'|']
        
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
            'g(C)', 'g(+)', 'g(0)', 'g(9)', 'g(A)', 'g(a)', 'g(Z)', 'g(z)', 
            'g(!)', 'g(@)', 'g(+)', 'g(#)', 'g($)', 'g(%)', 'g(&)', 'g(")', 'g(`)', 'g(/)', 'g(\\)', 'g(,)', 'g(.)', 
            'g(百)', 'g(ج)', 'g(छ)', 'お', ['g(a)', 'g(b)', 'g(c)', 'g(+)', 'g(=)', 'g(/)', 'g(\n)', 'g(|)']]
        self.assertEqual(exv, resv)










if __name__ == '__main__':
    main()

