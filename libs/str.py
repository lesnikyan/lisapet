
'''

'''


from nodes.builtins import *


def split(_, src, sep):
    val = getVal(src)
    sepVal = getVal(sep)
    parts = val.split(sepVal)
    return ListVal(elems = [Val(n, TypeString()) for n in parts])


def join(_, vals, sep=None) -> str:
    elems = built_list(0, vals).vals()
    if sep is None:
        sep = ""
    else:
        sep = str(sep.getVal())
    res = sep.join([n for n in elems])
    return Val(res, TypeString())

def replace(_, src, olds, news):
    sval = getVal(src)
    oval = getVal(olds)
    nval = getVal(news)
    res = sval.replace(oval, nval)
    return Val(res, TypeString())


