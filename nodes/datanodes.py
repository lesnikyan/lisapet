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

    # def do(self, ctx:Context):
    #     self.data = DictVar(None)


# class StructDefExpr(Block):
#     ''' struct User
#             name: string
#             age: int
#             weight: float
#     '''


# class StructFieldExpr(VarExpr):
#     ''' inst.field = val; var = inst.field '''



class TupleExpr(CollectionExpr):
    ''' res = (a, b, c); res = a, b, c '''
