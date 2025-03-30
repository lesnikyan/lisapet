
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
    setNativeFunc(ctx, 'print', print, TypeNull)
    setNativeFunc(ctx, 'len', len, TypeInt)
    setNativeFunc(ctx, 'iter', loop_iter, TypeInt)

    return ctx
