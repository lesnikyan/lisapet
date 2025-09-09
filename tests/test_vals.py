

from unittest import TestCase, main

import typex
from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, elemStream
from vars import *
from vals import numLex
from context import Context
from strformat import *
from nodes.structs import *
from tree import *
from eval import rootContext, moduleContext

from cases.utils import *
from nodes.tnodes import Var
from nodes import setNativeFunc, Function
from tests.utils import *

import pdb


class TestVals(TestCase):



    def test_builtin_type(self):
        ''' For left-arrow operator target is result of function call 
        (returns collection).
        '''
        code = r'''
        res = []
        
        # vals
        res <- type(1)
        res <- type(0x15)
        res <- type(2.3)
        res <- type(false)
        res <- type("string!")
        
        # # vars
        i, yy, nl = 11, true, null
        res <- type(i)
        res <- type(yy)
        res <- type(nl)
        
        #collections
        lval, dval, tval = [1,2,3], {4:5}, (6, 7)
        res <- type(lval)
        res <- type(dval)
        res <- type(tval)
        
        # print('res = ', res)
        
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        ex.do(ctx)
        rvar = ctx.get('res').get()
        res = rvar.vals()
        rtypes = [n.__class__ for n in res]
        # print('RTP:', rtypes)
        # print('RVL:', res)
        exp = [
            typex.TypeInt,
            typex.TypeInt,
            typex.TypeFloat,
            typex.TypeBool,
            typex.TypeString,
            typex.TypeInt,
            typex.TypeBool,
            typex.TypeNull,
            typex.TypeList,
            typex.TypeDict,
            typex.TypeTuple,
        ]
        self.assertEqual(exp, rtypes)


if __name__ == '__main__':
    main()
