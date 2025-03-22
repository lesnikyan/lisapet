

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
    def __init__(self):
        self.vtype:VType = TypeNull

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

# Collections

class ContVar(Var):
    ''' Contaiter Var list, dict, etc '''
    
    def setVal(self, key:Var, val:Var):
        pass

    def getVal(self, key:Var):
        pass


class ListVar(ContVar):
    ''' classic List / Array object'''
    
    def __init__(self, name=None):
        super().__init__(None, name, TypeList)
        self.elems:list[Var] = []
    
    def addVal(self, val:Var):
        # not sure, we need whole Var or just internal value?
        self.elems.append(val)
    
    def setVal(self, key:Var, val:Var):
        i = key.get()
        print('ListVar.setVal', i, val, 'Len=', len(self.elems), i < len(self.elems), self.elems)
        if i >= len(self.elems):
            raise EvalErr('List out of range by index %d ' % i)
        self.elems[i] = val

    def getVal(self, key:Var):
        print('ListVar.getVal1, key:', key)
        print('ListVar.getVal1, elems:', self.elems)
        i = key.get()
        print('@ i=', i)
        if i < len(self.elems):
            return self.elems[i]
        raise EvalErr('List out of range by index %d ' % i)

    def __str__(self):
        nm = self.name
        if not nm:
            nm = '#list-noname'
        return 'ListVar(%s, [%s])' % (nm, ', '.join([str(n.get()) for n in self.elems[:10]]))


class DictVar(ContVar):
    ''' classic List / Array object'''
    
    def __init__(self, name=None):
        super().__init__(None, name, TypeList)
        self.data:dict[Var,Var] = {}
        
    def inKey(self, key:Var)->str:
        return '%s__%s' % (key.get(), key.getType().__class__.__name__)

    def setVal(self, key:Var, val:Var):
        k = self.inKey(key)
        self.data[k] = val

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


class FuncInst(Var):
    '''function object is stored in context, callable, returns result '''

    def __init__(self, name):
        super().__init__(name, TypeFunc)

    def do(self, ctx: 'Context'):
        pass
    
    def get(self)->Var:
        pass


# Context

def instance(tp:VType)->Var:
    match tp.name:
        case 'list': return ListVar()
        case 'dict': return DictVar()
        case _: return Var(None, None, tp)


class Context:
    _defaultContextVals = {
        'true': Var(True, 'true', TypeBool),
        'false': Var(False, 'false', TypeBool),
    }
    def __init__(self, parent:'Context'=None):
        self.vars:dict = dict()
        self.types:dict[str, VType] = {}
        self.funcs:dict[str,FuncInst] = {}
        self.upper:Context = parent # upper level context

    def depth(self):
        d = []
        src = self
        while src is not None:
            d.append(src.vars.keys())
            if src.upper is None:
                break
            src = src.upper
        return d

    def addType(self, tp:VType):
        if tp.name not in self.types:
            self.types[tp.name] = tp

    def getType(self, name)->Base:
        if name in Context._defaultContextVals:
            return Context._defaultContextVals[name]
        src = self
        while True:
            if name in self.types:
                return self.types[name]
            if src.upper == None:
                raise EvalErr('Cant find var|type name `%s` in current context' % name)
            src = src.upper

    def addSet(self, vars:Var|dict[str,Var]):
        if not isinstance(vars, dict):
            vars = {vars.name: vars}
        print('x.addSet ---------1',  {(k, v.name, v.get()) for k, v in self.vars.items()})
        print('x.addSet ---------2', {(k, v.name, v.get()) for k, v in vars.items()})
        print('x.addSet ---------3', vars)
        self.vars.update(vars)
        
    def update(self, name, val:Var):
        print('x.update ====> :', name, val.get(), val.getType().__class__.__name__)
        src = self
        while True:
            print('#Ctx-upd,name:', name)
            print('#Ctx-upd2', src.vars)
            if name in src.vars:
                print('x.upd:found', name)
                val.name = name
                src.vars[name] = val
                # src.vars[name].set(val.get())
            if src.upper is None:
                print('-- src.upper == None --', name, val)
                val.name = name
                self.addVar(val)
                break
            src = src.upper

    def addVar(self, varName:Var|str, vtype:VType=None):
        print('x.addVar0 >> var:', varName, varName.name)
        var = varName
        name = varName
        print('x.addVar1 ====> :', varName, varName.__class__.__name__, vtype, vtype.__class__.__name__)
        if isinstance(varName, str):
            var = Var(None, varName, vtype)
        else:
            print('#>> var.name:', var.name)
            name = var.name
        print('x.addVar2 ====> :', name, var, ':', var.get(), var.getType().__class__.__name__)
        if isinstance(var, FuncInst):
            print('x.addVar ===>  ADD func ====> name:', name, ' var: ', var)
            self.funcs[name] = var
            return
        self.addSet({name:var})

    def getVar(self, name)->Base:
        if name in Context._defaultContextVals:
            return Context._defaultContextVals[name]
        src = self
        while True:
            # print('#Ctx-get,name:', name)
            # print('#Ctx-get2', src.vars)
            if name in src.vars:
                return src.vars[name]
            if src.upper == None:
                raise EvalErr('Cant find var|name `%s` in current context' % name)
            src = src.upper

    def get(self, name)->Base:
        if name in Context._defaultContextVals:
            return Context._defaultContextVals[name]
        src = self
        while src is not None:
            print('#Ctx-get,name:', name)
            print('#Ctx-get2', src.vars)
            print('#Ctx-get3', src.depth())
            if name in self.types:
                return self.types[name]
            if name in self.funcs:
                return self.funcs[name]
            if name in src.vars:
                return src.vars[name]
            if src.upper is None:
                raise EvalErr('Can`t find var|type name `%s` in current context' % name)
            src = src.upper

    def print(self, ind=0):
        c:Context = self
        while c:
            for k, v in c.vars.items():
                print('x>', ' ' * ind, k, ':', v.get())
            c = c.upper
            ind += 1
            
