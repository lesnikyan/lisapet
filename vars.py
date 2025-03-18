

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

class Var_(Base):
    ''' expr: _ '''
    pass

# type: Comparable, Container, Numeric 

class CompVar(Var):
    def compare(self, other:'CompVar')-> int:
        a, b = self.get(), other.get()
        if a == b:
            return 0
        return a - b

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
                src.vars[name].set(val.get())
            if src.upper == None:
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
        print('x.addVar2 ====> :', name, var.get(), var.getType().__class__.__name__)
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
            
