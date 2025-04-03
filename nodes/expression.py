'''
Base expression objects.
'''
from collections.abc import  Callable

from vars import *
from context import *

class Expression:
    def __init__(self, val=None, src:str=''):
        self.val = val
        self.block = False
        self.src:str = src
    
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
        self.val:Var = var

    def do(self, ctx:Context):
        pass

    def get(self)->Var:
        # print('#tn2-valEx-get:', self.val, self.val.get())
        return self.val

    def __str__(self):
        return 'ValExpr(%s)' % self.val


class VarExpr(Expression):
    def __init__(self, var:Var):
        self.val = var # or name,type ?
        self.name = var.name
    
    def do(self, ctx:Context):
        print('VarExpr.do ctx:', ctx, 'name=', self.name)
        newVal = ctx.get(self.name)
        print('VarExpr.do:', newVal)
        self.val = newVal
    
    # def set(self, val:Var):
    #     self.var = val.get()

    def get(self)->Var:
        return self.val

    def __str__(self):
        return 'VarExpr(%s, %s)' % (self.name, self.val)

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


class DebugExpr(Expression):
    def __init__(self, txt):
        print('**** DEBUG__init:', txt)
        self.val = txt
    
    def do(self, ctx:Context):
        print(" $$$ DEBUG: ", self.val)


# class Command(Expression):
#     def do(self, var:Var, src:Expression):
#         pass
    
#     def get(self):
#         return self.val


class ControlExpr(Expression):
    ''' for, if, match '''


class Block(Expression):
    def __init__(self):
        # self.ctx = Context()
        self.subs: list[Expression] = []
        self.storeRes = False
        self.lastVal:Var|list[Var] = None # result of last sequence, can be a list if many results: a, b, [1,2,3]

    def add(self, seqs:Expression|list[Expression]):
        if not isinstance(seqs, list):
            seqs = [seqs]
        self.subs.extend(seqs)

    def isEmpty(self):
        return len(self.subs)

    def do(self, ctx:Context):
        self.lastVal = None
        # eval sequences one by one, store result of each line, change vars in contexts
        elen = len(self.subs)
        if elen < 1:
            return
        lastInd = 0
        # self.ctx.upper = ctx
        print('!! Block.do')
        ctx.print()
        self.lastVal = None
        for i in range(elen):
            print('!! Block.iter ', i, self.subs[i])
            expr = self.subs[i]
            expr.do(ctx)
            if isinstance(expr, (DefinitionExpr)):
                # Skip actions with result
                continue
            lastInd = i
            lineRes = None
            lineRes = expr.get()
            if isinstance(lineRes, FuncRes):
                print(' - return::', lineRes)
            # if not isinstance(expr, Block) or expr.storeRes:
            #     lineRes = expr.get()
            # print(' - - Block.iter lineRes', lineRes)
            if isinstance(lineRes, FuncRes):
                # return expr
                self.lastVal = lineRes
                return
        if self.storeRes:
            self.lastVal = self.subs[lastInd].get()

    def get(self) -> list[Var]:
        return self.lastVal
    
    def isBlock(self)->bool:
        ''' True if one of: func, for, if, match, case'''
        return True


class ControlBlock(Block, ControlExpr):
    ''''''

class LoopBlock(ControlBlock):
    ''' '''
    
    def __init__(self):
        super().__init__()
        self.block:Block = Block() # empty block on start


class CollectionExpr(Expression):
    ''''''
    def addVal(self, val:Var):
        pass
    
    def setVal(self, index:Var, val:Var):
        pass

    def getVal(self, index:Var):
        pass


class MultilineVal:
    ''' begiinning of multiline declaration '''



class CollectElemExpr(Expression):
    
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

class TypeExpr(Expression):
    ''' int, string, bool, list, struct '''
    
    def __init__(self, val=None):
        # super().__init__(val)
        self.type:VType = Undefined
    
    def do(self, ctx:Context):
        ''' '''
    
    def get(self)->VType:
        ''' return '''

class DeclarationExpr(Expression):
    ''' var:type declaration '''
    
    def __init__(self):
        # super().__init__(val)
        self.var:Var = None
        self.varExpr:VarExpr = None
        self.typeExpr:TypeExpr = None
    
    def do(self, ctx:Context):
        self.typeExpr.do(ctx)
        self.var = self.varExpr.do(ctx)
        self.var.setType(self.typeExpr.get())
    
    def get(self)->Var:
        ''' return '''

class DefinitionExpr(Expression):
    ''' base for struct, function, alias
        func foo(arg1, arg2)
            expr
            expr

        struct User
            name: string
            age: int
            address: Address
    '''


class ServPairExpr(Expression):
    ''' service expression, works accordingly to context:
        - in dict 
        {a : b} >> key(Var):value(Var)
        - in var declaration:
        var with type >> name : type
        user: User; counter: int
        - in func definition
        func args and res type >> func-expr : type
        func foo(a:int, b:list): int
        - in field expression into struct type definition
        struct User
            name: string
            age: int
    '''

    def __init__(self):
        # super().__init__(':')
        self.left:Expression = None # key|name|def
        self.right:Expression = None # val|type

    def do(self, ctx:Context):
        self.left.do(ctx)
        self.right.do(ctx)

    def get(self):
        return self.left.get(), self.right.get()
    
    def getTypedVar(self):
        return TypedVarExpr(self.left, self.right)

    def setArgs(self, left:Expression|list[Expression], right:Expression|list[Expression]):
        # print('BinOper.setArgs', left, right)
        self.left = left
        self.right = right


class VarStrict(Var):
    ''' strict typed var '''
    def __init__(self, val, name, vtype):
        super().__init__(val, name, None)
        self.__type = vtype
    
    def getType(self):
        return self.__type


class TypedVarExpr(VarExpr):
    ''' name: type '''
    def __init__(self, left, right):
        var = Var(None)
        super().__init__(var)
        self.left = left
        self.right = right

    def do(self, ctx):
        self.right.do(ctx)
        tp = self.right.get()
        name = self.left.get().name
        # print('TypedVarExpr.do1 ', name, tp.get())
        self.val = VarStrict(None, name, tp.get())
        ctx.addVar(self.val)

