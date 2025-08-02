
'''

'''

from base import *


class TypeType(VType):
    name = 'type'


class TypeNull(VType):
    name = 'null'


class Undefined(VType):
    name='undefined'

class TypeNum(VType):
    name = 'num'
    defVal = 0


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
    defVal = False


class TypeMaybe(VType):
    name='maybe'


class TypeContainer(VType):
    pass

class TypeList(TypeContainer):
    name = 'list'
    defVal = []

class TypeDict(TypeContainer):
    name = 'dict'
    defVal = dict()


class TypeTuple(TypeContainer):
    name = 'tuple'
    defVal = tuple()


class TypeString(VType):
    name = 'string'
    defVal = ''


class TypeMString(TypeString):
    name='mstring'
    defVal = ''


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


class TypeModule:
    ''' imported module '''
    name = 'module'
    defVal = None


class ModuleTree:
    ''' Module tree of expressions '''

    def getName(self):
        pass
    
    def get(self, name=None):
        pass



class ModuleInst(Var):
    
    # def __init__(self):
    #     super().__init__(None, TypeModule)

    def getName(self):
        pass

    def hasImported(self, name):
        pass

    # def do(self, ctx: 'Context'):
    #     pass
    
    def get(self, name):
        pass


class TypeStruct(TypeContainer):
    name = 'struct'
    defVal = None

    def addMethod(self, name, func:FuncInst):
        pass
    
    def getMethod(self, name):
        pass
    
    def getName(self):
        pass


class TypeFunc(VType):
    name = 'function'
    defVal = None


class TypeAccess(VType):
    '''  '''
    name = 'handler'


class TypeIterator(VType):
    name = 'iterator'
    defVal = None


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
            TypeString, TypeList, TypeDict, TypeStruct, TypeTuple, TypeFunc]


def defaultValOfType(tp: VType):
    return tp.defVal


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



def valType(val):
    tps = {
        bool: TypeBool(),
        int: TypeInt(),
        float: TypeFloat(),
        str: TypeString(),
        list: TypeList(),
        dict: TypeDict(),
        tuple: TypeTuple(),
        object: TypeStruct(),
        callable: TypeFunc(),
        complex: TypeComplex()
    }
    tp = type(val)
    if tp in tps:
        return tps[tp]
    return Undefined()


def typeCast(val:Var, type:VType):
    ''' cast val ty type'''
    