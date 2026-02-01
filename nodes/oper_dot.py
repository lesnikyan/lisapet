'''

'''

from lang import *
from vars import *
from nodes.expression import *
from nodes.structs import StructInstance, StructConstr
from bases.ntype import *
from nodes.base_oper import *
from objects.func import ObjMethod


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

    def getTypeMethod(self):
        ''' res = obj.member; foo(obj.member); obj.member() '''
        return self.object.vtype.getMethod(self.member)
    
    def getInst(self):
        return self.object

    def get(self, ctx:Context=None):
        ''' res = obj.member; '''
        sob:StructInstance = self.object
        # print('obJ1:', sob.vtype.name,  sob.vtype)
        # print('obJ:', sob.vtype.name,  sob.vtype.debug())
        # print('self.member, get :: obj2:',self.object, ':', type(self.object), '; .member:', self.member)
        if isinstance(sob, StructInstance) :
            # print('Obj3Mem.get if Struct')
            # self.membExpr = MethodCallExpr(self.membExpr)
            if self.object.vtype.hasField(self.member):
                val = self.object.get(self.member)
                # print('ObjectMember, get :: obj, member, val: ', self.object, self.member, val)
                if isinstance(val, (StructInstance, Val)):
                    # print('membrr get struct')
                    return val
                return val.get()
            # print('Obj55Mem')
            if self.object.vtype.hasMethod(self.member):
                # print('ObjectMember (checkMethod), get :: obj, method-name: ', self.object, self.member)
                meth = self.getTypeMethod()
                return ObjMethod(sob, meth)
        else:
            # try to find bound method
            # print('Obj5Mem.get others')
            inst = self.object
            fname = self.member
            mctx:Context = ctx
            ctype = mctx.find(inst.getType().name)
            # print('ODt6. type:', inst.getType(), mctx, ctype, fname)
            if isinstance(ctype, TypeProperty):
                func = ctype.funcs.getMethod(fname)
                # print('Dot7Oper. type-func=', type(func))
                return func
                # self.membExpr = BoundMethodCall(func, fcall)
    
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


class OperDot(BinOper):
    ''' inst.field '''

    def __init__(self, member=None):
        super().__init__('.')
        # obj, foo(), arr[key], obj.sub 
        self.objExp:VarExpr = None
        # obj.field, obj.meth(), obj.field[key]
        self.membExpr:Expression = member
        self.val:ObjectMember= None

    def setObj(self, inst:Expression):
        self.objExp = inst

    def doModuleMember(self, ctx:NSContext, base:ModuleBox):
        # print('OperDot.do ModuleBox:', base, '; memb:', self.membExpr)
        
        if isinstance(self.membExpr, VarExpr):
            memName = self.membExpr.get().name
            # print('OperDot.Module/1', base.get(memName))
            res = base.get(memName)
            if res:
                # print('OpDot. mem res=', res)
                return res
        
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
        # print('ODt.src', expSrc(self), 'objExp:', expSrc( self.objExp))
        self.objExp.do(ctx)
        objVar = self.objExp.get()
        # print('>>3', objVar)
        # print('OperDot.do00', objVar, '; type=', type(objVar))
        if isinstance(objVar, ModuleBox):
            # process modules
            self.val = self.doModuleMember(ctx, objVar)
            return
            
        objVal = objVar
        if isinstance(objVar, Var):
            objVal = objVar.get()

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
