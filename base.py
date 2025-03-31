

LANG_WORDS = [word.strip() for line in '''
for while if else func type def var match case
list dict struct
'''.splitlines() for word in line.split(' ') if word.strip() != '']


# def inst(self, *args)->Base:
#     return VType()

class Base:
    ''' '''
    def get(self)->'Base':
        pass


class VType(Base):
    ''' Base of Var Type '''
    name = 'type'



class Var(Base):
    def __init__(self, val:Base, name=None, vtype:VType=None):
        self.val:Base = val
        self.name = name # if name is none - here Val, not Var
        self.vtype:VType = vtype
    
    def set(self, val):
        self.val = val
    
    def get(self):
        return self.val
    
    def setType(self, t:VType):
        self.vtype = t
    
    def getType(self):
        return self.vtype
    
    def __str__(self):
        n = self.name
        if not n:
            n = '#noname'
        tt = '#undefined'
        if self.vtype is not None:
            tt = self.vtype.name
        return '%s(%s, %s: %s)' % (self.__class__.__name__, n, self.val, tt)

