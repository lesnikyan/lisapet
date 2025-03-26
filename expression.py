'''
Base expression objects.
'''
from collections.abc import  Callable

from vars import *

class Expression:
    def __init__(self, val=None):
        self.val = val
        self.block = False
    
    def do(self, ctx:Context):
        pass
    
    def get(self) -> Var|list[Var]:
        return self.val
    
    def isBlock(self)->bool:
        ''' True if one of: func, for, if, match, case'''
        return False
    
    def __str__(self):
        return self.__class__.__name__

class CommentExpr(Expression):
    ''' for future usage'''
    def __init__(self, text:str):
        '''' text of comment line is value '''
        super().__init__(text)

class ValExpr(Expression):
    def __init__(self, var:Var):
        # print('#tn2-valEx:', var, var.get())
        self.val = var
    
    def do(self, ctx:Context):
        pass

    def get(self)->Var:
        # print('#tn2-valEx-get:', self.val, self.val.get())
        return self.val
    
    def __str__(self):
        return 'ValExpr(%s)' % self.val


class DebugExpr(Expression):
    def __init__(self, txt):
        print('**** DEBUG__init:', txt)
        self.val = txt
    
    def do(self, ctx:Context):
        print(" $$$ DEBUG: ", self.val)

class VarExpr(Expression):
    def __init__(self, var:Var):
        self.val = var # or name,type ?
        self.name = var.name
    
    def do(self, ctx:Context):
        newVal = ctx.get(self.name)
        print('#tn3:', newVal)
        self.val = newVal
    
    # def set(self, val:Var):
    #     self.var = val.get()

    def get(self)->Var:
        return self.val

    def __str__(self):
        return 'VarExpr(%s)' % (self.name)

class VarExpr_(VarExpr):
    def __init__(self, var:Var):
        self.name = '_'
    
    def do(self, ctx:Context):
        ''' nothing to do'''

    def get(self)->None:
        ''' nothing to do'''

    def set(self, x):
        ''' nothing to do'''

    def __str__(self):
        return 'VarExpr_(_)'
    

# class Command(Expression):
#     def do(self, var:Var, src:Expression):
#         pass
    
#     def get(self):
#         return self.val


class Block(Expression):
    def __init__(self):
        self.ctx = Context()
        self.subs: list[Expression] = []
        self.storeRes = False
        self.lastVal:Var|list[Var] = None # result of last sequence, can be a list if many results: a, b, [1,2,3]
    
    def add(self, seqs:Expression|list[Expression]):
        if not isinstance(seqs, list):
            seqs = [seqs]
        self.subs.extend(seqs)
    
    def isEmpty(self):
        return len(self.subs)

    def do(self, ctx:Context):
        self.lastVal = None
        # eval sequences one by one, store result of each line, change vars in contexts
        elen = len(self.subs)
        if elen < 1:
            return
        lastInd = 0
        self.ctx.upper = ctx
        # print('!! Block.do')
        lastVal = None
        for i in range(elen):
            # print('!! Block.iter ', i, self.subs[i])
            expr = self.subs[i]
            expr.do(ctx)
            lastInd = i
            lineRes = None
            if not isinstance(expr, Block) or expr.storeRes:
                lineRes = expr.get()
            if isinstance(lineRes, FuncRes):
                # return expr
                self.lastVal = lineRes
                return
        if self.storeRes:
            self.lastVal = self.subs[lastInd].get()

    def get(self) -> list[Var]:
        return self.lastVal
    
    def isBlock(self)->bool:
        ''' True if one of: func, for, if, match, case'''
        return True


class LoopBlock(Block):
    ''' '''

class CollectionExpr(Expression):
    ''''''
    def addVal(self, val:Var):
        pass
    
    def setVal(self, index:Var, val:Var):
        pass

    def getVal(self, index:Var):
        pass


class CollectElemExpr(Expression):
    
    def __init__(self):
        self.target:Collection = None
        self.varExpr:Expression = None
        self.keyExpr = None
        
    def setVarExpr(self, exp:Expression):
        self.varExpr = exp

    def setKeyExpr(self, exp:Expression):
        self.keyExpr = exp

    def do(self, ctx:Context):
        self.target = None
        self.varExpr.do(ctx) # before []
        self.target = self.varExpr.get() # found collection
        # print('## self.target', self.target)
        self.keyExpr.do(ctx) #  [ into ]

    def set(self, val:Var):
        ''' '''
        key = self.keyExpr.get()
        self.target.setVal(key, val)

    def get(self)->Var:
        key = self.keyExpr.get()
        elem = self.target.getVal(key)
        return elem

class TypeExpr(Expression):
    ''' int, string, bool, list, struct '''
    
    def __init__(self, val=None):
        # super().__init__(val)
        self.type:VType = Undefined
    
    def do(self, ctx:Context):
        ''' '''
    
    def get(self)->VType:
        ''' return '''

class DeclarationExpr(Expression):
    ''' var:type declaration '''
    
    def __init__(self):
        # super().__init__(val)
        self.var:Var = None
        self.varExpr:VarExpr = None
        self.typeExpr:TypeExpr = None
    
    def do(self, ctx:Context):
        self.typeExpr.do(ctx)
        self.var = self.varExpr.do(ctx)
        self.var.setType(self.typeExpr.get())
    
    def get(self)->Var:
        ''' return '''

class DefinitionExpr(Expression):
    ''' base for struct, function, alias
        func foo(arg1, arg2)
            expr
            expr

        struct User
            name: string
            age: int
            address: Address
    '''


class Function(FuncInst):
    ''' user-defined function object 
    args:
        foo(a, b, c)
        func foo(arg1, arg2, arg3)
        blok:
            arg1 + arg2 + arg3
    '''

    def __init__(self, name):
        super().__init__(None)
        # self.argExpr:list[Expression] = None # like ListExpression: expr, expr, expr
        self.name = name
        self.vtype = TypeFunc
        self.argNum = 0
        self.argVars:list[Var] = []
        self.block:Block = None
        self.defCtx:Context = None # for future: definition context (closure - ctx of module or upper block if function is local or lambda)
        self.res = None

    def addArg(self, arg:Var):
        self.argVars.append(arg)
        self.argNum += 1
        # print('Fuuu, addArg', arg, self.argNum)

    # TODO: flow-number arguments
    def setArgVals(self, args:list[Var]):
        if self.argNum != len(args):
            raise EvalErr('Number od args of fuction `%s` not correct. Exppected: %d, got: %d. ' % (self.name, self.argNum, len(args)))
        nn = len(args)
        for i in range(nn):
            arg = args[i]
            arg.name = self.argVars[i].name
            self.argVars[i] = arg
            # self.argVars[i].set(arg.get())

    def do(self, ctx: Context):
        self.res = None
        self.block.storeRes = True # save last expr value
        inCtx = Context(None) # inner context, empty new for each call
        inCtx.addVar(Var(1000001, 'debVal', TypeInt))
        for arg in self.argVars:
            # print('Fudo:', arg)
            inCtx.addVar(arg)
        inCtx.get('debVal')
        inCtx.upper = ctx
        self.block.do(inCtx)
        res = self.block.get()
        if isinstance(res, FuncRes):
            res = res.get()
        self.res = res

    def get(self)->Var:
        return self.res


class FuncCallExpr(Expression):
    ''' foo(agr1, 2, foo(3))  '''

    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.func:Function = None
        self.argExpr:list[Expression] = []

    def addArgExpr(self, exp:Expression):
        self.argExpr.append(exp)

    def do(self, ctx: Context):
        # inne rcontext
        args:list[Var] = []
        self.func = ctx.get(self.name)
        # print('#1# func-call do: ', self.name, self.func)
        for exp in self.argExpr:
            exp.do(ctx)
            print('FCdo:', exp, exp.get())
            args.append(exp.get())
        self.func.setArgVals(args)
        # TODO: add usage of Definishion Context instead of None
        callCtx = Context(ctx)
        self.func.do(callCtx)

    def get(self):
        return self.func.get()


class FuncDefExpr(DefinitionExpr, Block):
    ''' Expression of definition of function
        func foo(arg1, arg2)
            expr
            [return] expr
        make Function object
        make arg vars for internal context
        set Function to current context by name
        
    '''

    def __init__(self, name):
        # print('FuncDefExpr.__inint 1:', name)
        self.name = name
        self.res:Function
        self.blockLines:list[Expression] = []
        self.argVars:list[Var] = []
        self.signExp:Expression = None # func signature : name (arg set) ???

    def addArg(self, arg:VarExpr):
        ''' arg Var(noval|default, name, type)'''
        self.argVars.append(arg.get())

    def add(self, exp:Expression):
        ''' collect inner sequence of expressions'''
        print('Func-Def-Exp. add ', exp)
        self.blockLines.append(exp)
    
    def do(self, ctx:Context):
        ''''''
        # print('FuncDefExpr.do 1:', self.name)
        func = Function(self.name)
        for arg in self.argVars:
            func.addArg(arg)
        func.block = Block()
        # build inner block of function
        for exp in self.blockLines:
            func.block.add(exp)
        self.res = func
        # print('FuncDefExpr.do 2:', func.name)
        
        ctx.addFunc(func)
    
    def get(self)->Function:
        return self.res


class ReturnExpr(Expression):
    ''' '''
    def __init__(self):
        self.sub:Expression = None
        self.val = None
        

    def setSub(self, exp:Expression):
        ''' sub expr '''
        self.sub = exp

    def do(self, ctx:Context):
        ''' eval sub'''
        self.sub.do(ctx)
        self.val = FuncRes(self.sub.get())

    def get(self) -> Var|list[Var]:
        return self.val


class NFunc(Function):
    ''' '''
    def __init__(self, name):
        super().__init__(name)
        self.callFunc:Callable = lambda *args : 1
        self.res:Var = None
        self.resType:VType = TypeNull

    def setArgVals(self, args:list[Var]):
        self.argVars = []
        for arg in (args):
            # print('~NFsetA', arg)
            self.argVars.append(arg.get())

    def do(self, ctx: Context):
        args = []
        for arg in self.argVars:
            # print('#T arg = ', arg)
            args.append(arg)
        res = self.callFunc(*args)
        self.res = value(res, self.resType)

    def get(self)->Var:
        return self.res

def setNativeFunc(ctx:Context, name:str, fn:Callable, rtype:VType=TypeNull):
    func = NFunc(name)
    func.resType = rtype
    func.callFunc = fn
    ctx.addFunc(func)


