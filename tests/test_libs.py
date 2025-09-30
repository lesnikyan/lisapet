

from unittest import TestCase, main

import lang
import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
import context
from context import Context
from strformat import *
from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

from cases.utils import *
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from tests.utils import *



class TestLibs(TestCase):


    def test_builtin_split_join_replace(self):
        ''' '''
        code = r'''
        res = []
        
        src1 = "red,green,blue"
        
        res <- split(src1, ',')
        
        src2 = ['hello','dear','string']
        
        res <- join(src2, '_')
        
        src3 = "<div>Hello replace</div>"
        
        res <- replace(src3, 'div', 'span')
        
        # print('res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        # rvar = ctx.get('res')
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        exp = [['red', 'green', 'blue'], 'hello_dear_string', '<span>Hello replace</span>']
        self.assertEqual(exp, rvar.vals())



if __name__ == '__main__':
    main()
