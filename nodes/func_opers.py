'''
Operators for functions
'''




from nodes.base_oper import *
# from nodes.datanodes import ListConstr, DictConstr
from nodes.expression import *
from bases.ntype import *
from lang import *
from nodes.func_features import *
from nodes.oper_dot import *
from nodes.structs import StructConstrBegin 
from vars import *

from nodes.func_expr import NFunc, ComposedFunc, FuncCallExpr


class RTildArrowExpr(UnarOper):

    def __init__(self, inner = None):
        super().__init__('~>', inner)

    # def setInner(self, inner:Expression):
    #     self.inner = inner

    def do(self, ctx:Context):
        ''' '''
        # do inner
        self.inner.do(ctx)
        # get func from inner
        fval = self.inner.get()
        func = var2val(fval)
        # check func for currying
        if func.getType() != TypeFunc():
            raise EvalErr('Not function tried to curry')
        # call curry(), get result
        curFunc = func_curry(ctx, func)
        self.res = curFunc


class FuncApplyOper(BinOper):
    ''' func $ arg '''
    
    def __init__(self):
        super().__init__('$')
        self.callExpr = FuncCallExpr()

    def setArgs(self, fexp:Expression, argExp:Expression):
        self.callExpr.setFuncExpr(fexp)
        self.callExpr.addArgExpr(argExp)

    def do(self, ctx:Context):
        self.callExpr.do(ctx)

    def get(self):
        return self.callExpr.get()
