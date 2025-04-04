

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


class A:
    def __init__(self):
        self.field = '111'

class B:
    pass

class C(A,B):
    pass


class TestDev(TestCase):
    
    '''
    TODO:
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

    def test_struct_block_constr(self):
        code='''
        
        struct Btype title:string
        
        bb = Btype{title:'BBBBB'}

        struct Atype
            name: string
            num: int
            sub: Btype

        aa = Atype
            name:'Vasya'
            num:20
            sub: bb
        # tt = aa
        print('t-inst: ', aa.name , aa.num , aa.sub.title)
        #
        '''
        tt = '''

            sub: bb
            title: string
            vall: float
        bb = Btype{title: 'Bim-bom', vall: 11.55}
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
