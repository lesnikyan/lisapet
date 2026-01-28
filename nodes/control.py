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
from nodes.keywords import *
from nodes.match_patterns import *


# Structural blocks


# IF-ELSE

class ElseExpr(Block):
    ''' '''
    def __init__(self):
        super().__init__()
        self.subIf:IfExpr = None

    def hasIf(self):
        return bool(self.subIf)
    
    def setIf(self, sub: 'IfExpr'):
        self.subIf = sub
        self.add(sub)

class IfExpr(ControlBlock):
    
    def __init__(self, cond:Expression=None):
        # super().__init__()
        self.mainBlock:Block = Block()
        self.elseBlock:Block = None
        self.cond = cond
        self.preSubs:list[Expression] = [] # sub-expressions before conditions
        self.lastRes = None
        self.curBlock = self.mainBlock
        self.condRes = None
        self.inCtx = None

    def setCond(self, expr:Expression, subExp:list[Expression]=[]):
        # print('#IfExpr setCond ', expr, subExp)
        self.cond = expr
        self.preSubs = subExp
    
    def condCheck(self):
        return self.condRes
    
    def add(self, exp:Expression):
        self.curBlock.add(exp)
        
    def toElse(self, eBlock:ElseExpr):
        self.elseBlock = eBlock
        self.curBlock = self.elseBlock

    def do(self, ctx:Context):
        # print('# IfExpr.do1 ', self.cond, type(self.cond), ' | src:', self.cond.src)
        # print(' | src:', self.cond.src)
        inCtx = Context(ctx)
        for sub in self.preSubs:
            sub.do(inCtx)
        self.cond.do(inCtx)
        target:Block = self.mainBlock
        self.lastRes = None
        self.condRes = self.cond.get()
        self.inCtx = None
        # print('# IfExpr.do02 ', condRes, type(condRes))
        # print('## Cond-get', condRes, condRes.get())
        if not self.condRes.get():
            # print('## IF_ELSE')
            if not self.elseBlock:
                # if don't have else-block return from if-block without result
                return
            # enter to else-block
            target = self.elseBlock
        # print('# IfExpr.do2 ', target)
        self.inCtx = inCtx
        target.do(inCtx)
        self.lastRes = target.get() # for case if we need result from if block or one-line-if
        # print('# IfExpr.do2 ', self.lastRes)

    def get(self):
        return self.lastRes


class ElsFold:
    '''
    class covers main IF for folding inner `else if.
    
    '''
    def __init__(self, main:IfExpr):
        self.top:IfExpr = main
        self.cur:IfExpr = main
        self._lastElse = False
    
    def setNext(self, exp:ElseExpr):
        # self.cur.toElse(exp)
        # subIf = exp.subIf
        # self.cur.add(subIf)
        
        if self._lastElse:
            raise EvalErr("Can't put more `if` after `else` without subIf.")
        self.cur = exp.subIf

    def add(self, exp:Expression):
        # print(' -- ElsFold.add  >', expSrc(exp), self.cur)
        self.cur.add(exp)
    
    def toElse(self, exp:ElseExpr):
        if self._lastElse:
            raise EvalErr("Can't put more `else` after `else` without subIf.")
        if not exp.hasIf():
            self._lastElse = True
        self.cur.toElse(exp)

    def lastElse(self):
        return self._lastElse

    def getCur(self)->ElseExpr:
        return self.cur

    def getMain(self):
        return self.top


# # MATCH-CASE

class MatchExpr(ControlBlock):
    ''' 
    1. for unpack multiresults.
    2. for pattern matching like switch/case 
    match expr
        123 !- expr
        234 !-
            expr1
            expr2
        # type
        nums:list | len(nums) > 0 !- nums[0]
        x:int !- x + 2
        # sub condition
        u:User | u.name = 'Vasya' !- dprint(u.lastName)
        # constructor-patters
        u:User{name:'Vasya'} !- dprint(u.lastName)
        _ !- expr
    '''

    def __init__(self):
        super().__init__()
        self.match:Expression = None
        self.cases:list[CaseExpr] = []

    def add(self, xcase:CaseExpr):
        if not isinstance(xcase, CaseExpr):
            raise InterpretErr('Trying add not-case sub-expression (%s) to `match` block' % xcase.__class__.__name__)
        self.cases.append(xcase)

    def setMatch(self, exp:Expression):
        self.match = exp
    
    def do(self, ctx:Context):
        self.lastVal = None
        self.match.do(ctx)
        self.doCases(ctx)

    def doCases(self, ctx:Context):
        mval = self.match.get()
        vv = mval
        mval = var2val(mval)
        # print('Match. mval', self.match, vv, '::',  mval)
        for cs in self.cases:
            mctx = Context(ctx)
            cs.doExp(mctx)
            if cs.match(mval):
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
        
        self.iter:LeftArrowExpr = None
        self._origIter = None
        # self.iter:IterAssignExpr = None
        self.storeRes = False

    # def setIter(self, iter:IterAssignExpr):
    def setIter(self, iter:LeftArrowExpr):
        # raise EvalErr('LoopIterExpr setIter: ', iter)
        # dprint('LoopExpr.setIter', iter)
        self._origIter = iter

    def add(self, exp:Expression):
        # dprint('LoopExpr.add', exp)
        self.block.add(exp)

    def do(self, ctx:Context):
        self.lastVal = None
        subCtx = Context(ctx)
        if isinstance(self._origIter, LeftArrowExpr):
            # print('For iter')
            self._origIter.init(subCtx)
            if isinstance(self._origIter.expr, IterAssignExpr):
                self.iter = self._origIter.expr
        self.iter.start()
        while self.iter.cond():
            # print('# loop list iter ----------------------------------')
            self.iter.do(subCtx)
            self.block.do(subCtx)
            blockRes = self.block.get()
            if isinstance(blockRes, FuncRes):
                # return expr
                self.lastVal = blockRes
                return
            if isinstance(blockRes, PopupBreak):
                # break expr
                self.lastVal = None
                break
            if isinstance(blockRes, PopupContinue):
                ''' Nothing to do, just go to next iteration '''
                # continue expr
            self.iter.step()


class LoopExpr(LoopBlock):
    '''
    - pre, cond:
    for a -= 1; a > 0
    - init, cond, post:
    for i=0; i < 10; i += 1
    
    '''
    def __init__(self):
        super().__init__()
        self.initExpr = None
        self.cond:Expression = None
        self.preIter:Expression = None
        self.postIter:Expression = None
        
    def setExpr(self, **kwargs):
        for name,exp in kwargs.items():
            dprint('-- LoopExpr.setExpr', name, exp )
            match name:
                case 'init': self.initExpr = exp
                case 'cond': self.cond = exp
                case 'pre': self.preIter = exp
                case 'post': self.postIter = exp
                case _: raise InterpretErr('LoopExpr doesn`t have expression `%s` ' % name)


    def add(self, exp:Expression):
        # dprint('LoopExpr.add', exp)
        self.block.add(exp)

    def checkCond(self, ctx:Context)->bool:
        self.cond.do(ctx)
        return self.cond.get().get()

    def do(self, ctx:Context):
        if self.initExpr:
            self.initExpr.do(ctx)
        while self.checkCond(ctx):
            # print('# for i expr ----------------------------------')
            if self.preIter:
                self.preIter.do(ctx)
            self.block.do(ctx)
            blockRes = self.block.get()
            # print(' - loop1 ::', blockRes, type(blockRes))
            if isinstance(blockRes, FuncRes):
                # return expr
                self.lastVal = blockRes
                return
            if isinstance(blockRes, PopupBreak):
                # break expr
                # print(' - i-loop num stop ::', blockRes, type(blockRes))
                self.lastVal = None
                return
            if isinstance(blockRes, PopupContinue):
                ''' Nothing to do, just go to next iteration '''
                # print(' - loop num cont ::', blockRes, type(blockRes))
            if self.postIter:
                self.postIter.do(ctx)

    def get(self):
        return self.lastVal


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
        dprint('WhileExpr.add', exp)
        self.block.add(exp)

    def do(self, ctx:Context):
        self.cond.do(ctx)
        c = 0
        # print('# --------- while -----------------------')
        while self.cond.get().get():
            # TODO: remove debug counter
            c +=1
            if c > 100:
                break
            # print('# while iter ----------------------------------')
            self.block.do(ctx)
            blockRes = self.block.get()
            # print(' while :: ', blockRes, type(blockRes))
            if isinstance(blockRes, FuncRes):
                # return expr
                self.lastVal = blockRes
                return
            if isinstance(blockRes, PopupBreak):
                # break expr
                self.lastVal = None
                # print(' - loop stop ::', blockRes, type(blockRes))
                break
            if isinstance(blockRes, PopupContinue):
                # continue expr
                ''' Nothing to do, just go to next iteration '''
            
            self.cond.do(ctx)

