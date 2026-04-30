

from pathlib import Path

from parser import splitLine, splitLexems, charType, splitOper, elemStream
from tree import lex2tree
from eval import rootContext

from vars import *


null = Null()
true = True
false = False

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

def resRepr(src):
    # from nodes.builtins import pstr
    rr = []
    for n in src:
        # print('>>', n, type(n))
        if isinstance(n, (list, tuple)):
            n = resRepr(n)
        elif isinstance(n, (bytearray2, bytearray, bytes)):
            n = str(n)
        elif isinstance(n, (ObjectInstance)):
            n = 'st@%s' % str(n)
        elif isinstance(n, (Space)):
            n = '%s' % str(n)
        elif isinstance(n, (Glif)):
            n = 'g(%s)'%(n.val)
        elif isinstance(n, (Regexp)):
            n = '%s'%str(n)
        rr.append(n)
    if isinstance(src, tuple):
        rr = tuple(rr)
    return rr

