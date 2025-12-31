'''
methods bound to base types
'''
from vars import *
from nodes.iternodes import *
from nodes.structs import StructInstance
from nodes.func_expr import Function
from nodes.builtins import built_list, built_foldl

import libs.str as libst


# General

def seq_map(ctx:Context, inst:Collection|SequenceGen, fun:Function):
    elems = built_list(0, inst).rawVals()
    res = []
    for n in elems:
        fun.setArgVals([n])
        fun.do(ctx)
        r = fun.get()
        res.append(r)
    return res

def seq_each(ctx:Context, inst:Collection|SequenceGen, fun:Function):
    elems = built_list(0, inst).rawVals()
    for n in elems:
        # print('built', n)
        fun.setArgVals([n])
        fun.do(ctx)

# List

def list_reverse(_, inst:ListVal):
    src = inst.rawVals().copy()
    src.reverse()
    return ListVal(elems=src)

def list_map(ctx:Context, inst:ListVal|SequenceGen, fun:Function):
    res = seq_map(ctx, inst, fun)
    return ListVal(elems=res)


def list_join(_, data:ListVal, inst:StringVal):
    sep:str = inst.getVal()
    res = sep.join([str(var2val(n).get()) for n in data.rawVals()])
    return StringVal(res)


def seq_fold(ctx:Context, elems:ListVal|TupleVal, start:Val, fun:Function):
    return built_foldl(ctx, start, elems, fun)

def list_fold(ctx:Context, elems:ListVal, start:Val, fun:Function):
    return built_foldl(ctx, start, elems, fun)

def tuple_fold(ctx:Context, elems:TupleVal, start:Val, fun:Function):
    return built_foldl(ctx, start, elems, fun)

# Tuple

def tuple_map(ctx:Context, inst:TupleVal, fun:Function):
    res = seq_map(ctx, inst, fun)
    return TupleVal(elems=res)

def tuple_reverse(_, inst:TupleVal):
    src = inst.rawVals().copy()
    src.reverse()
    return TupleVal(elems=src)

# Dict

def dict_keys(_, inst:DictVal):
    kvals = inst.keys()
    return kvals

def dict_items(_, inst:DictVal):
    kvals = inst.items()
    return kvals


# String

def str_split(_, inst:StringVal, sep):
    return libst.split(_, inst, sep)

def str_replace(_, inst:StringVal, findptn:StringVal|Regexp, repl:StringVal|ListVal, count:Val=None):
    '''
    Docstring for str_replace
    
    :param _: not used
    :param inst: source string
    :type inst: StringVal
    :param findptn: finding pattern
    :type findptn: StringVal | Regexp
    :param repl: replacement
    :type repl: StringVal | ListVal
    '''
    return libst.replace(_, inst, findptn, repl, count)

def str_join(_, inst:StringVal, data:ListVal|TupleVal):
    sep:str = inst.getVal()
    res = sep.join([str(var2val(n).get()) for n in data.rawVals()])
    return StringVal(res)


def str_map(ctx:Context, inst:StringVal, fun:Function):
    res = seq_map(ctx, inst, fun)
    stres = ''.join([n.get() for n in res])
    return StringVal(stres)

#
