'''

'''

from lang import *


class LangError(Exception):
    def __init__(self, msg, *args):
        # super().__init__(*args)
        self.msg = msg
        self.args = args

class XDebug(LangError):
    def __init__(self, *args):
        super().__init__(*args)
    

class InterpretErr(LangError):
    def __init__(self, msg='', src:CLine=None, parent:Exception=None):
        super().__init__(msg)
        self.src:CLine = src
        self.parent = parent


class EvalErr(LangError):
    def __init__(self, *args):
        super().__init__(*args)


class TypeErr(LangError):
    def __init__(self, *args):
        super().__init__(*args)


# def inst(self, *args)->Base:
#     return VType()


LANG_WORDS = [word.strip() for line in '''
for while if else func type def var match case
list dict struct
'''.splitlines() for word in line.split(' ') if word.strip() != '']

class Base:
    ''' '''
    def __init__(self):
        pass
    def get(self)->'Base':
        pass


class VType(Base):
    ''' Base of Var Type '''
    name = 'type'
    ''' '''
    def __init__(self):
        pass


class TypeAny(VType):
    name = 'Any'


class Val(Base):
    ''' 
    Val is a value with type;
    type should be defined
    Val shouldn`t be changed after creation
    '''
    def __init__(self, val, vtype:VType):
        self.val = val
        if vtype is None:
            vtype = TypeAny()
        self.vtype:VType = vtype

    def get(self):
        return self.val

    def getVal(self):
        return self.get()

    def getType(self):
        return self.vtype

    def __str__(self):
        # n = self.name
        # if not n:
        #     n = '#noname'
        # tt = '#notype'
        # if self.vtype is not None:
        tt = self.vtype.name
        return '%s(%s: %s)' % (self.__class__.__name__, self.val, tt)


class Container(Val):
    ''' Contaiter Var list, dict, etc '''



class Var(Base):
    '''
    Var contains Val or any children of Val: ListVal, DictVal, StructInstance
    '''
    def __init__(self, name, vtype:VType, **kw):
        strict = False
        mutable = True
        if 'strict' in kw:
            strict = kw['strict']
        if 'const' in kw:
            mutable = not kw['const']
        # debug exception
        if not isinstance(name, str):
            dprint('name type:', type(name))
            raise InterpretErr('OLD VAR USAGE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! %s ' % type(name))
        self.val:Val = None
        self.name:str = name # if name is none - here Val, not Var
        self.vtype:VType = vtype
        self._mutable = mutable # makes Var const
        self._strict = strict # makes Var strict typed

    def set(self, val):
        if self.val is not None and not self._mutable:
            raise EvalErr('Attemps to change immutable variable %s ' % self.name)
        self.val = val
    
    def get(self):
        return self.val
    
    def getName(self):
        return self.name
    
    def getVal(self):
        if isinstance(self.val, Container):
            return self.val
        return self.val.getVal()
    
    def setType(self, t:VType):
        if self._strict:
            raise EvalErr('Attemps to change type (%s) of strict-typed variable %s : %s ' % (t.name, self.name, self.getType().name))
        self.vtype = t
    
    def getType(self):
        return self.vtype
    
    # TODO: fix Var-to-string for all builtin types: 
    # null, bool, int, float, complex-num, string,
    # list, dict, struct, tuple 
    def __str__(self):
        n = self.name
        if not n:
            n = '#noname'
        tt = '#notype'
        if self.vtype is not None:
            tt = self.vtype.name
        return '%s(%s, %s: %s)' % (self.__class__.__name__, n, self.val, tt)

