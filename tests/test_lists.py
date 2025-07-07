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
    ''' Testing lists, iterators, generators, other collections '''



    def test_barr_del_collection_elem_minus(self):
        ''' '''
        code = r'''
        
        res = []
        
        a1 = [1,2,3]
        r1 = a1 - [1]
        
        res <- r1
        res <- a1
        
        d2 = {'a':11, 'b':22}
        r2 = d2 - ['a']
        
        res <- r2
        res <- d2
        
        print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        dprint('rvar.vals()', rvar.vals())
        exp = [2, [1, 3], 11, {'b': 22}]
        self.assertEqual(exp, rvar.vals())

    def test_multi_assign_unpack_tuple(self):
        ''' unpack tuple to multiple vars '''
        code = r'''
        func foo()
            (1, 2, 3)

        a, b, c = foo()
        x = (4, 5)
        d, e = x

        res = {'a': a, 'b': b, 'c':c, 'd':d, 'e':e}
        print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rval = ctx.get('res').get()
        exp = {'a': 1, 'b': 2, 'c': 3, 'd':4, 'e':5}
        self.assertEqual(exp, rval.vals())

    def test_multi_assign_unpack_list(self):
        ''' unpack list to multiple vars '''
        code = r'''
        
        func foo()
            [1, 2, 3]
        
        a, b, c = foo()
        
        x = [4, 5]
        d, e = x
        
        res = {'a': a, 'b': b, 'c':c, 'd':d, 'e':e}
        print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rval = ctx.get('res').get()
        exp = {'a': 1, 'b': 2, 'c': 3, 'd':4, 'e':5}
        self.assertEqual(exp, rval.vals())

    def test_multi_assign_base(self):
        ''' multiple asignment '''
        code = r'''
        x = 5
        a, b, c = 1, 2, x
        
        res = [a,b,c]
        print('res = ', res)
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rval = ctx.get('res').get()
        self.assertEqual([1, 2, 5], rval.vals())

    def test_elem_to_dict_operator(self):
        ''' both cases of `<-` operator for dict
        #TODO:
        '''
        code = r'''
        nn = [1, 2, 3]
        keys = ['a','b','c']
        nr = {}
        for i <- [0..2]
            nr <- (keys[i], nn[i])
        print('nr:', nr)
        rr = []
        rr <- 'preval'
        for key, val <- nr
            rr <- key
        print('rr:', rr)
        '''
        _ = r'''
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('nr').get()
        self.assertEqual({'a' : 1, 'b' : 2, 'c' : 3}, rvar.vals())
        rvar = ctx.get('rr').get()
        self.assertEqual(['preval', 'a', 'b', 'c'], rvar.vals())

    def test_elem_to_list_operator(self):
        ''' both cases of `<-` operator
        # if left is a collection: put right elem to the end of left list|dict (append val case)
        # TODO: implement dict case
        nums = [1,2,3]
        nums <- 4
        # if left not a collection (right must be)
        # val from right list to left var according to the internal index of list (iterator case)
        i <- [1,2,3]
        '''
        code = r'''
        nn = [1, 2, 3]
        nr = []
        for i <- nn
            nr <- i * 10
        nr <- 500
        print('nr:', nr)
        '''
        _ = r'''
        '''
        code = norm(code[1:])
        # dprint('>>\n', code)
        # return
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        rvar = ctx.get('nr').get()
        self.assertEqual([10, 20, 30, 500], rvar.get())

    def test_list_comprh_multi_case(self):
        ''' multiline and multi-expression  '''
        code = '''
        nums = [
            {x:a, y:b, z:c};
            x <- [3..7];
            a = x * 10;
            x % 2 > 0;
            y <- [1..10];
            b = 2 ** y;
            y <= 5;
            z <- [1..3];
            c = 10 ** z;
            a + b + c < 1000
        ]
        res = [x ; i <-iter(len(nums)); x = nums[i]; i < 5 || i > 26]
        # print('src = ', src)
        print('nums = ', res)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)
        nums = ctx.get('res').get()
        nvals = [n.vals() for n in nums.rawVals()]
        dprint('#tt', nvals)
        exp = [{3: 30, 1: 10}, {3: 30, 1: 2, 2: 100}, {3: 30, 2: 4, 1: 10}, {3: 30, 2: 100},
               {3: 8, 1: 10}, {7: 70, 4: 16, 2: 100}, {7: 70, 5: 32, 1: 10}, {7: 70, 5: 32, 2: 100}]
        self.assertEqual(exp, nvals)

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
        # srcGen = [x ** 2 ; x <- [1..10]]
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
        # print('tuple_a', a[0], a[2][0], a[2][1])
        # print(a[2][:1])
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
        arr2 = ctx.get('arr2').get()
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
        arr2 = ctx.get('arr2').get()
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
        arr2 = ctx.get('arr2').get()
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
        arr2 = ctx.get('arr2').get()
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
        dprint('$$ run test ------------------')
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
        dprint('$$ run test ------------------')
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
        dprint('$$ run test ------------------')
        exp.do(ctx)
        res = ctx.get('res')
        dprint('# tt>> ', res)

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
            dprint('~~~~ test case: %s ~~~~' % code)
            ex.do(ctx)
            rr = [ctx.get('res').get() , ctx.get('r').get()]
            dprint('Test res = ', rr)

    def test_array_expr(self):
        data = [
            # '[1,2,3]', 
            '[a, b, c]',
            # '[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]',
        ]
        ctdata = {
            'a': 1,
            'b': 2,
            'c': 3
        }
        for code in data:
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            ex = lex2tree(clines)
            ress = []
            ctx = rootContext()
            for k, v in ctdata.items():
                vv = Var(k, TypeInt)
                vv.set(Val(v, TypeInt()))
                ctx.addSet({k: vv})
            dprint('~~~~ test case: %s ~~~~' % code)
            ex.do(ctx)



if __name__ == '__main__':
    main()
