
'''
Eval tree nodes: operators.

'''


from lang import *
from vars import *
from expression import *


class OperCommand(Expression):
    
    def __init__(self, oper):
        self.oper:str = oper
        self.res = None

    def get(self):
        print('# -> OperCommand.get() ', self.oper, self.res)
        return self.res

class OpAssign(OperCommand):
    ''' Set value `=` '''
    def __init__(self, left:Var|list[Var], right:Expression|list[Expression]):
        super().__init__('=')
        # self.oper = '='
        print('OpAssign__init', left, right)
        self.left:Var|list[Var] = left
        self.right:Expression|list[Expression] = right # maybe 1 only, tuple Expression with several subs inside

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
        print('#b3-s', src[0])
        print('#b3-d', self.left[0])
        resSet:list[Var] = [None]*size
        for i in range(size):
            src[i].do(ctx)
            tVal:Var = src[i].get() # val (anon var obj) from expression
            print('## op-assign, val = ', tVal.get(), tVal.name, tVal.getType())
            resSet[i] = tVal
        for  i in range(size):
            if isinstance(self.left[i], VarExpr_):
                # skip _ var
                continue
            # self.left[i].set(resSet[i].get()) # internal val from var obj
            # resSet[i].name = self.left[i].name
            self.left[i].set(resSet[i].get()) # internal val from var obj
            # dinamic typing
            self.left[i].setType(resSet[i].getType()) # type from var obj
            ctx.update(self.left[i].name, self.left[i]) # update context
            
        # TODO: think about multiresult expressions: a, b, c = trival(); // return 11, 22, 'ccc'
        # TODO: thik about one way of assignment: (something) = (something)

        # if len(self.left) == 1:
        #     # simple case
        #     var:VarExpr = self.left[0]
        #     self.right.do(ctx)
        #     varVal = self.right.get()
        #     # var.var.set(varVal)
        #     ctx.vars[var.var.name] = varVal
        # else:
        #     # if  matching of few vals...
        #     pass

class BinOper(OperCommand):
    
    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper)
        # self.oper = oper
        self.left = left
        self.right = right
    
    def setArgs(self, left:Expression, right:Expression):
        self.left = left
        self.right = right


class OpMath(BinOper):
    ''' simple impl of math operators: + - * /  ** %'''
    
    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper, left, right)
        # self.oper = oper
        # self.left = left
        # self.right = right
        # self.res
        
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
        # print('#tn1:', self.left, self.right)
        a, b = self.left.get(), self.right.get()
        # print('#tn1:', self.left.get(), self.right.get())
        print('#tn2:', self.oper, a.get(), b.get())
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
        print('#--OpCompare.do1', '`%s`'%self.oper,  self.left, self.right)
        print('#--OpCompare.do2',  a, b)
        print('#--OpCompare.do3',  a.get(), b.get())
        print('#--OpCompare.do3',  a.getType(), b.getType())
        type = a.getType()
        if type != b.getType():
            # naive impl: different types are not equal
            # return False
            # TODO: fix type comparison
            pass
        res = ff[self.oper](a.get(), b.get())
        print('# == == OpCompare.do ', res)
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


# class OpEqual(BinOper):
#     ''' Is equal `==` '''
#     def __init__(self, oper, left:Expression, right:Expression):
#         self.oper = '=='
#         self.oper = oper
#         self.left = left
#         self.right = right
#         self.res = None

#     def do(self, ctx:Context):
#         self.left.do(ctx)
#         self.right.do(ctx)
#         # get val objects from expressions
#         a, b = self.left.get(), self.right.get()
#         self.res = a.get() == b.get()

#     def get(self):
#         return self.res
