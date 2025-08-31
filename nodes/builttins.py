
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

def built_len(_, arg):
    return arg.len()


def built_int(_, x):
    return Val(int(x.getVal()), TypeInt())

def built_type(_, val):
    # TODO: add more correct type identification
    return Val(type(val.getVal()), TypeType())


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


def built_join(_, vals, sep=None) -> str:
    elems = built_list(0, vals).vals()
    if sep is None:
        sep = ""
    else:
        sep = str(sep.getVal())
    res = sep.join([n for n in elems])
    return Val(res, TypeString)


# TODO:
'''
str_split # split string by substring
list_join # join  list vals to string
int2char # int val to char as a string, int array to string
char_code # nuber code of char

'''
