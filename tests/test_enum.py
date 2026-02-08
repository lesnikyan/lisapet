'''
enum tests
'''


from unittest import TestCase, main
from tests.utils import *
from context import Context


class TestEnum(TestCase):




    def test_enum_block_definition(self):
        ''' '''
        code = r'''
        res = []
        
        enum Nums 
            one=1 
            two
            three 
            four 
            five 
            six
            seven
            nineteen = 19
            x20
        
        gnums = [Nums.two .. Nums.five]
        res <- ('n..n', tolist(gnums))
        
        nn = [0, 1, 2, 3, 4, 5, 6, 7, 8, 19, 20]
        
        dn = {}
            Nums.six : '|6|'
            Nums.seven : '|7|'
        
        tt = (Nums.nineteen, Nums.x20)
        
        for n <- nn
            if n == Nums.one
                res <- ('one', n)
            else if n ?> [Nums.four, Nums.two]
                res <- ('in [4, 2]', n)
            else if n < Nums.three
                res <- ('n < 3', n)
            else if n == Nums.three
                res <- ('three', n)
            else if n ?> tt
                res <- ('in (19, 20)', n)
            else if n ?> dn
                res <- ('in dict', n, dn[n])
            else
                res <- ('other', n)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [('n..n', [2, 3, 4, 5]), 
               ('n < 3', 0), ('one', 1), ('in [4, 2]', 2), ('three', 3), ('in [4, 2]', 4), 
               ('other', 5), ('in dict', 6, '|6|'), ('in dict', 7, '|7|'), ('other', 8), 
               ('in (19, 20)', 19), ('in (19, 20)', 20)]
        self.assertEqual(exv, rvar.vals())

    def test_enum_linear_definition(self):
        ''' '''
        code = r'''
        res = []
        
        # default vals
        
        enum Abc a,b,c,d,e,f,g
        
        res <- [-111, Abc.a, Abc.b, Abc.c, Abc.d, Abc.e, Abc.f, Abc.g ]
        
        # all assigned vals
        enum Colors red = 0xff0000, green = 0xff00, blue = 0xff
        
        res <- ~"{Colors.red:06x}"
        res <- ~"{Colors.green:06x}"
        res <- ~"{Colors.blue:06x}"
        
        # initiated first
        enum Nums one=1, two, three, four, five, six
        
        # just assign
        x = Nums.one
        res <- ('x', x)
        
        # if conditions test
        nn = [0, 1, 2, 3, 4, 5, 6]
        
        dn = {}
            Nums.six : '|6|'
        
        for n <- nn
            if n == Nums.one
                res <- ('one', n)
            else if n ?> [Nums.four, Nums.two]
                res <- ('in [4, 2]', n)
            else if n < Nums.three
                res <- ('n < 3', n)
            else if n == Nums.three
                res <- ('three', n)
            else if n ?> dn
                res <- ('in dict', n, dn[n])
            else
                res <- ('other', n)
        
        # init vals in random positions
        enum B a, b=10, c, d, e=20, f, g
        
        res <- [-333, B.a, B.b, B.c, B.d, B.e, B.f, B.g]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            [-111, 0, 1, 2, 3, 4, 5, 6],
            'ff0000', '00ff00', '0000ff', ('x', 1),
            ('n < 3', 0), ('one', 1), ('in [4, 2]', 2), ('three', 3), ('in [4, 2]', 4), ('other', 5), ('in dict', 6, '|6|'),
            [-333, 0, 10, 11, 12, 20, 21, 22]]
        self.assertEqual(exv, rvar.vals())


if __name__ == '__main__':
    main()
