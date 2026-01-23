'''
Common functions for types
'''

import copy

from lang import *
from vars import *
from typex import TypeStruct


def multiCompat( destT, srcT):
    for st in destT.getSubs():
        if isCompatible(st, srcT):
            return st
    return False


def equalType(dt, st):
    if not isinstance(dt, MultiType):
        return dt == st
    return dt.has(st)


def isCompatible( destT, srcT):
    if isinstance(destT, MultiType):
        return multiCompat(destT, srcT)
    
    if isinstance(destT, TypeStruct):
        # print('st?::', destT, srcT, structTypeCompat(destT, srcT))
        if structTypeCompat(destT, srcT):
            return destT
        return False
    # print('0?::', destT, srcT, typeCompat(destT, srcT))
    if typeCompat(destT, srcT):
        return destT
    return False


def resolveVal( desT:VType, val:Val):
    if not isinstance(desT, TypeStruct):
        val = converVal(desT, val)
    return val
    

def fixType( dest:Var, val:Val):
    ''' not for dest._strict '''
    if isinstance(val.val, Null):
        return
    valType = val.getType()
    if not isinstance(valType, TypeStruct):
        valType = copy.copy(valType)
    if dest.getType() != val.getType():
        dest.setType(valType)


def structTypeCompat(dtype:TypeStruct, stype:VType):
    ''' criterion: src should 
        have the same type the dest have,
        be child of dest type, 
        or null
        dtype - dest type
        stype = src type
    '''
    # stype = src.getType()
    # print('tcopmt1', stype)
    if isinstance(stype, TypeNull):
        return True
    # TODO: possible interface check for future
    
    # nest - for structs only
    if not isinstance(stype, TypeStruct):
        # not a struct
        return False
    if dtype == stype:
        return True
    if stype.hasParent(dtype):
        return True
    return False


def checkCompatArgs(destSet, callSet):
    ac = len(destSet)
    if ac != len(callSet):
        return False
    for ii in range(ac):
        if not isCompatible(destSet[ii], callSet[ii]):
            return False
    return True

