
from collections.abc import  Callable

from vars import *
from nodes.expression import *
from nodes.keywords import *
from bases.ntype import *
from nodes.base_oper import AssignExpr
from nodes.oper_dot import ObjectMember
from objects.func import Function

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
        # print('FCall.setFuncExpr')
        self.funcExpr = fexp

    def addArgExpr(self, exp:Expression):
        self.argExpr.append(exp)

    def doArgs(self, args:list, ctx: Context):
        named = {}
        for exp in self.argExpr:
            # print('-- #1#',self.name,' func-call do2 exp=: ', exp)
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
            if isinstance(arg, Var):
                arg = arg.get()
            # print('func-call do2:', valExp, arg)
            args.append(arg)
        return args, named

    def do(self, ctx: Context):
        args:list[Var] = []
        
        # Get function object
        self.funcExpr.do(ctx)
        func:Function|FuncOverSet = self.funcExpr.get()
        # print(f'\nF() expr:', self.funcExpr, 'func:', func )
                
        # Case of calling member of object / module
        if isinstance(func, ObjectMember):
            obj:ObjectMember = func
            memVal = func.get(ctx)
            # print('objMem val=', memVal)
            func = memVal
            # print('F.do: ObjectMember', obj, func)
            inst = obj.getInst()
            args.append(inst)
            
        '''
        # print(f'\nFunction `{self.name}`:', self.func)
        # named = {}
        # for exp in self.argExpr:
        #     # print('-- #1#',self.name,' func-call do2 exp=: ', exp)
        #     if isinstance(exp, AssignExpr):
        #         varExp = exp.left # arg name
        #         if not isinstance(varExp, VarExpr):
        #             raise EvalErr("Func named arg has incorrect type of name")
        #         argName = varExp.name
        #         valExp = exp.right
        #         valExp.do(ctx)
        #         named[argName] = valExp
        #         continue
        #     if len(named) != 0:
        #         # if not variadic args part:
        #         # if len(args) >= func.argNum and not func.extOrdered:
        #         raise EvalErr("Attempt to use ordered agr after named")
        #     valExp = exp
                
        #     valExp.do(ctx) # val or vaiable
        #     arg = valExp.get()
        #     if isinstance(arg, Var):
        #         arg = arg.get()
        #     # print('func-call do2:', valExp, arg)
        #     args.append(arg)
        '''
        
        args, named = self.doArgs(args, ctx)

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
                
        # Case with func in var
        if isinstance(func, Var):
            func = func.get()
        if isinstance(func, TypeVal):
            tVal = func.getVal()
            if isinstance(tVal, TypeStruct):
                func = tVal.getConstr()
        
        self.func = func
        # print('#3# func-call do05: ', self.name, 'F:', func)
        # print('#2# func-call do02: ', self.name, 'F:', self.func, 'line:', self.src)
        if not isinstance(self.func, Function):
            raise EvalErr(f'Function `{self.name}` can`t be found in current context.')
        self.func.setArgVals(args, named)
        callCtx = Context(None)
        # if len(inspect.stack(0)) > 40 :
        #     print('len(inspect.stack(0)) >>> ', len(inspect.stack(0)))
        #     raise EvalErr(f'DEBUG {self.name}')
        
        self.func.do(callCtx)
        self.res = self.func.get()

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
        # print('FuncDefExpr.__inint 1:', name)
        self.name = name
        self.res:Function
        self.blockLines:list[Expression] = []
        self.argVars:list[Var] = []
        self.defValCount = 0
        self.fullIdent = name
        # self.signExp:Expression = None # func signature : name (arg set) ???

    def addArg(self, arg:VarExpr):
        ''' arg Var(name, type)'''
        # print('FDef.addArg1 :', arg, type(arg))
        defVal = None
        
        # x:int = 1
        if isinstance(arg, AssignExpr):
            # print('Fdef3:', arg.left, arg.right)
            defVal = arg.right
            arg = arg.left
            # print('FDef.addArg2 :', arg, type(arg))
        # x : int
        if isinstance(arg, ServPairExpr):
            arg = arg.getTypedArg()
            # print('FDef.addArg11 :', arg, arg.left, ':', arg.right)
        # x
        if not isinstance(arg, (TypedArgExpr, ArgExtList, ArgExtDict)):
            # print('FDef.addArg#4', arg)
            arg = ArgExpr(arg.val)
            
        # if defVal is not None:
        arg.defVal = defVal
        
        # print('FDef.addArg1 :', arg.name, argType.name)
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
        # funcXname(func)
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
        # here we need local context for correct init of arg types
        argCtx = Context(ctx)
        for arg in self.argVars:
            # print('FDef.do#1', arg)
            argType = TypeAny()
            aName = arg.name
            if isinstance(arg, TypedArgExpr):
                arg.do(argCtx)
                # print('FDef.addArg11 :', arg, aName, argType.name)
            # if isinstance(arg, ArgExtList):
            #     print('##2')
                
            func.addArg(arg.get(), arg.defVal)
        func.block = Block()
        # build inner block of function
        for exp in self.blockLines:
            func.block.add(exp)
        func.setDefContext(ctx)
        self.res = func
        # dprint('FuncDefExpr.do 3:', func.getName())
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

    def setArgVals(self, args:list[Var], named:dict={}):
        self.argVars = []
        for arg in (args):
            # print('~NFsetA', self.getName(), arg)
            if isinstance(arg, Var):
                arg = arg.get()
            self.argVars.append(arg)

    def do(self, ctx: Context):
        args = []
        for arg in self.argVars:
            args.append(arg)
        # print('NF do1', [str(n) for n in args])
        res = self.callFunc(ctx, *args)
        if not isinstance(res, Val):
            # not Val, Not ListVal, etc.
            res =  Val(res, self.resType)
        self.res = res

    def get(self)->Val:
        return self.res


def coverFunc(name:str, fn:Callable, rtype:VType=TypeAny):
    func = NFunc(name)
    func.resType = rtype
    func.callFunc = fn
    return func

def setNativeFunc(ctx:Context, name:str, fn:Callable, rtype:VType=TypeAny):
    func = NFunc(name)
    func.resType = rtype
    func.callFunc = fn
    ctx.addFunc(func)


class BoundMethod(NFunc):
    
    def __init__(self, func:FuncCallExpr, fname, rtype = TypeAny()):
        super().__init__(fname, rtype)
        self.inst = None
        self.callArgs:list[Expression] = []
    
    def setInstance(self, inst):
        self.inst = inst

    def __str__(self):
        return 'func %s(???)' % (self._name)


def bindNativeMethod(ctx:Context, typeName, fn, fname, rtype:VType=None):
    if rtype is None:
        rtype = TypeAny
    # print('BM fn name:', fname)
    func = BoundMethod(fn, fname)
    func.resType = rtype
    func.callFunc = fn
    ctx.bindTypeMethod(typeName, func)


class MethodDefExpr(FuncDefExpr):
    ''' '''
    def __init__(self, name):
        super().__init__(name)
        self.instExpr:Expression = None
        self.typeName = None
        # raise EvalErr('DDD ', self.name)

    def setInst(self, exp:ServPairExpr):
        self.instExpr = exp.getTypedVar()

    def doFunc(self, ctx):
        func = Function(self.name)
        self.instExpr.do(ctx)
        inst = self.instExpr.get()
        dprint('MethodDefExpr.doFunc', inst, self.name)
        self.typeName = inst.getType().getName()
        # dprint('MethodDefExpr instType:', self.typeName)
        dprint('MethodDefExpr doFunc:', self.instExpr, self.instExpr.get())
        func.addArg(self.instExpr.get())
        return func

    def regFunc(self, ctx:Context, func:FuncInst):
        # print('M_Def reg', self.typeName, func)
        ctx.addTypeMethod(self.typeName, func)

    def do(self, ctx:Context):
        '''''' 
        super().do(ctx)

