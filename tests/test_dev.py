

from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex

from cases.utils import *

from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from nodes.structs import *

from context import Context
from tree import *
from eval import rootContext
import pdb


class TestDev(TestCase):


    def _test_list_gen_by_strings(self):
        '''   '''
        code = '''
        src = ['aaa', 'bbb', 'ccc']
        nums = [x ; ns <- src; x <- ns ; x % 5 > 0]
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)


    def _test_list_gen_empty_end(self):
        ''' list generator. [... expr;] empty last sub-case'''
        code = '''
        # nums = [x ** 2 ; x <- [1..10]; x % 5 > 0 && x > 3]
        nums = [[x ** 2, y] ; x <- [5..7]; y <- [1..3]]
        # src = [ [ a; a <- [y .. y + x]] ; x <- [1..3]; y <- [10, 20, 30] ]
        # print('src = ', src)
        print('nums = ', nums)
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ctx = rootContext()
        ex.do(ctx)

    def _test_list_gen_comprehention_iter_by_string(self):
        ''' list generator and strings
            case 1: list from string
            case 2: string from string ? 
             -- think about: string is a list of chars, but string is an immutable list
        '''
        code = '''
        src = ['a' .. 'k'] # >> 'abcdef...k' ?? do we need that?
        src = "Hello strings!"
        res = [ [a ; a <- src]
        # print('src = ', src)
        print('nums = ', nums)
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
