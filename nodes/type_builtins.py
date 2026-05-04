'''
methods bound to base types
'''

import math
from functools import cmp_to_key

from vars import *
from nodes.iternodes import *
from nodes.structs import StructInstance
from nodes.func_expr import Function
from nodes.builtins import built_list, built_foldl, built_tostr

import libs.str as libst
import libs.bytes as lbytes
import libs.regexp as rexp



def char_key(ctx, arg:StringVal):
    v = arg.getVal()
    if len(v) != 1:
        raise EvalErr('only 1-char string is a correct argument for int constructor.')
    v = ord(v)
    return Val(int(v), TypeInt())

# Type constructors

def int_constr(ctx, arg:Val):
    v = arg.getVal()
    match v:
        case Null():
            v = 0
        case Glif():
            v = ord(v.val)
        case '':
            v = 0
        case bytearray():
            lv = len(v)
            nn = [v[i] << ((lv-i-1)*8)  for i in range(lv)]
            v = sum(nn)
        case str():
            v = int(v)
    return Val(int(v), TypeInt())

def float_constr(ctx, arg:Val):
    v = arg.getVal()
    match v:
        case Null():
            v = 0
        case '':
            v = 0
    return Val(float(v), TypeFloat())

def bool_constr(ctx, arg:Val):
    v = arg.getVal()
    match v:
        case Null():
            v = False
        case str():
            if v in ['', 'false']:
                v = False
            else:
                v = True
        case bytearray():
            v = sum(int(b) for b in v) != 0
        case Glif():
            v  = ord(v.val) != 0
    return Val(bool(v), TypeBool())


def string_constr(ctx, arg:Val):
    if isinstance(arg.getType(), TypeGlif):
        arg = arg.get().val
    return built_tostr(ctx, arg)


def some_constr(ctx, arg:Val):
    val = var2val(arg)
    # print('$1', val, [val])
    return Some(val)


def regexp_constr(ctx, pattern:Val, flags:Val=None):
    pval = pattern.getVal()
    fval = ''
    if flags:
        fval = flags.getVal()
    # print('$1', fval, flags)
    ptr = rexp.compile(pval, rexp.str2flags(fval))
    return Regexp(ptr)


def glif_constr(ctx, arg:Val):
    v = arg.getVal()
    match arg.getType():
        case TypeGlif():
            v = arg.get().val
        case TypeInt():
            v = chr(v)
        case TypeString():
            if len(v) != 1:
                raise EvalErr('Glif constructor can take 1-symbol string only.')
            v = v[0]
        case TypeBytes():
            vv:bytearray2 = arg.getVal()
            v = vv.decode()[0]
    return Val(Glif(v), TypeGlif())


def bytes_constr(ctx, arg:Val):
    r = []
    match arg.getType():
        case TypeString():
            r = bytearray2(arg.getVal().encode())
        case TypeInt():
            r = bytearray2(arg.getVal())
        case TypeGlif():
            r = bytearray2(arg.getVal().val.encode())
        case TypeList():
            # all elements should be integers
            r = bytearray2(arg.get())
    return BytesVal(r)


def copyElems(src:list):
    r = []
    for v in src:
        if isinstance(v, (FuncInst, ObjectInstance, Collection)):
            r.append(v)
        elif isinstance(v, (Null)):
            r = Null()
        else:
            r.append(v.copy())
    # print('CopyEl', src, r)
    return r


def val2Seq(val:Val):
    # print('$1', val, val.getType())
    r = []
    match val.getType():
        case TypeInt():
            r = [Val(0, TypeInt()) for _ in range(val.getVal())]
        case TypeBytes():
            r = [Val(n, TypeInt()) for n in list(val.getVal())]
        case TypeString():
            r = [Val(Glif(c), TypeGlif()) for c in list(val.getVal())]
        case TypeTuple():
            r = copyElems(val.elems)
        case TypeList():
            r = copyElems(val.elems)
        case TypeIterator():
            r = val.getVal().makeElems()
        case TypeGenerator():
            r = val.getVal().makeElems()
    return r


def list_constr(ctx, arg:Val):
    r = val2Seq(arg)
    # print('$2', r,)
    return ListVal(elems = r)


def tuple_constr(ctx, arg:Val):
    r = val2Seq(arg)
    return TupleVal(elems=r)


def dict_constr(ctx, arg:Val):
    v = arg.getVal()
    dd = []
    match arg.getType():
        case TypeDict():
            dd = {k: v.copy() for k, v in arg.data.items()}
        case TypeTuple():
            kk = [k.getVal() for k in arg.elems[0].elems]
            vv = copyElems(arg.elems[1].elems)
            dd = dict(zip(kk, vv))
        case TypeList():
            # should be list of 2-val tuples
            # print('tpl:', [tt for tt in arg.elems])
            dd = {tt.elems[0].getVal(): tt.elems[1] for tt in arg.elems}
        case TypeGenerator():
            elems = arg.getVal().makeElems()
            # print('$3', elems)
            dd = {tt.elems[0].getVal(): tt.elems[1] for tt in elems}
                
    return DictVal(data=dd)


# def _constr(ctx, arg:Val):
#     v = arg.getVal()
#     return Val(float(v), Type())

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


def seq_sort(ctx:Context, elems:list, cmp:Function):
    nn = copyElems(elems)
    def cmpFunc(a:Val, b:Val):
        cmp.setArgVals([a, b])
        cmp.do(ctx)
        cval = cmp.get()
        return var2val(cval).getVal()
    return sorted(nn, key = cmp_to_key(cmpFunc))


def list_sort(ctx:Context, src:ListVal, cmp:Function):
    r = seq_sort(ctx, src.elems, cmp)
    return ListVal(elems=r)


def tuple_sort(ctx:Context, src:ListVal, cmp:Function):
    r = seq_sort(ctx, src.elems, cmp)
    return TupleVal(elems=r)


def filterFuncCall(ctx:Context, a:Val|list, cond:Function):
    arg = a
    if not isinstance(a, list):
        arg = [a]
    cond.setArgVals(arg)
    cond.do(ctx)
    cval = cond.get()
    return var2val(cval).getVal()


def seq_filter(ctx:Context, elems:list, cond:Function):
    nn = [v for v in elems if filterFuncCall(ctx, v, cond)]
    r = copyElems(nn)
    return r


def list_filter(ctx:Context, src:ListVal, cond:Function):
    r = seq_filter(ctx, src.elems, cond)
    return ListVal(elems=r)


def tuple_filter(ctx:Context, src:ListVal, cond:Function):
    r = seq_filter(ctx, src.elems, cond)
    return TupleVal(elems=r)


def dict_filter(ctx:Context, src:DictVal, cond:Function):
    elems = [ [dkeyCover(k), v] for k, v in src.data.items()]
    r = seq_filter(ctx, elems, cond)
    d = {n[0].getVal() : n[1] for n in r}
    return DictVal(data=d)


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


def string_bytes(_, inst:StringVal, encoding:Val=None):
    enc = 'utf-8'
    if encoding:
        enc = encoding.getVal()
    enc = enc.lower()
    if enc in encodeMap:
        enc = encodeMap[enc]
    bb = bytearray2(inst.val.encode(enc))
    return BytesVal(bb)


def string_glifs(_, inst:StringVal):
    r = [Val(Glif(s), TypeGlif()) for s in inst.getVal()]
    return ListVal(elems = r)


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


encodeMap = {
    'utff8': 'utf-8',
}


def bytes_string(_, inst:BytesVal, encoding:Val=None):
    enc = 'utf-8'
    if encoding:
        enc = encoding.getVal()
    enc = enc.lower()
    if enc in encodeMap:
        enc = encodeMap[enc]
    s = inst.val.decode(enc)
    return StringVal(s)


def glif_int(_, inst:Val):
    v = inst.get().val
    return Val(ord(v), TypeInt())


def glif_bytes(_, inst:Val):
    r = bytearray2(inst.getVal().val.encode())
    return BytesVal(r)


# Maybe

def maybe_get(_, inst:Some):
    return inst.get()


def maybe_map(ctx:Context, inst:Some|NoneVal, fun:Function):
    match inst:
        case Some():
            arg = inst.get()
            fun.setArgVals([arg])
            fun.do(ctx)
            r = fun.get()
            return Some(r)
        case NoneVal():
            return NoneVal()
    raise EvalErr('Incorrect instance of `maybe_map`')


def is_none(ctx:Context, inst:Some|NoneVal):
    res = isinstance(inst, NoneVal)
    return Val(res, TypeBool())


