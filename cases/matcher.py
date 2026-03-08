'''
match needed Case
'''


from lang import *
from vars import *
# from vals import isDefConst, elem2val, isLex

from cases.tcases import *
from cases.control import *
from cases.oper import *
from cases.collection import *
from cases.mt_cases import *

from nodes import *
from nodes.tnodes import *
from cases.sequence import *
from cases.runar_oper import *
from nodes.oper_nodes import *
from nodes.control import *
from cases.structs import *
from cases.funcs import *
from cases.operwords import *
from cases.modules import *

from parser import *
from bases.strformat import  *



# class CaseDebug(ExpCase):
#     def match(self, elems:list[Elem])-> bool:
#         # prels('--DEbug', elems)
#         return len(elems) > 0 and elems[0].text == '@debug'
    
#     def expr(self, elems:list[Elem])-> Expression:
#         ''' return base expression, Sub(elems) '''
#         return DebugExpr(' '.join([e.text for e in elems]))

 
# class UnclosedExpr:
#     ''' '''
#     def __init__(self, elems:list):
#         # super().__init__('')
#         self.elems:list = elems
        
#     def init(self, cline:CLine):
#         self.src = cline.src
#         self.indent = cline.indent

#     def add(self, part:list, src:TLine):
#         self.elems.extend(part)
#         self.src.add(src)


# class CaseUnclosedBrackets(ExpCase):
    
#     def match(self, elems:list[Elem])-> bool:
#         # prels('--', elems)
#         inBr = 0
#         maxLvl = 0
#         for el in elems:
#             if el.type != Lt.oper:
#                 continue
#             if el.text in '([{':
#                 inBr += 1
#                 if maxLvl < inBr:
#                     maxLvl = inBr
#                 continue
#             if el.text in ')]}':
#                 inBr -= 1
            
#         return maxLvl > 0 and inBr > 0
                
        
#     def expr(self, elems:list[Elem])-> Expression:
#         ''' return elems covered by operation case '''
#         return UnclosedExpr(elems)




# class StrFormatter(SFormatter):
#     '''parse interpret includes, eval includes, build result line'''
    
#     def __init__(self):
#         super().__init__()
#         self.fp = FormatParser()
    
#     def subExpr(self, code:str):
#         tlines = splitLexems(code)
#         clines:CLine = elemStream(tlines)
#         # print('SFm 1:', clines)
#         return line2expr(clines[0])

#     def partsToExpr(self, parts:str|subLex)->list[Expression]:
#         expp = []
#         fmOpPar = FmtOptParser()
#         for ss in parts:
#             if isinstance(ss, subLex):
#                 valExpr = self.subExpr(ss.expr)
#                 format = fmOpPar.parseSuff(ss.options)
#                 expr = ExprFormat(valExpr, format)
#                 expp.append(expr)
#             else:
#                 val = Val(ss, TypeString)
#                 expp.append(ValExpr(val))
#         rr = StrJoinExpr(expp)
#         return rr

#     def formatString(self, src:str):
#         ''' convers src string to expression '''
#         parts = self.fp.parse(src)
#         return self.partsToExpr(parts)


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


class CaseOption(ExpCase):
    ''' limitation case, it filters cases by light rules,
        container of more concrete cases '''
    
    def __init__(self, matcher, subs=None):
        if subs is None:
            subs = []
        self.subs:list[ExpCase] = subs
        self.matcher:ExpCase = matcher
    
    def match(self, elems:list[Elem])-> bool:
        # print('CO.match by %s' % (self.matcher.__class__.__name__), self.matcher.match(elems))
        return self.matcher.match(elems)
    
    def isLim(self):
        return True
    
    def find(self, elems:list[Elem]):
        cs:ExpCase|CaseOption = None
        for sub in self.subs:
            # print('co.find: %s %s' % (self.matcher.__class__.__name__, sub.__class__.__name__))
            if sub.match(elems):
                cs =  sub
                rr = '~~'
                if sub.isLim():
                    rr = 'COp.m=%s' % sub.matcher.__class__.__name__
                # print('co-found! %s' % sub.__class__.__name__, rr)
                break
        if cs and cs.isLim():
            # print('sub lim')
            cs = cs.find(elems)
        if not cs:
            return False
        # print('co-res! %s' % cs.__class__.__name__)
        return cs


class CaseLim(ExpCase):
    ''' General (parent) case '''


class CaseMatchcher:
    
    def __init__(self, cases):
        self.cases:list[ExpCase] = cases
    
    def find(self, elems:list[Elem]):
        cs = None
        for sub in self.cases:
            if sub.match(elems):
                if sub.isLim():
                    sub = sub.find(elems)
                if sub:
                    cs = sub
                # print('mch-res! %s' % cs.__class__.__name__)
                break
        return cs

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


class CaseWord(CaseLim):
    ''' vars, nums, break, etc '''
    
    # def __init__(self):
    #     super().__init__()
    #     self.subs = [CaseBreak(), CaseContinue(), CaseReturn(), CaseVar_(), CaseVar(), CaseNumVal()]
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) != 1:
            return False
        return elems[0].type in [Lt.word, Lt.num]


# Brackets

Exceptions = [ CaseBytesExplicit(), ]

class CaseBrkSquare(CaseLim):
    '''
    [expr]
    '''
    
    # def __init__(self):
    #     super().__init__()
    #     self.subs = [ CaseSlice(), CaseListGen(), CaseBytes(), CaseListComprehension(), CaseList(),]
        
    def match(self, elems:list[Elem])-> bool:
        return elems[0].text =='[' or elems[-1].text == ']'
    


class CaseGenBrackets(CaseLim):
    '''
    (expr) | [expr] | {expr}
    '''
    
    # def __init__(self):
    #     super().__init__()
    #     self.subs = [CaseBrkSquare(), CaseTuple(), CaseDictLine(), CaseBrackets()]

    
    def match(self, elems:list[Elem])-> bool:
        if elems[0].type != Lt.oper or elems[-1].type != Lt.oper:
            return False
        if elems[0].text not in ['(','[','{'] or elems[-1].text not in ['}',']',')']:
            return False
        r =  isSolidExpr(elems, getLast=True)
        if not isinstance(r, tuple):
            return False
        ok, pos = r
        if not ok or pos != 0:
            return False
        return True


# ! String cases check by not-match
class CaseStr(CaseLim):
    ''' 
    not strict matching category
    should be filtered by matchNot method first
    then - matchSubs
    '''

    def match(self, elems:list[Elem])-> bool:
        # TODO: refactor for more productivity
        if self.matchNot(elems):
            return False
        # elen = len(elems)
        return True

    def matchNot(self, elems:list[Elem])-> bool:
        ''' return 
        True if not one of string type
        False - is not certain result'''
        elen = len(elems)
        if elen not in [1, 2, 3, 5]:
            return True
        strInd = 0
        if elen > 1:
            strInd = 1
        if elems[strInd].type not in [Lt.text, Lt.mttext]:
            # print('$11', Lt.name(elems[strInd].type), elems[strInd].text)
            return True
        # print('$4', len(elems))
        match elen:
            # case 1:
            #     return elems[0].type not in [Lt.text, Lt.mttext]
            case 2:
                if not isLex(elems[0], Lt.word, ['g', 're']):
                    return True
            # case 3 if elems[0].text in ["'''", '"""', '```']:
            #     return elems[-1].text in ["'''", '"""', '```']
            case 3|5:
                if not isLex(elems[0], Lt.word, 're'):
                    return True
                if elen == 5 and (not isLex(elems[2], Lt.oper, '{') or not isLex(elems[-1], Lt.oper, '}')):
                    return True
        return False


class CaseSolid(CaseLim):
    ''' any solid expr '''
    # def __init__(self):
    #     super().__init__()
    
    def match(self, elems:list[Elem])-> bool:
        r = isSolidExpr(elems)
        # print('CaseSolid', r)
        return r


class CaseAny(CaseLim):
    
    def match(self, elems:list[Elem])-> bool:
        return True
    


class CaseSolidLeft(CaseLim):
    ''' solid with left-end '''
    
    def match(self, elems:list[Elem])-> bool:
        r = isSolidExpr(elems, True)
        # print('1>>',r)
        if not isinstance(r, tuple):
            return False
        ok, ind = r
        return ok and ind > 0
        



# # CaseMString
# # CaseBrackets -> CaseBrRound, CaseBrSquare, CaseBrCurl
# # CaseWord -> CaseKeyword, CaseVar, CaseVal
# # CaseEndBrackets -> funcCall, collectElem, structConstr
# # CaseExprLeft: ObjMember, ListExtr, FuncCurry
# expCaseSolids:list[ExpCase] = [
#     CaseBreak(), CaseContinue(), CaseReturn(),  CaseElse(), 
    
#     CaseVal(), CaseVar(), CaseVar_(), 
#     CaseString(), CaseGlif(), CaseRegexp(), 
#     CaseDotName(), CaseRTildArroy(), 
    
#     CaseListGen(), CaseBytes(), CaseBytesExplicit(),
#     CaseArgExtraList(), CaseArgExtraDict(),
#     CaseDictLine(), CaseListComprehension(),  
#     CaseTuple(), CaseList(),
    
#     CaseFunCall(), CaseStructConstr(),
#     CaseBrackets(), CaseMString()
# ]



class CaseRWord(CaseLim):
    ''' keyword expr '''
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) < 2:
            return False
        if elems[0].type != Lt.word:
            return False
        return elems[0].text in KEYWORDS_R


class CaseOperLim(CaseLim):
    ''' exrp `oper` expr '''
    
    def __init__(self):
        super().__init__()
        self.splitter = OperSplitter()
        self.opers = self.splitter.opers[5:]

    def match(self, elems:list[Elem]) -> bool:
        if len(elems) < 3:
            return False
        ind = self.splitter.mainOper(elems)
        if ind == 0 or  elems[ind].type != Lt.oper:
            return False
        return elems[ind].text in self.opers


class CaseServ(CaseLim):
    ''' '''
    
    def match(self, elems:list[Elem]) -> bool:
        if len(elems) == 0:
            return True
        if len(elems[0].text) > 1 and elems[0].text[0] == '@':
            return True



# # CaseService -> empty, debug, unclosed
# # CaseKeywordLeft -> definition, control, import
# # CaseOperators -> lambda, bin-common, inline-control, sequence, unarLeft
# #
# expCaseList:list[ExpCase] = [
#     CaseEmpty(), CaseDebug(),
#     CaseUnclosedBrackets(),
#     CaseInlineSub(),
    
#     CaseImport(), 
#     CaseFuncDef(), CaseMathodDef(), # ident func, then - method
#     CaseIf(), CaseElse(), CaseWhile(), CaseFor(),  CaseMatch(), CaseReturn(),  
#     CaseMatchCase(),
#     CaseStructBlockDef(), CaseStructDef(), CaseEnum(),
    
#     CaseLambda(),
#     CaseSemic(), CaseBinOper(), CaseCommas(),
#     CaseLUnar(StrFormatter()),
# ]