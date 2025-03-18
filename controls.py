'''
Controlling structures of execution tree.
IF-ELSE
WHILE
FOR

'''

from lang import *
from vars import *
from expression import *



# Structural blocks

# structural constrations: for, if, match



class ElseExpr(Block):
    ''' '''

class IfExpr(Block):
    
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

    def get(self):
        return self.lastRes


class WhileExpr(Block):
    ''' while var == true 
        TODO: think about pre-iteration expression 
        while x += 1; x < 10
        while stat.recalc(); stat.isCorrect()
    '''
    def __init__(self, cond=None):
        self.block:Block = Block() # empty block on start
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
            self.cond.do(ctx)

class IterGen(Expression):
    ''' '''
    
    def __init__(self, start=0, over=0, step=1, **kw):
        self.startIndex = start
        self.index:int = start # val, index of list (src[index]), index of keys of dict (src[keys[index]])
        self.diff = step
        self.over = over
        self.src = None # None, list, dict
        self.keys = None
        if 'src' in kw:
            self.src = kw['src']
        if isinstance(self.src, dict):
            self.keys = self.src.keys()
    
    def start(self):
        self.index = self.startIndex
    
    def step(self, ctx:Context):
        self.index += self.diff
        
    def hasNext(self):
        return self.index < self.over
    
    def get(self, ctx:Context):
        if self.src is None:
            return Var(self.index,None, TypeInt)
        elif isinstance(self.src, list):
            return Var(self.index,None, TypeInt), self.src[self.index]
        # TODO: for dict implementation
        # elif isinstance(self.keys, list):
        #     return self.keys[self.index], self.src[self.keys[self.index]]

class IterAssignExpr(Expression):
    ''' target <- iter|collection '''
    def __init__(self):
        self.target:list[Var] = None
        self.assignExpr:Expression = None
        self.itExp:IterGen = None
    
    def setTarget(self, vars:list[Var]):
        self.target = vars
    
    def setIter(self, exp:IterGen):
        self.itExp = exp
    
    def start(self, ctx:Context):
        self.itExp.start()
        for vv in self.target:
            ctx.addVar(vv)
    
    def cond(self)->bool:
        return self.itExp.hasNext()
    
    def step(self):
        self.itExp.step()
    
    def do(self, ctx:Context):
        ''' put vals into LOCAL context '''
        self.itExp.do(ctx)
        val = self.itExp.get()
        key = Var_()
        if isinstance(val, tuple):
            key, val = val
        # TODO: put key-val into context?
        k, v = self.target
        if not isinstance(key, Var_):
            ctx.update(k.name, key)
        ctx.update(v.name, val)
        # self.assignExpr.do(ctx)
        
    # def get(self):
    #     res = self.itExp


class LoopIterExpr(Block):
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
        self.block:Block = Block() # empty block on start
        self.iter:IterAssignExpr = None

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
            self.iter.step()



class LoopExpr(Block):
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
        self.block:Block = Block() # empty block on start
        self.initExpr = None
        self.cond:Expression = None
        self.preIter:Expression = None
        self.postIter:Expression = None
        
    def setExpr(self, **kwargs):
        expMap = {
            'init': self,
            'cond': self,
            'pre': self,
            'post': self,
        }
        for name,exp in kwargs.items():
            if name in expMap:
                expMap[name] = exp
            else:
                raise InerpretErr('LoopExpr doesn`t have expression `%s` ' % name)

    def setIter(self, iter:IterAssignExpr):
        pass

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
            if self.postIter:
                self.postIter.do(ctx)



# class Iter:
#     ''' base iter'''
    
#     def start(self, ctx:Context):
#         self.index = 0
        
#     def hasNext(self)->bool:
#         ''' show status by state '''
#         pass
    
#     def step(self, ctx:Context):
#         ''' change state '''
#         pass

# class IterList:
#     ''' for x <- [1,2,3]'''
#     def __init__(self, src=None):
#         self.src:list = None # list or iterator
#         self.over = 0
#         if src is not None:
#             self.setSrc(src)
        
#     def setSrc(self, src):
#         self.src = src
#         self.over = len(self.src)
#         # self.index = 0
    
#     def hasNext(self)->bool:
#         ''' check before next'''
#         return self.index < self.over

#     def step(self, ctx:Context):
#         ''' call after iteration '''
#         self.index += 1

#     def next(self, ctx:Context):
#         ''' return current value '''
#         val = self.src[self.index]


# class IterCounter(Iter):
#     '''
#         iter(10) >> 1 - 9
#         iter(5, 10) >> 5 - 9
#         iter(5, 10, 20) >> [5,7,9]
#         for i <- iter(10)
#     '''
#     def __init__(self, num, arg2=None, step=1):
#         self.over = num
#         self.start = 0
#         self.step = step
#         if arg2 is not None:
#             self.start = num
#             self.over = arg2
#         self.index = self.start
#         self.assignExpr:Expression = None
#         # self.src = range(self.start, self.over, self.step)
    
#     def setAssign(self, exp:Expression):
#         ''' x <- iter(1)'''
#         self.assignExpr = exp
    
#     def hasNext(self)->bool:
#         ''' check before next'''
#         return self.index < self.over

#     def step(self, ctx:Context):
#         ''' call after iteration '''
#         self.index += self.step
#         self.assignExpr

#     # def next(self, ctx:Context):
#     #     ''' return current value '''
#     #     return self.index

# class IterExpr(Iter):
#     ''' custom loop
#         for initExpr; conditionExpr; stepExpr
#         exm: for i = 0; i < 10; i += 1
#         exp: for it = iter(10); it.hasNext(); it.step()
#     '''
    
#     def __init__(self, init= None, cond=None, step=None):
#         # super().__init__()
#         self.initExpr:Expression = init
#         self.stepExpr: Expression = step
#         self.condExpr:Expression = cond

#     def start(self, ctx:Context):
#         self.initExpr.do(ctx)

#     def hasNext(self, ctx:Context)->bool:
#         ''' check before next'''
#         self.condExpr.do(ctx)
#         return self.condExpr.get().get()

#     def step(self, ctx:Context):
#         ''' call after iteration '''
#         # self.index += self.step
#         self.stepExpr.do(ctx)

#     def next(self, ctx:Context):
#         ''' return current value '''
#         # return self.index
        

# class IterAssignExpr(Expression):
#     ''' n <- iter(10) '''

# class ForExpr(Block):

#     def __init__(self, iter:Iter):
#         # super().__init__()
#         self.block = Block() # empty block on start
#         self.iter:Iter = iter
#         # self.lastRes = None
        
#     def setIter(self, iter:Iter):
#         self.iter = iter
        
#     def add(self, exp:Expression):
#         self.block.add(exp)
        
#     # цикл как прокрутка итератора, 
#     # или цикл как старт ; блок() + постБлок() - проверка условия
#     '''
#         for init(); cond(); step()
#         for i = 0; i < 10; i += 1
#         for it = iter(10); it.hasNext(); it.step()
#         for i <- iter(1, 10, 2)
#         for x <- [1,2,3]
        
#         iter(10) >> 1 - 9
#         iter(5, 10) >> 5 - 9
#         iter(5, 10, 20) >> [5,7,9]
#     '''
#     def do(self, ctx:Context):
#         self.iter.start(ctx)
#         # TODO: implement all cases of `for`
#         while self.iter.hasNext():
#             self.block.do(ctx)
#             # self.lastRes = self.block.get()
#             self.iter.step(ctx)
        
#     def get(self):
#         ''' if we use block-result case '''
#         return self.block.get()
