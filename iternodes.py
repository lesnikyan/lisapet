
'''
Iteration expressions
'''

from lang import *
from vars import *
from expression import *


class IterGen(Expression):
    ''' '''
    
    def __init__(self, start=0, over=0, step=1, **kw):
        self.startIndex = start
        self.index:int = start # val, index of list (src[index]), index of keys of dict (src[keys[index]])
        self.diff = step
        self.over = over
        # self.src = None # None, list, dict
        self.keys = None
        # if 'src' in kw:
        #     self.src = kw['src']
        # if isinstance(self.src, dict):
        #     self.keys = self.src.keys()
    
    def start(self):
        self.index = self.startIndex
    
    def step(self):
        self.index += self.diff
        
    def hasNext(self):
        return self.index < self.over
    
    def get(self):
        return Var(self.index,None, TypeInt)
        # if isinstance(self.src, list):
        #     return Var(self.index,None, TypeInt), self.src[self.index]/



class IterCollection(IterGen):
    ''' Iterator over collection '''

    def __init__(self, src:Collection):
        super().__init__(0, src.len(), 1)
        self.src:Collection = src # None, list, dict

    def get(self):
        val = self.src.getVal(self.index)
        return Var(self.index,None, TypeInt), val
        # TODO: for dict implementation
        # elif isinstance(self.keys, list):
        #     return self.keys[self.index], self.src[self.keys[self.index]]

class IterAssignExpr(Expression):
    ''' target <- iter|collection '''
    def __init__(self):
        # self.assignExpr:Expression = None
        self.itExp:IterGen = None # right part, iterator
        self.srcExpr:CollectionExpr = None # right part, collection constructor, func(), var
        # local vars in: key, val <- iterExpr
        self.key:Var = None
        self.val:Var = None

    def setTarget(self, vars:list[Var]|Var):
        if isinstance(vars, Var):
            vars = [Var]
        if len(vars) == 1:
            vars = [Var_(), vars[0]]
        self.key = vars[0]
        self.val = vars[1]
    
    def setIter(self, exp:IterGen):
        self.itExp = exp
    
    def setSrc(self, exp:Expression):
        self.srcExpr = exp
    
    def start(self, ctx:Context):
        # print('#iter-asg-expr1 target', self.key, self.val)
        # print('#iter-asg-expr1 self.srcExpr', self.srcExpr)
        if self.srcExpr:
            self.srcExpr.do(ctx) # make collection object
            # print('IterAssignExpr.start', self.srcExpr.get())
            self.itExp = IterCollection(self.srcExpr.get())
        # print('#iter-asg-expr2 itExp', self.itExp)
        self.itExp.start()
        for vv in [self.key, self.val]:
            if not vv or isinstance(vv, Var_):
                continue
            ctx.addVar(vv)
    
    def cond(self)->bool:
        return self.itExp.hasNext()
    
    def step(self):
        self.itExp.step()
    
    def do(self, ctx:Context):
        ''' put vals into LOCAL context '''
        self.itExp.do(ctx)
        # if iter or list; 
        val = self.itExp.get()
        # print('IterAssignExpr.do', self.itExp, self.itExp.src, val)
        key = Var_()
        if isinstance(val, tuple):
            key, val = val
        # TODO: put key-val into context?
        k, v = self.key, self.val
        # TODO: right way set values to local vars key, val
        if key and not isinstance(key, Var_):
            ctx.update(k.name, key)
        # print('IterAssignExpr.do', key, val)
        ctx.update(v.name, val)
    