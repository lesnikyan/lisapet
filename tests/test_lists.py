'''

'''

from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
from eval import rootContext
# from nodes.tnodes import Var
# from nodes import setNativeFunc, Function
from tree import *
# from nodes.structs import *
# import pdb


class TestLists(TestCase):




    def test_tuple_list_as_result(self):
        '''   '''
        code = '''
        src = ['aaa', 'bbb', 'ccc']
        res = [('uu', s) ; s <- src]
        print('res = ', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_gen_sub_assignment(self):
        ''' list generator  '''
        code = '''
        # nums = [x ** 2 ; x <- [1..10]; x % 5 > 0 && x > 3]
        # nums = [[x ** 2, y] ; x <- [1..10]; y <- [1..3]; x % 5 > 0 && x > 3]
        # src = [ [ a; a <- [y .. y + x]] ; x <- [1..3]; y <- [10, 20, 30] ]
        debVar = 100000
        nums = [[x, x**3, y**2] ; x <- [1..10]; y = x ** 2; y < 50 && x ** 3 > 10]
        # print('src = ', src)
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_compr_filter(self):
        ''' list generator. flatten list of lists. 2-nd iterator uses sublist from 1-st  '''
        code = '''
        srcGen = [x ** 2 ; x <- [1..10]]
        # filterRes = [x ; x <- src; x % 5 > 0 && x > 10]
        # full expr:
        nums = [x ** 2 ; x <- [1..10]; x % 5 > 0 && x ** 2 > 15]
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_compr_flatten_subs(self):
        ''' list generator. '''
        code = '''
        srcGen = [[x, y] ; x <- [5..7]; y <- [1..3]]
        src = [[5, 1], [5, 2], [5, 3], [6, 1], [6, 2], [6, 3], [7, 1], [7, 2], [7, 3]]
        nums = [ x ; sub <- src ; x <- sub]
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_compr_sublists(self):
        ''' list generator. '''
        code = '''
        nums = [[x ** 2, y] ; x <- [5..7]; y <- [1..3]]
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_compr_2_lists(self):
        ''' list generator. iterator in iterator '''
        code = '''
        nums = [x + y * 1000 ; x <- [5..7]; y <- [1..3]]
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_compr_from_gen(self):
        ''' list generator. simplest case  '''
        code = '''
        nums = [x ** 2 ; x <- [1..5]]
        print('src = ', src)
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_comprehention_simplest(self):
        ''' list generator. simplest case  '''
        code = '''
        src = [1,2,3,4,5]
        nums = [x ** 2 ; x <- src]
        print('src = ', src)
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_gen_assign(self):
        ''' list generator [from : to]'''
        code = '''
        nums = [5..10]
        res = 0
        for n <- nums
            print('  n >>', n)
            res += n
        print('res >>', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_gen_iter(self):
        ''' list generator [from : to]'''
        code = '''
        res = 0
        for n <- [5..10]
            print('  n >>', n)
            res += n
        print('res >>', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_in_list(self):
        code = '''
        a = [1, 2, ['aa','bb']]
        a[2][0] = 'a222'
        print('list_a', a[0], a[2][0], a[2][1])
        print(a[2][:1])
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_tuple_in_list(self):
        code = '''
        a = (1, 2, ['aa','bb'])
        a[2][0] = 'a222'
        print('tuple_a', a[0], a[2][0], a[2][1])
        print(a[2][:1])
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_tuple(self):
        code = '''
        a = (1, 2, ['aa','bb'])
        print('tuple_a', a[0], a[2])
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def test_list_slice_skip_both(self):
        ''' arr[:] same as full copy '''
        code='''
        arr = [1,2,3,4,5,6,7,8,9]
        arr2 = arr[:]
        print('arr2:', arr2, ' len:', len(arr2))
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        arr2 = ctx.get('arr2')
        self.assertEqual(9, len(arr2.elems))

    def test_list_slice_skip2(self):
        ''' '''
        code='''
        arr = [1,2,3,4,5,6,7,8,9]
        arr2 = arr[2:]
        print('arr2:', arr2, ' len:', len(arr2))
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        arr2 = ctx.get('arr2')
        self.assertEqual(7, len(arr2.elems))

    def test_list_slice_skip1(self):
        ''' '''
        code='''
        arr = [1,2,3,4,5,6,7,8,9]
        arr2 = arr[:5]
        # print('arr2:', arr2, ' len:', len(arr2))
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        arr2 = ctx.get('arr2')
        self.assertEqual(5, len(arr2.elems))

    def test_list_slice(self):
        ''' '''
        code='''
        arr = [1,2,3,4,5,6,7,8,9]
        arr2 = arr[2:-2]
        print('arr2:', arr2, ' len:', len(arr2))
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        arr2 = ctx.get('arr2')
        self.assertEqual(5, len(arr2.elems))

    def test_list_multiline(self):
        code = '''
        # create dict var with values in sub-block
        names = list
            'Anna'
            'Barbi'
            'Cindy'
            'Dolores'
            'no name'

        names[4] = 'Vahtang'
        for i <- [0,1,2,3,4]
            print(i, names[i])
        '''

        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        print('$$ run test ------------------')
        exp.do(ctx)

    def test_for_array(self):
        ''' for n <- [1,2,3] 
            for n <- arrVar
        '''
        code = '''
        for n <- [1,2,3]
            print('-----------------', n)
        '''
        code = '''
        nn = [1,2,3]
        for n <- nn
            print(n)
        '''
        code = '''
        func sum(nums)
            res = 0
            for n <- nums
                res += n
            res
        print(sum([10, 200, 300]))
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        print('$$ run test ------------------')
        exp.do(ctx)


    def test_array_set(self):
        src = '''
        a = 1
        b = 2
        val = 10
        arr = [1,2,3,4,5]
        arr[1] = 20
        arr[a+b] = val + arr[1]
        res = arr[a+b]
        '''
        code = norm(src[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = rootContext()
        print('$$ run test ------------------')
        exp.do(ctx)
        res = ctx.get('res')
        print('# tt>> ', res)

    def test_array(self):
        data = [
            '''
            arr = [1,2,3]
            res = arr[0]
            r = 1000
            for i <- iter(3)
                r = r + arr[i]
            '''
        ]

        for code in data:
            code = norm(code[1:])
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            ex = lex2tree(clines)
            ctx = rootContext()
            print('~~~~ test case: %s ~~~~' % code)
            ex.do(ctx)
            rr = [ctx.get('res').get() , ctx.get('r').get()]
            print('Test res = ', rr)

    def test_array_expr(self):
        data = [
            '[1,2,3]', 
            '[a, b, c]',
            '[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]',
        ]
        ctdata = {
            'a': 1,
            'b':2,
            'c':3
        }
        for code in data:
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            ex = lex2tree(clines)
            ress = []
            ctx = rootContext()
            for k, v in ctdata.items():
                vv = Var(k, TypeInt)
                vv.set(v)
                ctx.addSet({k: vv})
            print('~~~~ test case: %s ~~~~' % code)
            ex.do(ctx)



if __name__ == '__main__':
    main()
