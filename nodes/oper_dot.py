'''

'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.structs import StructInstance, MethodCallExpr, StructConstr, BoundMethodCall
from bases.ntype import *
from nodes.base_oper import *


class ObjectMember(ObjectElem):
    ''' '''
    def __init__(self, obj, member):
        super().__init__(None, TypeAccess)
        self.object:StructInstance = None
        self.member:str = None
        self.setArgs(obj, member)

    def setArgs(self, obj, member):
        self.object = obj
        self.member = member

    def getVal(self):
        return self.get().getVal()

    def get(self):
        ''' res = obj.member; foo(obj.member); obj.member() '''
        # print('self.member, get :: ',self.object, type(self.object), '::', self.member)
        val = self.object.get(self.member)
        
        # print('ObjectMember, get :: obj, member, val: ', self.object, self.member, val)
        if isinstance(val, (StructInstance, Val)):
            # dprint('membrr get struct')
            return val
        return val.get()
    
    def getType(self):
        # print('self.member', self.member)
        strType = self.object.getFieldType(self.member)
        return strType
    
    def set(self, val:Val):
        ''' obj.member = expr; obj.member[key] = expr (looks like a.b[c] is an subcase of a.b) '''
        # dprint('ObjectMember.set self.member, val :: ', self.member, val)
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
        if isinstance(inst, StructInstance) and isinstance(member, CallExpr):
            member = MethodCallExpr(member)
        self.membExpr = member
        # dprint('   >> OperDot.set', self.objExp, self.membExpr)

    def doMethod(self, ctx:NSContext, inst:StructInstance|Var|Val):
        # print('OperDot.do-001 CallExpr, inst:', inst, 'memExp:', self.membExpr)
        fname = self.membExpr.name
        fcall = self.membExpr
        if isinstance(inst, StructInstance) :
            self.membExpr = MethodCallExpr(self.membExpr)
        else:
            # try to find bound method
            mctx:Context = ctx
            ctype = mctx.find(inst.getType().name)
            # print('ODt2. type:', inst.getType(), mctx, ctype, fname)
            if isinstance(ctype, TypeProperty):
                func = ctype.funcs.getMethod(fname)
                # print('DotOper. type-func=', func)
                self.membExpr = BoundMethodCall(func, fcall)
    
        if not isinstance(self.membExpr, (MethodCallExpr)):
            raise EvalErr("Incorrect member in `inst.method()` call expression. ")

        # print('OperDot.do3 method1 =', self.membExpr, type(self.membExpr), '; methodname:', self.membExpr.name)
        # TODO: refactor to: 1. return func-member; 2. call method as usage of `()` operator
        self.membExpr.setInstance(inst)
        self.membExpr.do(ctx)
        self.val = self.membExpr.get()
        # print('OperDot.do4 method res =', self.val)


    def doModuleMember(self, ctx:NSContext, base:ModuleBox):
        # dprint('OperDot.do ModuleBox:', base, '; memb:', self.membExpr)
        if isinstance(self.membExpr, CallExpr):
            self.membExpr.do(base)
            self.val = self.membExpr.get()
            # dprint('OperDot.do mod method res =', self.val)
        if isinstance(self.membExpr, StructConstr):
            self.membExpr.do(base)
            self.val = self.membExpr.get()
            # print('OperDot.do mod method res =', self.val)
        
    def do(self, ctx:NSContext):
        # print('OperDot.do0', self.objExp, '; type=', type(self.objExp), ' :: ', self.membExpr)
        self.objExp.do(ctx)
        objVar = self.objExp.get()
        # dprint('OperDot.do00', objVar, '; type=', type(objVar))
        if isinstance(objVar, ModuleBox):
            # process modules
            return self.doModuleMember(ctx, objVar)
            
        objVal = objVar
        if isinstance(objVar, Var):
            objVal = objVar.get()
        # print('#2', objVal)
        
        if isinstance(self.membExpr, CallExpr):
            return self.doMethod(ctx, objVal)
        
        name = ''
        if isinstance(self.membExpr, VarExpr):
            name = self.membExpr.name # just name for struct
        else:
            # exp.get() - for array or dimanic field name obj.(fieldName(args))
            self.membExpr.do(ctx)
            sub = self.membExpr.get()
            name = sub.get()

        inst:StructInstance = objVal
        if isinstance(inst, ObjectMember):
            inst = inst.get()

        # dprint('OperDot.do2 <inst =', inst, 'name=', name ,'>')
        self.val = ObjectMember(inst, name)
        # print('OperDot.do5 fin field =', self.val)

    def get(self):
        return self.val
