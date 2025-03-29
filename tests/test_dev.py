

from unittest import TestCase, main
from tests.utils import *

from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
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
        

    def test_dict_multiline(self):

        code = '''
        # create dict var with values in sub-block
        dd = dict
            'red' :'#ff0000'
            'green' :'#00ff00'
            'blue' :'#0000ff'
            'orange' :'#ff8800'
            
        dd['blue'] = 'dark-blue'
        for n <- ['red', 'green', 'blue']
            print(n, dd[n])
        '''
        t='''
        '''

        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        exp = lex2tree(clines)
        ctx = Context(None)
        setNativeFunc(ctx, 'print', print, TypeNull)
        setNativeFunc(ctx, 'len', len, TypeInt)
        print('$$ run test ------------------')
        exp.do(ctx)



if __name__ == '__main__':
    main()
