

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
    


    def _test_list_gen_simplest(self):
        ''' make vars and assign vals from tuple  '''
        code = '''
        sqrs = [x ** 2 | x <- [0..10]]
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_tuple_assign_left(self):
        ''' make vars and assign vals from tuple  '''
        code = '''
        (a, b, s) = 1,2,3
        print('', a, b, c)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

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
        2. Struct methods.
        3. tuple
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
