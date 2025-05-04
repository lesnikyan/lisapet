
''' '''

import cmath
import re

from lang import *
from base import *
from vars import *

# rxNum = re.compile('^[0-9\.]$')
rxInt = re.compile(r'^[0-9]+$')
rxFloat = re.compile(r'^[0-9]+\.[0-9]*$')
rxBin = re.compile(r'^0b[01]+$')
rxHex = re.compile(r'^0x[0-9a-f]+$')
rxOct = re.compile(r'^0o[0-7]+$')
rxComplex = re.compile(r'^[0-9]+(?:\.[0-9]*)?j(?:[0-9]+(?:\.[0-9]*)?)?$')
rxExp = re.compile(r'^[0-9]+(?:\.[0-9]*)?e\-?[0-9]+$')


def isLex(ee:Elem, xtype, text):
    if ee.type != xtype:
        return False
    if isinstance(text, list):
        return ee.text in text
    return ee.text == text


def val(data, vtype)->Val:
    return Val(data, vtype)


def raw2val(raw):
    ''' native val to Val '''
    if isinstance(raw, Val):
        return raw
    t = TypeAny
    match raw:
        case int(): t = TypeInt
        case float(): t= TypeFloat
        case str(): t = TypeString

    return Val(raw, t)


def numLex(tx:str)->Var:
    ''' 123, 12.3, 1.2e3, 0b1001, 0o137, 0xabc01, 1.5j2.3 '''
    if rxInt.match(tx):
        return val(int(tx), TypeInt())
    if rxBin.match(tx):
        return val(int(tx, 2), TypeInt())
    if rxOct.match(tx):
        return val(int(tx, 8), TypeInt())
    if rxHex.match(tx):
        return val(int(tx, 16), TypeInt())
    if rxFloat.match(tx):
        return val(float(tx), TypeFloat())
    if rxComplex.match(tx):
        real, imag = tx.split('j')
        return val(complex(float(real), float(imag)), TypeComplex())
    if rxExp.match(tx):
        # TODO: think about 132e5 as int num
        m, n = tx.split('e')
        order = 10 ** int(n)
        return val(float(m) * order, TypeFloat())

    raise InterpretErr("Value is not number: '%s'" % tx)


def strLex(tx:str)->Var:
    ''' "abc" '''
    return val(tx, TypeString())


default_constants = ['false','true', 'null']
bool_constants = ['false','true']


def isDefConst(tx:str)->bool:
    return tx in default_constants


def elem2val(elem:Elem)->Var:
    ''' numbers, string, bool '''
    if elem.type == Lt.num:
        return numLex(elem.text)
    if elem.type == Lt.text:
        return val(elem.text, TypeString())
    if elem.type == Lt.word:
        if elem.text in bool_constants:
            return val(bool(elem.text), TypeBool)
        if elem.text == 'null':
            return Val(Null(), TypeNull())
            

