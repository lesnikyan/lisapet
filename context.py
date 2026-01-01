
'''
Execution context. General container of values.
Contains:
    Values of variables.
    Function objects.
    DataTypes (planned for `struct` type definition).
Each execution block has own context which is passed from parent block.
Current context can find var|func name up to root context (module).
'''

import lang
from vars import *


'''
# by arg count
self.overs = {
    0: foo()
    2: foo(a, b)
    3: foo(a,b,c)
}
# then by arg types
self.overs = {
    1:{
        int: foo(int)
        float: foo(float)
    },
    2: {
        int_float: foo(int, float),
        string_int: foo(string, int)
    }
}
'''
class FuncOverSet:
    def __init__(self, name):
        # print('F-Over--Init', name)
        self.name = name
        self.overs = {}

    def add(self, func:FuncInst):
        # put by count
        count = func.argCount()
        # print('FOver.add', self.name, count, self.overs)
        if count not in self.overs:
            # 1 added before
            self.overs[count] = func
    
    def get(self, argSet=list):
        '''
        :param argSet: like [int, float, string]
        '''
        count = len(argSet)
        # print('44#>>', count, count in self.overs, self.overs.keys())
        if count in self.overs:
            byCount = self.overs[count]
            if isinstance(byCount, FuncInst):
                return byCount
            # next - search by types
        
        return None


class Context(NSContext):
    def __init__(self, parent:'Context'=None):
        self.vars:dict = dict()
        self.types:dict[str, TypeProperty] = {}
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
        dprint('ctx.addType: ', tp, '::', type(tp))
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
        # print('>>>>>>> :tp:', tp)
        tprop = TypeProperty(tp, FuncBinder(tp.get()))
        self.types[name] = tprop

    def getType(self, name)->VType:
        tp = self.find(name)
        if isinstance(tp, TypeProperty):
            return tp.type
        return tp

    def addSet(self, vars:Var|dict[str,Var]):
        if not isinstance(vars, dict):
            vars = {vars.name: vars}
        self.vars.update(vars)
        
    def update(self, name, val:Var):
        # dprint('x.update ====> :', name, val.get(), val.getType().__class__.__name__)
        src = self
        while True:
            # dprint('#Ctx-upd,name:', name)
            # dprint('#Ctx-upd2', src.vars)
            if name in src.vars:
                # dprint('x.upd:found', name)
                val.name = name
                src.vars[name] = val
                # src.vars[name].set(val.get())
            if src.upper is None:
                # dprint('-- src.upper == None --', name, val)
                val.name = name
                self.addVar(val)
                break
            src = src.upper

    def addFunc(self, fn:FuncInst):
        name = fn.getName()
        # print('x.addFunc ===>  name:', name, ' var: ', fn)
        # fcont = self.funcs
        # instName = name # intername name for search instance
        if name not in self.funcs:
            self.funcs[name] = fn
            return
        # extName = f'{name}@$overs' # name of overloaded funcs
        # self.funcs[extName] = {}
        exist = self.funcs[name]
        if isinstance(exist, FuncInst):
            # start overloading
            overSet = FuncOverSet(name)
            overSet.add(exist)
            overSet.add(fn)
            self.funcs[name] = overSet
            return
        elif isinstance(exist, FuncOverSet):
            exist.add(fn)
    
    def addTypeMethod(self, typeName, func:FuncInst):
        typeVal = self.getType(typeName)
        xtype:TypeStruct|FuncBinder = typeVal.get()
        dprint('**addTypeMethod', typeName, xtype, func)
        if not isinstance(xtype, TypeStruct):
            raise EvalErr('Strange  type fpund by name `%s`' % typeName, xtype)
        xtype.addMethod(func)

    def bindTypeMethod(self, typeName, func:FuncInst):
        tp = self.findIn(typeName)
        if not isinstance(tp, TypeProperty):
            raise EvalErr("Incorrect name %s of type to bind method." % typeName)
        tp.funcs.addMethod(func)

    def addVar(self, varName:Var|str, vtype:VType=None):
        # dprint('x.addVar0 >> var:', varName, varName.name)
        var = varName
        name = varName
        # dprint('x.addVar1 ====> :', varName, varName.__class__.__name__, vtype, vtype.__class__.__name__)
        if isinstance(varName, str):
            var = Var(varName, vtype)
        else:
            name = var.name
        # print('x.addVar2: ', name, var)
        self.vars[name] = var
        # self.addSet({name:var})

    def get(self, name)->Base:
        res = self.find(name)
        if isinstance(res, TypeProperty):
            res = res.type
        return res

    def findIn(self, name):
        src = self
        # print('## --- ', name,  src, '\n', src.vars)
        if name in src.vars:
            return src.vars[name]
        if name in src.types:
            return src.types[name]
        if name in src.funcs:
            # dprint('CTX.find func ?', name, src.funcs[name].__class__.__name__)
            # if src.funcs[name].__class__.__name__ != 'NFunc':
                # dprint('CTX.find func:`%s`' % name, '::', src.funcs[name])
            return src.funcs[name]

        return None

    def find(self, name):
        src = self
        # print('#Ctx.find,:', name)
        while src is not None:
            # print('ctx cur types:', src.types.keys())
            res = src.findIn(name)
            # print('Ctx.find res=', res)
            if res:
                # print('Ctx.find : Found!')
                return res
            if src.upper is None:
                # raise EvalErr('Can`t find var|type name `%s` in current context' % name)
                var = VarUndefined(name)
                return var
            src = src.upper

    def print(self, ind=0, forsed=0):
        # return
        if not lang.FullPrint and not forsed:
            return
        c:Context = self
        while c:
            ttt = ['vars', 'types', 'funcs']
            iii = 0
            for data in [c.vars, c.types, c.funcs]:
                print('.' * ind, '  > ', ttt[iii])
                iii += 1
                for k, v in data.items():
                    if isinstance(v, TypeProperty):
                        v = v.type
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
        # print('mctx.findIn:', name)
        if name in self.aliases:
            name = self.aliases[name]
        res = super().findIn(name)
        # print('MC.findIn ## 1:', name, res)
        if res is not None:
            return res
        # find module
        # print('#-imported', [k for k in self.imported.keys()])
        if name in self.imported:
            # print('MC findIn', name)
            return self.imported[name]
        # find in modules
        for k, mbox in self.imported.items():
            if mbox.hasImported(name):
                dprint('has', name, ' in ', k)
                return mbox.get(name)
        # Nothing was found
        # print('findIn ## 2:', res)
        return None

    # def getType(self, name):
    #     tt = self.find(name)
    #     # print('Mctx.GetType : ', tt)
    #     if tt:
    #         return tt
        # raise EvalErr('ModCtx getType')
        

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
        dprint('hasImported1', self.name, ':', name)
        dprint('hasImported2', self.inames)
        return name in self.inames

    def get(self, name):
        if len(self.inames) > 0 and name not in self.inames:
            raise EvalErr(f'Trying use not imported name `{name}` from module `{self.name}`.')
        # dprint('ModuleBox.get(%s)' % name)
        return self.mcontext.get(name)

    def getName(self):
        return self.name

    def getvType(self):
        return TypeModule()

    def getType(self, name):
        dprint('ModuleBox', self.name)
        return self.mcontext.getType(name)
    
    def print(self):
        dprint('ModuleBox(%s)' % self.name)
        for vv in self.inames:
            dprint(' ', vv)

    def __str__(self):
        return 'ModuleBox(%s)' % (self.name)
