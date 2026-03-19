'''
match needed Case
'''


from lang import *
from vars import *
# from vals import isDefConst, elem2val, isLex

from cases.tcases import *
# from cases.control import *
# from cases.oper import *
# from cases.collection import *
# from cases.mt_cases import *
from cases.sequence import *
# from cases.runar_oper import *
# from cases.structs import *
# from cases.funcs import *
# from cases.operwords import *
# from cases.modules import *

# from nodes import *
# from nodes.tnodes import *
# from nodes.oper_nodes import *
# from nodes.control import *

# from parser import *
# from bases.strformat import  *


_1 = r''' 

single

    brackets
    ()
        (,), (expr)
    []
        list, slice, [iter: gen], [com;pre;hension], 0x[bytes], [by te s]
    {}
        dict
    
    right-brackets
        func-call()
        collect[elem]
        struct{constr}
    
    expr-chain
        obj.elem
        list...
        expr~>
        
        
    text-line
        string
        glif
        regexp
    
    numeric
        int, float, bool, null
    
    word
        _
        var
        keyword-single
            else, continue, break, return-empty

complex
    empty, debug
    unclosed-brackets
    operator
        bin-oper
        unar-left
    
    sequence
        n,n / n;n / n:n /
    inline-sub /:
    keyword-line
        def
            func, struct, enum, import
        control
            if, for, while, match
            match-case
        other
            return-val
    lambda
    m-string?

'''


class CaseLim(ExpCase):
    ''' General (parent) case '''
    
    def isLim(self):
        return True


class CaseAny(CaseLim):
    
    def match(self, elems:list[Elem])-> bool:
        return True


class CMatchInfo:
    
    def __init__(self, elems:list[Elem]):
        self.elems = elems
        self.solid = None # is solid res
        self.sid = None # solid id
        self.mid = None # main elem id
        self.splitter = OperSplitter.getInst()

    def isSolid(self):
        ok, id = isSolidExpr(self.elems, getLast=True)
        self.solid = ok
        self.sid = id
        return ok

    def findMain(self):
        self.mid =self.splitter.mainOper(self.elems)


class CaseOption(ExpCase):
    ''' limitation case, it filters cases by light rules,
        container of more concrete cases '''
    
    def __init__(self, matcher, subs=None):
        if subs is None:
            subs = []
        self.subs:list[ExpCase] = subs
        self.matcher:CaseLim = matcher
    
    def match(self, info:CMatchInfo)-> bool:
        # print('CO.match by %s' % (self.matcher.__class__.__name__), self.matcher.match(info))
        return self.matcher.match(info)
    
    def isLim(self):
        return True
    
    def find(self, info:CMatchInfo):
        cs:ExpCase|CaseOption = None
        for sub in self.subs:
            mtarg = info
            if not sub.isLim():
                mtarg = info.elems
            if sub.match(mtarg):
                cs =  sub
                break
        if cs and cs.isLim():
            # print('sub lim')
            cs = cs.find(info)
        if not cs:
            return False
        return cs



class CaseOptionPrepared(CaseOption):
    ''' limitation case, it filters cases by light rules,
        container of more concrete cases '''
    
    def __init__(self, matcher, subs=None):
        if subs is None:
            subs = []
        self.subs:list[ExpCase] = subs
        self.matcher:CaseLim = matcher
        self.found = None
    
    def match(self, info:CMatchInfo)-> bool:
        # print('COP.match by %s' % (self.matcher.__class__.__name__), self.matcher.match(info))
        self.found = None
        mres = self.matcher.match(info)
        if isinstance(mres, tuple):
            self.found = mres[1]
            mres = mres[0]
        return bool(mres)
    
    def find(self, info:CMatchInfo):
        cs:ExpCase|CaseOption = None
        for sub in self.subs:
            # print('co.find: %s %s' % (self.matcher.__class__.__name__, sub.__class__.__name__))
            extrArg = None
            if self.found is not None:
                extrArg = self.found
            
            if sub.match(info.elems, extrArg):
                cs =  sub
                break
        if cs and cs.isLim():
            # print('sub lim')
            cs = cs.find(info.elems)
        if not cs:
            return False
        # print('co-res! %s' % cs.__class__.__name__)
        return cs


class CaseMatchcher:
    
    def __init__(self, cases):
        self.cases:list[ExpCase] = cases
    
    def find(self, info:CMatchInfo):
        cs = None
        elems:list[Elem] = info.elems
        for sub in self.cases:
            if sub.match(info):
                if sub.isLim():
                    sub = sub.find(info)
                if sub:
                    cs = sub
                # print('mch-res! %s' % cs.__class__.__name__)
                break
        return cs


class CaseSolid(CaseLim):
    ''' any solid expr '''
    # def __init__(self):
    #     super().__init__()
    
    def match(self, info:CMatchInfo)-> bool:
        # ok, _ = isSolidExpr(info.elems)
        info.isSolid()
        return info.solid
    
    
class NonSolid(CaseLim):
    def match(self, info:CMatchInfo)-> bool:
        info.findMain()
        # return info.mid  > 0
        return True


class CaseSolidLeft(CaseLim):
    ''' solid with left-end '''
    
    def match(self, info:CMatchInfo)-> bool:
        # ok, ind = isSolidExpr(elems, True)
        # print('1>> CaseSolidLeft >> ', elemStr(elems), (ok, ind ),  ok and ind > 0)
        # if not isinstance(r, tuple):
        #     return False
        # ok, ind = r
        ok, ind = info.solid, info.sid
        # print('$2', ok, ind, ok and ind > 0)
        return (ok and ind > 0), ind


# class CaseCateg:
#     ''' General (parent) case '''
    
#     def __init__(self):
#         self.subs = []
    
#     def isGen(self):
#         return True
    
#     def match(self, elems:list[Elem])-> bool:
#         return False
    
#     def matchNot(self, elems:list[Elem])-> bool:
#         return False
    
#     def matchSubs(self, elems:list[Elem]):
#         for sub in self.subs:
#             if sub.match(elems):
#                 return sub
#         return False

_numWordTypes = [Lt.word, Lt.num]

class CaseWord(CaseLim):
    ''' vars, nums, break, etc '''
    
    # def __init__(self):
    #     super().__init__()
    #     self.subs = [CaseBreak(), CaseContinue(), CaseReturn(), CaseVar_(), CaseVar(), CaseNumVal()]
    
    def match(self, info:CMatchInfo)-> bool:
        if len(info.elems) != 1:
            return False
        return info.elems[0].type in _numWordTypes


# Brackets

Exceptions = [ CaseBytesExplicit(), ]

class CaseBrkSquare(CaseLim):
    '''
    [expr]
    '''
    
    # def __init__(self):
    #     super().__init__()
    #     self.subs = [ CaseSlice(), CaseListGen(), CaseBytes(), CaseListComprehension(), CaseList(),]
        
    def match(self, info:CMatchInfo)-> bool:
        return info.elems[0].text =='[' or info.elems[-1].text == ']'
    

_opnenBrs = ['(','[','{']
_closeBrs = ['}',']',')']

class CaseGenBrackets(CaseLim):
    '''
    (expr) | [expr] | {expr}
    '''
    
    # def __init__(self):
    #     super().__init__()
    #     self.subs = [CaseBrkSquare(), CaseTuple(), CaseDictLine(), CaseBrackets()]

    
    def match(self, info:CMatchInfo)-> bool:
        if not info.solid or info.sid != 0:
            return False
        elems = info.elems
        if elems[0].type != Lt.oper or elems[-1].type != Lt.oper:
            return False
        if elems[0].text not in _opnenBrs or elems[-1].text not in _closeBrs:
            return False
        # r =  isSolidExpr(elems, getLast=True)
        # if not isinstance(r, tuple):
        #     return False
        # ok, pos = r
        # if not ok or pos != 0:
        #     return False
        return True
        return info.solid and info.sid == 0

_strPerfs = ['g', 're']
_strLexTypes =  [Lt.text, Lt.mttext]

# ! String cases check by not-match
class CaseStr(CaseLim):
    ''' 
    not strict matching category
    should be filtered by matchNot method first
    then - matchSubs
    '''

    def match(self, info:CMatchInfo)-> bool:
        # TODO: refactor for more productivity
        if self.matchNot(info.elems):
            return False
        # elen = len(elems)
        return True

    def matchNot(self, elems:list[Elem])-> bool:
        ''' return 
        True if not one of string type
        False - is not certain result'''
        elen = len(elems)
        # print('strLim', elen)
        if elen not in [1, 2, 3, 5]:
            return True
        strInd = 0
        if elen > 1:
            if not isLex(elems[0], Lt.word, _strPerfs):
                return True
            strInd = 1
        if elems[strInd].type not in _strLexTypes:
            # print('$11', Lt.name(elems[strInd].type), elems[strInd].text)
            return True
        # print('$4', len(elems))
        match elen:
            # case 1:
            #     return elems[0].type not in [Lt.text, Lt.mttext]
            # case 2:
            # case 3 if elems[0].text in ["'''", '"""', '```']:
            #     return elems[-1].text in ["'''", '"""', '```']
            case 3:
                return elems[-1].type != Lt.word
            case 5:
                if (not isLex(elems[2], Lt.oper, '{') or not isLex(elems[-1], Lt.oper, '}')):
                    return True
        return False


class CaseRWord(CaseLim):
    ''' keyword expr '''
    
    def match(self, info:CMatchInfo)-> bool:
        elems = info.elems
        if len(elems) < 2:
            return False
        if elems[0].type != Lt.word:
            return False
        return elems[0].text in KEYWORDS_R


class CaseOperLim(CaseLim):
    ''' exrp `oper` expr '''
    
    def __init__(self):
        super().__init__()
        self.splitter = OperSplitter.getInst()
        self.opers = self.splitter.opers[5:]

    def match(self, info:CMatchInfo) -> bool:
        if len(info.elems) < 3:
            return False
        # ind = self.splitter.mainOper(info.elems)
        ind = info.mid
        if ind == 0 or  info.elems[ind].type != Lt.oper:
            return False
        return (info.elems[ind].text in self.opers), ind


class CaseServ(CaseLim):
    ''' '''
    
    def match(self, info:CMatchInfo) -> bool:
        if len(info.elems) == 0:
            return True
        if len(info.elems[0].text) > 1 and info.elems[0].text[0] == '@':
            return True

