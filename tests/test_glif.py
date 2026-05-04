''' 
'''


from unittest import TestCase, main

from tests.utils import *

import pdb


class TestGLif(TestCase):


    def test_glif_functions(self):
        '''  '''
        code = r'''
        res = []
        
        # string constructor
        res <- string(g'A')
        res <- string(g'Ы')
        res <- string(g'百')
        
        # int constructor
        res <- int(g'0')
        res <- int(g'1')
        res <- int(g'A')
        res <- int(g'W')
        res <- int(g'Ы')
        res <- int(g'百')
        res <- int(g'*')
        
        # bytes constructor
        res <- bytes(g'1')
        res <- bytes(g'A')
        res <- bytes(g'W')
        res <- bytes(g'Ы')
        res <- bytes(g'百')
        
        # bool
        
        res <- 'bool(glif)'
        res <- bool(g'0')
        res <- bool(g'Ы')
        res <- bool(glif(1))
        res <- bool(glif(0))
        
        # list(string)
        res <- 'list by string'
        res <- list('Hello! Ыщ,百 ')
        
        # string[index]
        ss = "Hello Ыщ:百"
        res <- ~'str index: {ss}'
        res <- ss[0]
        res <- ss[-4]
        res <- ss[-1]
        
        # string.glifs()
        res <- 'Ab'.glifs()
        'Hello / Ыф'.glifs()
        
        # glif.int()
        res <- 'glif->int'
        res <- g'0'.int()
        res <- g'Q'.int()
        res <- g'Ы'.int()
        res <- g'百'.int()
        
        # glif->bytes
        res <- 'glif.bytes()'
        res <- g'1'.bytes()
        res <- g'A'.bytes()
        res <- g'W'.bytes()
        res <- g'Ы'.bytes()
        res <- g'百'.bytes()
        
        
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
            'A', 'Ы', '百', 48, 49, 65, 87, 1067, 30334, 42, 
            '0x[31]', '0x[41]', '0x[57]', '0x[d0 ab]', '0x[e7 99 be]', 
            'bool(glif)', True, True, True, False, 
            'list by string', ['g(H)', 'g(e)', 'g(l)', 'g(l)', 'g(o)', 'g(!)', 'g( )', 'g(Ы)', 'g(щ)', 'g(,)', 'g(百)', 'g( )'], 
            'str index: Hello Ыщ:百', 'g(H)', 'g(Ы)', 'g(百)', ['g(A)', 'g(b)'], 
            'glif->int', 48, 81, 1067, 30334, 
            'glif.bytes()', '0x[31]', '0x[41]', '0x[57]', '0x[d0 ab]', '0x[e7 99 be]']
        self.assertEqual(exv, resv)

    def test_glif_percent_format_fix(self):
        '''  '''
        code = r'''
        res = []
        
        res <- '1) %s' << g'A'
        res <- '2) %x' << g'A'
        res <- '3) %d' << g'A'
        res <- '4) %06x' << g'百'
        res <- '5) %08x' << g'お'
        res <- '6) %c' << g'A'
        res <- '7) %o' << g'A'
        res <- '8) %r' << g'R'
        
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
        exv = ['1) A', '2) 41', '3) 65', '4) 00767e', '5) 0000304a', '6) A', '7) 101', "8) 'R'"]
        self.assertEqual(exv, resv)

    def test_glif_operators(self):
        '''  '''
        code = r'''
        res = []
        
        res <- 'plus-glif'
        
        res <- g'A' + g'B'
        
        res <- 'abc ' + g'D'
        
        res <- g'B' + ' cde'
        
        res <- g'A' + 1
        
        res <- 5 + g'A'
        
        res <- 'type-glif'
        res <- 5 :: glif
        res <- '5' :: glif
        res <- glif('5') :: glif
        res <- g'5' :: glif
        
        res <- 'format-glif'
        
        res <- '<%s>' << g'A'
        
        a, b = g'A', g'B'
        res <-  ~'g:str = {a};{b}'
        res <- ~'g:num {a:x};{b:d}'
        
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
            'plus-glif', 'AB', 'abc D', 'B cde', 'g(B)', 'g(F)', 
            'type-glif', False, False, True, True, 
            'format-glif', '<A>', 'g:str = A;B', 'g:num 41;66']
        self.assertEqual(exv, resv)

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

