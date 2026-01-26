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
from objects.func import Function

from bases.ntype import *

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
        self.nmethods = []
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

    def setConstr(self, cons:FuncInst):
        self.__constr = cons
    
    def getConstr(self):
        return self.__constr

    def addParent(self, superType: TypeStruct):
        # print('StructDef. addParent1 :', superType)
        self.__parents[superType.getName()] = superType
        self.nmethods.extend([mt for mt in superType.nmethods if mt not in self.nmethods])
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
        self.nmethods.append(name)
        # print('struct.add Method:', name)
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
    

    # TODO: Think about case with same name func in a child is overloaded for another args
    def getMethod(self, name):
        # dprint('getMeth', name)
        if not name in self.__typeMethods:
            for sname, stype in self.__parents.items():
                # dprint('StDef.getMethod ', sname, stype)
                try:
                    mt = stype.getMethod(name)
                    return mt
                except EvalErr:
                    return None
            # raise EvalErr('Method `%s` didn`t define in type `%s`.' % (name, self.name))
            return None
        return self.__typeMethods[name]

    def hasMethod(self, fname):
        # print('.---.hasMethod', self.nmethods)
        # return fname in self.nmethods
        return fname in self.methodList()

    def methodList(self):
        # TODO: need optimization
        ms = list(self.__typeMethods.keys())
        if self.__parents :
            for _, stype in self.__parents.items():
                mt = stype.methodList()
                ms.extend(mt)
        return ms

    def debug(self):
        mm = [(k, v) for k, v in self.__typeMethods.items()]
        return mm
        # dprint(mm)

    def find(self, name):
        if name in self.methods:
            return self.methods[name]
        raise EvalErr(f'Struct Type `{self.name}` doesn`t contain member `{name}`')

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
        return 'StructType %s{}' % self.name
    
    def __repr__(self):
        fields = ', '.join( f"{tt}:{self.ntypes[tt].name}" for tt in self.nfields)
        return 'Type-%s{%s}' % (self.name,fields)



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
        vals = [ var2val(a) for a in self.callArgs]
        # print('SCon3:', self.fields,  vals, '\n', self.argVars)
        for i in range(len(self.fields)):
            inst.set(self.fields[i][0], vals[i])

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

    # def _set(self, fname:str, val:Val):
    #     # check type
    #     # print('StructInstance.set:', fname, val)
    #     # print('StructInstance.set types:', self.vtype.name, '>', self.vtype.types)
    #     if fname in self.vtype.nfields:
    #         self.checkType(fname, val)
    #         self.data[fname] = val
    #         return
    #     raise EvalErr(f'Incorrect field `{fname}` of Type `{self.vtype.name}`')

    def set(self, fname:str, val:Val):
        ''' check type and set new value '''
        if fname in self.vtype.nfields:
            val = self.checkType(fname, val)
            self.data[fname] = val

    def checkType(self, fname, val:Val):
        '''check type and resolve compatible'''
        valType = val.getType()
        ftype = self.vtype.ntypes[fname]
        # dt, st = dest.getType(), val.getType()
        dt, st = ftype, valType
        if not equalType(dt, st):
            # print('Struct!::!', dt, st, val)
            comType = isCompatible(dt, st)
            # print('OpAsgn, comType', comType)
            if comType:
                # convert val
                val = resolveVal(comType, val)
            else:
                # print(f'\n--!-- Error during set field {self.vtype.name}.{fname}:{ftype.name} types: (:{dt} = {st})', val)
                raise EvalErr(f'\n--!-- Error during set field {self.vtype.name}.{fname}:{ftype.name} types: (:{dt} = {st})', val)
        return val

    # def _checkType(self, fname, val:Val):
    #     valType = val.getType()
    #     ftype = self.vtype.ntypes[fname] # class inherited of VType or inst of StructInstance
    #     fclass = ftype.__class__
    #     # print('Type Check ???1:', fname, ftype.__class__, '<<', valType.__class__, val)
    #     if ftype == TypeAny:
    #         return # ok
    #     # if primitives or collections
    #     if not isinstance(ftype, StructDef):
    #         # print('!! Not struct!', fclass)
    #         if not isinstance(valType, fclass):
    #             # TODO: add compatibility check
    #             # print('Str.checkType:', f'Incorrect type `{valType.name}` for field {self.vtype.name}.{fname}:{ftype.name}')
    #             raise TypeErr(f'Incorrect type `{valType.name}` for field {self.vtype.name}.{fname}:{ftype.name}')
    #         return
    #     # if struct
    #     # print('@ check type ', valType.name, '!=', self.vtype.name , valType.name != self.vtype.name)
    #     if valType != ftype:
    #         if not structTypeCompat(ftype, valType):
    #             raise TypeErr(f'Incorrect type `{valType.name}` for field {self.vtype.name}.{fname}:{ftype.name}')
        
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

    def __init__(self, obj:Expression=None):
        super().__init__()
        self.objExpr = obj
        self.fieldExp = []

    def setObj(self, obj:Expression):
        self.objExpr = obj

    def add(self, fexp:Expression):
        if isinstance(fexp, ServPairExpr):
            fexp = StructArgPair(fexp)
        self.fieldExp.append(fexp)
        self.inst = None

    def findType(self, ctx:Context):
        self.inst = None
        self.objExpr.do(ctx)
        # print('finfT.obj', self.objExpr, self.objExpr.get())
        stype = self.objExpr.get()
        # stype = ctx.getType(self.typeName)
        if isinstance(stype, TypeVal):
            return stype.get()
        

    def do(self, ctx:Context):
        # print('StructConstr.do1 >> ', stype)
        # if isinstance(stype, ModuleBox):
        #     print('ModuleBox is object', self.typeName)
        sType = self.findType(ctx)
        # print('Strc.{} type:', sType)
            
        inst = StructInstance(sType)
        vals = []
        # print('#dbg1', self.fieldExp)
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
                raise EvalErr('Struct def error: field expression returns incorrect result: %s ' % expRes)
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

