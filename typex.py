
'''

'''

from base import *


class TypeType(VType):
    name = 'type'


class TypeNull(VType):
    name = 'null'


class TypeAny(VType):
    name = 'Any'


class Undefined(VType):
    name='undefined'


class TypeNum(VType):
    name = 'num'


class TypeInt(TypeNum):
    name = 'int'


class TypeRatio(TypeNum):
    '''rational number n/m'''
    name = 'ratio'

class TypeFloat(TypeNum):
    name = 'float'


class TypeComplex(TypeNum):
    name = 'complex'


class TypeBool(VType):
    name = 'bool'


class TypeContainer(VType):
    pass

class TypeList(TypeContainer):
    name = 'list'

class TypeDict(TypeContainer):
    name = 'dict'


class TypeTuple(TypeContainer):
    name = 'tuple'


class TypeString(VType):
    name = 'string'


class FuncInst(Val):
    '''function object is stored in context, callable, returns result '''

    def __init__(self):
        super().__init__(None, TypeFunc)

    def getName(self):
        pass

    def do(self, ctx: 'Context'):
        pass
    
    def get(self)->Var:
        pass


class TypeStruct(TypeContainer):
    name = 'struct'

    def addMethod(self, name, func:FuncInst):
        pass
    
    def getName(self):
        pass


class TypeFunc(VType):
    name = 'function'


class TypeAccess(VType):
    '''  '''
    name = 'handler'


class TypeIterator(VType):
    name = 'iterator'


class ComparT:
    ''' Comparable type'''
    def compare(self, other:'ComparT'):
        pass


class NSContext:
    ''' namespeca contxt '''

def find(self, name)->Base:
    pass


def builtinTypes()->list[VType]:
    return [TypeAny, TypeBool, TypeInt, TypeFloat, TypeComplex, 
            TypeString, TypeList, TypeDict, TypeStruct, TypeNull, TypeTuple, TypeFunc]


def typeCompat(dest:VType, src:VType):
    '''Check if types compatible.
    src can be converted to dest.
    '''
    # compatList:list[VType] = []
    stype = src.type
    if stype == dest:
        return True
    match dest.name:
        case 'any': return True
        case 'string': return stype == TypeString
        case 'num': return stype in [TypeComplex, TypeBool, TypeInt, TypeFloat, TypeNull]
        case 'complex': return stype in [TypeBool, TypeInt, TypeFloat, TypeNull]
        case 'float': return stype in [TypeBool, TypeInt, TypeNull]
        case 'int': return stype in [TypeBool, TypeNull]
        case 'list'|'dict'|'struct': return stype in [TypeNull]
        case _: return False

def typeCast(val:Var, type:VType):
    ''' cast val ty type'''
    