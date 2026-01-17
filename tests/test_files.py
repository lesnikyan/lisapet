


from unittest import TestCase, main

import os
import pdb


from lang import CLine, dprint
from parser import splitLexems, elemStream
from vars import *
from context import Context
from tree import *
from nodes.func_expr import coverFunc
from objects.func import Function
from nodes.func_expr import setNativeFunc
from nodes.builtins import getVal
from eval import rootContext
from tests.utils import *


class Alter:
    def __init__(self):
        self.res = []
        
    def print(self, ctx:Context, *args):
        pargs = []
        for n in args:
            if isinstance(n, (Function)):
                pargs.append(str(n))
                continue
            v = getVal(n)
            if isinstance(v, StructInstance):
                v = v.istr()
            pargs.append(v)
        self.res.append(pargs)


class TestEvalFile(TestCase):
    
    def test_full(self):
        '''' '''
        fpath = filepath('full_example.et')
        alt = Alter()
        with open(fpath, 'r') as f:
            code = f.read()
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            exp = lex2tree(clines)
            ctx = rootContext()
            # replace `print` 
            ctx.funcs['print'] = coverFunc('print', alt.print, TypeNull)
            ctx.get('len')
            # return
            # dprint('$$ run test ------------------')
            # # pdb.set_trace()
            exp.do(ctx)
            # r1 = ctx.get('r1').get()
        # print('alt:', alt.res)
        exv = [
            ['n:', 2], ['n:', 2], [33, [1000, 200, 30, 4]], ['Hello print example!'], ['Hello print example!!!'], [25], ['inverted'], [10], 
            ['is prime 11', True], [1234], ['Dude'], ['Lorem ipsum dolor sit amet, consectetur adipiscing elit,'], 
            ['#00ff00'], ['Second day'], ['dict-data', 'red', '#ff0000'], ['dict-data', 'green', '#00ff00'], ['dict-data', 'blue', '#0000ff'], 
            ['Green  gardens', 'Bob Stinger', 100, 10.0], ['Blue, blue sky', 'Ani Arabesquin', 200, 20.0], 
            ['Silver sword of small town', 'Arnold Whiteshvartz', 300, 22.0], ['tp1 name:', 'New-Name'], 
            ['nums1 = ', [[25, 1], [25, 2], [25, 3], [36, 1], [36, 2], [36, 3], [49, 1], [49, 2], [49, 3]]], 
            ['nums2 = ', [5, 1, 5, 2, 5, 3, 6, 1, 6, 2, 6, 3, 7, 1, 7, 2, 7, 3]], 
            ['nums = ', [[3, 27, 81], [4, 64, 256], [5, 125, 625], [6, 216, 1296], [7, 343, 2401]]], 
            ['lambda test:', 32, 504, [2, 5, 10, 17, 26]]]
        self.assertEqual(exv, alt.res)


    def test_muliline_expr(self):
        '''' '''
        fpath = filepath('multiline_expr.et')
        with open(fpath, 'r') as f:
            code = f.read()
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            exp = lex2tree(clines)
            ctx = rootContext()
            ctx.get('len')
            # return
            # dprint('$$ run test ------------------')
            # # pdb.set_trace()
            exp.do(ctx)
            res = ctx.get('res').get()
            exp = [
                'a1;b2;c3',
                100,
                [99, 198, 297, 396, 495],
                5
            ]
            self.assertEqual(exp, res.vals())


if __name__ == '__main__':
    main()
