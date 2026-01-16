
from collections.abc import  Callable

from vars import *
from nodes.expression import *
from nodes.keywords import *
from bases.ntype import *
from nodes.base_oper import AssignExpr
from nodes.oper_dot import ObjectMember
from objects.func import Function

import inspect


# class Function(FuncInst):
#     ''' user-defined function object 
#     args:
#         call:
#         foo(a, b, c)
#         # def:
#         func foo(arg1, arg2, arg3)
#             # inner blok:
#             arg1 + arg2 + arg3
#     '''

#     def __init__(self, name):
#         super().__init__()
#         # self.argExpr:list[Expression] = None # like ListExpression: expr, expr, expr
#         self.isLambda = False
#         if name is None:
#             name = '@lambda'
#             self.isLambda = True
#         self._name = name
#         self.vtype = TypeFunc()
#         self.argNum = 0
#         self.argVars:list[Var] = []
#         self._argTypes:dict[str, VType] = {}
#         self.callArgs = []
#         self.defArgs = {}
#         self.block:Block = None
#         self.defCtx:Context = None # for future: definition context (closure - ctx of module or upper block if function is local or lambda)
#         self.res = None
#         self.argNames = []
#         self.extOrdered = None
#         # print('Fuu.init', self)

#     def setDefContext(self, ctx:Context):
#         self.defCtx = ctx

#     def getName(self):
#         return self._name
    
#     def argCount(self)->int:
#         return self.argNum
    
#     def argTypes(self)->list:
#         return list(self._argTypes.values())

#     def addArg(self, arg:Var|AssignExpr, defVal=None):
#         # print('F.AddArg:', arg, defVal)
#         self.argVars.append(arg)
#         arname = arg.getName()
#         if isinstance(arg, ArgSetOrd):
#             # only 1 per function
#             self.extOrdered = arname
            
#         self.argNames.append(arname)
#         self._argTypes[arname] = arg.getType()
#         if defVal is not None:
#             self.defArgs[arname] = defVal
#         self.argNum += 1

#     # TODO: flow-number arguments
#     def setArgVals(self, args:list[Val], named:dict={}):
#         passedCount = len(args)
#         # print('! argVars', ['%s'%ag for ag in self.argVars ], 'len=', len(self.argVars))
#         # print('! setArgVals', ['%s'%ag for ag in args ], 'len=', passedCount)
#         # argNames = [n.getName() for n in self.argVars]
#         namePassed = {k:v for k, v in named.items() if k in self.argNames} # filtering extra args
#         defNamedCount = len([k for k in self.defArgs.keys() if k not in namePassed]) + len(namePassed)
#         skipCount = int(self.extOrdered is not None)
#         if self.argNum - skipCount > len(args) + defNamedCount:
#             # print('Not enough args in call of fuction `%s`. Exppected: %d, got: %d. defVals+named: %d ; skip:%d' % (
#             #     self._name, self.argNum, len(args), defNamedCount, skipCount))
#             raise EvalErr('Not enough args in call of fuction `%s`. Exppected: %d, got: %d. ' % (self._name, self.argNum, len(args)))
#         self.callArgs = []
#         inCtx = Context(self.defCtx)
#         # ordCollector = []
#         noMoreOrds = False
#         # func foo(a, b, nn..., c=1, d='', dd$$)
#         #      foo(1, 2, 33, 44, 55, d='qwe', xx=77, yy='FF')
        
#         # loop over defined arguments
#         for i in range(self.argNum):
#             val = None
#             valExpr = None
#             aname = self.argVars[i].getName()
#             atype = self.argVars[i].getType()
#             # print('F.setArgVals#1', self.argVars[i])
#             if isinstance(self.argVars[i], ArgSetOrd):
#                 # variadic args: func foo(vargs...)
#                 noMoreOrds = True
#                 # all args from current - put into -> vargs...
#                 # ordCollector = args[i:]
#                 val = ListVal(elems=args[i:])
#             if not noMoreOrds and i < passedCount:
#                 # Regulat args: func foo(a, b)
#                 val = args[i]
#             else:
#                 if aname in namePassed:
#                     # Named args: foo(name='Bob')
#                     valExpr:Expression = namePassed[aname]
#                 elif aname in self.defArgs:
#                     # Default val: func foo(x=1, y=2)
#                     valExpr:ValExpr = self.defArgs[aname]
#                     valExpr.do(inCtx)
#                 if valExpr:
#                     val = valExpr.get()
#             if not val:
#                 # print(f'Func addVals: No val for argument {self.argVars[i].getName()}')
#                 raise EvalErr(f'Func addVals: No val for argument {self.argVars[i].getName()}')
#             valType = val.getType()
#             if atype != valType:
#                 if isCompatible(atype, valType):
#                     # convert val
#                     try:
#                         val = resolveVal(atype, val)
#                     except EvalErr as ex:
#                         # print('err.farg>', self.getName(), atype, valType)
#                         # print(ex.getMessage())
#                         raise ex
#                 else:
#                     raise EvalErr('Uncompatible val %s for func arg %s' % valType, atype)
            
#             # print('FN (%s), self.argVars[i]: ' % self._name, self.argVars[i], ' /:/', arg)
#             argVar = Var(aname, atype)
#             argVar.set(val)
#             # dprint('FN setArgVals-4: ', atype, aname)
#             if isinstance(atype, TypeAny):
#                 argVar.setType(valType)
#             # print('set arg8  >> ', self.argVars[i], 'val:', val)
#             # arg.name = self.argVars[i].name
#             self.callArgs.append(argVar)
#             # self.argVars[i].set(arg.get())

#     # def checkArgType(self, arg, val):
#     #     '''Use val.getType() and types compatibility '''
#     #     return typeCompat(arg, val)
#     #     # return True

#     def do(self, ctx: Context):
#         self.res = None
#         self.block.storeRes = True # save last expr value
#         inCtx = Context(self.defCtx) # inner context, empty new for each call
#         # inCtx.addVar(Var(1000001, 'debVal', TypeInt))
#         for arg in self.callArgs:
#             # print('Fu.do:', arg)
#             inCtx.addVar(arg)
#         # inCtx.get('debVal')
#         # inCtx.upper = ctx
#         self.block.do(inCtx)
#         res = self.block.get()
#         # print('Func.do res=', res)
#         if isinstance(res, FuncRes):
#             res = res.get()
#         if res is None:
#             res = Val(Null(), TypeNull())
#         self.res = var2val(res)

#     def get(self)->Var:
#         return self.res
#         # return Val(self, TypeFunc())
    
#     def __str__(self):
#         if self.__class__.__name__ == 'NFunc':
#             return 'func %s(???)' % (self._name)
#         args = []
#         # dprint('Func_str_. arg:', self.argVars)
#         for arg in self.argVars:
#             args.append('%s' % arg.name)
#         return 'func %s(%s)' % (self._name, ', '.join(args))


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
        print('FCall.setFuncExpr')
        self.funcExpr = fexp

    def addArgExpr(self, exp:Expression):
        self.argExpr.append(exp)

    def do(self, ctx: Context):
        # inne rcontext
        print('F().do/1')
        
        self.funcExpr.do(ctx)
        
        func:Function|FuncOverSet = self.funcExpr.get()
        # print(f'\nF() expr:', self.funcExpr, 'func:', func )
        
        args:list[Var] = []
        
        if isinstance(func, ObjectMember):
            obj:ObjectMember = func
            memVal = func.get(ctx)
            # print('objMem val=', memVal)
            func = memVal
            # print('F.do: ObjectMember', obj, func)
            inst = obj.getInst()
            args.append(inst)
            
        
        # print(f'\nFunction `{self.name}`:', self.func)
        named = {}
        for exp in self.argExpr:
            print('-- #1#',self.name,' func-call do2 exp=: ', exp)
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
            print('func-call do2:', valExp, arg)
            args.append(arg)
        
        # unpack function from var
        print('#1# func-call do03: ', self.name, 'F:', func)
        for aa in args: print('--- final args:', aa)
        for ak, av in named.items(): print('--- final nmed:', ak, av.get())
        # if isinstance(self.funcExpr, VarExpr):
        # call by defined name
        if isinstance(func, FuncOverSet):
            # overloaded set
            over:FuncOverSet = func
            callArgTypes = [ar.getType() for ar in args]
            # print('callArgTypes:', [f'{n.__class__.__name__}:{n.hash()}' for n in callArgTypes])
            func = over.get(callArgTypes)
            if not func:
                errMsg = f"Can't find overloaded function {self.name} with args = ({','.join([f'{n.__class__.__name__}' for n in callArgTypes])}) "
                raise EvalErr(errMsg)
                
        print('#2# func-call do04: ', self.name, 'F:', func)
        if isinstance(func, Var):
            func = func.get()
        if isinstance(func, TypeVal):
            tVal = func.getVal()
            if isinstance(tVal, TypeStruct):
                func = tVal.getConstr()
        # print('FCall.do.args:', self.name, args)
        self.func = func
        print('#3# func-call do05: ', self.name, 'F:', func)
        # print('#2# func-call do02: ', self.name, 'F:', self.func, 'line:', self.src)
        if isinstance(self.func, VarUndefined):
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
        # return self.func.get()


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
        print('M_Def reg', self.typeName, func)
        ctx.addTypeMethod(self.typeName, func)

    def do(self, ctx:Context):
        '''''' 
        super().do(ctx)


class MethodCallExpr(FuncCallExpr):
    ''' foo(agr1, 2, foo(3))  '''

    def __init__(self, func:FuncCallExpr):
        super().__init__(func.name, func.src)
        print('MCall.init:', func.name, 'src:', func.src)
        self.inst:ObjectInstance = None
        # self.name = name
        # self.func:Function = None
        self.argExpr:list[Expression] = func.argExpr

    def setInstance(self, inst: ObjectInstance|Val):
        dprint('MethCall set inst', inst)
        # raise XDebug('MethodCallExpr')
        self.inst = inst

    def getFunc(self, args:list):
        stype = self.inst.getType()
        fn = stype.getMethod(self.name)
        if isinstance(fn, FuncOverSet):
            over:FuncOverSet = fn
            callArgTypes = [ar.getType() for ar in args]
            fn = over.get(callArgTypes)
        self.func = fn

    def do(self, ctx: Context):
        okCond = isinstance(self.inst, ObjectInstance)
        # okCond = okCond or isinstance(self.func, BoundMethod)
        if not okCond:
            raise EvalErr('Incorrect instance of struct: %s ', self.inst)
        # print('MethodCallExpr.do 1', self.name, self.inst.getType())

        # instVar = self.inst[0].get(), self.inst[1].get()
        # print('instVar', self.inst, self.func.argVars)
        args:list[Var] = [self.inst]
        print('#1# meth-call do1: ', self.name, self.inst, 'f:', self.func, 'line:', self.src)
        for exp in self.argExpr:
            # print('#1# meth-call do20 exp=: ', exp)
            exp.do(ctx)
            vv = var2val(exp.get())
            # print('meth-call do3:', exp, vv, vv.get())
            args.append(vv)
        self.getFunc(args)
        self.func.setArgVals(args)
        # TODO: add usage of Definishion Context instead of None
        callCtx = Context(ctx)
        self.func.do(callCtx)

class BoundMethodCall(MethodCallExpr):
    def __init__(self, func:BoundMethod, callExpr:FuncCallExpr):
        super().__init__(callExpr)
        self.inst:Val = None
        self.func:BoundMethod = func
        self.argExpr:list[Expression] = callExpr.argExpr

    def do(self, ctx: Context):
        # print('instVar', self.inst, self.func.argVars)
        args:list[Var] = [self.inst]
        for exp in self.argExpr:
            exp.do(ctx)
            args.append(exp.get())
        self.func.setArgVals(args)
        callCtx = Context(ctx)
        self.func.do(callCtx)

    def get(self):
        return self.func.get()

