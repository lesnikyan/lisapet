'''
Multiple execute built script.
'''

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

from bases.strformat import *


from tests.utils import *


# def ivar(name, value):
#     vv = Var(name, TypeInt())
#     vv.set(Val(value, TypeInt()))
#     return vv


class TestMulticall(TestCase):
    


    def test_multicall_simple(self):
        ''' Build once and call ET object multiple times. '''
        code = r'''
        
        # args x1:int, x2:int is needed
        
        res = 0
        
        func foo()
            111
        
        func bar(a, b)
            a * b
        
        struct A a:int, b: int
        
        func inst:A aplusb()
            inst.a + inst.b
        
        a1 = A{a:2, b:3}
        a2 = A{a:x1, b:x2}
        
        nn = []
        nn <- a1.aplusb()
        nn <- a2.aplusb()
        
        res = foo() + bar(nn[0], nn[1])
        
        '''
        code = norm(code[1:])
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        ex = lex2tree(clines)
        rCtx = rootContext()
        results = []
        for i in range(1, 101):
            curCtx = rCtx.moduleContext()
            args = {'x1': ivar('x1', i), 'x2': ivar('x2', i + 10)}
            curCtx.addSet(args)
            ex.do(curCtx)
            rvar = curCtx.get('res')
            rval = rvar.getVal()
            results.append(rvar)
            a1 = (2 + 3)
            a2 = i + i + 10
            exp = 111 + a1 * a2
            self.assertEqual(exp, rval)
            # print('TT>>', ' 111 + 5 * (%d + %d)' % (i, i+10), '=', rval)


if __name__ == '__main__':
    main()
