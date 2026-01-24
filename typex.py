
'''

'''

from base import *
        

class TypeType(VType):
    name = 'type'
    th = TH.mk()


class TypeNull(VType):
    name = 'null'
    th = TH.mk()


class Undefined(VType):
    name='undefined'
    th = TH.mk()

class TypeNum(VType):
    name = 'num'
    _defVal = 0
    th = TH.mk()


class TypeInt(TypeNum):
    name = 'int'
    th = TH.mk()


class TypeRatio(TypeNum):
    '''rational number n/m'''
    name = 'ratio'
    th = TH.mk()

class TypeFloat(TypeNum):
    name = 'float'
    th = TH.mk()


class TypeComplex(TypeNum):
    name = 'complex'
    th = TH.mk()


class TypeBool(VType):
    name = 'bool'
    _defVal = False
    th = TH.mk()


class TypeMaybe(VType):
    name='maybe'
    th = TH.mk()


class TypeContainer(VType):
    pass
    th = TH.mk()

class TypeList(TypeContainer):
    name = 'list'
    th = TH.mk()

class TypeDict(TypeContainer):
    name = 'dict'
    _defVal = dict()
    th = TH.mk()


class TypeTuple(TypeContainer):
    name = 'tuple'
    _defVal = tuple()
    th = TH.mk()


class TypeString(VType):
    name = 'string'
    _defVal = ''
    th = TH.mk()

class TypeRegexp(VType):
    name='re'
    _defVal = None
    th = TH.mk()
    


class FuncInst(Objective):
    '''function object is stored in context, callable, returns result '''

    def __init__(self):
        super().__init__(None, TypeFunc)

    def getName(self):
        pass

    def do(self, ctx: 'Context'):
        pass
    
    def get(self)->Var:
        pass
    
    def argCount(self)->int:
        pass
    
    def argTypes(self)->list:
        pass
    
    @classmethod
    def sigHash(cc, argTypes:list[VType]):
        return '~'.join([at.hash() for at in argTypes])


class TypeModule:
    ''' imported module '''
    name = 'module'
    _defVal = None


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
    _defVal = None
    th = TH.mk()

    def setConstr(self, cons:FuncInst):
        pass
    def getConstr(self):
        pass

    def addMethod(self, name, func:FuncInst):
        pass
    
    def getMethod(self, name):
        pass
    
    def getName(self):
        pass


class TypeFunc(VType):
    name = 'function'
    _defVal = None
    th = TH.mk()


class FuncSpace:
    
    def __init__(self, btype:VType):
        pass
    
    def addMethod(self, func:FuncInst):
        pass
    
    def getMethod(self, name:str):
        pass



class TypeProperty:
    th = TH.mk()
    
    def __init__(self, btype:VType, funcs:FuncSpace):
        self.type = btype
        self.funcs:FuncSpace = funcs


class TypeAccess(VType):
    '''  '''
    name = 'handler'
    th = TH.mk()


class TypeIterator(VType):
    name = 'iterator'
    _defVal = None
    th = TH.mk()


class ComparT:
    ''' Comparable type'''
    def compare(self, other:'ComparT'):
        pass


class NSContext:
    ''' namespace context '''
    def get(self, name):
        pass


def find(self, name)->Base:
    pass


def builtinTypes()->list[VType]:
    return [TypeAny, TypeBool, TypeInt, TypeFloat, TypeComplex, 
            TypeString, TypeList, TypeDict, TypeStruct, TypeTuple, TypeFunc]


class MultiType(VType):
    ''' int|float, Abc|User, list|dict '''
    
    def __init__(self):
        super().__init__()
        self.subs:list[VType] = []
        self.name = 'multitype'
    
    def addSubType(self, sub:VType):
        self.subs.append(sub)
    
    def has(self, xtype):
        for sub in self.subs:
            if sub == xtype:
                return True
        return False
    
    def getSubs(self):
        return self.subs


def typeCompat(dest:VType, stype:VType):
    '''Check if types compatible.
    criterion: src can be converted to dest.
    '''
    if stype == dest:
        return True
    sclass = stype.__class__
    match dest.name:
        case 'any': return True
        case 'bool': return sclass in [TypeBool, TypeNull]
        case 'string': return sclass in [TypeString, TypeNull]
        case 'num': return sclass in [TypeComplex, TypeBool, TypeInt, TypeFloat, TypeNull]
        case 'complex': return sclass in [TypeBool, TypeInt, TypeFloat, TypeNull]
        case 'float': return sclass in [TypeBool, TypeInt, TypeNull]
        case 'int': return sclass in [TypeBool, TypeNull]
        case 'list'|'dict'|'struct': return sclass in [TypeNull]
        case _: return False


def converVal(dest:VType, val:Val):
    ''' applicable for compatible types only '''
    vval = val.getVal()
    vtype = val.getType()
    if vval is None or isinstance(vtype, TypeNull):
        # null to numeric
        if isinstance(dest, (TypeComplex, TypeInt, TypeFloat)):
            vval = 0
        if isinstance(dest, (TypeBool)):
            vval = False
            
    # print('converVal', vval, vtype, dest.name)
    match dest.name:
        case 'any': return val
        case 'bool': return Val(bool(vval), TypeBool())
        case 'string':
            if isinstance(vtype, TypeNull):
                return val
        case 'num': return val
        case 'complex': return val
        case 'float': return Val(float(vval), TypeFloat())
        case 'int': return Val(int(vval), TypeInt())
        case 'list'|'dict'|'struct':
            if isinstance(vtype, TypeNull):
                return val
        # case _:
    # print(f'Value conversion of unknown or incompatible dest type ({dest} << {vtype})')
    raise EvalErr(f'Value conversion of unknown or incompatible dest type ({dest} << {vtype})')
    


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

