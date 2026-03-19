'''
Cases with sequences:
String, bytes, enum
'''


import re

from lang import *
from vars import *
from vals import  elem2val, isLex

from cases.utils import *
from cases.tcases import *

from nodes.tnodes import *



class CaseString(CaseVal, SolidCase):
    ''' '''
    def match(self, elems:list[Elem]) -> bool:
        # print('StrCase:', elems, ' strlen=', len(elems))
        if len(elems) != 1:
            return False
        if elems[0].type in [Lt.text]:
            return True
        return False
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value rom local const'''
        res = StringExpr(elem2val(elems[0]), 'TODO:quot')
        return res


class CaseMString(ExpCase):
    ''' '''
    def __init__(self):
        super().__init__()
        self.mqoutes = '""" ``` \'\'\''.split(' ')
        
    
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) != 1:
            return False
        if elems[0].type != Lt.mttext:
            return False
        # print('CMSt#1', '|%s|' % elems[0].text[:3], '',  elems[0].text[:3] in mqoutes)
        # print('CMSt#1', '|%s|' % elems[-1].text[-3:], '',  elems[-1].text[-3:] in mqoutes)
        if elems[0].text[:3] not in self.mqoutes:
            return False
        if len(elems[-1].text) < 3 or elems[-1].text[-3:] not in self.mqoutes:
            return False
        
        for el in elems:
            if el.type != Lt.mttext:
                return False
        return True
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' Value rom local const'''
        res = []
        val = elems[0].text[3:-3]
        res = MString(val, elems[0].text[:3])
        return res


class CaseBytes(ExpCase, SolidCase):
    ''' hex numbers in [ ]
        [01 0a a0 ff] 
        maybe:
        [01 02 {var} 04] - thinking
    '''
    
    def __init__(self):
        super().__init__()
        self.nrx = re.compile(r'[0-9a-f]{1,2}', re.I) 
        self.numBases = {'x':16, 'b':2, 'd': 10, 'o':8}
    
    def match(self, elems:list[Elem], min3=0) -> bool:
        ''' '''
        ln = len(elems)
        min = 4 - min3
        if ln < min:
            return False
        if not isLex(elems[0], Lt.oper, '[') and not isLex(elems[-1], Lt.oper, ']'):
            return False
        okTypes = (Lt.num, Lt.word)
        for n in elems[1:-1]:
            # print('', n.text, Lt.name(n.type))
            if not (n.type in okTypes and self.nrx.match(n.text)):
                return False
        return True


    def expr(self, elems:list[Elem], pref=None)-> Expression:
        bb = bytearray2()
        # print('$1 ', pref)
        numBase = 16
        if pref:
            nb = pref[1]
            assert 'bdox'.index(nb) >= 0
            numBase = self.numBases[nb]
        # print('nbase', numBase)
        nums = [n.text for n in elems[1: -1]]
        
        # if nums without spaces: 0b[1010101010], 0x[f011dde50f1234]
        match numBase:
            case 2:
                t = []
                for p in nums:
                    if len(p) > 1:
                        p = list(p)
                    else:
                        p = [p]
                    t.extend(p)
                # print('$1: ', len(t))
                
                if len(t) % 8 > 0:
                    t = ['0' for _ in range(8 - (len(t) % 8))]  + t
                # print('$2: ', len(t), t)
                lnt = int(len(t) / 8)
                nums = [''.join(t[i*8 : (i+1) * 8]) for i in range(lnt)]
            case 16:
                t = []
                for p in nums:
                    lnp = len(p)
                    if lnp != 2:
                        # p = list(p)
                        if lnp % 2 >0:
                            # fix length by leading 0
                            p = f'0{p}'
                        p = [p[i * 2 : (i+1) * 2] for i in range(int(len(p)/2))]
                    else:
                        p = [p]
                    # print('$3:', p)
                    t.extend(p)
                nums = t
        # print('', nums)
        for n in nums:
            bb.append(int(n, numBase))
        # var2val
        bexp = BytesExpr(bb)
        return bexp


class CaseBytesExplicit(CaseBytes):
    def __init__(self):
        super().__init__()
        self.xre = re.compile(r'0[xobd]')
    
    def match(self, elems:list[Elem], ind=-1) -> bool:
        if len(elems) < 3:
            return False
        if not isLex(elems[1], Lt.oper, '[') and not isLex(elems[-1], Lt.oper, ']'):
            return False
        
        if elems[0].type != Lt.num:
            return False
        if len(elems[0].text) != 2 or not self.xre.match(elems[0].text):
            return False
        # print('$5:', elemStr(elems), Lt.name(elems[0].type))
        return super().match(elems[1:], 2)
    
    def expr(self, elems:list[Elem])-> Expression:
        return super().expr(elems[1:], elems[0].text)


class CaseEnum(SubCase):
    '''
    enum Name a, b, c
    enum Name a=1, b, c
    enum Name
        a = 10,
        b,
        c
    '''

    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 2:
            return False
        if isLex(elems[0], Lt.word, 'enum') and elems[1].type == Lt.word:
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ename = elems[1].text
        subStart = 2
        
        sub = elems[subStart:]
        # print('enum items: {=%s=}'% elemStr(sub))
        exp = EnumDef(ename, src=elems)
        subs = []
        if sub:
            subs = [sub]
        cs = CaseCommas()
        if cs.match(sub):
            _, subs = cs.split(sub)
        # print('subs:', ['{%s}'% elemStr(s) for s in subs])
        return exp, subs

    def setSub(self, base:EnumDef, subs:list[Expression])->Expression:
        # print('CaseEnum setSub', base, subs)
        for exp in subs:
            base.add(exp)
        return base



# Future cases
class CaseGenConstSet(SubCase):
    ''' set like enum but for other types,
    if enum elem is int value, so enum A a=1; a == 1 >> true
    otherwise this type is strictly related to set-type, and sub val.
    fixet B a=1; a == 1 >> false
    only B.a is equal to B.a
    '''

    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 3:
            return False
        if isLex(elems[0], Lt.word, 'enum') and elems[1].type == Lt.word:
            return True

    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ename = elems[1].text
        # prels('CaseStructDef.split', elems, show=1)
        # struct B(A,C)
        # superNames = []
        subStart = 2
        typeExpr = None
        # If enum has type of elem
        if len(elems) > 3 and isLex(elems[2], Lt.oper, ':'):
            # print('$1:', elems[2].text)
            cv = CaseVar()
            typeElems = elems[3:4]
            if not cv.match(typeElems):
                raise InterpretErr("Incorrect lexem sequence for types Enum definition.")
            typeExpr = cv.expr(typeElems)
            subStart = 4
        
        sub = elems[subStart:]
        #...
    
