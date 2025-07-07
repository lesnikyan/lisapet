
'''

'''

from nodes.iternodes import *
from nodes.structs import StructInstance


def loop_iter(*args):
    beg, over, step = Val(0, None), Val(0, None), Val(1, None)
    dprint('>>>>>>>>>>>>>>>>> loop_iter function')
    match len(args):
        case 1: over = args[0]
        case 2: beg, over = args
        case 3: beg, over, step = args
    it = IndexIterator(beg.get(), over.get(), step.get())
    return it

def buit_print(*args):
    pargs = []
    for n in args:
        v = n
        if isinstance(n, Var):
            v = n.get()
        if isinstance(v, (ListVal, DictVal, TupleVal)):
            v = v.vals()
        elif isinstance(v, StructInstance):
            v = v.istr()
        elif isinstance(v, Val):
            v = v.getVal()
        pargs.append(v)
    print(*pargs)

def built_len(arg):
    return arg.len()


def built_int(x):
    return int(x.getVal())


