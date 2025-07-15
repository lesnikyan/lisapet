
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


def getVal(arg):
    v = arg
    if isinstance(arg, Var):
        v = arg.get()
    if isinstance(v, (ListVal, DictVal, TupleVal)):
        v = v.vals()
    # elif isinstance(v, StructInstance):
    #     v = v.istr()
    elif isinstance(v, Val):
        v = v.getVal()
    return v



def buit_print(*args):
    pargs = []
    # print('b-print1:', args)
    for n in args:
        # print('b-print:::', n)
        v = getVal(n)
        # v = n
        # if isinstance(n, Var):
        #     v = n.get()
        # if isinstance(v, (ListVal, DictVal, TupleVal)):
        #     v = v.vals()
        # elif isinstance(v, StructInstance):
        #     v = v.istr()
        # elif isinstance(v, Val):
        #     v = v.getVal()
        if isinstance(v, StructInstance):
            v = v.istr()
        pargs.append(v)
    print(*pargs)

def built_len(arg):
    return arg.len()


def built_int(x):
    return int(x.getVal())

def built_list(src):
    ''' Convert list-generator, tuple, args, etc to list object.
        TODO: args needs variadic function syntax to be implemented.
    '''
    # print('b-list1:', src)
    val = getVal(src)
    res = None
    if isinstance(src, ListVal):
        res = src
    elif isinstance(val, ListGenIterator):
        res = val.allVals()
    # print('b-list2:', res)
    return res
