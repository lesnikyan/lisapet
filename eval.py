
'''
Eval parsed lexems
TODO: rename to preload.py
'''

from vars import *
from context import Context, RootContext
from nodes.func_expr import setNativeFunc, bindNativeMethod, addTypeConstr
from nodes.builtins import *
import libs.str as lstr
import libs.dicts as dc
from nodes.type_builtins import *
from nodes.func_features import func_curry, func_compose


def initFuncs(ctx:Context):
    # type constructors
    addTypeConstr(ctx, int_constr, TypeInt())
    addTypeConstr(ctx, float_constr, TypeFloat())
    addTypeConstr(ctx, bool_constr, TypeBool())
    addTypeConstr(ctx, string_constr, TypeString())
    addTypeConstr(ctx, bytes_constr, TypeBytes())
    addTypeConstr(ctx, list_constr, TypeList())
    addTypeConstr(ctx, tuple_constr, TypeTuple())
    addTypeConstr(ctx, dict_constr, TypeDict())
    addTypeConstr(ctx, glif_constr, TypeGlif())
    addTypeConstr(ctx, regexp_constr, TypeRegexp())
    
    # global funcs
    setNativeFunc(ctx, 'print', buit_print, TypeNull())
    setNativeFunc(ctx, 'len', built_len, TypeInt())
    setNativeFunc(ctx, 'iter', loop_iter, TypeIterator())
    setNativeFunc(ctx, 'type', built_type, TypeType())
    setNativeFunc(ctx, 'toint', built_int, TypeInt())
    setNativeFunc(ctx, 'tostr', built_tostr, TypeString())
    setNativeFunc(ctx, 'tolist', built_list, TypeList())
    setNativeFunc(ctx, 'foldl', built_foldl, TypeAny())
    setNativeFunc(ctx, 'join', lstr.join, TypeString())
    setNativeFunc(ctx, 'split', lstr.split, TypeList())
    setNativeFunc(ctx, 'replace', lstr.replace, TypeList())
    setNativeFunc(ctx, 'dkeys', dc.dict_keys, TypeList())
    setNativeFunc(ctx, 'ditems', dc.dict_items, TypeList())
    setNativeFunc(ctx, 'char_key', char_key, TypeInt())
    setNativeFunc(ctx, 'some', some_constr, TypeMaybe())
    # print('>>>\n\n~~~!!!!\n\n')
    
    # bind methods
    
    # sequence actions
    bindNativeMethod(ctx, 'list', list_join, 'join', TypeString)
    bindNativeMethod(ctx, 'list', list_reverse, 'reverse', TypeList)
    bindNativeMethod(ctx, 'tuple', tuple_reverse, 'reverse', TypeTuple)
    bindNativeMethod(ctx, 'bytes', bytes_reverse, 'reverse', TypeBytes)
    bindNativeMethod(ctx, 'string', str_split, 'split', TypeList)
    bindNativeMethod(ctx, 'string', str_join, 'join', TypeString)
    bindNativeMethod(ctx, 'string', str_replace, 'replace', TypeString)
    bindNativeMethod(ctx, 'bytes', bytes_replace, 'replace', TypeBytes)
    
    bindNativeMethod(ctx, 'dict', dict_keys, 'keys', TypeList)
    bindNativeMethod(ctx, 'dict', dict_items, 'items', TypeList)
    
    # functional set
    # map
    bindNativeMethod(ctx, 'list', list_map, 'map', TypeList)
    bindNativeMethod(ctx, 'tuple', tuple_map, 'map', TypeTuple)
    bindNativeMethod(ctx, 'string', str_map, 'map', TypeString)
    bindNativeMethod(ctx, 'bytes', bytes_map, 'map', TypeBytes)
    # fold
    bindNativeMethod(ctx, 'list', list_fold, 'fold', TypeList)
    bindNativeMethod(ctx, 'tuple', tuple_fold, 'fold', TypeTuple)
    bindNativeMethod(ctx, 'bytes', bytes_fold, 'fold', TypeBytes)
    # each
    bindNativeMethod(ctx, 'list', seq_each, 'each', None)
    bindNativeMethod(ctx, 'tuple', seq_each, 'each', None)
    bindNativeMethod(ctx, 'bytes', seq_each, 'each', None)
    
    # bytes
    bindNativeMethod(ctx, 'bytes', bytes_blocks, 'blocks', TypeList)
    bindNativeMethod(ctx, 'bytes', bytes_nums, 'nums', TypeList)
    bindNativeMethod(ctx, 'bytes', bytes_bits, 'bits', TypeList)
    bindNativeMethod(ctx, 'bytes', bytes_split, 'split', TypeList)
    bindNativeMethod(ctx, 'bytes', bytes_string, 'string', TypeString)
    
    # string
    bindNativeMethod(ctx, 'string', lstr.string_upper, 'upper', TypeString)
    bindNativeMethod(ctx, 'string', lstr.string_lower, 'lower', TypeString)
    bindNativeMethod(ctx, 'string', string_bytes, 'bytes', TypeBytes)
    bindNativeMethod(ctx, 'string', string_glifs, 'glifs', TypeList)
    
    # list
    bindNativeMethod(ctx, 'list', list_sort, 'sort', TypeList)
    bindNativeMethod(ctx, 'list', list_filter, 'filter', TypeList)
    
    # tuple
    bindNativeMethod(ctx, 'tuple', tuple_sort, 'sort', TypeTuple)
    bindNativeMethod(ctx, 'tuple', tuple_filter, 'filter', TypeTuple)
    
    # dict
    bindNativeMethod(ctx, 'dict', dict_filter, 'filter', TypeDict)
    
    # glif
    bindNativeMethod(ctx, 'glif', glif_int, 'int', TypeInt)
    bindNativeMethod(ctx, 'glif', glif_bytes, 'bytes', TypeBytes)
    
    # function
    setNativeFunc(ctx, 'curry', func_curry, TypeFunc())
    setNativeFunc(ctx, 'compose', func_compose, TypeFunc())
    
    # maybe
    bindNativeMethod(ctx, 'maybe', maybe_get, 'get', TypeAny())
    
    


def setDefaultTypes(ctx:Context):
    types = builtinTypes()
    for tt in types:
        ctx.addType(tt())


def rootContext(ctx:Context = None)->RootContext:
    ''' Make root context with builtin functions. '''
    # if ctx is None:
    ctx = RootContext()
    setDefaultTypes(ctx)
    initFuncs(ctx)
    
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
