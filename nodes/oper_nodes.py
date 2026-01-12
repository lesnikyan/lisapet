
'''
Eval tree nodes: operators.

'''


from nodes.base_oper import *
from nodes.datanodes import ListConstr, DictConstr
from nodes.expression import *
from bases.ntype import *
from lang import *
from nodes.oper_dot import *
from nodes.structs import StructConstrBegin 
from vars import *



class OpAssign(AssignExpr):
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
        print('OpAssig.add', expSrc(self.right), ' < ', expSrc(expr))
        if isinstance(self.right, CallExpr):
            rr = self.right
            print('OpAsg. CallExpr:', rr)
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
        # for n in left: print('#22', n)
        size = len(left)

        # prepare right
        resSet = self.doRight(ctx, size)
        # ctx.print(forsed=1)

        # assign loop
        for  i in range(size):
            if isinstance(left[i], VarExpr_):
                # skip _ var
                continue
            # print('L-1', left[i])
            left[i].do(ctx)
            # print('L-2', left[i])
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
                # dprint('Assign new var', newVar, 'val-type:', valType)
                ctx.addVar(newVar)
                dest = newVar
            
            # print('= OpAssign before set', dest, val, expSrc(self.src))
            # print('# op-assign set2, var-type:', dest, ' dest.class=', dest.getType().__class__)
            # print(' (a = b) dest =', dest, ' val = ', val, val.getType().__class__, 'isNew:', isNew)
            
            destStrict = False
            
            if isinstance(dest, ObjectMember):
                # struct field as left operand
                # dest.getType()
                destStrict = True
                # dest.set(val)
                # return
            else:
                destStrict = dest.strictType()

            # single var
            # print('OpAssig: single var', dest, destStrict)
            if destStrict:
                dt, st = dest.getType(), val.getType()
                if dt != st:
                    # print('!::!')
                    # check compatibility
                    if isCompatible(dt, st):
                        # convert val
                        val = resolveVal(dt, val)
                    else:
                        # print(f'\n--!-- Trying assign val to strictly typed variable (:{dt} = {st})', dest, val)
                        raise EvalErr(f'Trying assign val with different type to strictly typed variable (:{dt} =/= {st})')
            else:
                # if not strict type
                fixType(dest, val)
                
            dest.set(val)
            
            if isinstance(dest, ObjectMember):
                return

            self.res = val
            # name = dest.name
            # saved = ctx.get(name)
            # print(' (a = b) saved ', saved, saved.get().getType())


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
        
        # Some operations can return another type
        postType = {
            '/': TypeFloat
        }
        
        # eval expressions
        # dprint('#oper-left:', self.left)
        # dprint('#oper-right:', self.right)
        self.left.do(ctx)
        self.right.do(ctx)
        # print('#bin-oper1:',' ( %s )' % self.oper, self.left, self.right) # expressions
        # get val objects from expressions
        a, b = self.left.get(), self.right.get() # Var objects
        # print('#bin-oper2', a, b)
        
        # overloaded operators:
        over, res = self.overs(a, b)
        # dprint('#bin-oper-over:', over, res)
        if over:
            self.res = res
            return
        
        # NEXT shuld be numeric operations
        
        # print(' ( %s )' % self.oper, a.getVal(), b.getVal())
        # print('>types (%s %s %s)' % (a.getType(), self.oper, b.getType()))
        atype = a.getType()
        btype = b.getType()
        
        # convert b-operand to correct numeric type
        numTs = (TypeNull, TypeBool, TypeInt, TypeFloat)
        if not isinstance(atype, numTs) or not isinstance(btype, numTs):
            # incorrect operand for math operator!
            print(f'Incorrect types {atype} , {btype} for math operator {self.oper}')
            raise EvalErr(f'Incorrect types {atype.name} , {btype.name} for math operator {self.oper}')
        
        rtype = atype
        if isinstance(atype, (TypeNull, TypeBool)):
            atype = TypeInt()
            a = resolveVal(atype, valFrom(a))
        if isinstance(btype, (TypeNull, TypeBool)):
            btype = TypeInt()
            b = resolveVal(btype, valFrom(b))
        if atype != btype:
            if isinstance(atype, TypeFloat) or isinstance(btype, TypeFloat):
                rtype = TypeFloat()
        # get numeric values and call math function 
        val = ff[self.oper](valFrom(a).getVal(), valFrom(b).getVal())
        
        # resolve result type for specific cases
        resType = rtype
        if self.oper in postType:
            target = postType[self.oper]
            resType = target()
        
        self.res = Val(val, resType)
    
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
        key = b.getElem(Val(0, TypeInt()))
        val = a.getElem(key)
        a.delete(key)
        return val

    def listPlus(self, a:ListVal, b:ListVal):
        # print('listPlus:', a, b)
        res = a.copy()
        res.addMany(b)
        return res
    
    def stringPlus(self, a, b):
        res = a.getVal() + b.getVal()
        return StringVal(res)

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

    def normalize(self, val:Val):
        # print('O-nod.normalize', val)
        if isinstance(val, ObjectMember):
            # print('OMb:', val, val.get())
            return val.get()
        if isinstance(val, Val) and isinstance(val.getVal(), SequenceGen):
            return val.val.allVals()
        return val

    def overs(self, a, b):
        a, b = valFrom(a), valFrom(b)
        # print('#bin-overs-1', a, b)
        a, b = self.normalize(a), self.normalize(b)
        # print('#bin-overs-1', a, b)
        match self.oper:
            case '+' :
                if isinstance(a, (ListVal)) and isinstance(b, ListVal):
                    return (True, self.listPlus(a, b))
                if isinstance(a, (StringVal)) and isinstance(b, StringVal):
                    return (True, self.stringPlus(a, b))
            case '-' :
                if isinstance(a, (ListVal, DictVal)) and isinstance(b, ListVal):
                    return (True, self.collMinus(a, b))
            case '<<':
                if isinstance(a.getVal(), (str)):
                    return (True, self.strLshift(a, b))
            
        return (False, 0)


# class OpMathAssign(OperCommand):
#     ''' a += 5; a += b; a += foo(b); a += foo(b) - 5/c '''


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
        res = ff[self.oper](bool(a.getVal()), bool(b.getVal()))
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
        # print(' !x', self.inner, inVal)
        res = not bool(inVal.getVal())
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



# BinOper


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
        if isinstance(res, (ObjectInstance)):
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

def valHasType(val:Val|Var, typeVal:TypeVal):
    lop = var2val(val)
    rop = var2val(typeVal)
    expt = rop.getVal()
    if not isinstance(rop, TypeVal):
        raise EvalErr("Incorrect right operand of `::` operator.")
    return isinstance(lop.getType(), expt.__class__)


class IsTypeExpr(BinOper):
    ''' val :: type '''

    def __init__(self, left=None, right=None):
        super().__init__('::', left, right)
    
    def do(self, ctx:Context):
        self.left.do(ctx)
        lop = var2val(self.left.get())
        
        # print(':: expr:', self.right)
        if isinstance(self.right, (ListConstr, DictConstr)) and self.right.byword:
            tname = self.right.tname
            self.right = VarExpr(Var(tname, TypeAny()))
        self.right.do(ctx)
        rop = var2val(self.right.get())
        
        if not isinstance(rop, (TypeVal)):
            if not isinstance(rop.get(), Null):
                raise EvalErr("Incorrect right operand of `::` operator.")
            
        
        # Null case trick
        if isinstance(rop.get(), Null):
            if lop.getVal() == Null():
                self.res = Val(isinstance(lop.get(), Null), TypeBool())
                return
         
        expt = rop.getVal()
        # print('::2>', expt, lop.getType())
        res = Val(isinstance(lop.getType(), expt.__class__), TypeBool())
        # print(':: 3> ', res)
        self.res = res


class RegexpOper(BinOper):
    ''' re <oper> string '''

    def __init__(self, oper, left:Expression=None, right:Expression=None):
        super().__init__(oper, left, right)


class RegexpMatchOper(RegexpOper):
    ''' re =~ string '''
    
    def __init__(self, left = None, right = None):
        super().__init__('=~', left, right)

    def do(self, ctx:Context):
        self.left.do(ctx)
        rx = self.left.get()
        if isinstance(rx, (Var)):
            rx = rx.getVal()
        self.right.do(ctx)
        src = self.right.get()
        src = var2val(src)
        res = rx.match(src)
        self.res = Val(res, TypeBool())


class RegexpSearchOper(RegexpOper):
    ''' re =~ string '''
    
    def __init__(self, left = None, right = None):
        super().__init__('?~', left, right)

    def do(self, ctx:Context):
        self.left.do(ctx)
        rx = self.left.get()
        if isinstance(rx, (Var)):
            rx = var2val(rx)
        self.right.do(ctx)
        src = self.right.get()
        src = var2val(src)
        res = rx.find(src)
        self.res = res
    