
'''
Eval parsed lexems
'''

from vars import *
from context import Context
from nodes.func_expr import setNativeFunc
from nodes.builttins import *


def rootContext():
    ''' Make root context with builtin functions. '''
    ctx = Context(None)
    setDefaultTypes(ctx)
    setNativeFunc(ctx, 'print', print, TypeNull)
    setNativeFunc(ctx, 'len', buit_len, TypeInt)
    setNativeFunc(ctx, 'iter', loop_iter, TypeIterator)
    setNativeFunc(ctx, 'type', type, TypeType)
    
    constants = {
    'true': (TypeBool, Val(True, TypeBool)),
    'false': (TypeBool, Val(False, TypeBool)),
    }
    for name, cn in constants.items():
        vv = Var(name, cn[0], const=True)
        vv.set(cn[1])
        ctx.addVar(vv)

    return ctx

def setDefaultTypes(ctx:Context):
    types = builtinTypes()
    for tt in types:
        ctx.addType(tt())
