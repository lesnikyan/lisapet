'''
Controlling structures of execution tree.

IF-ELSE
WHILE
FOR
MATCH

'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.iternodes import *


# Structural blocks


# IF-ELSE

class ElseExpr(Block):
    ''' '''

class IfExpr(ControlBlock):
    
    def __init__(self, cond:Expression=None):
        # super().__init__()
        self.mainBlock:Block = Block()
        self.elseBlock:Block = None
        self.cond = cond
        self.lastRes = None
        self.curBlock = self.mainBlock
        # TODO: add init block for if-statement, like Golang has

    def setCond(self, expr:Expression):
        print('# setCond ', expr)
        self.cond = expr
    
    def add(self, exp:Expression):
        self.curBlock.add(exp)
        
    def toElse(self, eBlock:ElseExpr):
        self.elseBlock = eBlock
        self.curBlock = self.elseBlock

    def do(self, ctx:Context):
        print('# IfExpr.do1 ', self.cond)
        self.cond.do(ctx)
        target:Block = self.mainBlock
        self.lastRes = None
        condRes = self.cond.get()
        print('## Cond-get', condRes, condRes.get())
        if not condRes.get():
            print('## IF_ELSE')
            if not self.elseBlock:
                # if don't have else-block return from if-block without result
                return
            # enter to else-block
            target = self.elseBlock
        print('# IfExpr.do2 ', target)
        target.do(ctx)
        self.lastRes = target.get() # for case if we need result from if block or one-line-if
        print('# IfExpr.do2 ', self.lastRes)

    def get(self):
        return self.lastRes


# MATCH-CASE

class CaseExpr(ControlBlock):
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
        # simple equal value
        print('~~~ %s == %s >>  %s' % (self.expect.get(), val.get(), self.expect.get() == val.get()))
        if self.expect.get().get() == val.get():
            return True

        # type case
        et = self.expect.get()
        if isinstance(et, VType) and et == val.getType():
            return True

        # TODO: 
        
        # list case
        
        # tuple case
        
        # dict case
        
        # struct-constructor case
        
        return False
    
    def do(self, ctx:Context):
        self.block.do(ctx)
        self.lastVal = self.block.get()


class MatchExpr(ControlBlock):
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
        super().__init__()
        self.match:Expression = None
        self.cases:list[CaseExpr] = []
        self.defaultCase:CaseExpr = None

    def add(self, xcase:CaseExpr):
        if not isinstance(xcase, CaseExpr):
            raise InterpretErr('Trying add not-case sub-expression (%s) to `match` block' % xcase.__class__.__name__)
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
                self.lastVal = cs.get()
                return True
        return False


# LOOP-FOR

class LoopIterExpr(LoopBlock):
    '''
    - iterator
    for n <- names
    for n <- iter(10)
    '''

    def __init__(self):
        super().__init__()
        
        self.iter:IterAssignExpr = None
        self.storeRes = False

    def setIter(self, iter:IterAssignExpr):
        self.iter = iter

    def add(self, exp:Expression):
        self.block.add(exp)

    def do(self, ctx:Context):
        self.iter.start(ctx)
        while self.iter.cond():
            print('# loop iter ----------------------------------')
            self.iter.do(ctx)
            self.block.do(ctx)
            blockRes = self.block.get()
            if isinstance(blockRes, FuncRes):
                # return expr
                self.lastVal = blockRes
                return
            self.iter.step()


class LoopExpr(LoopBlock):
    '''
    - pre, cond:
    for a -= 1; a > 0
    - init, cond, post:
    for i=0; i < 10; i += 1
    - iterator
    for n <- names
    for n <- iter(10)
    '''
    def __init__(self):
        super().__init__()
        self.initExpr = None
        self.cond:Expression = None
        self.preIter:Expression = None
        self.postIter:Expression = None
        
    def setExpr(self, **kwargs):
        for name,exp in kwargs.items():
            print('-- LoopExpr.setExpr', name, exp )
            match name:
                case 'init': self.initExpr = exp
                case 'cond': self.cond = exp
                case 'pre': self.preIter = exp
                case 'post': self.postIter = exp
                case _: raise InterpretErr('LoopExpr doesn`t have expression `%s` ' % name)


    def add(self, exp:Expression):
        # print('LoopExpr.add', exp)
        self.block.add(exp)

    def checkCond(self, ctx:Context)->bool:
        self.cond.do(ctx)
        return self.cond.get().get()

    def do(self, ctx:Context):
        if self.initExpr:
            self.initExpr.do(ctx)
        while self.checkCond(ctx):
            print('# loop expr ----------------------------------')
            if self.preIter:
                self.preIter.do(ctx)
            self.block.do(ctx)
            blockRes = self.block.get()
            if isinstance(blockRes, FuncRes):
                # return expr
                self.lastVal = blockRes
                return
            if self.postIter:
                self.postIter.do(ctx)

    def get(self):
        return self.block.get()


# LOOP-WHILE

class WhileExpr(LoopBlock):
    ''' while var == true 
        TODO: think about pre-iteration expression 
        while x += 1; x < 10
        while stat.recalc(); stat.isCorrect()
    '''

    def __init__(self, cond=None):
        super().__init__()
        self.cond:Expression = cond
        
    def setCond(self, cond:Expression):
        self.cond = cond

    def add(self, exp:Expression):
        print('WhileExpr.add', exp)
        self.block.add(exp)

    def do(self, ctx:Context):
        self.cond.do(ctx)
        c = 0
        while self.cond.get().get():
            # TODO: remove debug counter
            c +=1
            if c > 100:
                break
            print('# while iter ----------------------------------')
            self.block.do(ctx)
            blockRes = self.block.get()
            if isinstance(blockRes, FuncRes):
                # return expr
                self.lastVal = blockRes
                return
            self.cond.do(ctx)

