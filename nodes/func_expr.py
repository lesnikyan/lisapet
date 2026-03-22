
from collections.abc import  Callable

from vars import *
from bases.ntype import *
from nodes.expression import *
from nodes.keywords import *
from nodes.base_oper import AssignExpr
from nodes.oper_dot import ObjectMember
from objects.func import Function, ObjMethod

import inspect


class FuncCallExpr(CallExpr):
    ''' foo(agr1, 2, foo(3))  '''

    def __init__(self, strName = 'func', src:str=''):
        super().__init__(strName, src)
        self.name = strName
        self.res = None
        self.funcExpr = None
        self.func:Function = None
        self.argExpr:list[Expression] = []

    def setFuncExpr(self, fexp:Expression):
        self.funcExpr = fexp

    def addArgExpr(self, exp:Expression):
        self.argExpr.append(exp)

    def doArgs(self, args:list, ctx: Context):
        named = {}
        for exp in self.argExpr:
            # print('F.call() #1#',self.name,' do2 exp=: ', exp)
            
            if isinstance(exp, AssignExpr):
                varExp = exp.left # arg name
                if not isinstance(varExp, VarExpr):
                    raise EvalErr("Func named arg has incorrect type of name")
                argName = varExp.name
                valExp = exp.right
                valExp.do(ctx)
                named[argName] = valExp
                continue
            if len(named) != 0:
                # if not variadic args part:
                # if len(args) >= func.argNum and not func.extOrdered:
                raise EvalErr("Attempt to use ordered agr after named")
            valExp = exp
                
            valExp.do(ctx) # val or vaiable
            arg = valExp.get()
            
            
            if isinstance(exp, ArgExtList):
                vv = var2val(arg)
                for n in vv.elems:
                    args.append(var2val(n))
                continue
            
            if isinstance(arg, (Var, CollectElem)):
                arg = arg.get()
            elif isinstance(arg, (ObjectMember)):
                arg = arg.get(ctx)
            
            # print('func-call do2:', valExp, arg)
            args.append(arg)
        return args, named

    def takeFunc(self, ctx: Context):
        args:list[Var] = []
        # Get function object
        self.funcExpr.do(ctx)
        func:Function|FuncOverSet = self.funcExpr.get()
        # Here and next we can get one of: 
        # Var, Function, NFunc, BoundMethod, FuncOverSet, ObjectMember, ObjMethod
        # print('FC/1', func)
        
        # Case with func in var
        if isinstance(func, Var):
            func = func.get()
        # print(f'\nF() expr:', self.funcExpr, 'func:', func )
        
        objInst = None
        
        # Case of calling member of object / module
        if isinstance(func, ObjectMember):
            objMem:ObjectMember = func
            objInst = objMem.object
            memVal = func.get(ctx)
            func = memVal
            # print('F.func: ObjectMember', obj, func)
        
        # ObjMethod can be found by any expr: 
        method:ObjMethod = None
        #   1) obj.member, 2) var/arg, 3) collection elem, func call result,   
        if isinstance(func, ObjMethod):
            # method but not a function object in the field of struct
            method = func
            # next we need Function to resolve overload case
            func = method.func
            objInst = method.obj
            args.append(objInst)
        
        if isinstance(func, BoundMethod):
            method = func
            args.append(objInst)
        
        args, named = self.doArgs(args, ctx)
        if isinstance(func, TypeVal):
            tVal = func.getVal()
            if isinstance(tVal, TypeStruct):
                func = tVal.getConstr()
            elif 1:
                cc = ctx.getRoot()
                ctype = func.get()
                constrName = typeConstrName(ctype)
                func = cc.get(constrName)
        
        # Case with overloaded function
        if isinstance(func, FuncOverSet):
            # overloaded set
            over:FuncOverSet = func
            callArgTypes = [ar.getType() for ar in args]
            # print('callArgTypes:', [f'{n.__class__.__name__}:{n.hash()}' for n in callArgTypes])
            func = over.get(callArgTypes)
            if not func:
                errMsg = f"Can't find overloaded function {self.name} with args = ({','.join([f'{n.__class__.__name__}' for n in callArgTypes])}) "
                raise EvalErr(errMsg)
            
        if not isinstance(func, Function):
            raise EvalErr(f'Function `{self.name}` can`t be found in current context.')
        
        func.objInst = objInst
        return func, args, named

    def do(self, ctx: Context):
        func, args, named = self.takeFunc(ctx)
        self.func = func
        # print('#3# func-call do05: ', self.name, 'F:', func, args)
        # print('#2# func-call do02: ', self.name, 'F:', self.func, 'line:', self.src)
        # print('F.call.do/1', func, args, named)
        self.func.setArgVals(args, named)
        callCtx = Context(None)
        # if len(inspect.stack(0)) > 40 : # debug stop by stack depth
        #     print('len(inspect.stack(0)) >>> ', len(inspect.stack(0)))
        #     raise EvalErr(f'DEBUG {self.name}')
        
        self.func.do(callCtx)
        self.res = self.func.get()
        self.func.objInst = None

    def get(self):
        # print('F.get', self.name, '=', self.func.get())
        return self.res


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
        self.name = name
        self.res:Function
        self.blockLines:list[Expression] = []
        self.argVars:list[Var] = []
        self.defValCount = 0
        self.fullIdent = name
        # self.signExp:Expression = None # func signature : name (arg set) ???

    def addArg(self, arg:VarExpr):
        ''' arg Var(name, type)'''
        defVal = None
        
        # x:int = 1
        if isinstance(arg, AssignExpr):
            defVal = arg.right
            arg = arg.left
        # x : int
        if isinstance(arg, ServPairExpr):
            arg = arg.getTypedArg()
        # x
        if not isinstance(arg, (TypedArgExpr, ArgExtList, ArgExtDict)):
            arg = ArgExpr(arg.val)
            
        # if defVal is not None:
        arg.defVal = defVal
        self.argVars.append(arg)

    def add(self, exp:Expression):
        ''' collect inner sequence of expressions'''
        dprint('Func-Def-Exp. add ', exp)
        self.blockLines.append(exp)

    def doFunc(self, ctx:Context):
        # print('\nFDef.doF', self.name)
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
        # here we need local context for correct init of arg types
        argCtx = Context(ctx)
        for arg in self.argVars:
            # print('FDef.do#1', arg)
            if isinstance(arg, TypedArgExpr):
                arg.do(argCtx)
            # print('-> addArg', arg.get(), arg.defVal)
            func.addArg(arg.get(), arg.defVal)
        func.block = Block()
        # build inner block of function
        for exp in self.blockLines:
            func.block.add(exp)
        func.setDefContext(ctx)
        self.res = func
        if not func.isLambda:
            self.regFunc(ctx, func)
    
    def get(self)->Function:
        return self.res



class NFunc(Function):
    ''' '''
    def __init__(self, name, fn:Callable=None, rtype:VType=TypeAny()):
        super().__init__(name)
        self.callFunc:Callable = fn
        self.res:Val = None
        if fn:
            sign = inspect.signature(fn)
            self.argNum = len(sign.parameters) - 1 # except 1st arg - context
        self.resType:VType = rtype

    def copy(self, defCtx:Context):
        r = NFunc(self._name, self.callFunc)
        r.callFunc = self.callFunc
        r.resType = self.resType
        r.setDefContext(defCtx)

    def setArgVals(self, args:list[Var], named:dict={}):
        self.argVars = []
        for arg in (args):
            if isinstance(arg, Var):
                arg = arg.get()
            self.argVars.append(arg)

    def do(self, ctx: Context):
        args = []
        for arg in self.argVars:
            args.append(arg)
        inCtx = Context(self.getDefContext())
        # print('NF', args, self.callFunc)
        res = self.callFunc(inCtx, *args)
        if not isinstance(res, Val):
            # not Val, Not ListVal, etc.
            res =  Val(res, self.resType)
        self.res = res

    def get(self)->Val:
        return self.res


class ComposedFunc(NFunc):
    '''
    composed = foo * bar * baz
    '''
    def __init__(self):
        name = 'composed_%x' % hash(self)
        super().__init__(name, None)
        self.funcs:list[Function] = []

    def add(self, func:Function):
        self.funcs.append(func)

    def do(self, ctx: Context):
        arg = self.argVars[0]
        rval = None
        for i in range(len(self.funcs) -1, -1 , -1):
            fn = self.funcs[i]
            # print('CmF.do2', fn, fn.__class__)
            args = []
            if isinstance(fn, (ObjMethod, BoundMethod)):
                args.append(fn.getInst())
            args.append(arg)
            inCtx = Context(fn.getDefContext())
            fn.setArgVals(args)
            fn.do(inCtx)
            rval = fn.get()
            arg = rval
            
        self.res = rval


def coverFunc(name:str, fn:Callable, rtype:VType=TypeAny):
    func = NFunc(name, fn)
    func.resType = rtype
    # func.callFunc = fn
    return func


def setNativeFunc(ctx:Context, name:str, fn:Callable, rtype:VType=TypeAny):
    func = NFunc(name, fn)
    func.setDefContext(ctx)
    func.resType = rtype
    # func.callFunc = fn
    ctx.addFunc(func)


def typeConstrName(rtype:VType):
    tname = rtype.name
    return f'{tname}#construct'

def addTypeConstr(ctx:Context, fn:Callable, rtype:VType):
    setNativeFunc(ctx, typeConstrName(rtype), fn, rtype)
    

class BoundMethod(NFunc,MethodOfType):
    
    def __init__(self, func:FuncCallExpr, fname, rtype = TypeAny()):
        super().__init__(fname, func, rtype)
        self.callArgs:list[Expression] = []

    def instCase(self, inst):
        return InstBMethod(inst, self)

    def __str__(self):
        return 'func %s(???)' % (self._name)


class InstBMethod(BoundMethod):
    def __init__(self, inst, meth:BoundMethod):
        super().__init__(meth.callFunc, meth._name, meth.resType)
        self.inst = inst

    def getInst(self):
        return self.inst


def bindNativeMethod(ctx:Context, typeName, fn, fname, rtype:VType=None):
    if rtype is None:
        rtype = TypeAny
    # print('BM fn name:', fname)
    func = BoundMethod(fn, fname)
    func.setDefContext(ctx)
    func.resType = rtype
    ctx.bindTypeMethod(typeName, func)


class MethodDefExpr(FuncDefExpr):
    ''' '''
    def __init__(self, name):
        super().__init__(name)
        self.instExpr:Expression = None
        self.typeName = None

    def setInst(self, exp:ServPairExpr):
        self.instExpr = exp.getTypedVar()

    def doFunc(self, ctx):
        func = Function(self.name)
        self.instExpr.do(ctx)
        inst = self.instExpr.get()
        # dprint('MethodDefExpr.doFunc', inst, self.name)
        self.typeName = inst.getType().getName()
        # dprint('MethodDefExpr doFunc:', self.instExpr, self.instExpr.get())
        func.addArg(self.instExpr.get())
        return func

    def regFunc(self, ctx:Context, func:FuncInst):
        ctx.addTypeMethod(self.typeName, func)

    def do(self, ctx:Context):
        '''''' 
        super().do(ctx)

