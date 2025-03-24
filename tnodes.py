
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


class CaseExpr(Block):
    ''' case in `match` block
    '''
    
    # TODO: do we need result from `match` blok?

    def __init__(self):
        # super().__init__()
        self.block = Block()
        self.expect:Expression = None

    def add(self, exp:Expression):
        self.block.add(exp)

    def setExp(self, exp:Exception):
        self.expect = exp

    def doExp(self, ctx:Context):
        self.expect.do(ctx)

    def matches(self, val:Var):
        # simple equal
        print('~~~ %s == %s >>  %s' % (self.expect.get(), val.get(), self.expect.get() == val.get()))
        if self.expect.get().get() == val.get():
            return True

        # TODO: list case
        
        # tuple case

        # type case
        et = self.expect.get()
        if isinstance(et, VType) and et == val.getType():
            return True
        
        # struct-val case
        
        return False
    
    def do(self, ctx:Context):
        self.block.do(ctx)


class MatchExpr(Block):
    ''' 
    1. for unpack multiresults.
    2. for pattern matching like switch/case 
    match expr
        123 -> expr
        234 ->
            expr1
            expr2
        # type
        nums:list | len(nums) > 0 -> nums[0]
        x:int -> x + 2
        # sub condition
        u:User | u.name = 'Vasya' -> print(u.lastName)
        # constructor-patters
        u:User('Vasya') -> print(u.lastName)
        _ -> expr
    '''

    def __init__(self):
        self.match:Expression = None
        self.cases:list[CaseExpr] = []
        self.defaultCase:CaseExpr = None

    def add(self, xcase:CaseExpr):
        if not isinstance(xcase, CaseExpr):
            raise InerpretErr('Trying add not-case sub-expression (%s) to `match` block' % xcase.__class__.__name__)
        if isinstance(xcase.expect, VarExpr_):
            self.defaultCase = xcase
            return
        self.cases.append(xcase)

    def setMatch(self, exp:Expression):
        self.match = exp
    
    def do(self, ctx:Context):
        self.match.do(ctx)
        mctx = Context(ctx)
        done = self.doCases(mctx)
        if not done:
            self.defaultCase.do(mctx)

    def doCases(self, mctx:Context):
        for cs in self.cases:
            cs.doExp(mctx)
            mval = self.match.get()
            if cs.matches(mval):
                cs.do(mctx)
                return True
        return False
            


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

