
'''
Execution context. General container of values.
Contains:
    Values of variables.
    Function objects.
    DataTypes (planned for `struct` type definition).
Each execution block has own context which is passed from parent block.
Current context can find var|func name up to root context (module).
'''

from vars import *


class FuncInst(Var):
    '''function object is stored in context, callable, returns result '''

    def __init__(self, name):
        super().__init__(name, TypeFunc)

    def do(self, ctx: 'Context'):
        pass
    
    def get(self)->Var:
        pass


class Context(NSContext):
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
        print('ctx.addType: ', tp)
        if tp.name in self.types:
            raise EvalErr(f'Type {tp.name} already defined.')
        if not isinstance(tp, (VType, VarType)):
            raise EvalErr(f'Trying to put non-type {tp.name} to ctx.types.')
        # if tp.name not in self.types:
        name = tp.name if isinstance(tp, VType) else tp.get().name
        if not isinstance(tp, VarType):
            tp = VarType(tp)
        self.types[name] = tp

    def getType(self, name)->VType:
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
        # print('x.addSet ---------0', vars)
        if not isinstance(vars, dict):
            vars = {vars.name: vars}
        # print('x.addSet ------ 1 pre',  {(k, v.name, '%s' %v.get()) for k, v in self.vars.items()})
        # print('x.addSet ------ 2 add', {(k, v.name, '%s' % v.get()) for k, v in vars.items()})
        # print('x.addSet ------ 3 add', vars)
        self.vars.update(vars)
        
    def update(self, name, val:Var):
        # print('x.update ====> :', name, val.get(), val.getType().__class__.__name__)
        src = self
        while True:
            # print('#Ctx-upd,name:', name)
            # print('#Ctx-upd2', src.vars)
            if name in src.vars:
                # print('x.upd:found', name)
                val.name = name
                src.vars[name] = val
                # src.vars[name].set(val.get())
            if src.upper is None:
                # print('-- src.upper == None --', name, val)
                val.name = name
                self.addVar(val)
                break
            src = src.upper

    def addFunc(self, fn:FuncInst):
        name = fn.name
        print('x.addFunc ===>  name:', name, ' var: ', fn)
        self.funcs[name] = fn

    def addVar(self, varName:Var|str, vtype:VType=None):
        # print('x.addVar0 >> var:', varName, varName.name)
        var = varName
        name = varName
        # print('x.addVar1 ====> :', varName, varName.__class__.__name__, vtype, vtype.__class__.__name__)
        if isinstance(varName, str):
            # print('! Just name', varName)
            var = Var(None, varName, vtype)
        else:
            name = var.name
        #     print('#>> var.name:', var.name)
        # print('x.addVar2 ====> :', name, var, ':', var.get(), var.getType().__class__.__name__)
        # if isinstance(var, FuncInst):
        #     print('x.addVar ===>  ADD func ====> name:', name, ' var: ', var)
        #     self.funcs[name] = var
        #     return
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
        return self.find(name)

    def find(self, name):
        if name in Context._defaultContextVals:
            return Context._defaultContextVals[name]
        src = self
        print('#Ctx-get0,:', name)
        while src is not None:
            # print('#Ctx-get,name:', name)
            # print('#Ctx-get2 vars', src.vars)
            # print('#Ctx-get3 funcs', (name in src.funcs), src.funcs)
            # print('#Ctx-depth', src.depth())
            if name in src.types:
                return src.types[name]
            if name in src.funcs:
                return src.funcs[name]
            if name in src.vars:
                return src.vars[name]
            if src.upper is None:
                # raise EvalErr('Can`t find var|type name `%s` in current context' % name)
                var = VarUndefined(name)
                # self.addVar(var)
                return var
            src = src.upper

    def print(self, ind=0):
        c:Context = self
        while c:
            for data in [c.vars, c.types]:
                for k, v in data.items():
                    vstr = v.get()
                    if isinstance(v, Collection):
                        vstr = v.vals()
                    print('x>', ' ' * ind, k, ':', vstr)
            c = c.upper
            ind += 1
            

def instance(tp:VType)->Var:
    match tp.name:
        case 'list': return ListVar()
        case 'dict': return DictVar()
        case _: return Var(None, None, tp)

