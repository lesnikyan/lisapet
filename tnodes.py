
"""
Structural components of execution tree.
"""

from lang import *
from vars import *
from expression import *

# class Node:
#     def __init__(self):
#         command = 0
#         arg = 0
        


# Expression

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

    def addArg(self, arg:Var):
        self.argVars.append(arg)
        self.argNum += 1
        print('Fuuu, addArg', arg, self.argNum)

    def setArgVals(self, args:list[Var]):
        if self.argNum != len(args):
            raise EvalErr('Number od args of fuction `%s` not correct. Exppected: %d, got: %d. ' % (self.name, self.argNum, len(args)))
        for i in range(len(args)):
            self.argVars[i].set(args[i].get())

    def do(self, ctx: Context):
        self.block.storeRes = True # save last expr value
        inCtx = Context(None) # inner context, empty new for each call
        inCtx.addVar(Var(1000001, 'debVal', TypeInt))
        for arg in self.argVars:
            inCtx.addVar(arg)
        inCtx.get('debVal')
        inCtx.upper = ctx
        self.block.do(inCtx)

    def get(self)->Var:
        return self.block.get()


class FuncCallExpr(Expression):
    ''' foo(agr1, 2, foo(3))  '''

    def __init__(self, name):
        super().__init__(name)
        self.func:Function = None
        self.argExpr:list[Expression] = []

    def addArgExpr(self, exp:Expression):
        self.argExpr.append(exp)

    def do(self, ctx: Context):
        # inne rcontext
        args:list[Var] = []
        for exp in self.argExpr:
            exp.do(ctx)
            args.append(exp.get())
        self.func.setArgVals(args)
        # TODO: add usage of Definishion Context instead of None
        callCtx = Context(None)
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
        print('FuncDefExpr.do 2:', func.name)
        
        ctx.addVar(func)
    
    def get(self)->Function:
        return self.res


class ListExpr(CollectionExpr):
    ''' [1,2,3, var, foo(), []]
    Make `list` object 
    '''
    def __init__(self):
        self.valsExprList:list[Expression] = []
        self.listObj:ListVar = None

    def add(self, exp:Expression):
        ''' add next elem of list'''
        self.valsExprList.append(exp)

    def do(self, ctx:Context):
        self.listObj = ListVar(None)
        print('## ListExpr.do1 self.listObj:', self.listObj, 'size:', len(self.valsExprList))
        for exp in self.valsExprList:
            exp.do(ctx)
            self.listObj.addVal(exp.get())
        print('## ListExpr.do2 self.listObj:', self.listObj)

    def get(self):
        print('## ListExpr.get self.listObj:', self.listObj)
        return self.listObj


class StructDefExpr(Block):
    ''' struct User
            name: string
            age: int
            weight: float
    '''


class StructFieldExpr(VarExpr):
    ''' inst.field = val; var = inst.field '''


class DictExpr(CollectionExpr):
    ''' {'key': val, keyVar: 13, foo():bar()} '''


class TupleExpr(CollectionExpr):
    ''' res = (a, b, c); res = a, b, c '''


class Matching(Expression):
    ''' 
    1. for unpack multiresults.
    2. for pattern matching like switch/case '''


class Module(Block):
    ''' Level of one file. 
    functions, constants, structs with methods '''
    def __init__(self):
        super().__init__()
        self.imported:dict[str, Context] = {}

    # def do(self):
    #     self.lastVal = None
    #     # TODO: eval sequences one by one, store result of each line, change vars in contexts

    # def get(self) -> list[Var]:
    #     return None

    def importIn(self, name, module):
        ''' Add other modules here'''
        self.imported[name] = module
        # TODO: merge contexts by resolved names
        
    def exportOut(self):
        ''' Call from other module `importIn '''
        return self.ctx

