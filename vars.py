

from lang import *
from base import *

# Datatype part


class TypeNull(VType):
    name = 'null'

class Undefined(VType):
    name='undefined'

class ComparT:
    ''' Comparable type'''
    def compare(self, other:'ComparT'):
        pass

class TypeNum(VType):
    name = 'num'

class TypeInt(TypeNum):
    name = 'int'

class TypeFloat(TypeNum):
    name = 'float'

class TypeComplex(TypeNum):
    name = 'complex'

class TypeBool(VType):
    name = 'bool'

class TypeList(VType):
    name = 'list'

class TypeTuple(VType):
    name = 'tuple'

class TypeString(VType):
    name = 'string'

class TypeStruct(VType):
    name = 'struct'

class TypeFunc(VType):
    name = 'function'


class Var_(Var):
    ''' expr: _ '''
    name = '_'
    def __init__(self):
        self.vtype:VType = TypeNull
        self.val = None

class VarNull(Var):
    ''' None|null'''

    def __init__(self, name=None):
        self.name = name

    def get(self):
        return None

    def setType(self, t:VType):
        pass

def value(val, vtype:VType)->Var:
    return Var(val, None, vtype)

# type: Comparable, Container, Numeric 

class CompVar(Var):
    def compare(self, other:'CompVar')-> int:
        a, b = self.get(), other.get()
        if a == b:
            return 0
        return a - b


class FuncRes(Var):
    ''' '''
    def __init__(self, val):
        super().__init__(val, None)


# Collections

class Container(Var):
    ''' Contaiter Var list, dict, etc '''
    
    def setVal(self, key:Var, val:Var):
        pass

    def getVal(self, key:Var|int):
        pass


class Collection(Container):
    
    def len(self)->int:
        return 0


class ListVar(Collection):
    ''' classic List / Array object'''
    
    def __init__(self, name=None, **kw):
        super().__init__(None, name, TypeList)
        ees = []
        if 'elems' in kw:
            ees = kw['elems']
        self.elems:list[Var] = ees

    def len(self)->int:
        return len(self.elems)
    
    def addVal(self, val:Var):
        # not sure, we need whole Var or just internal value?
        self.elems.append(val)
    
    def setVal(self, key:Var, val:Var):
        i = key.get()
        # print('ListVar.setVal', i, val, 'Len=', len(self.elems), i < len(self.elems), self.elems)
        if i >= len(self.elems):
            raise EvalErr('List out of range by index %d ' % i)
        self.elems[i] = val

    def getVal(self, key:Var|int):
        # print('ListVar.getVal1, key:', key)
        # print('ListVar.getVal1, elems:', self.elems)
        i = key
        if isinstance(key, Var):
            i = key.get()
        print('@ i=', i)
        if i < len(self.elems):
            return self.elems[i]
        raise EvalErr('List out of range by index %d ' % i)

    def get(self):
        return  [n.get() for n in self.elems] # debug
        # return self.elems

    def __str__(self):
        nm = self.name
        if not nm:
            nm = '#list-noname'
        return 'ListVar(%s, [%s])' % (nm, ', '.join([str(n.get()) for n in self.elems[:10]]))


class DictVar(Collection):
    ''' classic List / Array object'''
    
    def __init__(self, name=None):
        super().__init__(None, name, TypeList)
        self.data:dict[Var,Var] = {}

    def len(self)->int:
        return len(self.data)
        
    def inKey(self, key:Var)->str:
        return '%s__%s' % (key.get(), key.getType().__class__.__name__)

    def setVal(self, key:Var, val:Var):
        k = self.inKey(key)
        self.data[k] = val

    def getKeys(self):
        # res = [ListVar(k) for k in self.data]
        res = ListVar()
        for k in self.data:
            res.addVal(k)
        return res
        

    def getVal(self, key:Var):
        k = self.inKey(key)
        if k in self.data:
            return self.data[k]
        raise EvalErr('List out of range by index %d ' % key.get())


class UserStruct(TypeStruct):
    ''' struct TypeName '''
    
    def __init__(self, name:str):
        self._typeName = name
        self.fieldNames:list[str] = []
        self.fieldsTypes:dict[str, VType] = {}

    def addField(self, name:str, stype:VType):
        if name in self.fieldNames:
            raise EvalErr('Field %d in struct %s already defined.')
        self.fieldNames.append(name)
        self.fieldsTypes[name] = stype

    def typeName(self):
        return self._typeName


class StructVar(Var):
    ''' instance of user-defined struct'''

    def __init__(self, name=None, stype=UserStruct):
        super().__init__(None, name, )
        self.type:UserStruct = stype
        self.data:dict[str,Var] = {}

    def checkField(self, name, val:Var=None):
        if name not in self.type.fieldNames:
            raise EvalErr('Struct %s doesn`t have field %s' % (name, self.type.typeName()))
        if val is not None:
            # field type doesn't change
            if name in self.data and self.type.fieldsTypes[name].name != val.getType().name:
                raise EvalErr('Incorrect value type in struct  field assignments: %s != %s' 
                            % (self.data[name].getType().name, val.getType().name))

    def setVal(self, key:Var, val:Var):
        '''set value of a field by name'''
        k = key.get()
        self.checkField(k, val)
        self.data[k].setVal(val.getVal())

    def getVal(self, key:Var)->Var:
        fn = key.get()
        self.checkField(fn)
        if fn in self.data:
            return self.data[fn]
        raise EvalErr('Incorrect field name %s of struct %s ' % (fn, self.type.typeName()))



# Context

def instance(tp:VType)->Var:
    match tp.name:
        case 'list': return ListVar()
        case 'dict': return DictVar()
        case _: return Var(None, None, tp)


