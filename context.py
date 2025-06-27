
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


class Context(NSContext):
    # _defaultContextVals = {}
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

    def getRoot(self):
        ctx = self
        while True:
            if ctx.upper is None:
                return ctx
            ctx = ctx.upper
        

    def addType(self, tp:VType):
        print('ctx.addType: ', tp, '::', type(tp))
        if not isinstance(tp, (VType, TypeVal)):
            raise EvalErr(f'Trying to put non-type {tp.name} to ctx.types.')
        # if tp.name not in self.types:
        name = tp.name if isinstance(tp, VType) else tp.get().name
        if not isinstance(tp, TypeVal):
            tp = TypeVal(tp)
        elif isinstance(tp.get(), TypeStruct):
            name = tp.get().getName()
        if name in self.types:
            raise EvalErr(f'Type {tp.name} already defined.')
        print('>>>>>>> :tp:', tp)
        self.types[name] = tp

    def getType(self, name)->VType:
        # if name in Context._defaultContextVals:
        #     return Context._defaultContextVals[name]
        # print('Context.getType-1:', name)
        # self.print()
        src = self
        while True:
            # print('ctx cur types:', src.types.keys())
            if name in src.types:
                return src.types[name]
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
        name = fn.getName()
        print('x.addFunc ===>  name:', name, ' var: ', fn)
        self.funcs[name] = fn

    # def getFunc(self, name):
    #     fvar = self.find(name)

    def addTypeMethod(self, typeName, func:FuncInst):
        typeVal = self.getType(typeName)
        xtype:TypeStruct = typeVal.get()
        print('**addTypeMethod', typeName, xtype, func)
        if not isinstance(xtype, TypeStruct):
            raise EvalErr('Strange  type fpund by name `%s`' % typeName, xtype)
        xtype.addMethod(func)

    def addVar(self, varName:Var|str, vtype:VType=None):
        # print('x.addVar0 >> var:', varName, varName.name)
        var = varName
        name = varName
        # print('x.addVar1 ====> :', varName, varName.__class__.__name__, vtype, vtype.__class__.__name__)
        if isinstance(varName, str):
            # print('! Just name', varName)
            var = Var(varName, vtype)
        else:
            name = var.name
        print('x.addVar2: ', name, var)
        self.vars[name] = var
        # self.addSet({name:var})

    def get(self, name)->Base:
        return self.find(name)

    def findIn(self, name):
        src = self
        if name in src.vars:
            return src.vars[name]
        if name in src.types:
            return src.types[name]
        if name in src.funcs:
            print('CTX.find func ?', name, src.funcs[name].__class__.__name__)
            if src.funcs[name].__class__.__name__ != 'NFunc':
                print('CTX.find func:`%s`' % name, '::', src.funcs[name])
            # if name == 'xprint':
            #     raise EvalErr('@@3')
            return src.funcs[name]
        # if src.upper is None:
        #     # raise EvalErr('Can`t find var|type name `%s` in current context' % name)
        #     var = VarUndefined(name)
        #     # self.addVar(var)
        #     return var
        return None

    def find(self, name):
        # if name in Context._defaultContextVals:
        #     return Context._defaultContextVals[name]
        src = self
        print('#Ctx-get0,:', name)
        while src is not None:
            # # print('#Ctx-get,name:', name)
            # # print('#Ctx-get2 vars', src.vars)
            # # print('#Ctx-get3 funcs', (name in src.funcs), src.funcs)
            # # print('#Ctx-depth', src.depth())
            # # print('#Ctx-get,name:', name)
            # # print('#Ctx-get2', src.vars, "\n\t\t\t", src.funcs)
            # if name in src.vars:
            #     return src.vars[name]
            # if name in src.types:
            #     return src.types[name]
            # if name in src.funcs:
            #     print('CTX.find func ?', name, src.funcs[name].__class__.__name__)
            #     if src.funcs[name].__class__.__name__ != 'NFunc':
            #         print('CTX.find func:`%s`' % name, '::', src.funcs[name])
            #     # if name == 'xprint':
            #     #     raise EvalErr('@@3')
            #     return src.funcs[name]
            res = src.findIn(name)
            print('ctx.find res=', res)
            if res:
                return res
            if src.upper is None:
                # raise EvalErr('Can`t find var|type name `%s` in current context' % name)
                var = VarUndefined(name)
                # self.addVar(var)
                return var
            src = src.upper

    def print(self, ind=0):
        c:Context = self
        while c:
            ttt = ['vars', 'types', 'funcs']
            iii = 0
            for data in [c.vars, c.types, c.funcs]:
                print('.' * ind, '  > ', ttt[iii])
                iii += 1
                for k, v in data.items():
                    vstr = v.get()
                    if isinstance(v, Collection):
                        vstr = v.vals()
                    elif isinstance(v, FuncInst):
                        vstr = 'Function(%s)' % v.getName()
                    print(' ' * ind, 'x>', k, v.__class__.__name__, ':', vstr)
            c = c.upper
            ind += 1
            

def instance(tp:VType)->Var:
    match tp.name:
        case 'list': return ListVal()
        case 'dict': return DictVal()
        case _: return Var(None, tp)


class RootContext(Context):
    ''' Top context '''
    
    def __init__(self):
        super().__init__(None)
        self.loaded:dict[str, ModuleTree] = {} # loaded modules

    def loadModule(self, module:ModuleTree):
        name = module.getName()
        self.loaded[name] = module
        
    def findloaded(self, name)->ModuleTree:
        if name in self.loaded:
            return self.loaded[name]
        return None

    def moduleContext(self)->'ModuleContext':
        mctx = ModuleContext(self)
        return mctx


class ModuleContext(Context):
    ''' Module-level context '''
    
    def __init__(self, parent:'Context'=None):
        super().__init__(parent)
        self.imported:dict[str, ModuleInst] = {} # imported modules contexts
        self.aliases:dict[str, str] = {} # imported aliases
        

    def addModule(self, name, ctx:ModuleInst):
        self.imported[name] = ctx
        
    def findModule(self, name)->ModuleInst:
        if name in self.imported:
            return self.imported[name]
        return None
    
    # def starImport(self, ctx):
    #     pass
    
    def addAlias(self, alias, orig):
        self.aliases[alias] = orig
    
    def findIn(self, name):
        ''' 
        internal: `name`
        full-imported by *: 'name'
         -- imported module: 'module.name' # Not applicable
        alias: 'name' -> `module.name`
        '''
        print('mctx.findIn:', name)
        if name in self.aliases:
            name = self.aliases[name]
        res = super().findIn(name)
        if res is not None:
            return res
        # find module
        print('#-imported', [k for k in self.imported.keys()])
        if name in self.imported:
            return self.imported[name]
        # find in modules
        for k, mbox in self.imported.items():
            if mbox.hasImported(name):
                print('has', name, ' in ', k)
                return mbox.get(name)
        # Nothing was found
        return None


class ModuleBox(ModuleInst):
    ''' imported module as object-container in context
    MB has internal module-context tree'''
    def __init__(self, name:str, ctx:ModuleContext):
        # self.module:ModuleInst = module
        self.name = name
        self.mcontext:ModuleContext = ctx
        self.inames = [] # imported names, if import module > names

    def importAll(self):
        nn = []
        nn.extend([n for n in self.mcontext.vars.keys()])
        nn.extend([n for n in self.mcontext.funcs.keys()])
        nn.extend([n for n in self.mcontext.types.keys()])
        self.inames = nn

    def importThing(self, name):
        self.inames.append(name)
    
    def hasImported(self, name):
        print('hasImported1', name)
        print('hasImported2', self.inames)
        return name in self.inames

    def get(self, name):
        if len(self.inames) > 0 and name not in self.inames:
            raise EvalErr(f'Trying use not imported name `{name}` from module `{self.name}`.')
        # print('ModuleBox.get(%s)' % name)
        return self.mcontext.get(name)

    def getName(self):
        return self.name

    def getType(self):
        return TypeModule()
    
    def print(self):
        print('ModuleBox(%s)' % self.name)
        for vv in self.inames:
            print(' ', vv)

    def __str__(self):
        return 'ModuleBox(%s)' % (self.name)
