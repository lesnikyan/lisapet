'''
execution nodes with user-defining types expressios
StructType : object for serving user-defined type object.
StructInstance instance of StructType

StructDef : definition expr, creates StructType(name)
StructConstr : create struct instance
StructField : struct.field for get/set operations
AnonStructConstr *? : create instance of anonymous struct (json-like object)

'''

from nodes.expression import *
from context import *
from nodes.expression import ServPairExpr, defaultValOfType
from bases.ntype import structTypeCompat
from nodes.func_expr import FuncDefExpr, FuncCallExpr, Function, BoundMethod



class StructDef(TypeStruct):
    ''' struct definition
        it does created as result of struct definition expression: struct Typename ...
        Definition objects are stores in Context as a types
    '''

    def __init__(self, name, fields:list[Var]=[]):
        self.name=name
        self._th = TH.mk()
        # print('SDef', self.name, self._th)
        self.fields = []
        self.nfields = [] # full fields count with inherited
        self.__parents:dict[str,TypeStruct] = {}
        self.methods:dict[str,FuncInst] = []
        self.types:dict[str, VType] = {}
        self.ntypes:dict[str, VType] = {}
        if fields:
            self.__fillData(fields)
        self.__typeMethods:dict[str,FuncInst] = {}
        self.__constr = None

    def initConstr(self):
        self.__constr = StructDefConstrFunc(self)

    def hash(self):
        return self._th

    def setConstr(self, cons:Function):
        self.__constr = cons
    
    def getConstr(self):
        return self.__constr

    def addParent(self, superType: TypeStruct):
        # dprint('StructDef. addParent1 :', superType)
        self.__parents[superType.getName()] = superType
        self.nfields = [n for n in superType.nfields if n not in self.nfields] + self.nfields
        self.ntypes.update({k:v for k, v in superType.ntypes.items() if k not in self.ntypes})
        
    def getParents(self):
        return self.__parents
    
    def hasParent(self, vtype:'StructDef'):
        if vtype.name in self.__parents:
            return vtype == self.__parents[vtype.name]
        for _, pp in self.__parents.items():
            if pp.hasParent(vtype):
                return True
        return False

    def addMethod(self, func:FuncInst):
        name = func.getName()
        # print('struct.add Method:', name)
        # if name in self.__typeMethods:
        #     exist = self.__typeMethods
        #     raise EvalErr('Method `%s` already defined in type `%s`.' % (name, self.name))
        if name not in self.__typeMethods:
            self.__typeMethods[name] = func
            return
        exist = self.__typeMethods[name]
        if isinstance(exist, FuncInst):
            # start overloading
            overSet = FuncOverSet(name)
            overSet.add(exist)
            overSet.add(func)
            self.__typeMethods[name] = overSet
            return
        elif isinstance(exist, FuncOverSet):
            exist.add(func)
    

    # TODO: Think about case with same name func in child overloaded for another args
    def getMethod(self, name):
        # dprint('getMeth', name)
        if not name in self.__typeMethods:
            for sname, stype in self.__parents.items():
                # dprint('StDef.getMethod ', sname, stype)
                try:
                    mt = stype.getMethod(name)
                    return mt
                except EvalErr:
                    pass
            raise EvalErr('Method `%s` didn`t define in type `%s`.' % (name, self.name))
        return self.__typeMethods[name]

    def debug(self):
        mm = [(k, v) for k, v in self.__typeMethods.items()]
        dprint(mm)

    def find(self, name):
        if name in self.methods:
            return self.methods[name]
        raise EvalErr('Struct Type `self.name` doesn`t contain member `{name}`')

    def __fillData(self, fields):
        for f in fields:
            self.add(f)

    def add(self, f:Var):
        tp:VType = f.getType()
        # print('StructDef.add ## ', f, tp)
        self.fields.append(f.name)
        self.nfields.append(f.name)
        self.types[f.name] = tp
        self.ntypes[f.name] = tp

    def getFieldsNested(self):
        fields = []
        for sname, stype in self.__parents.items():
            fields.extend(stype.getFieldsNested())
        fields.extend([(fname, self.types[fname]) for fname in self.fields])
        return fields

    def getFields(self):
        return self.fields

    def getName(self):
        return self.name
    
    def hasField(self, fname):
        if fname in self.fields:
            return True
        for _,par in self.__parents.items():
            if par.hasField(fname):
                return True
        return False
    
    def isInstance(self, sType:'StructDef'):
        # print('.isInstance', sType.name ,':<>:', self.name, ' ??>', sType == self)
        if sType == self:
            return True
        # print('__parents:', self.__parents)
        for _,par in self.__parents.items():
            if par.isInstance(sType):
                return True
        return False

    def __eq__(self, value):
        if not isinstance(value, StructDef):
            return False
        return id(self) == id(value)

    def __str__(self):
        return 'type struct %s{}' % self.name



class StructDefConstrFunc(Function):
    ''' TypeName(args) '''
    
    def __init__(self, stype:StructDef):
        super().__init__(stype.getName()+'')
        self.stype = stype
        self.block = Block()
        fnames = []
        ftypes = {}
        self.fields = []
        nfields = stype.getFieldsNested()
        # print('\nSCon1:', self.stype.name,'::', nfields)
        for fname, ftype in nfields:
            # print('SCon2:', fname, ftype)
            if fname not in fnames:
                # print('SCon200:', fname)
                fnames.append(fname)
                ftypes[fname] = ftype
                self.fields.append((fname, ftype))
        for fname, ftype in self.fields:
            self.addArg(Var(fname, ftype))

    def do(self, ctx: Context):
        self.res = None
        self.block.storeRes = True # save last expr value

        inst = StructInstance(self.stype)
        # fields = self.stype.getFieldsNested()
        vals = []
        vals = [ var2val(a) for a in self.callArgs]
        # print('SCon3:', self.fields,  vals, '\n', self.argVars)
        for i in range(len(self.fields)):
            # inst.set(fields[i][0], self.argVars[i])
            inst.set(self.fields[i][0], vals[i])
        # if len(vals) > 0:
        #     inst.setVals(vals)
        inst.initDefVals()
        self.res = inst

class DefaultStruct(StructDef):
    ''' type of anonymous struct
    struct{feild:value, ...} '''
    def __init__(self, fields):
        super().__init__('anonimous', fields)


class StructInstance(ObjectInstance, NSContext):
    ''' data of struct '''

    def __init__(self, stype:StructDef):
        super().__init__(None, stype)
        # print('StructInstance.__init__', '>>', stype)
        self.vtype:StructDef = stype
        self.ifields = [] # fields of instance
        self.data:dict[str, Val] = {}
        self.supers:dict = {}
        self.initSuper()

    def initSuper(self):
        self.ifields = self.vtype.nfields[:]


    def initDefVals(self):
        '''
        ignore already filled in child instance (?)
        '''
        for fname in self.vtype.nfields:
            if fname not in self.data:
                ftype = self.vtype.ntypes[fname]
                dv = defaultValOfType(ftype) # default by type: 0, null, false, "", [], {}, (,)
                # print('def #2:', fname, ftype, '>>', dv)
                self.data[fname] = dv

    def getType(self):
        return self.vtype

    def getFieldType(self, fname):
        return self.vtype.ntypes[fname]

    def get(self, fname=None):
        if fname is None:
            # dprint('StructInstance.DEBUG::: getting enmpty fieldname')
            return 'st@' + str(self) # debug
        if fname in self.vtype.nfields:
            # print('\n  == Strc.get', self.data[fname], type(self.data[fname]))
            return self.data[fname]
        raise EvalErr(f'Incorrect field `{fname}` of struct `{self.vtype.getName()}` ')
    
    def find(self, fname):
        ''' find sub-field by name'''
        # dprint('st.find', fname, ':', self.vtype.fields)
        return self.data[fname]

    def setVals(self, vals:list[Val]):
        if len(vals) != len(self.vtype.nfields):
            raise EvalErr(f'Incorrect number of values in constructor of struct {self.vtype.name}')
        for i in range(len(vals)):
            self.set(self.vtype.fields[i], vals[i])

    def set(self, fname:str, val:Val):
        # check type
        # print('StructInstance.set:', fname, val)
        # print('StructInstance.set types:', self.vtype.name, '>', self.vtype.types)
        if fname in self.vtype.nfields:
            self.checkType(fname, val)
            self.data[fname] = val
            return
        raise EvalErr(f'Incorrect field `{fname}` of Type `{self.vtype.name}`')

    def checkType(self, fname, val:Val):
        valType = val.getType()
        ftype = self.vtype.ntypes[fname] # class inherited of VType or inst of StructInstance
        fclass = ftype.__class__
        # print('Type Check ???1:', fname, ftype.__class__, '<<', valType.__class__, val)
        if ftype == TypeAny:
            return # ok
        # if primitives or collections
        if not isinstance(ftype, StructDef):
            # print('!! Not struct!', fclass)
            if not isinstance(valType, fclass):
                # TODO: add compatibility check
                # print('Str.checkType:', f'Incorrect type `{valType.name}` for field {self.vtype.name}.{fname}:{ftype.name}')
                raise TypeErr(f'Incorrect type `{valType.name}` for field {self.vtype.name}.{fname}:{ftype.name}')
            return
        # if struct
        # print('@ check type ', valType.name, '!=', self.vtype.name , valType.name != self.vtype.name)
        if valType != ftype:
            if not structTypeCompat(ftype, valType):
                raise TypeErr(f'Incorrect type `{valType.name}` for field {self.vtype.name}.{fname}:{ftype.name}')
        
    def istr(self):
        fns = self.vtype.nfields
        vals = ','.join(['%s: %s' % (f, self.get(f).get()) for f in fns])
        return vals

    def __str__(self):
        vals = self.istr()
        return '%s{%s}' % (self.vtype.name, vals)

# Expressions

class StructDefExpr(DefinitionExpr):
    ''' expr `struct TypeName [fields]` '''

    def __init__(self, typeName:str, src=''):
        super().__init__(src=src)
        self.typeName:str = typeName
        self.fields:list = [] # fields expressions
        self.superNames:list = [] # names of super types (parents)

    def setSuper(self, names):
        self.superNames = names

    def add(self, fexp:Expression):
        '''fexp - field expression: VarExpr | ServPairExpr '''
        # dprint('@@StructDefExpr.add1', fexp)
        self.fields.append(fexp)

    def do(self, ctx:Context):
        strType = StructDef(self.typeName)
        # print('struct def:', expSrc(self.src))
        for fexp in self.fields:
            fexp:ServPairExpr = fexp
            # print('@1>', fexp)
            fexp.do(ctx)
            field = fexp.get()
            fname, ftype = '', TypeAny
            # ctx.print()
            # print('@2>>', field)
            if isinstance(field, tuple) and len(field) == 2:
                fn, ft = field
                # print('@20>>', fn, ft)
                fname = fn.name
                ftype = ft.get()
                # print('@21>> type', self.typeName,',fname:', fname, ' >> ',  ftype, type(ftype))
                if not isinstance(ftype, (VType)):
                    # dprint('fname:', type(ft))
                    raise EvalErr(f'Trying to put {fname} with no type.')

            elif isinstance(field, Var):
                fname = field.name
            else:
                raise EvalErr('Struct def error: fiels expression returns incorrect result: %s ' % field)
            strType.add(Var(fname, ftype))
        for sname in self.superNames:
            supType = ctx.getType(sname)
            if not supType:
                raise EvalErr('Supertype `%s` of type `%s` wasn`t found.' % (sname, self.typeName))
            strType.addParent(supType.get())
        # register new type
        strType.initConstr()
        typeVal = TypeVal(strType)
        ctx.addType(typeVal)

    def get(self):
        raise EvalErr('Type(struct) definition expression can`t return result.')


class StructArgPair(Expression):
    ''' pairs of {fieldName: val}
        as arguments of struct constructor
    '''
    def __init__(self, pair:ServPairExpr):
        # super().__init__()
        self.valExpr = pair.right
        # left sould be a VarExpr
        self.name = pair.left.name
        self.res = None

    def do(self, ctx):
        self.res = None
        self.valExpr.do(ctx)
        val = self.valExpr.get()
        # print('StructArgPair.do1', self.name, val)
        self.res = self.name, val
    
    def get(self):
        return self.res


class StructConstr(Expression):
    ''' Typename{[field-values]} '''

    def __init__(self,  typeName):
        super().__init__()
        self.typeName:str = typeName
        self.fieldExp = []

    def add(self, fexp:Expression):
        if isinstance(fexp, ServPairExpr):
            fexp = StructArgPair(fexp)
        self.fieldExp.append(fexp)
        self.inst = None

    def do(self, ctx:Context):
        self.inst = None
        stype = ctx.getType(self.typeName)
        # print('StructConstr.do1 >> ', stype)
        inst = StructInstance(stype.get())
        vals = []
        for fexp in self.fieldExp:
            fexp.do(ctx)
            # if val only
            # if pair name:val
            expRes = fexp.get()

            if isinstance(expRes, tuple) and len(expRes) == 2:
                fname, val = expRes
                # print('Strc.do >> ', expRes, fname, val)
                var2val(val)
                inst.set(fname, val)
            else:
                raise EvalErr('Struct def error: fiels expression returns incorrect result: %s ' % expRes)
        if len(vals) > 0:
            inst.setVals(vals)
        # print('StructConstr: before defaults', len(vals))
        inst.initDefVals()
        self.inst = inst

    def get(self):
        return self.inst


class StructConstrBegin(StructConstr, MultilineVal):
    def __init__(self, typeName):
        super().__init__(typeName)



class MethodDefExpr(FuncDefExpr):
    ''' '''
    def __init__(self, name):
        super().__init__(name)
        self.instExpr:Expression = None
        self.typeName = None
        # raise EvalErr('DDD ', self.name)

    def setInst(self, exp:ServPairExpr):
        self.instExpr = exp.getTypedVar()

    def doFunc(self, ctx):
        func = Function(self.name)
        self.instExpr.do(ctx)
        inst = self.instExpr.get()
        dprint('MethodDefExpr.doFunc', inst, self.name)
        self.typeName = inst.getType().getName()
        # dprint('MethodDefExpr instType:', self.typeName)
        dprint('MethodDefExpr doFunc:', self.instExpr, self.instExpr.get())
        func.addArg(self.instExpr.get())
        return func

    def regFunc(self, ctx:Context, func:FuncInst):
        ctx.addTypeMethod(self.typeName, func)

    def do(self, ctx:Context):
        '''''' 
        super().do(ctx)


class MethodCallExpr(FuncCallExpr):
    ''' foo(agr1, 2, foo(3))  '''

    def __init__(self, func:FuncCallExpr):
        super().__init__(func.name, func.src)
        self.inst:StructInstance = None
        # self.name = name
        # self.func:Function = None
        self.argExpr:list[Expression] = func.argExpr

    def setInstance(self, inst: StructInstance|Val):
        dprint('MethCall set inst', inst)
        # raise XDebug('MethodCallExpr')
        self.inst = inst

    def getFunc(self, args:list):
        stype = self.inst.getType()
        fn = stype.getMethod(self.name)
        if isinstance(fn, FuncOverSet):
            over:FuncOverSet = fn
            callArgTypes = [ar.getType() for ar in args]
            fn = over.get(callArgTypes)
        self.func = fn

    def do(self, ctx: Context):
        okCond = isinstance(self.inst, StructInstance)
        # okCond = okCond or isinstance(self.func, BoundMethod)
        if not okCond:
            raise EvalErr('Incorrect instance of struct: %s ', self.inst)
        # print('MethodCallExpr.do 1', self.name, self.inst.getType())

        # instVar = self.inst[0].get(), self.inst[1].get()
        # print('instVar', self.inst, self.func.argVars)
        args:list[Var] = [self.inst]
        # dprint('#1# meth-call do1: ', self.name, self.inst, 'f:', self.func, 'line:', self.src)
        for exp in self.argExpr:
            # dprint('#1# meth-call do20 exp=: ', exp)
            exp.do(ctx)
            # print('meth-call do3:', exp, exp.get())
            args.append(exp.get())
        self.getFunc(args)
        self.func.setArgVals(args)
        # TODO: add usage of Definishion Context instead of None
        callCtx = Context(ctx)
        self.func.do(callCtx)

class BoundMethodCall(MethodCallExpr):
    def __init__(self, func:BoundMethod, callExpr:FuncCallExpr):
        super().__init__(callExpr)
        self.inst:Val = None
        self.func:BoundMethod = func
        self.argExpr:list[Expression] = callExpr.argExpr

    def do(self, ctx: Context):
        # print('instVar', self.inst, self.func.argVars)
        args:list[Var] = [self.inst]
        for exp in self.argExpr:
            exp.do(ctx)
            args.append(exp.get())
        self.func.setArgVals(args)
        callCtx = Context(ctx)
        self.func.do(callCtx)

    def get(self):
        return self.func.get()


# def structTypeCompat(dtype:StructInstance, stype:VType):
#     ''' criterion: src should 
#         have the same type the dest have,
#         be child of dest type, 
#         or null
#         dtype - dest type
#         stype = src type
#     '''
#     # stype = src.getType()
#     # print('tcopmt1', stype)
#     if isinstance(stype, TypeNull):
#         return True
#     # TODO: possible interface check for future
    
#     # nest - for structs only
#     if not isinstance(stype, StructDef):
#         # not a struct
#         return False
#     if dtype == stype:
#         return True
#     if stype.hasParent(dtype):
#         return True
#     return False
    

