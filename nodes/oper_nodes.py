
'''
Eval tree nodes: operators.

'''


from lang import *
from vars import *
from nodes.expression import *
from nodes.structs import StructInstance

class OperCommand(Expression):
    
    def __init__(self, oper):
        self.src = ''
        self.oper:str = oper
        self.res = None
        self._block = False

    def get(self):
        # print('# -> OperCommand.get() ', self.oper, self.res)
        return self.res

    def isBlock(self)->bool:
        ''' can be changed for multi-line assignment expressions '''
        return self._block

class BinOper(OperCommand):

    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper)
        # self.oper = oper
        self.left:Expression = left
        self.right:Expression = right

    def setArgs(self, left:Expression|list[Expression], right:Expression|list[Expression]):
        # print('BinOper.setArgs', left, right)
        self.left = left
        self.right = right


class OpAssign(OperCommand):
    ''' Set value `=` '''
    def __init__(self, left:Expression|list[Expression]=None, right:Expression|list[Expression]=None):
        super().__init__('=')
        self.left:Var|list[Expression]|Expression = left
        self.right:Expression|list[Expression] = right # maybe 1 only, tuple Expression with several subs inside

    def setArgs(self, left:Expression|list[Expression], right:Expression|list[Expression]):
        '''
        left - dest
        right - src
        '''
        print('OpAssign__setArgs1', left, right)
        self.left = left
        print('isinstance(right, MultilineVal) = ', isinstance(right, MultilineVal))
        # print('isinstance(right, ) = ', right))
        r0 = None
        if isinstance(right, list):
            r0 = right[0]
        else:
            r0 = right
        if isinstance(r0, MultilineVal):
            print('-- dict here')
            self._block = True
            right = r0
        self.right = right

    def add(self, expr:Expression):
        ''' where right is MultilineVal '''
        self.right.add(expr)

    def do(self, ctx:Context):
        ''' var = src'''
        src = self.right
        if not isinstance(src, list):
            src = [src]
        size = len(src)
        if not isinstance(self.left, list):
            self.left = [self.left]
        if len(self.left) != size:
            raise InerpretErr('Count of left and right parts of assignment are different')

        # 1 or more asignments: a, b, c = 1, 2, 3
        ctx.print()
        # print('#b3-srs0', src[0])
        # print('#b3-dtcn', self.left[0])
        resSet:list[Var] = [None]*size
        for i in range(size):
            src[i].do(ctx)
            tVal:Var = src[i].get() # val (anon var obj) from expression
            # print('## op-assign, src.get() -> ', tVal, ':', tVal.name, tVal.get(), tVal.getType())
            resSet[i] = tVal
        for  i in range(size):
            if isinstance(self.left[i], VarExpr_):
                # skip _ var
                continue
            print(' (a = b) :1')
            # eval left expressopm
            self.left[i].do(ctx)
            print(' (a = b) :2')
            val = resSet[i]
            if isinstance(self.left[i], CollectElemExpr):
                ''' '''
                val.name = None
                self.left[i].set(val)
                return
            
            #get destination var
            dest = self.left[i].get()
            print('# op-assign set1, varX, valX:', self.left[i], src[i])
            print('# op-assign set2, var-type:', dest.getType().__class__)
            # print('# op-assign set,',' val = ', type(resSet[i]))
            print(' (a = b) dest =', dest, ' val = ', val)
            if isinstance(dest.getType(), TypeStruct):
                dest.set(val)
                print('!!!!!! struct', dest)
                return
                
                # dest.set()
            # single var
            name = dest.name
            dest = val
            dest.name = name
            ctx.update(dest.name, val)
            ctx.update(dest.name, resSet[i])
            saved = ctx.get('n')
            print(' (a = b) saved ', saved)


        # TODO: think about multiresult expressions: a, b, c = triple_vals(); // return 11, 22, 'ccc'
        # TODO: thik about one way of assignment: (something) = (something)


class OpMath(BinOper):
    ''' simple impl of math operators: + - * /  ** %'''
    
    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper, left, right)

    def do(self, ctx:Context):
        ff = {
            '+': self.plus, 
            '-': self.minus,
            '*': self.mult,
            '/': self.div,
            '**': self.pow,
            '%': self.divmod,
            '<<': self.lshift,
            '>>': self.rshift
        }
        # eval expressions
        self.left.do(ctx)
        self.right.do(ctx)
        # get val objects from expressions
        print('#bin-oper1:', self.left, self.right) # expressions
        a, b = self.left.get(), self.right.get() # Var objects
        # print('#bin-oper2', a, b)
        print(' ( %s )' % self.oper, a.get(), b.get())
        type = a.getType()
        if type != b.getType():
            # TODO fix different types
            pass
        # get numeric values and call math function 
        val = ff[self.oper](a.get(), b.get())
        self.res = Var(val, None, type)
        
    def plus(self, a, b):
        return a + b

    def minus(self, a, b):
        return a - b
    
    def mult(self, a, b):
        return a * b

    def div(self, a, b):
        return a / b

    def pow(self, a, b):
        return a ** b

    def divmod(self, a, b):
        return a % b

    def lshift(self, a, b):
        return a << b

    def rshift(self, a, b):
        return a >> b


class OpMathAssign(OperCommand):
    ''' a += 5; a += b; a += foo(b); a += foo(b) - 5/c '''


class OpBinBool(BinOper):
    ''' simple impl of bool logic: && || '''
    
    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper, left, right)

    def do(self, ctx:Context):
        ff = {
            '&&': self.op_and, 
            '||': self.op_or,
        }
        # eval expressions
        self.left.do(ctx)
        self.right.do(ctx)
        # get val objects from expressions
        a, b = self.left.get(), self.right.get()
        print(' ( %s )' % self.oper, a.get(), b.get())
        type = a.getType()
        if type != b.getType():
            # naive impl: different types are not equal
            return False
        res = ff[self.oper](a.get(), b.get())
        self.res = Var(res, None, a.getType())
    
    def op_and(self, a, b):
        return a and b
    
    def op_or(self, a, b):
        return a or b


class OpCompare(BinOper):
    ''' == != > < >= < <=  '''
    
    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper, left, right)

    def do(self, ctx:Context):
        ff = {
            '==': self.eq,
            '!=': self.not_eq,
            '<': self.less,
            '<=': self.less_eq,
            '>': self.more,
            '>=': self.more_eq,
        }
        # eval expressions
        self.left.do(ctx)
        self.right.do(ctx)
        # get val objects from expressions
        a, b = self.left.get(), self.right.get()
        # print('( %s )' % self.oper,  self.left, self.right)
        # print('#--OpCompare.do2',  a, b)
        print(' ( %s )' % self.oper,  a.get(), b.get())
        # print('#--OpCompare.do3',  a.getType(), b.getType())
        type = a.getType()
        if type != b.getType():
            # naive impl: different types are not equal
            # return False
            # TODO: fix type comparison
            pass
        res = ff[self.oper](a.get(), b.get())
        # print('# == == OpCompare.do ', res)
        self.res = Var(res, None, TypeBool)


    def eq(self, a, b):
        return a == b
    
    def not_eq(self, a, b):
        return a != b
    
    def less(self, a, b):
        return a < b
    
    def less_eq(self, a, b):
        return a <= b
    
    def more(self, a, b):
        return a > b
    
    def more_eq(self, a, b):
        return a >= b


class OpBitwise(BinOper):
    ''' & | ^  '''

    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper, left, right)

    def do(self, ctx:Context):
        ff = {
            '&': self.bt_and,
            '|': self.bt_or,
            '^': self.bt_xor,
        }
        # eval expressions
        self.left.do(ctx)
        self.right.do(ctx)
        # get val objects from expressions
        a, b = self.left.get(), self.right.get()
        type = a.getType()
        if type != b.getType():
            # TODO type??
            return False
        res = ff[self.oper](a.get(), b.get())
        self.res = Var(res, None, a.getType())

    def bt_and(self, a, b):
        return a & b
    
    def bt_or(self, a, b):
        return a | b
    
    def bt_xor(self, a, b):
        return a ^ b


class OpDot(BinOper):
    ''' inst.field
        expr.expr.expr.expr
        expr.method()
        get member from object
    '''

    def __init__(self, left:Expression=None, right:Expression=None):
        super().__init__('.', left, right)

    def do(self, ctx:Context):
        self.left.do(ctx) # find object (struct instance)
        inst = self.left.get()
        field = self.right.name
        self.res = inst.get(field)
        print('oper .... ', inst, field,' :: ', self.res)

    # def get(self):
    #     # print('# -> OperCommand.get() ', self.oper, self.res)
    #     return self.res


class UnarOper(OperCommand):
    def __init__(self, oper:str, inner:Expression=None):
        super().__init__(oper)
        self.inner = inner
        # self.res = None

    def setInner(self, inner:Expression):
        self.inner = inner


class BoolNot(UnarOper):
    def __init__(self, oper:str, inner:Expression=None):
        super().__init__(oper, inner)
        
    def do(self, ctx:Context):
        self.inner.do(ctx)
        inVal = self.inner.get()
        res = not inVal.get()
        self.res = Var(res, None, inVal.getType())


class BitNot(UnarOper):
    def __init__(self, oper:str, inner:Expression=None):
        super().__init__(oper, inner)

    def do(self, ctx:Context):
        self.inner.do(ctx)
        inVal = self.inner.get()
        res = ~inVal.get()
        self.res = Var(res, None, inVal.getType())


class UnarSign(UnarOper):
    ''' + - '''
    def __init__(self, oper:str, inner:Expression=None):
        super().__init__(oper, inner)

    def do(self, ctx:Context):
        self.inner.do(ctx)
        inVal = self.inner.get()
        num = inVal.get()
        if self.oper == '-':
            num = -num
        self.res = Var(num, None, inVal.getType())

    # def negative(self, x):
    #     return -x


class MultiOper(OperCommand):
    ''' All expressions with more than 1 operator: (2 + 5 * 7) '''
    def __init__(self, exp:Expression=None):
        self.root:Expression = exp
        # self.res = None
        
    def setInner(self, exp:Expression):
        self.root = exp

    def do(self, ctx:Context):
        ''' '''
        self.root.do(ctx)
        # self.res = self.root.get()

    def get(self):
        return self.root.get()


class ServPairExpr(BinOper):
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
        super().__init__(':')
        self.left:Expression = None # key|name|def
        self.right:Expression = None # val|type

    def do(self, ctx:Context):
        self.left.do(ctx)
        self.right.do(ctx)

    def get(self):
        return self.left.get(), self.right.get()

# BinOper
class OperDot(Expression):
    ''' inst.field '''

    def __init__(self):
        self.objExp:VarExpr = None
        self.field:str = ''
        self.val:Var = None

    def set(self, inst:VarExpr, field:VarExpr):
        self.objExp = inst
        self.field = field.name

    def do(self, ctx:Context):
        # print('StructField.do1', self.objExp, self.field)
        self.objExp.do(ctx)
        inst:StructInstance = self.objExp.get()
        self.val = inst.get(self.field)
        # print('StructField.do2', inst, self.val)

    def get(self):
        return self.val



# class OpColon(OperCommand):
#     ''' `a : b` expr in dict '''

#     def __init__(self,):
#         super().__init__(':')

#     def do(self, ctx:Context):
        # pass

