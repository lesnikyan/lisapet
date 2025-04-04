
'''
Iteration expressions.
Mostly for usage into for-loop or generators.
'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.func_expr import FuncCallExpr
from nodes.datanodes import DictVar, ListVar


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
    
    # def setIter(self, exp:IterGen):
    #     print('> IterAssignExpr setIter', exp)
    #     self.itExp = exp
    
    def setSrc(self, exp:Expression):
        print('> IterAssignExpr setSrc', exp)
        self.srcExpr = exp
    
    def start(self, ctx:Context):
        # print('#iter-start0 target', self.key, self.val)
        print('#iter-start1 self.srcExpr', self.srcExpr)
        # if self.srcExpr:
        self.srcExpr.do(ctx) # make collection object
        # print('IterAssignExpr.start', self.srcExpr.get())
        # self.itExp = IterCollection(self.srcExpr.get())
        iterSrc = self.srcExpr.get()
        print('#iter-start2 itSrc', iterSrc)
        if isinstance(iterSrc, (ListVar, DictVar)):
            self.itExp = SrcIterator(iterSrc)
        elif isinstance(iterSrc.get(), (IndexIterator)):
            self.itExp = iterSrc.get()
        # self.itExp = self.srcExpr.get().get()
        self.itExp.start()
        print('#iter-start3', self.key, self.val)
        for vv in [self.key, self.val]:
            print('>>', vv)
            if not vv or isinstance(vv, Var_):
                continue
            ctx.addVar(vv)
    
    def cond(self)->bool:
        return self.itExp.hasNext()
    
    def step(self):
        self.itExp.step()
    
    def do(self, ctx:Context):
        ''' put vals into LOCAL context '''
        print('IterAssignExpr.do', self.itExp)
        # self.itExp.step()
        # if iter or list; 
        val = self.itExp.get()
        print('IterAssignExpr.do1', val)
        key = Var_()
        if isinstance(val, tuple):
            key, val = val
        # TODO: put key-val into context?
        k, v = self.key, self.val
        # TODO: right way set values to local vars key, val
        print('IterAssignExpr.do2', key, val)
        if key and not isinstance(key, Var_):
            ctx.update(k.name, key)
        ctx.update(v.name, val)


class NIterator:
    ''' '''


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
    
    def start(self):
        self.index = self.first

    def step(self):
        self.index += self.__step

    def hasNext(self):
        return self.index < self.last

    def get(self):
        return Var(self.index, None, TypeInt)

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

