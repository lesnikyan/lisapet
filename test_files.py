

from collections.abc import  Callable
import unittest
from unittest import TestCase, main



from lang import Lt, Mk, CLine
from parser import splitLine, splitLexems, charType, splitOper, buildLexems, elemStream
from vars import *
from vals import numLex
from tnodes import Var, Context
from tree import *



import pdb


# class NativeExpr(Expression):
    
#     def __init__(self, val=None):
#         super().__init__(val)
#         self.callFunc = None
#         self.val:Var = None
#         self.run:Callable = lambda args : 1

#     def do(self, ctx:Context):
#         args = ctx.get('args') # TODO: get args from context
#         self.run(args)

#     # def run(self, *args):
#     #     pass

#     def get(self) -> Var|list[Var]:
#         return self.val


class NFunc(Function):
    ''' '''
    def __init__(self, name):
        super().__init__(name)
        self.callFunc:Callable = lambda *args : 1
        self.res:Var = None
        self.resType:VType = TypeNull

    def setArgVals(self, args:list[Var]):
        self.argVars = []
        # for i in range(len(args)):
        for arg in (args):
            print('~NFsetA', arg)
            self.argVars.append(arg.get())

    def do(self, ctx: Context):
        # self.block.storeRes = True # save last expr value
        # inCtx = Context(None) # inner context, empty new for each call
        # inCtx.addVar(Var(1000001, 'debVal', TypeInt))
        args = []
        for arg in self.argVars:
            print('#T arg = ', arg)
            args.append(arg)
        res = self.callFunc(*args)
        self.res = value(res, self.resType)

    def get(self)->Var:
        return self.res

def setFunc(ctx:Context, name:str, fn:Callable, rtype:VType=TypeNull):
    func = NFunc(name)
    func.resType = rtype
    func.callFunc = fn
    ctx.addFunc(func)

# def getPrint(ctx:Context):
#     func = NFunc('len')
#     func.callFunc = len
#     ctx.addVar(func)

# def tprint(ctx:Context):
#     func = Function('print')
#     # TODO: call system print as LEP function
#     code = 'func print(args)'
#     tlines = splitLexems(code)
#     clines:CLine = elemStream(tlines)
#     expr = lex2tree(clines)
#     # ctx = Context(None)
#     expr.do(ctx)
#     func:Function = ctx.get('print')
#     print(func)
#     func.block = Block()
#     pexp = NativeExpr()
#     def _print(x):
#         print(x)
#     pexp.run = _print
#     func.block.add(pexp)
#     return func


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
            setFunc(ctx, 'print', print, TypeNull)
            setFunc(ctx, 'len', len, TypeInt)
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
