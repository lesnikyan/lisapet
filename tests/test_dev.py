

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
import pdb


class A:
    pass

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

    def test_for_iter(self):
        code = '''
        res = 0
        for i <- iter(10)
            res += i
        print('res: ', res)
        '''
        code = norm(code[1:])
        # data = [6]
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        ress = []
        ctx = rootContext()
        ex.do(ctx)
        print('##################t-IF1:', ctx.get('res').get())
        

if __name__ == '__main__':
    main()
