
'''

'''


from nodes.builtins import *


def rx_split(src:StringVal, rx:Regexp):
    return rx.split(src)


def split(_, src:StringVal, sep:Regexp):
    src, sep = var2val(src), var2val(sep)
    if isinstance(sep, Regexp):
        return rx_split(src, sep)
    # sepVal = getVal(sep)
    parts = src.getVal().split(sep.getVal())
    return ListVal(elems = [StringVal(s) for s in parts])


def join(_, vals:ListVal, sep=None) -> str:
    elems = built_list(0, vals).vals()
    if sep is None:
        sep = ""
    else:
        sep = str(sep.getVal())
    res = sep.join([n for n in elems])
    return StringVal(res)


def rx_replace(src:StringVal, rx:Regexp, repl:StringVal, count:Val=None):
    return rx.replace(src, repl, count)


def replace(_, src:StringVal, findptn:StringVal, repl:StringVal, count:Val=None):
    findptn = var2val(findptn)
    src, repl = var2val(src), var2val(repl)
    if isinstance(findptn, Regexp):
        return rx_replace(src, findptn, repl, count)
    sval:str = getVal(src)
    oval = getVal(findptn)
    nval = getVal(repl)
    cval = -1
    if count is not None:
        cval = count.getVal()
    res = sval.replace(oval, nval, cval)
    return StringVal(res)


