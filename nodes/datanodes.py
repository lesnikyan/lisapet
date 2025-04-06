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
        super().__init__()
        self.valsExprList:list[Expression] = []
        self.listObj:ListVar = None

    def add(self, exp:Expression):
        ''' add next elem of list'''
        self.valsExprList.append(exp)

    def do(self, ctx:Context):
        self.listObj = ListVar(None)
        # print('## ListExpr.do1 self.listObj:', self.listObj, 'size:', len(self.valsExprList))
        for exp in self.valsExprList:
            exp.do(ctx)
            self.listObj.addVal(exp.get())
        # print('## ListExpr.do2 self.listObj:', self.listObj)

    def get(self):
        # print('## ListExpr.get self.listObj:', self.listObj)
        return self.listObj


class ListConstr(MultilineVal, ListExpr):
    ''' list '''

    def __init__(self):
        super().__init__()


class DictExpr(CollectionExpr):
    ''' {'key': val, keyVar: 13, foo():bar()} '''
    def __init__(self):
        super().__init__()
        self.exprList:list[ServPairExpr] = []
        self.data:DictVar = None

    def add(self, exp:ServPairExpr):
        ''' add next elem of list'''
        print('DictExpr_add', self,  exp)
        self.exprList.append(exp)

    def do(self, ctx:Context):
        self.data = DictVar(None)
        # print('## DictExpr.do1 self.data:', self.data)
        for exp in self.exprList:
            # print('dictExp. next:', exp)
            exp.do(ctx)
            key, val = exp.get()
            self.data.setVal(key, val)
        # print('## DictExpr.do2 self.data:', self.data)

    def get(self):
        # print('## DictExpr.get self.data:', self.data)
        return self.data


class DictConstr(MultilineVal, DictExpr):
    ''' dict '''

    def __init__(self):
        super().__init__()


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
        self.varExpr.do(ctx) # before []
        self.target = self.varExpr.get() # found collection
        # print('## self.target', self.target)
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
        self.target:ListVar = None
        self.varExpr:Expression = None
        self.beginExpr = None
        self.closeExpr = None
        
    def setVarExpr(self, exp:Expression):
        self.varExpr = exp

    def setKeysExpr(self, beginExpr:Expression, closeExpr:Expression):
        ''' openExpr, closeExpr'''
        if isinstance(beginExpr, NothingExpr):
            beginExpr = ValExpr(Var(0, None, TypeInt))
        # if isinstance(closeExpr, NothingExpr):
        #     closeExpr = ValExpr(Var(-1, None, TypeInt))
        self.beginExpr = beginExpr
        self.closeExpr = closeExpr

    def do(self, ctx:Context):
        self.target = None
        self.varExpr.do(ctx) # before []
        self.target = self.varExpr.get() # found collection
        self.beginExpr.do(ctx)
        self.closeExpr.do(ctx)
        if isinstance(self.closeExpr, NothingExpr):
            self.closeExpr = ValExpr(Var(self.target.len(), None, TypeInt))
        print('## self.target', self.target)

    def get(self)->Var:
        beg, end = self.beginExpr.get(), self.closeExpr.get()
        res = self.target.getSlice(beg.get(), end.get())
        return res


class TupleExpr(CollectionExpr):
    ''' res = (a, b, c); res = a, b, c '''

    def __init__(self):
        super().__init__()
        self.valsExpr:list[Expression] = []
        self.obj:ListVar = None

    def add(self, exp:Expression):
        ''' add next elem of list'''
        self.valsExpr.append(exp)

    def do(self, ctx:Context):
        self.obj = TupleVar(None)
        for exp in self.valsExpr:
            exp.do(ctx)
            self.obj.addVal(exp.get())

    def get(self):
        return self.obj
