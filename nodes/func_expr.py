
from collections.abc import  Callable

from vars import *
from nodes.expression import *
from nodes.keywords import *


class Function(FuncInst):
    ''' user-defined function object 
    args:
        call:
        foo(a, b, c)
        # def:
        func foo(arg1, arg2, arg3)
            # inner blok:
            arg1 + arg2 + arg3
    '''

    def __init__(self, name):
        super().__init__()
        # self.argExpr:list[Expression] = None # like ListExpression: expr, expr, expr
        self.isLambda = False
        if name is None:
            name = '@lambda'
            self.isLambda = True
        self._name = name
        self.vtype = TypeFunc()
        self.argNum = 0
        self.argVars:list[Var] = []
        self.argTypes:dict[str, VType] = {}
        self.callArgs = []
        self.block:Block = None
        self.defCtx:Context = None # for future: definition context (closure - ctx of module or upper block if function is local or lambda)
        self.res = None
        # print('Fuu.init', self)

    def setDefContext(self, ctx:Context):
        self.defCtx = ctx

    def getName(self):
        return self._name

    def addArg(self, arg:Var):
        self.argVars.append(arg)
        self.argTypes[arg.getName()] = arg.getType()
        self.argNum += 1

    # TODO: flow-number arguments
    def setArgVals(self, args:list[Val]):
        nn = len(args)
        # print('! argVars', ['%s'%ag for ag in self.argVars ], 'len=', len(self.argVars))
        # print('! setArgVals', ['%s'%ag for ag in args ], 'len=', nn)
        if self.argNum != len(args):
            # print('Number od args of fuction `%s` not correct. Exppected: %d, got: %d. ' % (self._name, self.argNum, len(args)))
            raise EvalErr('Number od args of fuction `%s` not correct. Exppected: %d, got: %d. ' % (self._name, self.argNum, len(args)))
        self.callArgs = []
        for i in range(nn):
            arg = args[i]
            aname = self.argVars[i].getName()
            self.checkArgType(aname, arg)
            # print('FN (%s), self.argVars[i]: ' % self._name, self.argVars[i], ' /:/', arg)
            atype = self.argVars[i].getType()
            argVar = Var(aname, atype)
            argVar.set(arg)
            # dprint('FN setArgVals-4: ', atype, aname)
            if isinstance(atype, TypeAny):
                argVar.setType(arg.getType())
            # print('set arg8  >> ', self.argVars[i], 'val:', arg)
            # arg.name = self.argVars[i].name
            self.callArgs.append(argVar)
            # self.argVars[i].set(arg.get())

    def checkArgType(self, name, val):
        '''Use val.getType() and types compatibility '''
        return True

    def do(self, ctx: Context):
        self.res = None
        self.block.storeRes = True # save last expr value
        inCtx = Context(self.defCtx) # inner context, empty new for each call
        # inCtx.addVar(Var(1000001, 'debVal', TypeInt))
        for arg in self.callArgs:
            dprint('Fu.do:', arg)
            inCtx.addVar(arg)
        # inCtx.get('debVal')
        # inCtx.upper = ctx
        self.block.do(inCtx)
        res = self.block.get()
        if isinstance(res, FuncRes):
            res = res.get()
        self.res = res

    def get(self)->Var:
        return self.res
        # return Val(self, TypeFunc())
    
    def __str__(self):
        if self.__class__.__name__ == 'NFunc':
            return 'func %s(???)' % (self._name)
        args = []
        # dprint('Func_str_. arg:', self.argVars)
        for arg in self.argVars:
            args.append('%s' % arg.name)
        return 'func %s(%s)' % (self._name, ', '.join(args))


class FuncCallExpr(Expression):
    ''' foo(agr1, 2, foo(3))  '''

    def __init__(self, strName = 'func', src:str=''):
        super().__init__(strName, src)
        self.name = strName
        self.funcExpr = None
        self.func:Function = None
        self.argExpr:list[Expression] = []

    def setFuncExpr(self, fexp:Expression):
        self.funcExpr = fexp

    def addArgExpr(self, exp:Expression):
        self.argExpr.append(exp)

    def do(self, ctx: Context):
        # inne rcontext
        args:list[Var] = []
        # print(f'Function `{self.name}`:', self.func)
        self.funcExpr.do(ctx)
        func = self.funcExpr.get()
        # unpack function from var
        # print('#1# func-call do00: ', self.name, 'F:', func)
        if isinstance(func, Var):
            func = func.get()
        if isinstance(func, TypeVal):
            tVal = func.getVal()
            if isinstance(tVal, TypeStruct):
                func = tVal.getConstr()
        # print('#1# func-call do01: ', self.name, 'F:', func)
        self.func = func
        if isinstance(self.func, VarUndefined):
            raise EvalErr(f'Function `{self.name}` can`t be found in current context.')
        # print('#2# func-call do02: ', self.name, 'F:', self.func, 'line:', self.src)
        for exp in self.argExpr:
            # dprint('#1# func-call do2 exp=: ', exp)
            exp.do(ctx)
            # print('func-call do2:', exp, exp.get())
            arg = exp.get()
            if isinstance(arg, Var):
                arg = arg.get()
            args.append(arg)
        # print('FCall.do.args:', self.name, args)
        self.func.setArgVals(args)
        callCtx = Context(None)
        self.func.do(callCtx)

    def get(self):
        return self.func.get()


class FuncDefExpr(ObjDefExpr, Block):
    ''' Expression of definition of function
        func foo(arg1, arg2)
            expr
            [return] expr
        make Function object
        make arg vars for internal context
        set Function to current context by name
        
    '''

    def __init__(self, name):
        # dprint('FuncDefExpr.__inint 1:', name)
        self.name = name
        self.res:Function
        self.blockLines:list[Expression] = []
        self.argVars:list[Var] = []
        # self.signExp:Expression = None # func signature : name (arg set) ???

    def addArg(self, arg:VarExpr):
        ''' arg Var(name, type)'''
        # dprint('addArg1 :', arg, type(arg))
        if isinstance(arg, ServPairExpr):
            arg = arg.getTypedVar()
            # print('FDef.addArg11 :', arg, arg.right)
        # print('FDef.addArg2 :', arg, type(arg))
        self.argVars.append(arg)

    def add(self, exp:Expression):
        ''' collect inner sequence of expressions'''
        dprint('Func-Def-Exp. add ', exp)
        self.blockLines.append(exp)

    def doFunc(self, ctx:Context):
        func = Function(self.name)
        return func

    def regFunc(self, ctx:Context, func:FuncInst):
        fname = func.getName()
        # check if name is type
        strtype:TypeStruct = ctx.getType(fname)
        # print('regFunc1', fname, strtype)
        if isinstance(strtype, TypeVal):
            strtype = strtype.getVal()
        if strtype is not None and isinstance(strtype, TypeStruct):
            strtype.setConstr(func)
            return
        ctx.addFunc(func)

    def do(self, ctx:Context):
        ''''''
        func = self.doFunc(ctx)
        # print('FuncDefExpr.do 1:', self.name, 'argExps:', self.argVars)
        for arg in self.argVars:
            if isinstance(arg, TypedVarExpr):
                arg.do(ctx)
            func.addArg(arg.get())
        func.block = Block()
        # build inner block of function
        for exp in self.blockLines:
            func.block.add(exp)
        func.setDefContext(ctx)
        self.res = func
        dprint('FuncDefExpr.do 3:', func.getName())
        if not func.isLambda:
            self.regFunc(ctx, func)
    
    def get(self)->Function:
        return self.res



class NFunc(Function):
    ''' '''
    def __init__(self, name, rtype:VType=TypeAny()):
        super().__init__(name)
        self.callFunc:Callable = lambda *args : 1
        self.res:Val = None
        self.resType:VType = rtype

    def setArgVals(self, args:list[Var]):
        self.argVars = []
        for arg in (args):
            dprint('~NFsetA', arg)
            if isinstance(arg, Var):
                arg = arg.get()
            self.argVars.append(arg)

    def do(self, ctx: Context):
        args = []
        for arg in self.argVars:
            dprint('#T arg = ', arg)
            a = arg
            args.append(a)
        res = self.callFunc(ctx, *args)
        # if isinstance(res, Var):
        #     res = res.get()
        if not isinstance(res, Val):
            # not Val, Not ListVal, etc.
            res =  Val(res, self.resType)
        self.res = res

    def get(self)->Val:
        return self.res

def setNativeFunc(ctx:Context, name:str, fn:Callable, rtype:VType=TypeAny):
    func = NFunc(name)
    func.resType = rtype
    func.callFunc = fn
    ctx.addFunc(func)

