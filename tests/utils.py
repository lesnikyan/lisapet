

from pathlib import Path

from parser import splitLine, splitLexems, charType, splitOper, elemStream
from tree import lex2tree
from eval import rootContext

from vars import *


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


def doCode(code):
    tlines = splitLexems(code)
    clines:CLine = elemStream(tlines)
    ex = lex2tree(clines)
    rCtx = rootContext()
    ctx = rCtx.moduleContext()
    ex.do(ctx)
    return ctx
    