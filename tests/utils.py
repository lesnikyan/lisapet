

from pathlib import Path

from parser import splitLine, splitLexems, charType, splitOper, elemStream
from tree import lex2tree
from eval import rootContext

from vars import *
from nodes.builtins import getVal


null = Null()
true = True
false = False
none = NoneVal()

def norm(code):
    ''' Normalize input code: 
    - cut extra indent'''
    ind = 0
    for s in code:
        if s == ' ':
            ind += 1
        else:
            break
    return '\n'.join([s[ind:] for s in code.splitlines()])


class TestSome(Some):
    def __init__(self, val):
        super().__init__(val)
    
    def __eq__(self, value):
        if not isinstance(value, (Some, TestSome)):
            return False
        vv = getVal(value.val)
        return self.val == vv
    
    def __repr__(self):
        vv = (self.val)
        return 'some(%r)' % (vv, )


def some(val):
    return TestSome(val)


def ivar(name, value):
    vv = Var(name, TypeInt())
    vv.set(Val(value, TypeInt()))
    return vv


def filepath(fname):
    return Path(__file__).with_name(fname)
    
def trydo(expr, ctx, out=True):
    try:
        expr.do(ctx)
    except LangError as ex:
        if out:
            print('\n!! Eval Error:', ex.msg)
        raise ex
    except Exception as ex:
        if out:
            print(ex.args)
        raise ex

def tryParse(code):
    try:
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        expTree = lex2tree(clines)
        return expTree
    except InterpretErr as ex:
        print('\n!! Error Interpretation :', ex.msg)
        raise ex
    except LangError as ex:
        print('\n!! Error Parsing:', ex.msg)
        raise ex
    except Exception as ex:
        print('\n!! Common Error', ex.args)
        raise ex


def doCodeMute(code):
    # ex = tryParse(code)
    tlines = splitLexems(code)
    clines:CLine = elemStream(tlines)
    ex = lex2tree(clines)
    rCtx = rootContext()
    ctx = rCtx.moduleContext()
    ex.do(ctx)
    return ctx


def doCode(code):
    ex = tryParse(code)
    # tlines = splitLexems(code)
    # clines:CLine = elemStream(tlines)
    # ex = lex2tree(clines)
    rCtx = rootContext()
    ctx = rCtx.moduleContext()
    trydo(ex, ctx)
    return ctx


def typevals(src:ListVal|TupleVal):
    r = []
    for n in src.elems:
        r.append((n.get(), n.getType().__class__.__name__))
    if isinstance(src, TupleVal):
        r = tuple(r)
    return r


def reprElem(arg):
    n = arg
    # print('>>', n, type(n))
    if isinstance(n, (ListVal, TupleVal, DictVal)):
        n = reprElem(n.vals())
    elif isinstance(n, (list, tuple)):
        n = resRepr(n)
    elif isinstance(n, (Maybe)):
        match n:
            case NoneVal():
                n = n
            case Some():
                n = TestSome(reprElem(n.get()))
    elif isinstance(n, (bytearray2, bytearray, bytes)):
        n = str(n)
    elif isinstance(n, (ObjectInstance)):
        n = 'st@%s' % str(n)
    elif isinstance(n, (Space)):
        n = '%s' % str(n)
    elif isinstance(n, (StringVal)):
        n = '%s' % n.val
    elif isinstance(n, (Glif)):
        n = 'g(%s)'%(n.val)
    elif isinstance(n, (Regexp)):
        n = '%s'%str(n)
    
    if isinstance(arg, tuple):
        n = tuple(n)
    return n


def resRepr(src):
    # from nodes.builtins import pstr
    rr = []
    for n in src:
        rn = reprElem(n)
        # print('n rn', n, rn)
        rr.append(rn)
    if isinstance(src, tuple):
        rr = tuple(rr)
    # print('rr>', rr)
    return rr

