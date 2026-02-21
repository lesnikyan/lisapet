'''
Functions and objects for implementation elements of functional programming
1) currying
2) composition 
'''

from vars import *
from bases.ntype import *
from nodes.expression import *
from nodes.keywords import *
# from nodes.base_oper import AssignExpr
# from nodes.oper_dot import ObjectMember
from objects.func import Function
from nodes.func_expr import NFunc, ComposedFunc


'''
Currying process structure

f curry(multifunc)
    defnCtx # definition context, all args in child nodes of it
    f f1(a1)
        f f2(a2)
            f f3(a3)
                r = multifunc(a1, a2, a3)
                return r
            return f3
        return f2
    return f1

ff = curry(foo) # f1 returned here
'''

def hiddenName(i:int):
    return '#var-%d'% (i)


def defineFunc(defCtx:Context, name:str, fn:Callable):
    func = NFunc(name, 1)
    func.setDefContext(defCtx)
    func.resType = TypeFunc()
    func.callFunc = fn
    return func


def cascadeStep(i, func:Callable):
    '''
    i = name-index
    func - function to cover
    '''
    vn = hiddenName(i)
    funcName = 'f%d'%i
    def inFunc(ctx:Context, arg:Val):
        vvar = Var(vn, arg.getType())
        vvar.set(arg)
        ctx.addVar(vvar)
        rfunc = defineFunc(ctx, funcName, func)
        return rfunc
    return inFunc


def coverTarget(i, func:Callable):
    '''
    i = name-index
    func - function to cover
    '''
    vn = hiddenName(i)
    def resFunc(ctx:Context, arg:Val):
        vvar = Var(vn, arg.getType())
        vvar.set(arg)
        ctx.addVar(vvar)
        return func(ctx)
    return resFunc


def func_curry(defCtx:Context, fun:Function):
    ''' Curry pased function
    :param defCtx - definition context.
    :param fun - the target function being curried
    :return - NFunc obj with a cascase of currying. 
    '''
    argNum = fun.argCount()
    isMethod = isinstance(fun, MethodInst)
    if isMethod:
        argNum -= 1
    
    # deepest raw function in currying cascade
    def cover(ctx:Context):
        vars = [ctx.get(hiddenName(i+1)) for i in range(argNum)]
        args = []
        if isMethod:
            args.append(fun.getInst())
        args.extend([var2val(a) for a in vars])
        fun.setArgVals(args)
        fun.do(ctx)
        r = fun.get()
        return r
    cfun:Callable = coverTarget(argNum, cover)
    
    # making currying cascade
    outNum = argNum - 1
    covN:NFunc = cfun
    for i in range(outNum):
        fn = cascadeStep(outNum - i, covN)
        covN = fn
    # cover final cascade 
    rfun = defineFunc(defCtx, '#top-local-%s' % fun.getName(), covN)
    return rfun


def func_compose(ctx:Context, *funcs):
    com = ComposedFunc()
    com.setDefContext(ctx)
    for fn in funcs:
        com.add(fn)
    return com

# # dev check 
# def curr1(_, fun:Function):
#     def cover(ctx:Context, arg:Val):
#         fun.setArgVals([var2val(arg)])
#         fun.do(ctx)
#         r = fun.get()
#         return r
#     cfun = coverFunc('cov1', cover, TypeAny())
#     return cfun

