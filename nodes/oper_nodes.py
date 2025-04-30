
'''
Eval tree nodes: operators.

'''


from lang import *
from vars import *
# from typex import *
from nodes.expression import *
from nodes.structs import StructInstance
from nodes.func_expr import FuncCallExpr
from nodes.structs import MethodCallExpr
from nodes.structs import StructConstrBegin


class OperCommand(Expression):
    
    def __init__(self, oper):
        super().__init__(oper)
        self.src = ''
        self.oper:str = oper
        self.res = None
        # self._block = False

    def get(self):
        # print('# -> OperCommand.get() ', self.oper, self.res)
        return self.res

    # def isBlock(self)->bool:
    #     ''' can be changed for multi-line assignment expressions '''
    #     return self._block

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
        if isinstance(left, ServPairExpr):
            left = left.getTypedVar()

        self.left = left
        r0 = None
        if isinstance(right, list):
            r0 = right[0]
        else:
            r0 = right
        
        if isinstance(r0, VarExpr):
            exvar = r0.get()
            name = exvar.name
            # print('@@ exvar', name)
            if InterpretContext.get().hasStruct(name):
                # print('@@ struct Type here ')
                r0 = StructConstrBegin(name)
        
        if isinstance(r0, MultilineVal):
            # print('-- MultilineVal or Struct here')
            self.toBlock()
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
            raise InterpretErr('Count of left and right parts of assignment are different '
                               'left = %d, right = %d' % (len(self.left), len(self.right)))

        # ctx.print()
        resSet:list[Var] = [None]*size
        for i in range(size):
            print('OpAssign.do src[i]', src[i])
            src[i].do(ctx)
            ctx.print()
            tVal:Var = src[i].get() # val (anon var obj) from expression
            print('## op-assign, src.get() -> ', tVal, ':', tVal.get(), tVal.getType())
            resSet[i] = tVal
        for  i in range(size):
            if isinstance(self.left[i], VarExpr_):
                # skip _ var
                continue
            # print(' (a = b) :1')
            # eval left expressopm
            self.left[i].do(ctx)
            val = resSet[i]
            valType = val.getType()
            print(' (a = b) :2', val)
            if isinstance(val, ObjectMember):
                val = val.get()
            print(' (a = b) :3', val)
            if isinstance(val, Var):
                val = val.get()
            print(' (a = b) :4', val)
            
            if isinstance(self.left[i], CollectElem):
                ''' '''
                # print('(=) if dest CollectElem, val: ', val)
                val.name = None
                self.left[i].set(val)
                return
            
            #get destination var
            dest = self.left[i].get()
            print('Assign dest1 =', dest, '; val=', val)
            isNew = False
            self.res = val
            if isinstance(dest, VarUndefined):
                # new var for assignment
                isNew = True
                newVar = Var(dest.name, valType)
                print('Assign new var', newVar, 'val-type:', valType)
                ctx.addVar(newVar)
                dest = newVar
            dest.set(val)
                
            # print('# op-assign set1, varX, valX:', self.left[i], src[i])
            print('# op-assign set2, var-type:', dest, ' dest.class=', dest.getType().__class__)
            # print('# op-assign set,',' val = ', type(resSet[i]))
            print(' (a = b) dest =', dest, ' val = ', val, 'isNew:', isNew)
                
            if isinstance(dest, ObjectMember):
                # struct field as left operand
                # print('!!!!!! struct.2', dest, dest.object, dest.member)
                dest.set(val)
                # raise EvalErr(' = ObjMem')
                return

            # print(' (a = b) dest2: ', dest)
            # single var
            name = dest.name
            # dest = val
            # dest.name = name
            # dest.set(val)
            
            # ctx.update(dest.name, val)
            
            self.res = val
            # ctx.update(dest.name, resSet[i])
            saved = ctx.get(name)
            print(' (a = b) saved ', saved)


        # TODO: think about multiresult expressions: a, b, c = triple_vals(); // return 11, 22, 'ccc'
        # TODO: thik about one way of assignment: (something) = (something)


class OpBinAssign(OpAssign):
    ''' += -= *= /= %= '''
    def __init__(self, oper):
        super().__init__()
        self.oper = oper
        self.moper = self.splitOper(oper)

    def splitOper(self, oper):
        print('OpBinAssign biOper:', oper)
        return OpMath(oper[0])

    def setArgs(self, left:Expression|list[Expression], right:Expression|list[Expression]):
        super().setArgs(left, right)
        self.moper.setArgs(self.left, self.right)
        self.right = self.moper


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
        print('#bin-oper1:',' ( %s )' % self.oper, self.left, self.right) # expressions
        # get val objects from expressions
        a, b = self.left.get(), self.right.get() # Var objects
        print('#bin-oper2', a, b)
        print(' ( %s )' % self.oper, a.getVal(), b.getVal())
        print(' (%s %s %s)' % (a.getType(), self.oper, b.getType()))
        type = a.getType()
        if type != b.getType():
            # TODO fix different types
            pass
        # get numeric values and call math function 
        val = ff[self.oper](a.getVal(), b.getVal())
        self.res = Val(val, type)
        
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
        print(' ( %s )' % self.oper, a.getVal(), b.getVal())
        print(' (types)', a.getType(), b.getType())
        # TODOO: type check needs further development
        # vtype = a.getType()
        # if not isinstance(vtype, TypeAny) and not isinstance(b.getType(), TypeAny) and vtype != b.getType():
        #     # naive impl: different types are not equal
        #     print('break comarison because types not equal %s <> %s' % (a.getType(), b.getType()) )
        #     return False
        res = ff[self.oper](a.getVal(), b.getVal())
        print('# == == OpCompare.do ', res)
        self.res = Val(res, TypeBool)
    
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
        print('( %s )' % self.oper,  self.left, self.right)
        # print('#--OpCompare.do2',  a, b)
        print(' ( %s )' % self.oper,  a.getVal(), b.getVal())
        # print('#--OpCompare.do3',  a.getType(), b.getType())
        type = a.getType()
        if type != b.getType():
            # naive impl: different types are not equal
            # return False
            # TODO: fix type comparison
            pass
        res = ff[self.oper](a.getVal(), b.getVal())
        # print('# == == OpCompare.do ', res)
        self.res = Val(res, TypeBool)


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
        res = ff[self.oper](a.getVal(), b.getVal())
        self.res = Val(res, a.getType())

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
        # print(' !x', self.inner, inVal)
        res = not inVal.getVal()
        self.res = Val(res, inVal.getType())


class BitNot(UnarOper):
    def __init__(self, oper:str, inner:Expression=None):
        super().__init__(oper, inner)

    def do(self, ctx:Context):
        self.inner.do(ctx)
        inVal = self.inner.get()
        res = ~inVal.getVal()
        self.res = Val(res, inVal.getType())


class UnarSign(UnarOper):
    ''' + - '''
    def __init__(self, oper:str, inner:Expression=None):
        super().__init__(oper, inner)

    def do(self, ctx:Context):
        self.inner.do(ctx)
        inVal = self.inner.get()
        num = inVal.getVal()
        if self.oper == '-':
            num = -num
        self.res = Val(num, inVal.getType())

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


class ObjectMember(Val):
    ''' '''
    def __init__(self, obj, member):
        super().__init__(None, TypeAccess)
        self.object:StructInstance = None
        self.member:str = None
        self.setArgs(obj, member)

    def setArgs(self, obj, member):
        print('ObjectMember.setArgs (', obj, ' -> ', member, ')')
        self.object = obj
        self.member = member

    def getVal(self):
        return self.get().getVal()

    def get(self):
        ''' res = obj.member; foo(obj.member); obj.member() '''
        print('self.member, get :: ',self.object, type(self.object), '::', self.member)
        val = self.object.get(self.member)
        
        print('ObjectMember, get :: obj, member, val: ', self.object, self.member, val)
        if isinstance(val, (StructInstance, Val)):
            # print('membrr get struct')
            return val
        return val.get()
    
    def getType(self):
        val = self.object.get(self.member)
        return val.getType()
    
    def set(self, val:Val):
        ''' obj.member = expr; obj.member[key] = expr (looks like a.b[c] is an subcase of a.b) '''
        print('ObjectMember.set self.member, val :: ', self.member, val)
        self.object.set(self.member, val)

    def __str__(self):
        return "node ObjectMember(inst=%s, name=%s)" % (self.object, self.member)


# BinOper
class OperDot(BinOper):
    ''' inst.field '''

    def __init__(self):
        super().__init__('.')
        # obj, foo(), arr[key], obj.sub 
        self.objExp:VarExpr = None
        # obj.field, obj.meth(), obj.field[key]
        self.membExpr:Expression = None
        self.val:ObjectMember= None

    def setArgs(self, inst:VarExpr, member:VarExpr):
        self.objExp = inst
        if isinstance(member, FuncCallExpr):
            member = MethodCallExpr(member)
        self.membExpr = member
        print('   >> OperDot.set', self.objExp, self.membExpr)

    def do(self, ctx:NSContext):
        print('OperDot.do0', self.objExp, '; type=', type(self.objExp), ' :: ', self.membExpr)
        self.objExp.do(ctx)
        objVar = self.objExp.get()
        print('OperDot.do00', objVar, '; type=', type(objVar))
        if isinstance(objVar, Var):
            objVar = objVar.get()
        inst:StructInstance = objVar
        print('OperDot.do1 inst:', inst, 'memExp:', self.membExpr)
        # self.membExpr.do(inst)
        name = ''
        
        if isinstance(self.membExpr, MethodCallExpr):
            print('OperDot.do3 method1 =', self.membExpr, type(self.membExpr), '; methodname:', self.membExpr.name)
            # TODO: refactor to: 1. return func-member; 2. call method as usage of `()` operator
            self.membExpr.setInstance(inst)
            self.membExpr.do(ctx)
            self.val = self.membExpr.get()
            print('OperDot.do4 method res =', self.val)
            return
        
        if isinstance(self.membExpr, VarExpr):
            name = self.membExpr.name # just name for struct
        else:
            # exp.get() - for array or dimanic field name obj.(fieldName(args))
            self.membExpr.do(ctx)
            sub = self.membExpr.get()
            name = sub.get()

        if isinstance(inst, ObjectMember):
            inst = inst.get()

        # print('OperDot.do2 <inst =', inst, 'name=', name ,'>')
        self.val = ObjectMember(inst, name)
        print('OperDot.do5 fin field =', self.val)

    def get(self):
        return self.val
