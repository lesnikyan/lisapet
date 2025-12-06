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
from nodes.func_expr import FuncDefExpr, FuncCallExpr, Function



class StructDef(TypeStruct):
    ''' struct definition
        it does created as result of struct definition expression: struct Typename ...
        Definition objects are stores in Context as a types
    '''

    def __init__(self, name, fields:list[Var]=[]):
        self.name=name
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

    def addMethod(self, func:FuncInst):
        name = func.getName()
        # dprint('struct.add Method:', name)
        if name in self.__typeMethods:
            raise EvalErr('Method `%s` already defined in type `%s`.' % (name, self.name))
        self.__typeMethods[name] = func

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

    # def __str__(self):
    #     return 'type struct %s{}' % self.name


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
        # superTypes = self.vtype.getParents()
        # for pname, st in superTypes.items():
        #     # pname = st.getName()
        #     self.supers[pname] = StructInstance(st)

    # def initDefVals0(self, skip=None):
    #     '''
    #     ignore already filled in child instance (?)
    #     '''
    #     # set current
    #     if skip is None:
    #         skip = []
    #     for fname in self.vtype.fields:
    #         # print('def #1:', self.vtype.name, ' :: ', fname, skip)
    #         if fname not in self.data and fname not in skip:
    #             ftype = self.vtype.types[fname]
    #             dv = defaultValOfType(ftype) # default by type: 0, null, false, "", [], {}, (,)
    #             # print('def #2:', fname, ftype, '>>', dv)
    #             self.data[fname] = dv
    #     skip += self.vtype.fields
    #     # set parents
    #     if self.supers:
    #         # print('def-supers')
    #         for _, sup in self.supers.items():
    #             skip = sup.initDefVals(skip)
    #     return skip

    def initDefVals(self, skip=None):
        '''
        ignore already filled in child instance (?)
        '''
        # set current
        # if skip is None:
        #     skip = []
        for fname in self.vtype.nfields:
            # print('def #1:', self.vtype.name, ' :: ', fname, skip)
            if fname not in self.data:
                ftype = self.vtype.ntypes[fname]
                dv = defaultValOfType(ftype) # default by type: 0, null, false, "", [], {}, (,)
                # print('def #2:', fname, ftype, '>>', dv)
                self.data[fname] = dv
        # skip += self.vtype.nfields
        # set parents
        # if self.supers:
        #     # print('def-supers')
        #     for _, sup in self.supers.items():
        #         skip = sup.initDefVals(skip)
        # return skip

    # def get(self, fname=None):
    #     if fname is None:
    #         # dprint('StructInstance.DEBUG::: getting enmpty fieldname')
    #         return 'st@' + str(self) # debug
    #     if fname in self.vtype.fields:
    #         # print('\n  == Strc.get', self.data[fname], type(self.data[fname]))
    #         return self.data[fname]
    #     if self.supers:
    #         for _, sup in self.supers.items():
    #             if fname not in sup.vtype.fields:
    #                 continue
    #             return sup.get(fname)
    #     raise EvalErr(f'Incorrect field `{fname}` of struct `{self.vtype.getName()}` ')

    def get(self, fname=None):
        if fname is None:
            # dprint('StructInstance.DEBUG::: getting enmpty fieldname')
            return 'st@' + str(self) # debug
        if fname in self.vtype.nfields:
            # print('\n  == Strc.get', self.data[fname], type(self.data[fname]))
            return self.data[fname]
        # if self.supers:
        #     for _, sup in self.supers.items():
        #         if fname not in sup.vtype.fields:
        #             continue
        #         return sup.get(fname)
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
        # TODO: Fix deeper inheritance than 2 lvls
        # if self.supers:
        #     for _, sup in self.supers.items():
        #         if fname not in sup.vtype.fields:
        #             continue
        #         return sup.set(fname, val)
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
        if valType.name != ftype.name:
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
            # print('StructConstr.do res:', expRes[0], expRes[1])
            # fname, val = '', None
            # if isinstance(expRes, Var):
            #     val = expRes
            #     vals.append(val)
            #     continue
                # fieldName by order
            if isinstance(expRes, tuple) and len(expRes) == 2:
                fname, val = expRes
                # fname = fn
                # val = fv
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

    # def addArgExpr(self, exp:Expression):
    #     self.argExpr.append(exp)

    def setInstance(self, inst: StructInstance):
        dprint('MethCall set inst', inst)
        # raise XDebug('MethodCallExpr')
        self.inst = inst

    def do(self, ctx: Context):
        if not isinstance(self.inst, StructInstance):
            raise EvalErr('Incorrect instance of struct: %s ', self.inst)
        dprint('MethodCallExpr.do 1', self.name, self.inst.getType())
        stype = self.inst.getType()
        # dprint('MethodCallExpr.do2', stype, stype.debug()) #
        
        self.func = stype.getMethod(self.name)
        # instVar = self.inst[0].get(), self.inst[1].get()
        dprint('instVar', self.inst, self.func.argVars)
        args:list[Var] = [self.inst]
        dprint('#1# meth-call do1: ', self.name, self.inst, 'f:', self.func, 'line:', self.src)
        # argInd = 0
        # avs = self.func.argVars
        # dprint('#1# meth-call do2 exp=: ', avs, self.argExpr)
        for exp in self.argExpr:
            # dprint('#1# meth-call do20 exp=: ', exp)
            exp.do(ctx)
            dprint('meth-call do3:', exp, exp.get())
            args.append(exp.get())
        self.func.setArgVals(args)
        # TODO: add usage of Definishion Context instead of None
        callCtx = Context(ctx)
        self.func.do(callCtx)
