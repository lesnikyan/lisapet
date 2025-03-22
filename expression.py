'''
Base expression objects.
'''

from vars import *

class Expression:
    def __init__(self, val=None):
        self.val = val
        self.block = False
    
    def do(self, ctx:Context):
        pass
    
    def get(self) -> Var|list[Var]:
        return self.val
    
    def isBlock(self)->bool:
        ''' True if one of: func, for, if, match, case'''
        return False
    
    def __str__(self):
        return self.__class__.__name__

class CommentExpr(Expression):
    ''' for future usage'''
    def __init__(self, text:str):
        '''' text of comment line is value '''
        super().__init__(text)

class ValExpr(Expression):
    def __init__(self, var:Var):
        # print('#tn2-valEx:', var, var.get())
        self.val = var
    
    def do(self, ctx:Context):
        pass

    def get(self)->Var:
        # print('#tn2-valEx-get:', self.val, self.val.get())
        return self.val
    
    def __str__(self):
        return 'ValExpr(%s)' % self.val


class DebugExpr(Expression):
    def __init__(self, txt):
        print('**** DEBUG__init:', txt)
        self.val = txt
    
    def do(self, ctx:Context):
        print(" $$$ DEBUG: ", self.val)

class VarExpr(Expression):
    def __init__(self, var:Var):
        self.val = var # or name,type ?
        self.name = var.name
    
    def do(self, ctx:Context):
        newVal = ctx.get(self.name)
        print('#tn3:', newVal)
        self.val = newVal
    
    # def set(self, val:Var):
    #     self.var = val.get()

    def get(self)->Var:
        return self.val

    def __str__(self):
        return 'VarExpr(%s)' % (self.name)

class VarExpr_(VarExpr):
    def __init__(self, var:Var):
        self.name = '_'
    
    def do(self, ctx:Context):
        ''' nothing to do'''

    def get(self)->None:
        ''' nothing to do'''

    def set(self, x):
        ''' nothing to do'''

    def __str__(self):
        return 'VarExpr_(_)'
    

# class Command(Expression):
#     def do(self, var:Var, src:Expression):
#         pass
    
#     def get(self):
#         return self.val


class Block(Expression):
    def __init__(self):
        self.ctx = Context()
        self.subs: list[Expression] = []
        self.storeRes = False
        self.lastVal:Var|list[Var] = None # result of last sequence, can be a list if many results: a, b, [1,2,3]
    
    def add(self, seqs:Expression|list[Expression]):
        if not isinstance(seqs, list):
            seqs = [seqs]
        self.subs.extend(seqs)
    
    def do(self, ctx:Context):
        self.lastVal = None
        # eval sequences one by one, store result of each line, change vars in contexts
        elen = len(self.subs)
        if elen < 1:
            return
        lastInd = 0
        self.ctx.upper = ctx
        print('!! Block.do')
        for i in range(elen):
            print('!! Block.iter ', i, self.subs[i])
            expr = self.subs[i]
            expr.do(ctx)
            lastInd = i
        if self.storeRes:
            self.lastVal = self.subs[lastInd].get()

    def get(self) -> list[Var]:
        return self.lastVal
    
    def isBlock(self)->bool:
        ''' True if one of: func, for, if, match, case'''
        return True


class CollectElemExpr(Expression):
    
    def __init__(self):
        self.target:ContVar = None
        self.varExpr:Expression = None
        self.keyExpr = None
        
    def setVarExpr(self, exp:Expression):
        self.varExpr = exp

    def setKeyExpr(self, exp:Expression):
        self.keyExpr = exp

    def do(self, ctx:Context):
        self.target = None
        self.varExpr.do(ctx) # before []
        self.target = self.varExpr.get() # found collection
        print('## self.target', self.target)
        self.keyExpr.do(ctx) #  [ into ]

    def set(self, val:Var):
        ''' '''
        key = self.keyExpr.get()
        self.target.setVal(key, val)

    def get(self)->Var:
        key = self.keyExpr.get()
        elem = self.target.getVal(key)
        return elem


