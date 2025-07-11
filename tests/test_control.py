


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
from eval import rootContext, moduleContext

from strformat import *


from tests.utils import *



class TestControl(TestCase):

    def test_else_if_nested_if(self):
        ''' '''
        code = r'''
        
        res = 1
        
        if a == 2
            res = 2
        if a == 2
            res = 2
        else if b == 15
            res = 15
        else if a > 2
            res = 8
            if b == 1
                res = 101
            else if b == 2
                res = 102
            else if b == 3
                res = 103
            else if b == 4 || b == 5 || b == 6
                res = 105
            else if b == 7 && a == 3
                res = 110 
            else if b >= 8 && b <= 12 
                res = 108
                if a == 3
                    res = 123
                    if b == 10
                        res = 130
                    else
                        res = 133
                    if b == 12
                        res = 122
                else if a == 4 && b == 9
                    res = 124
                else if a == 5 && b == 9
                    res = 125
                else
                    if b > 8
                        res = 129
            else if b < 20
                if b != 13
                    res = 199
        else if a < 0
            res = 1001
        else
            res = 7

        #print(a, b, ' : res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        data = [
            (2, 0, 2),
            (0, 15, 15),
            (0, 1, 7),
            (11, 13, 8),
            (11, 14, 199),
            (3, 1, 101),
            (3, 2, 102),
            (3, 3, 103),
            (3, 4, 105),
            (3, 5, 105),
            (3, 6, 105),
            (4, 6, 105),
            (3, 7, 110),
            (4, 7, 199),
            (4, 8, 108),
            (4, 10, 129),
            (3, 8, 133),
            (3, 10, 130),
            (3, 12, 122),
            (4, 9, 124),
            (5, 9, 125),
            (5, 10, 129),
            (10, 7, 199),
            (-10, 10, 1001),
            (1, 1, 7),
            (0, 100, 7),
        ]
        for nn in data:
            a, b, exp = nn
            dprint('>>>', a, b, exp)
            vals = {'a': ivar('a', a), 'b': ivar('b', b)}
            ctx.addSet(vals)
            ex.do(ctx)
            rvar = ctx.get('res')
            self.assertEqual(exp, rvar.getVal())

    def test_else_if(self):
        ''' '''
        code = r'''
        
        res = 1
        
        if a == 2
            res = 2
        else if b == 5
            res = 5
        else if a > 2 &&  a == b
            res = 8
        else
            res = 7

        #print(a, b, ' : res = ', res)
        '''
        code = norm(code[1:])

        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        data = [
            (2, 0, 2),
            (0, 5, 5),
            (0, 1, 7),
            (11, 11, 8)
        ]
        for nn in data:
            a, b, exp = nn
            dprint('>>>', a, b, exp)
            vals = {'a': ivar('a', a), 'b': ivar('b', b)}
            ctx.addSet(vals)
            ex.do(ctx)
            rvar = ctx.get('res')
            self.assertEqual(exp, rvar.getVal())


if __name__ == '__main__':
    main()
