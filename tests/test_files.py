


from unittest import TestCase, main

import os
import pdb
from pathlib import Path


from lang import CLine
from parser import splitLexems, elemStream
from vars import *
from context import Context
from tree import *
from nodes.func_expr import setNativeFunc


def filepath(fname):
    return Path(__file__).with_name(fname)


class TestEvalFile(TestCase):
    
    def test_full(self):
        '''' '''
        fpath = filepath('full_example.et')
        with open(fpath) as f:
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
