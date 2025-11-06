
'''

'''

from nodes.iternodes import *
from nodes.structs import StructInstance
from nodes.func_expr import Function


def loop_iter(_, *args):
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



def buit_print(_,*args):
    pargs = []
    # print('b-print1:', args)
    for n in args:
        # print('b-print:::', n)
        if isinstance(n, (Function)):
            pargs.append(str(n))
            continue
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
        # print('b-print2:::', v)
    print(*pargs)

def built_len(_, arg):
    # print('##len:', arg.__class__)
    return arg.len()


def built_int(_, x):
    return Val(int(x.getVal()), TypeInt())

def built_type(_, val:Val|Var):
    # TODO: add more correct type identification
    # print('bltype:', val,  type(val), val.getType())
    # return Val(type(val.getType()), TypeType())
    return Val(val.getType(), TypeType())


def built_list(_, src):
    ''' Convert list-generator, tuple, args, etc to list object.
        TODO: args needs variadic function syntax to be implemented.
    '''
    # print('b-list1:', src)
    val = getVal(src)
    
    # print('b-list1:', val)
    res = None
    if isinstance(src, ListVal):
        res = src
    elif isinstance(val, ListGenIterator):
        res = val.allVals()
    elif isinstance(val, str):
        res = str2list(val)
    # print('b-list2:', res)
    return res


def built_foldl(ctx:Context, start, elems, fun:Function):
    r = start
    elems = built_list(0, elems).rawVals()
    for n in elems:
        fun.setArgVals([r, n])
        fun.do(ctx)
        r = fun.get()
    # rval = r.getVal()
    # rtype = valType(rval)
    return r


# TODO:
'''
str_split # split string by substring
int2char # int val to char as a string, int array to string
char_code # nuber code of char

'''
