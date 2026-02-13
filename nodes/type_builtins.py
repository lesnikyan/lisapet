'''
methods bound to base types
'''

import math

from vars import *
from nodes.iternodes import *
from nodes.structs import StructInstance
from nodes.func_expr import Function
from nodes.builtins import built_list, built_foldl

import libs.str as libst
import libs.bytes as lbytes


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

# Bytes

def bytes_map(ctx:Context, inst:BytesVal, fun:Function):
    res = seq_map(ctx, inst, fun)
    stres = bytearray2([(n.get() % 256) for n in res])
    return BytesVal(stres)


def bytes_reverse(_, inst:BytesVal):
    data = bytearray2(inst.val[:])
    data.reverse()
    return BytesVal(data)


def bytes_fold(ctx:Context, elems:ListVal, start:Val, fun:Function):
    return built_foldl(ctx, start, elems, fun)


def bytes_replace(_, inst:BytesVal, findptn:StringVal|DictVal, repl:BytesVal, count:Val=None):
    ''' thinking. few way to implement
        1) simple byte - byte (map can do the same)
        2) find sequence, replace by sequence, dict with find-repl pairs
        3) find by function / lambda , replace by val or another lambda
        3) full regexp (why? use string)
        DONE - 2
    '''
    src = inst.val
    old = findptn.val
    new = repl.val
    n = -1
    if count:
        n = count.getVal()
    res = bytearray2(src.replace(old, new, n))
    return BytesVal(res)


def bytes_blocks(_, inst:BytesVal, size:Val):
    '''
    Split byte set into blocks of a passed size.
    If length of source is not a multiple of size, 
    the source will be padded with zero bytes on the left.
    '''
    slen = len(inst.val)
    bsize = size.getVal()
    rowlen = slen / bsize
    blen = int(math.ceil(rowlen)) # blocks length
    data = inst.val
    if slen % bsize > 0:
        need = bsize * blen - slen
        data = bytearray(need) + data
    res = []
    for i in range(blen):
        part = data[i * bsize : (i + 1) * bsize]
        res.append(BytesVal(bytearray2(part)))
    return ListVal(elems=res)


def bytes_nums(_, inst:BytesVal, size:Val, signed:Val=None):
    '''
    Split byte set into int numbers by a passed size.
    If length of source is not a multiple of size, 
    the source will be padded with zero bytes on the left.
    
    :param inst: source ByteVal
    :param size: size of each part
    :param signed - to make or not signed int, default = false
    '''
    slen = len(inst.val)
    bsize = size.getVal()
    rowlen = slen / bsize
    blen = int(math.ceil(rowlen)) # blocks length
    data = inst.val
    if slen % bsize > 0:
        need = bsize * blen - slen
        data = bytearray(need) + data
    sg = False
    if signed is not None:
        sg = bool(signed.getVal())
    res = []
    for i in range(blen):
        part = data[i * bsize : (i + 1) * bsize]
        num = Val(int.from_bytes(part, 'big', signed=sg), TypeInt())
        res.append(num)
    return ListVal(elems=res)


def bytes_bits(_, inst:BytesVal):
    '''
    Split byte set into bit-array.
    inst: source ByteVal
    '''
    data = inst.val
    res = [Val(i, TypeInt()) for b in data for i in [(b >> i) & 1 for i in range(7, -1, -1)] ]
    return ListVal(elems=res)


def bytes_split(_, inst:BytesVal, sep:BytesVal, limit:Val=None):
    data:bytearray = inst.val
    lim = -1
    if limit:
        lim = limit.getVal()
    parts = data.split(sep.val, lim)
    res = [BytesVal(bytearray2(p)) for p in parts]
    return ListVal(elems=res)


