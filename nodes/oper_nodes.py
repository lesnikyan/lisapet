
'''
Eval tree nodes: operators.

'''

from lang import *
from vars import *
# from typex import *
from nodes.expression import *
from nodes.tnodes import MString
from nodes.structs import StructInstance
from nodes.func_expr import FuncCallExpr
from nodes.structs import MethodCallExpr
from nodes.structs import StructConstr, StructConstrBegin

# from formatter import  StrFormatter


class OperCommand(Expression):
    
    def __init__(self, oper):
        super().__init__(oper)
        self.src = ''
        self.oper:str = oper
        self.res = None
        self.__block = False

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
        # dprint('BinOper.setArgs', left, right)
        self.left = left
        self.right = right

class OpAssign(OperCommand):
    ''' Set value `=` '''
    def __init__(self, left:Expression|list[Expression]=None, right:Expression|list[Expression]=None):
        super().__init__('=')
        self.left:Var|list[Expression]|Expression = left
        self.right:Expression|list[Expression] = right # maybe 1 only, tuple Expression with several subs inside

    def setArgs(self, left:Expression, right:Expression):
        '''
        left - dest
        right - src
        '''
        dprint('OpAssign__setArgs1', left, right)
        self.left = left
        r0 = right
        
        if isinstance(r0, VarExpr):
            exvar = r0.get()
            name = exvar.name
            # dprint('@@ exvar', name)
            if InterpretContext.get().hasStruct(name):
                # dprint('@@ struct Type here ')
                r0 = StructConstrBegin(name)
        
        if isinstance(r0, MultilineVal):
            # dprint('-- MultilineVal or Struct here')
            self.toBlock()
            right = r0
        self.right = right

    def add(self, expr:Expression):
        ''' where right is MultilineVal '''
        self.right.add(expr)

    def doRight(self, ctx:Context, leftSize):
        src = self.right
        # Do right (val expr)
        # print('OpAssign.do src', src)
        resSet:list[Var] = []
        if isinstance(src, SequenceExpr):
            dprint('## op-assign, SequenceExpr src -> ', src, )
            resSet = src.getVals(ctx)
        else:
            src.do(ctx)
            tVal:Var = src.get() # val (anon var obj) from expression
            # dprint('## op-assign, src.get() -> ', tVal, ':', tVal.get(), tVal.getType())
            resSet.append(tVal)
        # ctx.print()
        if leftSize > 1 and len(resSet) == 1:
            # unpack colelction here
            tval = resSet[0]
            if isinstance(tval, Var):
                tval = resSet[0].getVal()
            
            dprint('resSet[0] to unpack:', resSet[0], tval)
            if not isinstance(tval, (ListVal, TupleVal)):
                raise EvalErr('Count of left and right parts of assignment are different '
                               'left = %d, right = %d' % (leftSize, len(resSet)))
            resSet = tval.rawVals()

        return resSet

    def leftSet(self):
        # prepare left operand
        if isinstance(self.left, SequenceExpr):
            left = self.left.getSubs()
        else:
            left = [self.left]
        
        pleft = []
        for lexp in left:
            if isinstance(lexp, ServPairExpr):
                lexp = lexp.getTypedVar()
            pleft.append(lexp)
        return pleft
        
    def readVal(self, val):
        # valType = val.getType()
        # print(' (a = b) :2', val)
        if isinstance(val, ObjectMember):
            val = val.get()
        if isinstance(val, ModuleMember):
            val = val.get()
        dprint(' (a = b) :3', val)
        if isinstance(val, Var):
            val = val.get()
        # dprint(' (a = b) :4', val)
        return val

    def do(self, ctx:Context):
        ''' var = src'''

        # prepare left
        left = self.leftSet()
        size = len(left)

        # prepare right
        resSet = self.doRight(ctx, size)

        # assign loop
        for  i in range(size):
            if isinstance(left[i], VarExpr_):
                # skip _ var
                continue
            left[i].do(ctx)
            val = resSet[i]
            
            val = self.readVal(val)
            valType = val.getType()
            if isinstance(left[i], CollectElem):
                ''' '''
                # print('(=) if dest CollectElem, val: ', val)
                val.name = None
                left[i].set(val)
                return
            
            #get destination var
            dest = left[i].get()
            # print('oper:', self.oper, 'dest:', left[i])
            # print('Assign dest1 =', dest, '; val=', val)

            isNew = False
            self.res = val
            if isinstance(dest, VarUndefined):
                # new var for assignment
                isNew = True
                newVar = Var(dest.name, valType)
                dprint('Assign new var', newVar, 'val-type:', valType)
                ctx.addVar(newVar)
                dest = newVar
            dest.set(val)
                
            # print('# op-assign set2, var-type:', dest, ' dest.class=', dest.getType().__class__)
            # print(' (a = b) dest =', dest, ' val = ', val, 'isNew:', isNew)
                
            if isinstance(dest, ObjectMember):
                # struct field as left operand
                dest.set(val)
                return

            # single var
            name = dest.name

            self.res = val
            # saved = ctx.get(name)
            # dprint(' (a = b) saved ', saved)

        # TODO: think about multiresult expressions: a, b, c = triple_vals(); // return 11, 22, 'ccc'
        # TODO: thik about one way of assignment: (something) = (something)


class OpBinAssign(OpAssign):
    ''' += -= *= /= %= '''
    def __init__(self, oper):
        super().__init__()
        self.oper = oper
        self.moper = self.splitOper(oper)
        self.trivial = True

    def splitOper(self, oper):
        # print('OpBinAssign biOper:', oper)
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
        dprint('#oper-left:', self.left)
        dprint('#oper-right:', self.right)
        self.left.do(ctx)
        self.right.do(ctx)
        # print('#bin-oper1:',' ( %s )' % self.oper, self.left, self.right) # expressions
        # get val objects from expressions
        a, b = self.left.get(), self.right.get() # Var objects
        dprint('#bin-oper2', a, b)
        
        # overloaded operators:
        over, res = self.overs(a, b)
        dprint('#bin-oper-over:', over, res)
        if over:
            self.res = res
            return
        
        # dprint(' ( %s )' % self.oper, a.getVal(), b.getVal())
        dprint('>types (%s %s %s)' % (a.getType(), self.oper, b.getType()))
        vtype = a.getType()
        if vtype != b.getType():
            # TODO fix different types
            pass
        # get numeric values and call math function 
        val = ff[self.oper](valFrom(a).getVal(), valFrom(b).getVal())
        # rounding to int
        if isinstance(val, (int, float)):
            if val % 1 == 0:
                # print(type(val))
                val = int(val)
                if isinstance(a.getType(), TypeInt):
                    vtype = TypeInt()
        self.res = Val(val, vtype)
        
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

    def collMinus(self, a:Collection, b:list):
        ''' a:dict|list - b:[int] '''
        key = b.getVal(Val(0, TypeInt()))
        val = a.getVal(key)
        a.delete(key)
        return val

    def listPlus(self, a:ListVal, b:ListVal):
        # print('listPlus:', a, b)
        res = a.copy()
        res.addMany(b)
        return res

    def strLshift(self, a, b):
        ''' "str pattern " << (vals) '''
        if not isinstance(b, TupleVal):
            t = b
            b = TupleVal()
            b.addVal(t)
        # reuse python old format %
        args = tuple(n.getVal() for n in b.rawVals())
        tpl = a.getVal()
        # dprint('tpl % args: ', tpl % args)
        return Val(tpl % args, TypeString)

    def overs(self, a, b):
        a, b = valFrom(a), valFrom(b)
        dprint('#bin-overs-1', a, b)
        match self.oper:
            case '+' :
                if isinstance(a, (ListVal)) and isinstance(b, ListVal):
                    return (True, self.listPlus(a, b))
            case '-' :
                if isinstance(a, (ListVal, DictVal)) and isinstance(b, ListVal):
                    return (True, self.collMinus(a, b))
            case '<<':
                if isinstance(a.getVal(), (str)):
                    return (True, self.strLshift(a, b))
            
        return (False, 0)


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
        dprint(' ( %s )' % self.oper, a.getVal(), b.getVal())
        dprint(' (types)', a.getType(), b.getType())
        # TODOO: type check needs further development
        # vtype = a.getType()
        # if not isinstance(vtype, TypeAny) and not isinstance(b.getType(), TypeAny) and vtype != b.getType():
        #     # naive impl: different types are not equal
        #     dprint('break comarison because types not equal %s <> %s' % (a.getType(), b.getType()) )
        #     return False
        res = ff[self.oper](a.getVal(), b.getVal())
        dprint('# == == OpCompare.do ', res)
        self.res = Val(res, TypeBool())
    
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
        dprint('( %s )' % self.oper,  self.left, self.right)
        # dprint('#--OpCompare.do2',  a, b)
        dprint(' ( %s )' % self.oper,  a.getVal(), b.getVal())
        # dprint('#--OpCompare.do3',  a.getType(), b.getType())
        type = a.getType()
        if type != b.getType():
            # naive impl: different types are not equal
            # return False
            # TODO: fix type comparison
            pass
        res = ff[self.oper](a.getVal(), b.getVal())
        # dprint('# == == OpCompare.do ', res)
        self.res = Val(res, TypeBool())


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
        # print('OpBitwise ():', self.oper)
        # print('self.left, self.right = ', self.left, self.right)
        # print('a, b : ', a, b)
        # print('types: : ', a.getType(), b.getType())
        type = a.getType()
        # if type != b.getType():
        #     # TODO type??
        #     self.res = Val(False, TypeBool())
        #     return False
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
        # dprint(' !x', self.inner, inVal)
        res = not inVal.getVal()
        self.res = Val(res, inVal.getType())


class BitNot(UnarOper):
    def __init__(self, oper:str, inner:Expression=None):
        super().__init__(oper, inner)

    def strFormat(self, arg:str, ctx:Context)->Val:
        val = '' # TODO: parse string, parse and interpret includes, eval includes, build result line
        # fm = StrFormatter()
        # expf = fm.toExpr(arg)
        # expf.do(ctx)
        # val = expf.get()
        return val

    def do(self, ctx:Context):
        self.inner.do(ctx)
        inVal = self.inner.get()
        val = inVal.getVal()
        
        # overload for string: formatting by included vars
        if isinstance(val, str):
            self.res = self.strFormat(val, ctx)
            return
        res = ~val
        self.res = Val(res, inVal.getType())

    def setInner(self, inner:Expression):
        # if isinstance(inner, (StringExpr, MString)):
        #     sf = StrFormatter()
        #     inner = sf.toExpr(inner.val)
        self.inner = inner


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


class MultiOper(OperCommand):
    ''' All expressions with more than 1 operator: (2 + 5 * 7) '''
    def __init__(self, exp:Expression=None):
        super().__init__('')
        self.root:Expression = exp
        
    def setInner(self, exp:Expression):
        self.root = exp

    def do(self, ctx:Context):
        ''' '''
        self.root.do(ctx)
        # self.res = self.root.get()

    def get(self):
        # val = self.root.get()
        # print('#MultiOper', self.root, val, val.vtype)
        return self.root.get()


class ObjectMember(ObjectElem):
    ''' '''
    def __init__(self, obj, member):
        super().__init__(None, TypeAccess)
        self.object:StructInstance = None
        self.member:str = None
        self.setArgs(obj, member)

    def setArgs(self, obj, member):
        dprint('ObjectMember.setArgs (', obj, ' -> ', member, ')')
        self.object = obj
        self.member = member

    def getVal(self):
        return self.get().getVal()

    def get(self):
        ''' res = obj.member; foo(obj.member); obj.member() '''
        dprint('self.member, get :: ',self.object, type(self.object), '::', self.member)
        val = self.object.get(self.member)
        
        # print('ObjectMember, get :: obj, member, val: ', self.object, self.member, val)
        if isinstance(val, (StructInstance, Val)):
            # dprint('membrr get struct')
            return val
        return val.get()
    
    def getType(self):
        val = self.object.get(self.member)
        return val.getType()
    
    def set(self, val:Val):
        ''' obj.member = expr; obj.member[key] = expr (looks like a.b[c] is an subcase of a.b) '''
        dprint('ObjectMember.set self.member, val :: ', self.member, val)
        self.object.set(self.member, val)

    def __str__(self):
        return "node ObjectMember(inst=%s, name=%s)" % (self.object, self.member)


class ModuleMember:
    ''' member of module taken by `.` dot-operator '''
    def __init__(self, module:ModuleBox):
        self.module:ModuleBox = module
        self.member = None
    
    def setMember(self, memb):
        ''' member name for using in get() '''
        self.member = memb
    
    def get(self):
        dprint('ModuleMember.get')
        return self.module.get(self.member)
    
    def getType(self):
        return self.member.getType()


# BinOper
# TODO: refactor from custom solutions of each case to universal:
# src . member  >> src.getInner(member) >> if member() >> src.getInner(member).call(args)
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
        if isinstance(inst, StructInstance) and isinstance(member, FuncCallExpr):
            member = MethodCallExpr(member)
        self.membExpr = member
        dprint('   >> OperDot.set', self.objExp, self.membExpr)

    def do(self, ctx:NSContext):
        # print('OperDot.do0', self.objExp, '; type=', type(self.objExp), ' :: ', self.membExpr)
        self.objExp.do(ctx)
        objVar = self.objExp.get()
        dprint('OperDot.do00', objVar, '; type=', type(objVar))
        if isinstance(objVar, ModuleBox):
            # process modules
            dprint('OperDot.do ModuleBox:', objVar, '; memb:', self.membExpr)
            # mod = ModuleMember(objVar)
            # mod.setMember(self.membExpr.name)
            # self.val = mod
            if isinstance(self.membExpr, FuncCallExpr):
                self.membExpr.do(objVar)
                self.val = self.membExpr.get()
                dprint('OperDot.do mod method res =', self.val)
            if isinstance(self.membExpr, StructConstr):
                self.membExpr.do(objVar)
                self.val = self.membExpr.get()
                # print('OperDot.do mod method res =', self.val)
                
            return
            
        if isinstance(objVar, Var):
            objVar = objVar.get()
        inst:StructInstance = objVar
        
        if isinstance(inst, StructInstance) and isinstance(self.membExpr, FuncCallExpr):
            self.membExpr = MethodCallExpr(self.membExpr)
        # print('OperDot.do-001 inst:', inst, 'memExp:', self.membExpr)
        # self.membExpr.do(inst)
        name = ''
        
        if isinstance(self.membExpr, MethodCallExpr):
            dprint('OperDot.do3 method1 =', self.membExpr, type(self.membExpr), '; methodname:', self.membExpr.name)
            # TODO: refactor to: 1. return func-member; 2. call method as usage of `()` operator
            self.membExpr.setInstance(inst)
            self.membExpr.do(ctx)
            self.val = self.membExpr.get()
            dprint('OperDot.do4 method res =', self.val)
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

        # dprint('OperDot.do2 <inst =', inst, 'name=', name ,'>')
        self.val = ObjectMember(inst, name)
        # print('OperDot.do5 fin field =', self.val)

    def get(self):
        return self.val


class TernarExpr(BinOper):
    ''' cond ? expr1 : expr2 '''
    
    def __init__(self):
        super().__init__('?')
        self.cond:Expression = None
        self.res1Exp:Expression = None # res if true
        self.res2Exp:Expression = None # res if false
        self.res:Val|Var= None

    def setArgs(self, cond:Expression, res:ServPairExpr):
        self.cond = cond
        res1, res2 = res.left, res.right
        self.res1Exp= res1
        self.res2Exp = res2

    def do(self, ctx:Context):
        self.cond.do(ctx)
        resExp = self.res2Exp
        if self.cond.get().getVal():
            resExp = self.res1Exp
        resExp.do(ctx)
        self.res = var2val(resExp.get())

    def get(self):
        return self.res


class FalseOrExpr(BinOper):
    ''' expr1 ?: expr2 
        if bool(expr1) == true: expr1
        else: expr2
    '''
    
    def __init__(self):
        super().__init__('?:')
        self.res1Exp:Expression = None # res if true
        self.res2Exp:Expression = None # res if false
        self.res:Val|Var= None

    def setArgs(self, res1:ServPairExpr, res2:ServPairExpr):
        self.res1Exp= res1
        self.res2Exp = res2

    def isOk(self, res:Var|Val):
        ''' means - non zero val'''
        if isinstance(res, Var):
            res = res.get()
        if isinstance(res.getType(), (TypeNull, Undefined)):
            return False
        if isinstance(res, (StructInstance)):
            return True
        if isinstance(res, (ListVal, TupleVal)):
            return res.len() > 0
        if isinstance(res,(Val)):
            return res.getVal() not in ['', 0, False]
        return False

    def do(self, ctx:Context):
        self.res1Exp.do(ctx)
        res1 = self.res1Exp.get()
        res = None
        if self.isOk(res1):
            res = self.res1Exp.get()
        else:
            self.res2Exp.do(ctx)
            res = self.res2Exp.get()
        self.res = var2val(res)

    def get(self):
        return self.res


class IsInExpr(BinOper):
    ''' val ?> list|dict|tuple '''
    
    def __init__(self, isNot=False):
        oper = '?>'
        if isNot:
            oper = '!?>'
        super().__init__(oper)
        self.valExpr:Expression = None # val we find in
        self.collExp:Expression = None # collection expr
        self.res:Val|Var= None
        self.isNot = isNot
        # print('IsIn:', oper, isNot)

    def setArgs(self, left:Expression, right:Expression):
        self.valExpr= left
        self.collExp = right

    def check(self, val, coll):
        if self.isNot:
            return val not in coll
        return val in coll

    def do(self, ctx:Context):
        # dprint('IsInExpr ?>> (1)', )
        self.valExpr.do(ctx)
        val = self.valExpr.get()
        val = valFrom(self.valExpr.get())
        self.collExp.do(ctx)
        coll = valFrom(self.collExp.get())
        res = False
        # dprint('IsInExpr ?>>', coll)
        if isinstance(coll, (ListVal, DictVal, TupleVal, Maybe)):
            res = coll.has(val)
        if isinstance(coll.getType(), TypeString):
            res = val.getVal() in coll.getVal()
        if self.isNot:
            res = not res
        self.res = Val(res, TypeBool())

    def get(self):
        return self.res


class CtrlSubExpr(Expression):
    ''' expr /: expr '''
    def __init__(self):
        super().__init__()
        self.control:ControlBlock = None
        self.sub = None

    def setArgs(self, left:Expression, right:Expression):
        # print('CtrlSubExpr setArgs: ', left, right)
        self.control = left
        self.sub = right

    def add(self, expr:Expression):
        # print('CtrlSubExpr add:',expr)
        self.sub.add(expr)

    def toControl(self):
        # print(' __ CtrlSubExpr.toCon1 sub:', self.sub)
        if isinstance(self.sub, CtrlSubExpr):
            # print(' __ CtrlSubExpr.toCon')
            self.sub = self.sub.toControl()
        self.control.add(self.sub)
        return self.control

