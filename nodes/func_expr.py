
from collections.abc import  Callable

from vars import *
from nodes.expression import *


class Function(FuncInst):
    ''' user-defined function object 
    args:
        foo(a, b, c)
        func foo(arg1, arg2, arg3)
        blok:
            arg1 + arg2 + arg3
    '''

    def __init__(self, name):
        super().__init__()
        # self.argExpr:list[Expression] = None # like ListExpression: expr, expr, expr
        self.name = name
        self.vtype = TypeFunc
        self.argNum = 0
        self.argVars:list[Var] = []
        self.block:Block = None
        self.defCtx:Context = None # for future: definition context (closure - ctx of module or upper block if function is local or lambda)
        self.res = None

    def getName(self):
        return self.name

    def addArg(self, arg:Var):
        # if arg is None:
        #     raise EvalErr('!23')
        # if isinstance(arg, tuple):
            # for xx in arg:
            #     print('arg@@>', xx)
            # raise EvalErr('!22')
        self.argVars.append(arg)
        self.argNum += 1
        # print('Fuuu, addArg', arg, self.argNum)

    # TODO: flow-number arguments
    def setArgVals(self, args:list[Var]):
        nn = len(args)
        print('! argVars', ['%s'%ag for ag in self.argVars ], 'len=', len(self.argVars))
        print('! setArgVals', ['%s'%ag for ag in args ], 'len=', nn)
        if self.argNum != len(args):
            raise EvalErr('Number od args of fuction `%s` not correct. Exppected: %d, got: %d. ' % (self.name, self.argNum, len(args)))
        for i in range(nn):
            arg = args[i]
            print('set arg8  >> ', self.argVars[i], 'val:', arg)
            arg.name = self.argVars[i].name
            self.argVars[i] = arg
            # self.argVars[i].set(arg.get())

    def do(self, ctx: Context):
        self.res = None
        self.block.storeRes = True # save last expr value
        inCtx = Context(None) # inner context, empty new for each call
        # inCtx.addVar(Var(1000001, 'debVal', TypeInt))
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

    def __init__(self, name, src:str):
        super().__init__(name, src)
        self.name = name
        self.func:Function = None
        self.argExpr:list[Expression] = []

    def addArgExpr(self, exp:Expression):
        self.argExpr.append(exp)

    def do(self, ctx: Context):
        # inne rcontext
        print('FuncCallExpr.do')
        args:list[Var] = []
        self.func = ctx.get(self.name)
        if isinstance(self.func, VarUndefined):
            raise EvalErr(f'Function `{self.name}` can`t be found in current context.')
        print('#1# func-call do1: ', self.name, 'F:', self.func, 'line:', self.src)
        for exp in self.argExpr:
            # print('#1# func-call do2 exp=: ', exp)
            exp.do(ctx)
            # print('func-call do2:', exp, exp.get())
            args.append(exp.get())
        self.func.setArgVals(args)
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
        ''' arg Var(name, type)'''
        print('addArg1 :', arg, type(arg))
        if isinstance(arg, ServPairExpr):
            arg = arg.getTypedVar()
        self.argVars.append(arg)

    def add(self, exp:Expression):
        ''' collect inner sequence of expressions'''
        print('Func-Def-Exp. add ', exp)
        self.blockLines.append(exp)

    def doFunc(self, ctx:Context):
        func = Function(self.name)
        return func

    def regFunc(self, ctx:Context, func:FuncInst):
        ctx.addFunc(func)

    def do(self, ctx:Context):
        ''''''
        print('FuncDefExpr.do 1:', self.name, 'argExps:', self.argVars)
        func = self.doFunc(ctx)
        for arg in self.argVars:
            if isinstance(arg, TypedVarExpr):
                arg.do(ctx)
            print('FuncDefExpr.do 2:', arg)
            func.addArg(arg)
        func.block = Block()
        # build inner block of function
        for exp in self.blockLines:
            func.block.add(exp)
        self.res = func
        print('FuncDefExpr.do 3:', func.name)
        self.regFunc(ctx, func)
    
    def get(self)->Function:
        return self.res



class ReturnExpr(Expression):
    ''' '''
    def __init__(self):
        super().__init__()
        self.sub:Expression = None
        # self.val = None
        

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
    def __init__(self, name, rtype:VType=TypeAny()):
        super().__init__(name)
        self.callFunc:Callable = lambda *args : 1
        self.res:Var = None
        self.resType:VType = rtype

    def setArgVals(self, args:list[Var]):
        self.argVars = []
        for arg in (args):
            print('~NFsetA', arg)
            self.argVars.append(arg.get())

    def do(self, ctx: Context):
        args = []
        for arg in self.argVars:
            # print('#T arg = ', arg)
            a = arg
            if isinstance(arg, Var):
                a = arg.get()
            args.append(a)
        res = self.callFunc(*args)
        self.res = Val(res, self.resType)

    def get(self)->Var:
        return self.res

def setNativeFunc(ctx:Context, name:str, fn:Callable, rtype:VType=TypeAny):
    func = NFunc(name)
    func.resType = rtype
    func.callFunc = fn
    ctx.addFunc(func)

