
'''
Iteration expressions.
Mostly for usage into for-loop or generators.
'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.func_expr import FuncCallExpr
from nodes.datanodes import DictVal, ListVal


class IterAssignExpr(Expression):
    ''' target <- iter|collection '''
    def __init__(self):
        # self.assignExpr:Expression = None
        self.itExp:NIterator = None # right part, iterator
        self.srcExpr:CollectionExpr = None # right part, collection constructor, func(), var
        # local vars in: key, val <- iterExpr
        self.key:Var = None
        self.val:Var = None

    def setArgs(self, target, src):
        print('(iter =1)', target, )
        self.setTarget(target.get())
        print('(iter =2)', src)
        self.setSrc(src)

    def setTarget(self, vars:list[Var]|Var):
        print('> IterAssignExpr setTarget1', vars)
        if not isinstance(vars, list):
            vars = [vars]
        if len(vars) == 1:
            vars = [Var_(), vars[0]]
        self.key = vars[0]
        self.val = vars[1]
        print('> IterAssignExpr setTarget2', self.key, self.val)

    def setSrc(self, exp:Expression):
        print('> IterAssignExpr setSrc', exp)
        self.srcExpr = exp

    def start(self, ctx:Context):
        # print('#iter-start1 self.srcExpr', self.srcExpr)
        self.srcExpr.do(ctx) # make iter object
        iterSrc = self.srcExpr.get()
        print('#iter-start2 itSrc', iterSrc)
        if isinstance(iterSrc, (ListVal, DictVal)):
            self.itExp = SrcIterator(iterSrc)
        elif isinstance(iterSrc.get(), (NIterator)):
            self.itExp = iterSrc.get()
        self.itExp.start()
        # print('#iter-start3', self.key, self.val)
        for vv in [self.key, self.val]:
            # print('>>', vv)
            if not vv or isinstance(vv, Var_):
                continue
            ctx.addVar(vv)
    
    def cond(self)->bool:
        return self.itExp.hasNext()
    
    def step(self):
        self.itExp.step()
    
    def do(self, ctx:Context):
        ''' put vals into LOCAL context '''
        # print('IterAssignExpr.do', self.itExp)
        val = self.itExp.get()
        # print('IterAssignExpr.do1', val)
        key = Var_()
        if isinstance(val, tuple):
            key, val = val
        k, v = self.key, self.val
        # TODO: right way set values to local vars key, val
        # print('IterAssignExpr.do2', key, val)
        if key and not isinstance(key, Var_):
            ctx.update(k.name, key)
        ctx.update(v.name, val)


class NIterator:
    ''' '''
    
    def start(self):
        ''' reset iterator to start position '''
        pass

    def step(self):
        ''' move to next pos '''
        pass

    def hasNext(self):
        ''' if not last position '''
        pass

    def get(self):
        ''' get current element '''
        pass


class IndexIterator(NIterator):
    ''' x <- iter(0, 10, 2)'''
    def __init__(self, a, b=None, c=None):
        if c is None:
            c = 1
        if b is None:
            b = a
            a = 0
        self.first = a
        self.last = b # not last, but next after last
        self.__step = c
        self.index = a
        self.vtype = TypeIterator()
    
    def start(self):
        self.index = self.first

    def step(self):
        self.index += self.__step

    def hasNext(self):
        return self.index < self.last

    def get(self):
        return Val(self.index, TypeInt)


class SrcIterator(NIterator):
    ''' x <- [10,20,30] '''
    def __init__(self, src:list|dict):
        self.src = src.elems
        # self.iterFunc = self._iterList
        self._isDict = isinstance(self.src, dict)
        self._keys = None
        # if self._isDict:
            # self.iterFunc = self._iterDict
        self.iter = None
        self.vtype = TypeIterator()

    def start(self):
        seq = self.src
        if self._isDict:
            seq = seq.keys()
            self._keys = seq
            # self.iterFunc = self._iterDict
        self.iter = IndexIterator(0, len(seq))
        

    def step(self):
        self.iter.step()
        # self.iterFunc()

    def hasNext(self):
        return self.iter.hasNext()
        
    def get(self):
        key = self.iter.get().get()
        if self._isDict:
            key = self._keys[key]
        return self.src[key]


class ListGenIterator(NIterator):
    ''' [a..b] from a to b, step |1| '''

    def __init__(self, a, b):
        ''' a - begin, 
            b - end '''
        c = 1
        if b < a:
            c = -1
        self.first = a
        self.last = b # last val
        self.__step = c
        self.index = a
        self.vtype = TypeIterator()
    
    def start(self):
        self.index = self.first

    def step(self):
        self.index += self.__step

    def hasNext(self):
        return self.index <= self.last

    def get(self):
        return Val(self.index, TypeInt)


class ListGenExpr(Expression):
    ''' [a .. b] '''
    def __init__(self):
        self.iter:NIterator = None
        self.beginExpr = None
        self.endExpr = None

    def setArgs(self, a:Expression, b:Expression):
        self.beginExpr = a
        self.endExpr = b

    def do(self, ctx:Context):
        self.beginExpr.do(ctx)
        self.endExpr.do(ctx)
        a = self.beginExpr.get()
        b = self.endExpr.get()
        self.iter = ListGenIterator(a.getVal(), b.getVal())
        
    def get(self):
        return Val(self.iter, TypeIterator())
    

