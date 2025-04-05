

from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
from eval import rootContext
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from tree import *
from nodes.structs import *
import pdb


class TestDev(TestCase):


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

    def _test_list_slice(self):
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
        

    def _test_struct_anon(self):
        code = '''
        user = struct {name:'Anod', age:25, sex:male, phone:'123-45-67'}
        # uf = user.fields()
        print(user.name)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    _ = '''
        TODO features:
        1. List comprehetion / generator
    [-10..10]; [..10] >> IterGen(beg, over, step)
    [n.name | n <- arr] ##### [2 * n | n <- [0..10]] ##### [2 * n | n <- iter(10)] >> add over-item expression
    [n <- iter(10) | n %2 == 0] >> add sub-condition
    [n | subArr <- arr n <- subArr] >> flat sub-list
    [n * m | n <- arr1, m <- arr2] >> iterator over iterator
    [n + m | n <- arr, m = n / 10, k <- arr2 | m != k] >> add sub expression
    [n + m | n <- arr, m:int = int (n / 10), k <- arr2[m] | m > 0 && m < len(arr2)] ?? >> add sub expression
        2. List slice
    arr[0:5] ##### arr[3:] ##### arr[:3] ##### arr[2:-3] 
        TODO tests:
    test assignment and read 
    global var and local block
    local var and function-block
    var <- val
    var <- var
    var <- array
    array <- var
    dict of items str : array
    array of dicts
    
    '''

if __name__ == '__main__':
    main()
