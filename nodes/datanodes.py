'''
Expressions of definition and usage of data structures.
Data structures:
List, 
Dict, 
Struct,
Tree, 

'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.oper_nodes import ServPairExpr


class ListExpr(CollectionExpr):
    ''' [1,2,3, var, foo(), []]
    Make `list` object 
    '''
    def __init__(self):
        super().__init__()
        self.valsExprList:list[Expression] = []
        self.listObj:ListVal = None

    def add(self, exp:Expression):
        ''' add next elem of list'''
        # print('ListExpr.add', exp)
        self.valsExprList.append(exp)

    def do(self, ctx:Context):
        self.listObj = ListVal()
        # dprint('## ListExpr.do1 self.listObj:', self.listObj, 'size:', len(self.valsExprList))
        for exp in self.valsExprList:
            exp.do(ctx)
            v = exp.get()
            # print('-=ListExpr.do1', exp, ' : : ', v, type(v))
            val = var2val(v)
            # print('ListExpr.do2', val, type(val))
            self.listObj.addVal(val)
        # dprint('## ListExpr.do2 self.listObj:', self.listObj)

    def get(self):
        # dprint('## ListExpr.get self.listObj:', self.listObj)
        return self.listObj


class ListConstr(MultilineVal, ListExpr):
    ''' list '''
    tname = 'list'

    def __init__(self, byword = False):
        super().__init__()
        self.byword = byword



class DictExpr(CollectionExpr):
    ''' {'key': val, keyVar: 13, foo():bar()} '''
    def __init__(self):
        super().__init__()
        self.exprList:list[ServPairExpr] = []
        self.data:DictVal = None

    def add(self, exp:ServPairExpr):
        ''' add next elem of list'''
        dprint('DictExpr_add', self,  exp)
        self.exprList.append(exp)

    def do(self, ctx:Context):
        self.data = DictVal(None)
        # dprint('## DictExpr.do1 self.data:', self.data)
        for exp in self.exprList:
            # dprint('dictExp. next:', exp)
            exp.do(ctx)
            k, v = exp.get()
            key = var2val(k)
            val = var2val(v)
            self.data.setVal(key, val)
        # dprint('## DictExpr.do2 self.data:', self.data)

    def get(self):
        # dprint('## DictExpr.get self.data:', self.data)
        return self.data


class DictConstr(MultilineVal, DictExpr):
    ''' dict '''
    tname = 'dict'

    # def __init__(self):
    #     super().__init__()

    def __init__(self, byword = False):
        super().__init__()
        self.byword = byword

class CollectElemExpr(Expression, CollectElem):
    
    def __init__(self):
        self.target:Collection = None
        self.varExpr:Expression = None
        self.keyExpr = None
        
    def setVarExpr(self, exp:Expression):
        self.varExpr = exp

    def setKeyExpr(self, exp:Expression):
        self.keyExpr = exp

    def do(self, ctx:Context):
        self.target = None
        dprint('## COLL[x1] self.varExpr', self.varExpr)
        self.varExpr.do(ctx) # before []
        target = self.varExpr.get() # found collection
        dprint('## COLL[x2] target1', self.target)
        if isinstance(target, Var):
            target = target.get()
        self.target = target
        dprint('## COLL[x3] target2', self.target)
        self.keyExpr.do(ctx) #  [ into ]

    def set(self, val:Var):
        ''' '''
        key = self.keyExpr.get()
        self.target.setVal(key, val)

    def get(self)->Var:
        key = self.keyExpr.get()
        elem = self.target.getVal(key)
        return elem


class SliceExpr(Expression, CollectElem):
    ''' array[start : last+1] '''

    def __init__(self):
        self.target:ListVal = None
        self.varExpr:Expression = None
        self.beginExpr = None
        self.closeExpr = None
        
    def setVarExpr(self, exp:Expression):
        self.varExpr = exp

    def setKeysExpr(self, beginExpr:Expression, closeExpr:Expression):
        ''' openExpr, closeExpr'''
        if isinstance(beginExpr, NothingExpr):
            beginExpr = ValExpr(Val(0, TypeInt()))
        # if isinstance(closeExpr, NothingExpr):
        #     closeExpr = ValExpr(Var(-1, None, TypeInt))
        self.beginExpr = beginExpr
        self.closeExpr = closeExpr

    def do(self, ctx:Context):
        self.target = None
        self.varExpr.do(ctx) # before []
        target = self.varExpr.get() # found collection
        # dprint('SliceExpr.do1', target, '::', target.getType())
        if isinstance(target.getType(), (TypeIterator)):
            target = target.getVal()
        if isinstance(target, Var):
            target = target.getVal()
        self.target = target
        # dprint('SliceExpr.do2', target, '::')
        self.beginExpr.do(ctx)
        self.closeExpr.do(ctx)
        if isinstance(self.closeExpr, NothingExpr):
            self.closeExpr = ValExpr(Val(self.target.len(), TypeInt()))
        # dprint('## self.target', self.target)

    def get(self)->Var:
        beg, end = self.beginExpr.get(), self.closeExpr.get()
        # dprint('Slice:', beg.get(), end.get())
        res = self.target.getSlice(beg.get(), end.get())
        return res


class TupleExpr(CollectionExpr):
    ''' res = (a, b, c); res = a, b, c '''

    def __init__(self):
        super().__init__()
        self.valsExpr:list[Expression] = []
        self.obj:TupleVal = None

    def add(self, exp:Expression):
        ''' add next elem of list'''
        self.valsExpr.append(exp)

    def do(self, ctx:Context):
        self.obj = TupleVal()
        for exp in self.valsExpr:
            exp.do(ctx)
            v = exp.get()
            self.obj.addVal(var2val(v))

    def get(self):
        return self.obj
