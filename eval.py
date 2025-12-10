
'''
Eval parsed lexems
'''

from vars import *
from context import Context, RootContext
from nodes.func_expr import setNativeFunc
from nodes.builtins import *
import libs.str as lstr
import libs.dicts as dc


def rootContext(ctx:Context = None)->RootContext:
    ''' Make root context with builtin functions. '''
    # if ctx is None:
    ctx = RootContext()
    setDefaultTypes(ctx)
    setNativeFunc(ctx, 'print', buit_print, TypeNull)
    setNativeFunc(ctx, 'len', built_len, TypeInt)
    setNativeFunc(ctx, 'iter', loop_iter, TypeIterator)
    setNativeFunc(ctx, 'type', built_type, TypeType)
    setNativeFunc(ctx, 'toint', built_int, TypeInt)
    setNativeFunc(ctx, 'tostr', built_tostr, TypeString)
    setNativeFunc(ctx, 'tolist', built_list, TypeList)
    setNativeFunc(ctx, 'foldl', built_foldl, TypeAny)
    setNativeFunc(ctx, 'join', lstr.join, TypeString)
    setNativeFunc(ctx, 'split', lstr.split, TypeList)
    setNativeFunc(ctx, 'replace', lstr.replace, TypeList)
    setNativeFunc(ctx, 'dkeys', dc.dict_keys, TypeList)
    setNativeFunc(ctx, 'ditems', dc.dict_items, TypeList)
    
    constants = {
    'true': (TypeBool, Val(True, TypeBool())),
    'false': (TypeBool, Val(False, TypeBool())),
    }
    for name, cn in constants.items():
        vv = Var(name, cn[0], const=True)
        vv.set(cn[1])
        ctx.addVar(vv)

    return ctx


def moduleContext(root:Context)->ModuleContext:
    mctx = ModuleContext(root)
    return mctx

def setDefaultTypes(ctx:Context):
    types = builtinTypes()
    for tt in types:
        ctx.addType(tt())
