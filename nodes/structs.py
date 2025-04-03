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
from nodes.expression import ServPairExpr



class StructDef(TypeStruct):
    ''' struct definition
        it does created as result of struct definition expression: struct Typename ...
        Definition objects are stores in Context as a types
    '''

    def __init__(self, name, fields:list[Var]=[]):
        self.name=name
        self.fields = []
        self.methods:dict[str,FuncInst] = []
        self.types:dict[str, VType] = {}
        if fields:
            self.__fillData(fields)

    def find(self, name):
        if name in self.methods:
            return self.methods[name]
        raise EvalErr('Struct Type `self.name` doesn`t contain member `{name}`')

    def __fillData(self, fields):
        for f in fields:
            self.add(f)

    def add(self, f:Var):
        tp:VType = f.getType()
        print('StructDef.add ## ', f, tp)
        self.fields.append(f.name)
        self.types[f.name] = tp

    def getFields(self):
        return self.fields

    def __str__(self):
        return 'type struct %s{}' % self.name



class DefaultStruct(StructDef):
    ''' type of anonymous struct
    struct{feild:value, ...} '''
    def __init__(self, fields):
        super().__init__('anonimous', fields)


class StructInstance(Var, NSContext):
    ''' data of struct '''

    def __init__(self, name, stype:StructDef):
        super().__init__(self, name, stype)
        print('StructInstance.__init__', '>>', stype)
        self.vtype:StructDef = stype
        self.data:dict[str, Var] = {}

    def get(self, fname=None):
        if fname is None:
            # print('StructInstance.DEBUG::: getting enmpty fieldname')
            return '@struct debug / ' + str(self) # debug 
        return self.data[fname]
    
    def find(self, fname):
        ''' find sub-field by name'''
        print('st.find', fname, ':', self.vtype.fields)
        return self.data[fname]

    def setVals(self, vals:list[Var]):
        if len(vals) != len(self.vtype.fields):
            raise EvalErr(f'Incorrect number of values in constructor of struct {self.vtype.name}')
        for i in range(len(vals)):
            self.set(self.vtype.fields[i], vals[i])

    def set(self, fname:str, val:Var):
        # check type
        print('StructInstance.set:', fname, val)
        # print('@3>> ', dir(self))
        # print('StructInstance.set type:', self.vtype, )
        # print('StructInstance.set types:', '>', self.vtype.types)
        if fname not in  self.vtype.types:
            raise EvalErr(f'Incorrect field `{fname}` of Type `{self.vtype.name}`')
        # TODO: Fic to use types compatibility
        self.checkType(fname, val)
        self.data[fname] = val

    def checkType(self, fname, val:Var):
        valType = val.getType()
        ftype = self.vtype.types[fname] # class inherited of VType or inst of StructInstance
        fclass = ftype.__class__
        print('Type: name / members', self.vtype.name, self.vtype.types)
        print('Type Check ???1:', valType, '<?>', ftype)
        print('Type Check ???2:', valType.__class__, '<?>', fclass,' if:', isinstance(valType, fclass))
        print('Type struct???3:', isinstance(valType, StructInstance))
        if ftype == TypeAny:
            return # ok
        # if primitives or collections
        # print('if prim and !types', not isinstance(valType, StructInstance) and not isinstance(valType, ftype))
        if not isinstance(ftype, StructDef):
            print('!! Not struct!', fclass)
            if not isinstance(valType, fclass):
                # TODO: add compatibility check
                raise TypeErr(f'Incorrect type `{valType.name}` for field {self.vtype.name}.{fname}:{ftype.name}')
            return
        # if struct
        print('@ check type ', valType.name, '!=', self.vtype.name , valType.name != self.vtype.name)
        if valType.name != ftype.name:
            raise TypeErr(f'Incorrect type `{valType.name}` for field {self.vtype.name}.{fname}:{ftype.name}')
        

    def __str__(self):
        fns = self.vtype.fields
        vals = ','.join(['%s: %s' % (f, self.get(f).get()) for f in fns])
        return 'struct %s(%s)' % (self.vtype.name, vals)

# Expressions

class StructDefExpr(DefinitionExpr):
    ''' expr `struct TypeName [fields]` '''

    def __init__(self, typeName:str):
        self.typeName:str = typeName
        self.fields:list = [] # fields expressions
        
    def add(self, fexp:Expression):
        '''fexp - field expression: VarExpr | ServPairExpr '''
        self.fields.append(fexp)

    def do(self, ctx:Context):
        tdef = StructDef(self.typeName)
        for fexp in self.fields:
            fexp.do(ctx)
            field = fexp.get()
            fname, ftype = '', TypeAny
            if isinstance(field, tuple) and len(field) == 2:
                fn, ft = field
                print('@2>>', fn, ft)
                fname = fn.name
                ftype = ft.get()
                print('@21>>', fname, ftype)
            elif isinstance(field, Var):
                fname = field.name
            else:
                raise EvalErr('Struct def error: fiels expression returns incorrect result: %s ' % field)
            tdef.add(Var(None, fname, ftype))
        # register new type
        ctx.addType(tdef)

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
        # field = Var(None, self.name)
        print('StructArgPair.do1', self.name, val)
        self.res = self.name, val
    
    def get(self):
        return self.res


class StructConstr(Expression):
    ''' Typename{[field-values]} '''

    def __init__(self,  typeName):
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
        print('StructConstr.do1 >> ', stype)
        inst = StructInstance(None, stype.get())
        vals = []
        for fexp in self.fieldExp:
            fexp.do(ctx)
            # if val only
            # if pair name:val
            expRes = fexp.get()
            print('StructConstr.do res:', expRes[0], expRes[1])
            # fname, val = '', None
            if isinstance(expRes, Var):
                val = expRes
                vals.append(val)
                continue
                # fieldName by order
            if isinstance(expRes, tuple) and len(expRes) == 2:
                fname, val = expRes
                # fname = fn
                # val = fv
                print('Strc.do >> ', expRes, fname, val)
                inst.set(fname, val)
            else:
                raise EvalErr('Struct def error: fiels expression returns incorrect result: %s ' % expRes)
        if len(vals) > 0:
            inst.setVals(vals)
        self.inst = inst

    def get(self):
        return self.inst

# class StructField(Expression):
#     ''' inst.field '''

#     def __init__(self):
#         self.objExp:VarExpr = None
#         self.field:str = ''
#         self.val:Var = None

#     def set(self, inst:VarExpr, field:VarExpr):
#         self.objExp = inst
#         self.field = field.name

#     def do(self, ctx:Context):
#         # print('StructField.do1', self.objExp, self.field)
#         self.objExp.do(ctx)
#         inst:StructInstance = self.objExp.get()
#         self.val = inst.get(self.field)
#         # print('StructField.do2', inst, self.val)

#     def get(self):
#         return self.val



# class _UserStruct(TypeStruct):
#     ''' struct TypeName '''
    
#     def __init__(self, name:str):
#         self._typeName = name
#         self.fieldNames:list[str] = []
#         self.fieldsTypes:dict[str, VType] = {}

#     def addField(self, name:str, stype:VType):
#         if name in self.fieldNames:
#             raise EvalErr('Field %d in struct %s already defined.')
#         self.fieldNames.append(name)
#         self.fieldsTypes[name] = stype

#     def typeName(self):
#         return self._typeName


# class _StructVar(Var):
#     ''' instance of user-defined struct'''

#     def __init__(self, name=None, stype=UserStruct):
#         super().__init__(None, name, )
#         self.type:UserStruct = stype
#         self.data:dict[str,Var] = {}

#     def checkField(self, name, val:Var=None):
#         if name not in self.type.fieldNames:
#             raise EvalErr('Struct %s doesn`t have field %s' % (name, self.type.typeName()))
#         if val is not None:
#             # field type doesn't change
#             if name in self.data and self.type.fieldsTypes[name].name != val.getType().name:
#                 raise EvalErr('Incorrect value type in struct  field assignments: %s != %s' 
#                             % (self.data[name].getType().name, val.getType().name))

#     def setVal(self, key:Var, val:Var):
#         '''set value of a field by name'''
#         k = key.get()
#         self.checkField(k, val)
#         self.data[k].setVal(val.getVal())

#     def getVal(self, key:Var)->Var:
#         fn = key.get()
#         self.checkField(fn)
#         if fn in self.data:
#             return self.data[fn]
#         raise EvalErr('Incorrect field name %s of struct %s ' % (fn, self.type.typeName()))

