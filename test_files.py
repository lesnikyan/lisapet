


import unittest
from unittest import TestCase, main



from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from tnodes import Var, Context
from tree import *



import pdb




class TestEvalFile(TestCase):
    
    def test_full(self):
        '''' '''
        srcf = 'full_example.et'
        with open(srcf) as f:
            code = f.read()
            # print(code)
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            exp = lex2tree(clines)
            ctx = Context(None)
            setNativeFunc(ctx, 'print', print, TypeNull)
            setNativeFunc(ctx, 'len', len, TypeInt)
            ctx.get('len')
            # return
            print('$$ run test ------------------')
            # # pdb.set_trace()
            exp.do(ctx)
            # r1 = ctx.get('r1').get()
            # # r2 = ctx.get('r2').get()
            # print('#t >>> r:', r1)


if __name__ == '__main__':
    main()
