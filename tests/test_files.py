


from unittest import TestCase, main

import os
import pdb


from lang import CLine, dprint
from parser import splitLexems, elemStream
from vars import *
from context import Context
from tree import *
# from nodes.func_expr import setNativeFunc
from eval import rootContext
from tests.utils import *


class TestEvalFile(TestCase):
    
    def test_full(self):
        '''' '''
        fpath = filepath('full_example.et')
        with open(fpath, 'r') as f:
            code = f.read()
            tlines = splitLexems(code)
            clines:CLine = elemStream(tlines)
            exp = lex2tree(clines)
            ctx = rootContext()
            ctx.get('len')
            # return
            dprint('$$ run test ------------------')
            # # pdb.set_trace()
            exp.do(ctx)
            # r1 = ctx.get('r1').get()


if __name__ == '__main__':
    main()
