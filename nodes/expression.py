'''
Base expression objects.
'''
from collections.abc import  Callable

from vars import *
from typex import *
from context import *




def repr(obj):
    if not obj:
        return str(obj)
    return '%s= %s' % (obj.__class__.__name__, '~%03d' % (hash(obj) % 1000))

class Expression:
    def __init__(self, val=None, src=None):
        self.val = val
        self.__block = False
        # dprint('Expression init', self)
        self.src:CLine = src
    
    def do(self, ctx:NSContext):
        pass
    
    def get(self) -> Var|list[Var]:
        return self.val
    
    def isBlock(self)->bool:
        ''' True if one of: func, for, if, match, case'''
        return self.__block

    def toBlock(self):
        self.__block = True
    
    def __str__(self):
        return self.__class__.__name__

    add = None


class CommentExpr(Expression):
    ''' for future usage'''
    def __init__(self, text:str):
        '''' text of comment line is value '''
        super().__init__(text)


class NothingExpr(Expression):
    ''' nothing, empty plase in code or skipper lexem '''
    def __init__(self):
        '''' '''
        super().__init__('')


class ValExpr(Expression):
    def __init__(self, val:Val):
        super().__init__(val)

    def do(self, ctx:NSContext):
        pass

    def get(self)->Var:
        # dprint('#tn2-valEx-get:', self.val, self.val.get())
        return self.val

    def __str__(self):
        return 'ValExpr(%s)' % self.val


class VarExpr(Expression):
    def __init__(self, var:Var):
        super().__init__(var)
        # self.val = var # or name,type ?
        self.name = var.name
    
    def do(self, ctx:NSContext):
        # dprint('VarExpr.do ctx:', ctx, 'name=', self.name)
        # ctx.print(forsed=1)
        newVal = ctx.get(self.name)
        # print('VarExpr.do:', self.name, newVal)
        self.val = newVal
    
    # def set(self, val:Var):
    #     self.var = val.get()

    def get(self)->Var:
        return self.val

    def __str__(self):
        # dprint('VVV', self)
        return '%s(%s, %s)' % (self.__class__.__name__, self.name, self.val)


class ArgExpr(VarExpr):
    def __init__(self, var:Var):
        super().__init__(var)
        self.defVal = None

class ArgSetOrd(Var):
    def __init__(self, name):
        super().__init__(name, TypeList())
        self.vals = []
    
    def add(self, elem:Val):
        self.vals.append(elem)


class ArgSetNamed:
    def __init__(self):
        # super().__init__(val, vtype)
        self.elems = {}
    
    def add(self, name:str, elem:Val):
        self.elems[name] = elem


class ArgExtList(ArgExpr):
    def __init__(self, var:Var):
        super().__init__(var)


class ArgExtDict(ArgExpr):
    def __init__(self, var:Var):
        super().__init__(var)


class VarExpr_(VarExpr):
    def __init__(self, var:Var=None):
        super().__init__(Var_())
        self.name = '_'
    
    def do(self, ctx:NSContext):
        ''' nothing to do'''

    def get(self)->None:
        ''' nothing to do'''

    def set(self, x):
        ''' nothing to do'''

    def __str__(self):
        return 'VarExpr_(_)'


class DebugExpr(Expression):
    def __init__(self, txt):
        dprint('**** DEBUG__init:', txt)
        super().__init__()
        self.val = txt
    
    def do(self, ctx:NSContext):
        dprint(" $$$ >>> >>> DEBUG: ", self.val)


class ControlExpr(Expression):
    ''' for, if, match '''


class Block(Expression):
    def __init__(self):
        super().__init__()
        self.subs: list[Expression] = []
        self.skipLines = []
        self.storeRes = False
        self.lastVal:Var|list[Var] = None # result of last sequence, can be a list if many results: a, b, [1,2,3]

    def add(self, seqs:Expression|list[Expression]):
        if not isinstance(seqs, list):
            seqs = [seqs]
        self.subs.extend(seqs)
        # print('Block.add:', type(self), '::', self.subs)

    def isEmpty(self):
        return self.linesIter() < 1

    def linesIter(self):
        return len(self.subs)

    def do(self, ctx:NSContext):
        self.lastVal = None
        # eval sequences one by one, store result of each line, change vars in contexts
        # elen = len(self.subs)
        if self.isEmpty():
            return
        lastInd = 0
        # print('!! Block.do', self.storeRes)
        self.lastVal = None
        for i in range(self.linesIter()):
            # print('!! Block.iter ', i, self.subs[i])
            expr = self.subs[i]
            # print('!! Block.iter ', i, expr, expSrc(expr) ) # '{{ %s }}' % expr.src.src.src
            expr.do(ctx)
            if isinstance(expr, (DefinitionExpr)): # and not isinstance(expr, (ObjDefExpr))
                # Skip actions with result
                continue
            lastInd = i
            # lineRes = None
            lineRes = expr.get()
            if isinstance(lineRes, FuncRes):
                # dprint(' - return::', lineRes)
                self.lastVal = lineRes
                return
            if isinstance(lineRes, (PopupBreak, PopupContinue)):
                # break, continue
                # print(' - block stop ::', lineRes, type(lineRes))
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


class CollectElem:
    ''' dataVar[key-or-index] '''


class TypeExpr(Expression):
    ''' int, string, bool, list, struct '''
    
    def __init__(self, val=None):
        # super().__init__(val)
        self.type:VType = Undefined
    
    def do(self, ctx:NSContext):
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
    
    def do(self, ctx:NSContext):
        self.typeExpr.do(ctx)
        self.var = self.varExpr.do(ctx)
        self.var.setType(self.typeExpr.get())

    def get(self)->Var:
        ''' return '''


class DefinitionExpr(Expression):
    ''' base for struct, alias

        struct User
            name: string
            age: int
            address: Address
    '''

class ObjDefExpr(Expression):
    ''' definition which can return value
    function
        func foo(arg1, arg2)
            expr
            expr
    lambda
    '''


class SkippedExpr(VarExpr):
    ''' Literally - nothing in the place wher ewe are waiting some value.
        Special case for list slices, generators, etc.
    '''
    def __init__(self):
        super().__init__(None)


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
        super().__init__()
        self.left:Expression = None # key|name|def
        self.right:Expression = None # val|type

    def do(self, ctx:NSContext):
        self.left.do(ctx)
        self.right.do(ctx)

    def get(self):
        # ll, rr = self.left.get(), self.right.get()
        return self.left.get(), self.right.get()
    
    def getTypedVar(self):
        return TypedVarExpr(self.left, self.right)
    
    def getTypedArg(self):
        return TypedArgExpr(self.left, self.right)

    def setArgs(self, left:Expression|list[Expression], right:Expression|list[Expression]):
        # print('ServPairExpr.setArgs', left, right)
        self.left = left
        self.right = right

    def add(self, expr:Expression):
        ''' where right is MultilineVal '''
        self.right.add(expr)


class VarStrict(Var):
    ''' strict typed var '''
    def __init__(self, name, vtype):
        super().__init__(name, vtype)
        self.__type = vtype
    
    def getType(self):
        return self.__type


class TypedVarExpr(VarExpr):
    ''' name: type '''
    def __init__(self, left, right):
        # var:Var = None
        super().__init__(left)
        self.left = left
        self.right = right
        self.val = None

    def do(self, ctx:NSContext):
        self.right.do(ctx)
        tpv = self.right.get()
        name = self.left.get().name
        tpName = self.right.name
        # dprint('TypedVarExpr.ctx print:')
        # ctx.print()
        tpInst = ctx.getType(tpName)
        # print('TypedVarExpr.do/-1 ', ctx, '>', tpName, ':', tpInst)
        tpVal = TypeAny()
        if not tpInst:
            tpVal = Undefined()
        else:
            tpVal = tpInst.get()
        # print('TypedVarExpr.do1 ', name, 'tp:', tpv, '{%s: %s}' % (tpv.val, tpv.vtype), tpName)
        
        self.val = Var(name, tpVal, strict=True)
        ctx.addVar(self.val)


class TypedArgExpr(TypedVarExpr):
    '''  foo(x:int = 1) '''
    
    def __init__(self, left, right):
        # var:Var = None
        super().__init__(left, right)
        self.defVal = None


class InterpretContext:
    ''' store for specific details of interpretation process
        1. list of user-defined structs
        2. ?? functions
    '''
    
    __inst = None
    
    def __init__(self):
        self._structs = {}
    
    def addStruct(self, name):
        self._structs[name] = len(self._structs)
        
    def hasStruct(self, name):
        return name in self._structs

    @classmethod
    def get(cc):
        if cc.__inst is None:
            cc.__inst = InterpretContext()
        return cc.__inst


class SequenceExpr(Expression):
    
    def __init__(self, delim=None, src = ''):
        super().__init__(None, src)
        self.delim = delim
        self.subs = []
    
    def add(self, exp:Expression):
        self.subs.append(exp)

    def getDelim(self):
        return self.delim

    def getSubs(self):
        return self.subs

    def getVals(self, ctx:NSContext):
        res = []
        for sub in self.subs:
            dprint('SEQ getTuple:', sub)
            sub.do(ctx)
            res.append(sub.get())
        return res


class CallExpr(Expression):
    ''' expr() '''
    def doArgs(self, args:list, ctx: Context):
        pass


class StringExpr(ValExpr):
    def __init__(self, val:Val, quot):
        super().__init__(val)
        self.quot = quot

    def __str__(self):
        return 'StrExpr(%s)' % self.val


class MString(StringExpr, MultilineVal):
    
    def __init__(self, val, quot):
        super().__init__(val, quot)
        self.val = StringVal(''.join(val), TypeString())

    def add(self, next:'MString'):
        text = self.val.val + next.val.val
        self.val.val = text


class SFormatter:
    def formatString(self, code:str):
        pass

def expSrc(expr:Expression|ParseErr|InterpretErr):
    exsrc = '-=-'
    if expr and expr.src:
        if isinstance(expr.src, str):
            exsrc = expr.src
        if isinstance(expr.src, TLine):
            exsrc = expr.src.src
        elif isinstance(expr.src, CLine):
            exsrc = expr.src.src.src
        else:
            exsrc = str(expr.src)
    if expr is None:
        exsrc = 'None_src'
    return "`%s`" % exsrc


def defaultValOfType(tp: VType):
    match tp:
        case TypeStruct():
            return Val(Null(), TypeNull())
        case TypeAny() | TypeNull():
            return Val(Null(), TypeNull())
        case TypeBool():
            return Val(False, TypeBool())
        case TypeInt() | TypeFloat() | TypeComplex():
            return Val(0, tp) 
        case TypeString():
            return Val('', tp)
        case TypeList():
            return ListVal()
        case TypeDict():
            return DictVal()
        case TypeTuple():
            return TupleVal()
        case TypeStruct():
            return StringVal('') # TODO: resolve defined struct type: TypeName{}
        case TypeFunc():
            return Val(Null(), TypeNull())
    return tp.defVal()

