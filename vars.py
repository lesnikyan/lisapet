

from lang import *

# Datatype part

class VType:
    ''' Base of Var Type '''
    name = 'type'

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


class Base:
    def get(self)->'Base':
        pass

class Var(Base):
    def __init__(self, val, name, vtype:VType=Undefined()):
        self.val = val
        self.name = name # if name is none - here Val, not Var
        self.vtype:VType = vtype
    
    def set(self, val):
        self.val = val
    
    def get(self):
        return self.val
    
    def setType(self, t:VType):
        self.vtype = t
    
    def getType(self):
        return self.vtype
    
    def __str__(self):
        n = self.name
        if not n:
            n = '#noname'
        return 'Var(%s, %s)' % (n, self.val)

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
    
    def __init__(self, name):
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
    
    def __init__(self, name):
        super().__init__(None, name, TypeList)
        self.data:dict[Var,Var] = {}

    def setVal(self, key:Var, val:Var):
        k = key.get()
        self.data[k] = val

    def getVal(self, key:Var):
        i = key.get()
        if i in self.data:
            return self.data[i]
        raise EvalErr('List out of range by index %d ' % i)


# Context


class Context:
    _defaultContextVals = {
        'true': Var(True, 'true', TypeBool),
        'false': Var(False, 'false', TypeBool),
    }
    def __init__(self, parent:'Context'=None):
        self.vars:dict = dict()
        self.types:dict[str, VType] = {}
        self.upper:Context = parent # upper level context
    
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
            if src.upper == None:
                print('-- src.upper == None --', name, val)
                val.name = name
                self.addVar(val)
                break
            src = src.upper
    
    def addVar(self, varName:Var|str, vtype:VType=None):
        var = varName
        name = varName
        print('x.addVar1 ====> :', varName, varName.__class__.__name__, vtype, vtype.__class__.__name__)
        if isinstance(varName, str):
            var = Var(None, varName, vtype)
        else:
            name = var.name
        print('x.addVar2 ====> :', name, var, ':', var.get(), var.getType().__class__.__name__)
        self.addSet({name:var})

    # for user types
    def addType(self, name:str, vtype:VType):
        self.types[name] = vtype

    def get(self, name)->Base:
        if name in Context._defaultContextVals:
            return Context._defaultContextVals[name]
        src = self
        while True:
            print('#Ctx-get,name:', name)
            print('#Ctx-get2', src.vars)
            if name in src.vars:
                return src.vars[name]
            if src.upper == None:
                raise EvalErr('Cant find var|name `%s` in current context' % name)
            src = src.upper

    def print(self, ind=0):
        c:Context = self
        while c:
            for k, v in c.vars.items():
                print('x>', ' ' * ind, k, ':', v.get())
            c = c.upper
            ind += 1
            
