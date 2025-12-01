
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
    if isinstance(v, (ListVal, TupleVal)):
        t = [getVal(e) for e in v.vals()]
        if isinstance(v, TupleVal):
            t = tuple(t)
        v = t
    elif isinstance(v, (DictVal)):
        v = {k: getVal(vv) for k,vv in v.data.items()}
        # v = [getVal(e) for e in v.vals()]
    # elif isinstance(v, StructInstance):
    #     v = v.istr()
    elif isinstance(v, Val):
        v = v.getVal()
    return v


def esc_str(s:str):
    scov = "'%s'"
    if s.find("'") > -1:
        scov = '"%s"'
        if s.find('"') > -1:
            s = s.replace('"', '\\"')
    # print('\\e:', s, scov)
    return scov % s
    

def _elem_str(arg, parent=None):
    ''' prepare elem of collection for tostr() '''
    e = arg
    k = ''
    isDictPair = isinstance(parent, dict) and isinstance(arg, tuple)
    if isDictPair:
        k, e = e
        k = tostr(k)
        if isinstance(k, str):
            k = esc_str(k)
        else:
            k = tostr(k) # mostly for numeric
    
    if isinstance(e, str):
        e = esc_str(e)
    else:
        e = tostr(e)
    se = e
    if isDictPair:
        se = '%s:%s' % (k, se)
    # print('se:', se)
    return se

def tostr(arg):
    v = getVal(arg)
    rval = v
    # print('\n_tostr1:::', arg, '>>', v, v.__class__.__name__)
    # if isinstance(v, str):
    #     rval = esc_str(v)
        
    
    if isinstance(v, (list, tuple, dict)):
        # [1, 2, 'a', [3, 'b']]
        #
        vals = []
        isrc = v
        if isinstance(v, dict):
            isrc = v.items()
        for e in isrc:
            se = _elem_str(e, v)
            vals.append(se)
        cover = '%s'
        match v:
            case list():
                cover = "[%s]"
            case tuple():
                cover = "(%s)"
            case dict():
                cover = "{%s}"
        # print('cover:', cover)
        rval = cover % (','.join(vals))
        
    if isinstance(v, StructInstance):
        rval = v.istr()
    if isinstance(v, (Null)):
        rval = 'null'
    elif isinstance(v, (bool)):
        rval = str(v).lower()
    elif isinstance(v, (int, float, Function)):
        rval = str(v)
    # print('_tosrt9:', arg, ':', rval)
    return rval


def built_tostr(_, arg):
    # pargs = []
    # print('_tostr:', args)
    rval = tostr(arg)
    # print('_tostr3::', rval, rval.__class__.__name__)
    return StringVal(rval)
    

def buit_print(_,*args):
    pargs = []
    # print('b-print1:', args)
    for n in args:
        # print('b-print:::', n, n.__class__.__name__)
        if isinstance(n, (Function)):
            pargs.append(str(n))
            continue
        v = getVal(n)
        # print('b-print0::', v, v.__class__.__name__)
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


# TODO: refactor
def built_list(_, src):
    ''' Convert list-generator, tuple, args, etc to list object.
        TODO: args needs variadic function syntax to be implemented.
    '''
    # print('b-list0:', src)
    val = getVal(src)
    
    # print('b-list1:', val)
    res = None
    if isinstance(src, ListVal):
        res = src
    elif isinstance(val, ListGenIterator):
        res = val.allVals()
    elif isinstance(val, str):
        res = str2list(val)
    elif isinstance(src, TupleVal):
        res = ListVal(elems=[n for n in src.elems])
    # print('b-list2:', res)
    return res


def built_foldl(ctx:Context, start, elems, fun:Function):
    r = start
    elems = built_list(0, elems).rawVals()
    for n in elems:
        fun.setArgVals([r, n])
        fun.do(ctx)
        r = fun.get()
    return r


# TODO:
'''
str_split # split string by substring
int2char # int val to char as a string, int array to string
char_code # nuber code of char

'''
