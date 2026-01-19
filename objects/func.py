''' '''

from typex import FuncInst, TypeFunc, VType
from base import Var, Val, EvalErr
from bases.ntype import *
from vars import ListVal
from nodes.expression import Expression, Block, ArgSetOrd, ValExpr
from context import Context
from nodes.expression import CallExpr
from nodes.base_oper import AssignExpr


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
        self._argTypes:dict[str, VType] = {}
        self.callArgs = []
        self.defArgs = {}
        self.block:Block = None
        self.defCtx:Context = None # for future: definition context (closure - ctx of module or upper block if function is local or lambda)
        self.res = None
        self.argNames = []
        self.extOrdered = None
        # print('Fuu.init', self)

    def setDefContext(self, ctx:Context):
        self.defCtx = ctx

    def getName(self):
        return self._name
    
    def argCount(self)->int:
        return self.argNum
    
    def argTypes(self)->list:
        return list(self._argTypes.values())

    def addArg(self, arg:Var|AssignExpr, defVal=None):
        # print(f'F.AddArg # {self._name}:', arg, defVal)
        self.argVars.append(arg)
        arname = arg.getName()
        if isinstance(arg, ArgSetOrd):
            # only 1 per function
            self.extOrdered = arname
            
        self.argNames.append(arname)
        self._argTypes[arname] = arg.getType()
        if defVal is not None:
            self.defArgs[arname] = defVal
        self.argNum += 1

    def setArgVals(self, args:list[Val], named:dict={}):
        passedCount = len(args)
        # print('! argVars', ['%s'%ag for ag in self.argVars ], 'len=', len(self.argVars))
        # print('! setArgVals', ['%s'%ag for ag in args ], 'len=', passedCount)
        # argNames = [n.getName() for n in self.argVars]
        namePassed = {k:v for k, v in named.items() if k in self.argNames} # filtering extra args
        defNamedCount = len([k for k in self.defArgs.keys() if k not in namePassed]) + len(namePassed)
        skipCount = int(self.extOrdered is not None)
        if self.argNum - skipCount > len(args) + defNamedCount:
            # print('Not enough args in call of fuction `%s`. Exppected: %d, got: %d. defVals+named: %d ; skip:%d' % (
            #     self._name, self.argNum, len(args), defNamedCount, skipCount))
            raise EvalErr('Not enough args in call of fuction `%s`. Exppected: %d, got: %d. ' % (self._name, self.argNum, len(args)))
        self.callArgs = []
        inCtx = Context(self.defCtx)
        # ordCollector = []
        noMoreOrds = False
        # func foo(a, b, nn..., c=1, d='', dd$$)
        #      foo(1, 2, 33, 44, 55, d='qwe', xx=77, yy='FF')
        
        # loop over defined arguments
        for i in range(self.argNum):
            val = None
            valExpr = None
            aname = self.argVars[i].getName()
            atype = self.argVars[i].getType()
            # print('F.setArgVals#1', self.argVars[i])
            if isinstance(self.argVars[i], ArgSetOrd):
                # variadic args: func foo(vargs...)
                # all args from current - put into -> vargs...
                val = ListVal(elems=args[i:])
                noMoreOrds = True
            
            if not noMoreOrds and i < passedCount:
                # Regulat args: func foo(a, b)
                val = args[i]
            else:
                if aname in namePassed:
                    # Named args: foo(name='Bob')
                    valExpr:Expression = namePassed[aname]
                elif aname in self.defArgs:
                    # Default val: func foo(x=1, y=2)
                    valExpr:ValExpr = self.defArgs[aname]
                    valExpr.do(inCtx)
                if valExpr:
                    val = valExpr.get()
            if not val:
                # print(f'Func addVals: No val for argument {self.argVars[i].getName()}')
                raise EvalErr(f'Func addVals: No val for argument {self.argVars[i].getName()}')
            valType = val.getType()
            if atype != valType:
                if isCompatible(atype, valType):
                    # convert val
                    try:
                        val = resolveVal(atype, val)
                    except EvalErr as ex:
                        # print('err.farg>', self.getName(), atype, valType)
                        # print(ex.getMessage())
                        raise ex
                else:
                    raise EvalErr('Uncompatible val %s for func arg %s' % (valType, atype))
            
            # print('FN (%s), self.argVars[i]: ' % self._name, self.argVars[i], ' /:/', arg)
            argVar = Var(aname, atype)
            argVar.set(val)
            # dprint('FN setArgVals-4: ', atype, aname)
            if isinstance(atype, TypeAny):
                argVar.setType(valType)
            # print('set arg8  >> ', self.argVars[i], 'val:', val)
            # arg.name = self.argVars[i].name
            self.callArgs.append(argVar)
            # self.argVars[i].set(arg.get())

    def tailRecur(self, inCtx: Context):
        # print('tail rec')
        recBlock = ResursionLoop(self)
        recBlock.doLoop(inCtx)
        # print('recBlock.get()', recBlock.get())
        return recBlock.get()

    def fillArgs(self, ctx:Context):
        for arg in self.callArgs:
            # print('Fu.do:', arg)
            ctx.addVar(arg)

    def do(self, ctx: Context):
        self.res = None
        self.block.storeRes = True # save last expr value
        inCtx = Context(self.defCtx) # inner context, empty new for each call
        
        # trying to detect tail recursion
        lastExpr = self.block.subs[-1]
        isTail = False
        if isinstance(lastExpr, CallExpr):
            # print('F.do', self, lastExpr.name)
            if self.getName() == lastExpr.name:
                rname = lastExpr.name
                rfunc = self.defCtx.get(rname)
                # print('same name', rname, rfunc)
                if rfunc == self:
                    # print('-- same fn:', rname, rfunc)
                    isTail = True
        
        self.fillArgs(inCtx)
        if isTail:
            res = self.tailRecur(inCtx)
        else:
            self.block.do(inCtx)
            res = self.block.get()
        
        # print('Func.do res=', res)
        if isinstance(res, FuncRes):
            res = res.get()
        if res is None:
            res = Val(Null(), TypeNull())
        self.res = var2val(res)

    def get(self)->Var:
        return self.res
        # return Val(self, TypeFunc())
    
    def __str__(self):
        if self.__class__.__name__ == 'NFunc':
            return 'func %s(???)' % (self._name)
        args = []
        # print('Func_str_. arg:', self._name, self.argVars)
        for arg in self.argVars:
            args.append('%s' % arg.name)
        return 'func %s(%s)' % (self._name, ', '.join(args))


class ResursionLoop(Block):
    def __init__(self, f:Function):
        """
        f - function which do recursion
        """
        super().__init__()
        self.subs: list[Expression] = f.block.subs
        self.callExpr:CallExpr = f.block.subs[-1]
        self.func = f
        self.storeRes = False
        self.lastVal:Var|list[Var] = None

    def linesIter(self):
        return len(self.subs) - 1

    def doLoop(self, ctx:NSContext):
        # prepare args
        # TODO: fix struct instance as a 1-st arg for method call
        while True:
            super().do(ctx)
            # print('recLoop.i=', i, self.lastVal)
            args = [] # add instance for methods
            args, named = self.callExpr.doArgs(args, ctx)
            self.func.setArgVals(args, named)
            self.func.fillArgs(ctx)
            if isinstance(self.lastVal, FuncRes):
                # print('RecLoop. return result', self.lastVal)
                break
        # return self.get()
            

