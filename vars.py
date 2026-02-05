'''
Var types
'''

from lang import *
from base import *
from typex import *


class TypeVal(Val):
    def __init__(self, val:VType):
        super().__init__(val, TypeType)


class Var_(Var):
    ''' expr: _ '''
    name = '_'
    def __init__(self):
        self.vtype:VType = TypeNull()
        self.val = None

    def __str__(self):
        return '<_>'


class VarUndefined(Var):
    def __init__(self, name):
        super().__init__(name, Undefined)


# class NullisNull:
#     ''' '''

class Null:
    '''null'''

    def __init__(self):
        self.val = 0
        # super().__init__(0, TypeNull())

    def __str__(self):
        return 'null{0}'

    def __repr__(self):
        return 'null'
    
    def __eq__(self, other):
        # print('(>', other,'<)')
        return isinstance(other, Null)

    def __hash__(self):
        return hash('Null-object')

    # def get(self):
    #     return Null()

    # def setType(self, t:VType):
    #     pass


def value(val, vtype:VType)->Val:
    return Val(val, vtype)

# type: Comparable, Container, Numeric 

class CompVar(Var):
    def compare(self, other:'CompVar')-> int:
        a, b = self.get(), other.get()
        if a == b:
            return 0
        return a - b


class VarRatio(CompVar):
    def __init__(self, a:int, b:int, name=None):
        super().__init__(name, TypeRatio)
        self.numer:int = a # numerator
        self.denom:int = b # denominator

    def float(self):
        return Val(self.numer / self.denom, TypeFloat())


class FuncRes(Val):
    ''' '''
    def __init__(self, val):
        super().__init__(val, TypeAny())

class PopupBreak(Val):
    ''' '''
    def __init__(self):
        super().__init__(None, TypeNoVal())

class PopupContinue(Val):
    ''' '''
    def __init__(self):
        super().__init__(None, TypeNoVal())

# Objects


class ObjectInstance(Val):
    ''' parent of struct instances etc.  '''


class ObjectElem(Val):

    def set(self, val:Var):
        pass

    def get(self):
        pass

    def getVal(self):
        pass

# Collections


class ValSequence(Val):
    
    def getElem(self, key:Val):
        pass



class Collection(Container, ValSequence):

    def setVal(self, key:Var, val:Var):
        pass

    # def getVal(self, key:Var):
    #     pass
    
    def len(self)->int:
        return 0

    def vals(self):
        pass


class SequenceGen:

    def allVals(self):
        pass


class ListVal(Collection):
    ''' classic List / Array object'''
    
    def __init__(self, **kw):
        super().__init__(None, TypeList())
        ees = []
        if 'elems' in kw:
            ees = kw['elems']
        self.elems:list[Val] = ees

    def len(self)->int:
        return len(self.elems)
    
    def addVal(self, val:Val):
        # not sure, we need whole Var or just internal value?
        # print('List_Val.addVal:', val)
        self.elems.append(val)
    
    def addMany(self, vals:'ListVal'):
        # not sure, we need whole Var or just internal value?
        # print('ListVal.addVal:', val)
        self.elems.extend(vals.elems)
    
    def setVal(self, key:Val, val:Val):
        i = key.getVal()
        # print('List_Var.setVal', i, val, 'Len=', len(self.elems), i < len(self.elems), self.elems)
        if i >= len(self.elems):
            raise EvalErr('List out of range by index %d ' % i)
        self.elems[i] = val
    
    def getElem(self, key:Val):
        i = key.getVal()
        if i < len(self.elems):
            return self.elems[i]
        raise EvalErr('List out of range by index %d ' % i)

    def getSlice(self, beg, end):
        if beg < 0 or end > len(self.elems):
            raise EvalErr('indexes of List slice are out of range [%d : %d] with len = %d' % (beg, end, len(self.elems)))
        rdata = self.elems[beg: end]
        return ListVal(elems=rdata)

    def copy(self):
        return ListVal(elems=self.elems[:])

    def get(self):
        # print('ListVal.get', len(self.elems))
        return  [n.get() for n in self.elems] # debug

    def delete(self, index:Val):
        del self.elems[index.getVal()]

    def vals(self):
        
        r = []
        for n in self.elems:
            if isinstance(n, (FuncInst, ObjectInstance)):
                r.append(n)
                continue
            r.append(n.get())
        return r
        # return [(n.get()) for n in self.elems]
        # return [(n.get() if not isinstance(n, Collection) else n.vals()) for n in self.elems]

    def rawVals(self):
        return [n for n in self.elems]

    def has(self, val:Val):
        v = val.getVal()
        for el in self.elems:
            if v == el.getVal():
                return True
        return False

    def __str__(self):
        # nm = self.name
        # if not nm:
            # nm = '#list-noname'
        def strv(var):
            # dprint('@>>', var, var.getType(),  isinstance(var.getType(), TypeContainer), ' str:', str(var))
            if isinstance(var.getType(), TypeContainer):
                return str(var)
            return str(var.get())
        vals = [strv(n) for n in self.elems[:10]]
        return 'ListVal([%s])' % (', '.join(vals))


class TupleVal(Collection):
    ''' '''
    def __init__(self, **kw):
        super().__init__(None, TypeTuple())
        ees = []
        if 'elems' in kw:
            ees = kw['elems']
        self.elems:list[Val] = ees
        # self.vals:list = [] # TODO: optimization by store vals only

    def len(self)->int:
        return len(self.elems)
    
    def get(self):
        return tuple([n.get() for n in self.elems])
        # return tuple(self.elems)

    def addVal(self, val:Val):
        # print('() <-', val)
        self.elems.append(val)

    # def getVal(self, key:Val|int):
    #     raise XDebug("dict getVal")
        # i = key.getVal()
        # if i < len(self.elems):
        #     return self.elems[i]
        # raise EvalErr('Tuple out of range by index %d ' % i)
    
    def getElem(self, key:Val):
        i = key.getVal()
        if i < len(self.elems):
            return self.elems[i]
        raise EvalErr('Tuple out of range by index %d ' % i)

    def rawVals(self):
        return [n for n in self.elems]
    
    def vals(self):
        r = []
        for n in self.elems:
            if isinstance(n, (FuncInst, ObjectInstance)):
                r.append(n)
                continue
            r.append(n.get())
        return tuple(r)

    def has(self, val:Val):
        v = val.getVal()
        for el in self.elems:
            if v == el.getVal():
                return True
        return False

    def __str__(self):
        vals = ', '.join([ '%s' % str(n.get()) for n in self.elems])
        return 'TupleVal(%s)' %  (vals)


def dkeyCover(k):
      if isinstance(k, str):
            return StringVal(k) 
      return Val(k, valType(k))


class DictVal(Collection):
    ''' classic List / Array object'''
    
    def __init__(self):
        super().__init__(None, TypeDict())
        self.data:dict[str|int|bool,Val] = {}

    def len(self)->int:
        return len(self.data)
        
    def inKey(self, key:Var)->str:
        return '%s__%s' % (key.get(), key.getType().__class__.__name__)
    
    def getElem(self, key:Val):
        k = key.getVal()
        if k in self.data:
            return self.data[k]
        raise EvalErr('List out of range by key %s ' % k)
    
    def get(self):
        return  self.vals() # debug
    
    def delete(self, key:Val):
        del self.data[key.getVal()]

    def has(self, key:Val):
        k = key.getVal()
        return k in self.data

    def setVal(self, key:Val, val:Val):
        # k = self.inKey(key)
        self.data[key.get()] = val

    def keys(self) -> ListVal:
        kk = [dkeyCover(k) for k in self.data.keys()]
        return ListVal(elems=kk)
    
    def items(self):
        kv = [TupleVal(elems=[dkeyCover(k), v])
              for k,v in self.data.items()]
        return ListVal(elems=kv)

    def vals(self):
        return {k: v.get() for k,v in self.data.items()}

    def rawVals(self):
        return {k: v for k,v in self.data.items()}

    def __str__(self):
        def key(k):
            if isinstance(k, str):
                return "'%s'" % k
            return '%s' % k
        
        vals = '{%s}' % ', '.join([ '%s : %s' %(key(k), v) for k, v in self.vals().items()])
        return 'DictVal(%s)' %  (vals)


class StringVal(ValSequence):
    ''' '', "", ``, etc '''
    def __init__(self, val, stype=None):
        if not stype:
            stype = TypeString()
        super().__init__(val, stype)
    
    def getElem(self, key:Val):
        k = key.getVal()
        data = self.getVal()
        if len(data) <= k:
            raise EvalErr('List out of range by key %s ' % k)
        return StringVal(data[k])
    
    def len(self)->int:
        return len(self.val)

    def getSlice(self, beg, end):
        if beg < 0 or end > len(self.val):
            raise EvalErr('indexes of List slice are out of range [%d : %d] with len = %d' % (beg, end, len(self.val)))
        res =  self.val[beg: end]
        return StringVal(res)


class Regexp(Val):

    def __init__(self, pattern):
        # value of super-Val is just for debug needs
        super().__init__(pattern, TypeRegexp())
        self.pattern:re.Pattern = pattern

    def match(self, src:Val) -> Val:
        ''' '''
        res = self.pattern.match(src.getVal())
        # print('rx.match:', src.getVal(), self.pattern.pattern, bool(res))
        return bool(res)
        
    def replace(self, src:StringVal, repl:StringVal, count:Val=None) -> StringVal:
        ''' '''
        sval:str = src.getVal()
        repVal:str = repl.getVal()
        cval = 0
        if count is not None:
            cval = count.getVal()
        res = self.pattern.sub(repVal, sval, cval)
        return StringVal(res)
    
    def split(self, src:StringVal) -> ListVal:
        '''  '''
        sval = src.getVal()
        rval = self.pattern.split(sval)
        return ListVal(elems=[StringVal(s) for s in rval])
    
    def find(self, src:StringVal) -> ListVal:
        '''Searches all the matches and return table (list of lists)
            1-st (index=0) column contains matching of  full-pattern
            2-nd and others - sub values of groups
            src = value with string
            returns ListVal object
        '''
        iter = self.pattern.finditer(src.getVal())
        rvals = []
        for mt in iter:
            full = mt.group(0)
            # print('Rx.find1:', full)
            groups = mt.groups()
            grval = [full]
            grval.extend(groups)
            rvals.append(ListVal(elems=[StringVal(s) for s in grval]))
        return ListVal(elems=rvals)




class EnumItem(Val):
    def __init__(self, name, val):
        super().__init__(val, TypeInt())
        self.name = name


class Enum(Container):
    
    def __init__(self, name):
        # super().__init__(None)
        self.name = name
        self.items = []
        self.imap = {}
    
    def add(self, item:EnumItem):
        index = len(self.items)
        self.items.append(item)
        self.imap[item.name] = index
    
    def getItem(self, name):
        if name not in self.imap:
            raise EvalErr(f"Enum {self.name} doesn't have item {name}")
        return self.items[self.imap[name]]
    
    def getNames(self):
        ''' get list of all names'''
        
    def getVals(self):
        ''' get list of all vals '''
    
    def toDict(self):
        ''' DictVal {Name: val} '''



class FuncBinder(FuncSpace):
    '''
    Binds functions to the type like method to struct definition
    '''
    def __init__(self, btype:VType):
        '''
        Docstring for __init__
        
        :param btype: base type
        '''
        self.type = btype
        self.name = btype.name
        self.__funcs:dict[str, FuncInst] = {}
    
    def addMethod(self, func:FuncInst):
        name = func.getName()
        # dprint('struct.add Method:', name)
        if name in self.__funcs:
            raise EvalErr('Bound function `%s` already defined for type `%s`.' % (name, self.name))
        self.__funcs[name] = func
        
    def getMethod(self, name):
        # dprint('getMeth', name)
        if not name in self.__funcs:
            raise EvalErr('Method `%s` didn`t define in type `%s`.' % (name, self.name))
        return self.__funcs[name]


# not sure, maybe simple struct will be enough?

class Maybe(Val):
    ''' '''

    def has(self, val:Val):
        return False


class Nothing(Maybe):
    ''' x = nop '''
    def __init__(self):
        super().__init__(None, TypeMaybe())


class Thing(Maybe):
    ''' x = yep(1) '''
    def __init__(self, val):
        super().__init__(val, TypeMaybe())

    def has(self, val:Val):
        return self.val == val


def valFrom(src:Var|Val):
    if isinstance(src, (Val, Collection, StringVal, Regexp)):
        return src
    if isinstance(src, (Var)):
        return src.get()


def var2val(var:Var|Val):
    ''' Convert Var to Val instance  '''
    # print('var2val 1 :', var, type(var), var.__class__)
    var = valFrom(var)
    
    if isinstance(var, (ObjectElem)):
        var = var.get()
    if isinstance(var, (Val, Collection, Regexp, StringVal, FuncInst)):
        return var
    val = var.getVal()
    if isinstance(val, (Val, Collection, ObjectInstance, FuncInst)):
        return val
    tp = var.getType()
    return Val(val, tp)

def str2list(val):
    return ListVal(elems=[StringVal(s) for s in list(val)])
