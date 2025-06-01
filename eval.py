
'''
Eval parsed lexems
'''

from vars import *
from context import Context
from nodes.func_expr import setNativeFunc
from nodes.builttins import *


def rootContext(ctx:Context = None)->Context:
    ''' Make root context with builtin functions. '''
    if ctx is None:
        ctx = Context(None)
    setDefaultTypes(ctx)
    setNativeFunc(ctx, 'print', print, TypeNull)
    setNativeFunc(ctx, 'len', buit_len, TypeInt)
    setNativeFunc(ctx, 'iter', loop_iter, TypeIterator)
    setNativeFunc(ctx, 'type', type, TypeType)
    setNativeFunc(ctx, 'toint', built_int, TypeInt)
    
    constants = {
    'true': (TypeBool, Val(True, TypeBool)),
    'false': (TypeBool, Val(False, TypeBool)),
    }
    for name, cn in constants.items():
        vv = Var(name, cn[0], const=True)
        vv.set(cn[1])
        ctx.addVar(vv)

    return ctx


def moduleContext()->ModuleContext:
    mctx = ModuleContext()
    return rootContext(mctx)

def setDefaultTypes(ctx:Context):
    types = builtinTypes()
    for tt in types:
        ctx.addType(tt())
