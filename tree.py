
"""
"""

# import re

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
from nodes.oper_nodes import *
from nodes.control import *
from cases.structs import *
from cases.funcs import *
from cases.operwords import *
from cases.modules import *

from parser import *
from bases.strformat import  *


class CaseDebug(ExpCase):
    def match(self, elems:list[Elem])-> bool:
        # prels('--DEbug', elems)
        return len(elems) > 0 and elems[0].text == '@debug'
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' return base expression, Sub(elems) '''
        return DebugExpr(' '.join([e.text for e in elems]))

 
class UnclosedExpr:
    ''' '''
    def __init__(self, elems:list):
        # super().__init__('')
        self.elems:list = elems
        
    def init(self, cline:CLine):
        self.src = cline.src
        self.indent = cline.indent

    def add(self, part:list, src:TLine):
        # prels('Uncl.add: ', part)
        self.elems.extend(part)
        self.src.add(src)


class CaseUnclosedBrackets(ExpCase):
    
    def match(self, elems:list[Elem])-> bool:
        # prels('--', elems)
        inBr = 0
        maxLvl = 0
        for el in elems:
            if el.type != Lt.oper:
                continue
            if el.text in '([{':
                inBr += 1
                if maxLvl < inBr:
                    maxLvl = inBr
                continue
            if el.text in ')]}':
                inBr -= 1
            
        return maxLvl > 0 and inBr > 0
                
        
    def expr(self, elems:list[Elem])-> Expression:
        ''' return elems covered by operation case '''
        return UnclosedExpr(elems)




class StrFormatter(SFormatter):
    '''parse interpret includes, eval includes, build result line'''
    
    def __init__(self):
        super().__init__()
        self.fp = FormatParser()
    
    def subExpr(self, code:str):
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        # dprint('SFm 1:', clines)
        return line2expr(clines[0])

    def partsToExpr(self, parts:str|subLex)->list[Expression]:
        expp = []
        fmOpPar = FmtOptParser()
        for ss in parts:
            if isinstance(ss, subLex):
                valExpr = self.subExpr(ss.expr)
                format = fmOpPar.parseSuff(ss.options)
                expr = ExprFormat(valExpr, format)
                expp.append(expr)
            else:
                val = Val(ss, TypeString)
                expp.append(ValExpr(val))
        rr = StrJoinExpr(expp)
        return rr

    def formatString(self, src:str):
        ''' convers src string to expression '''
        parts = self.fp.parse(src)
        return self.partsToExpr(parts)

# CaseMString
expCaseSolids:list[ExpCase] = [
    CaseBreak(), CaseContinue(), CaseRegexp(), CaseReturn(),  CaseElse(), 
    CaseVal(), CaseVar(), CaseVar_(), CaseDotName(), CaseString(),
    CaseTuple(),
    CaseListGen(),
    CaseDictLine(), CaseListComprehension(), CaseSlice(), CaseList(), CaseCollectElem(), 
    CaseFunCall(), CaseStructConstr(),
    CaseBrackets()
    ]

expCaseList:list[ExpCase] = [ 
    CaseEmpty(), CaseComment(), CaseDebug(),
    CaseUnclosedBrackets(),
    CaseImport(),
    CaseInlineSub(),
    CaseFuncDef(), CaseMathodDef(),
    # CaseBreak(), CaseContinue(), CaseRegexp(),
    CaseIf(), CaseElse(), CaseWhile(), CaseFor(),  CaseMatch(), CaseReturn(),  
    CaseMatchCase(),
    CaseArgExtraList(), CaseArgExtraDict(),
    CaseStructBlockDef(), CaseStructDef(),
    CaseLambda(), 
    CaseSemic(), CaseBinOper(), CaseCommas(),
    # CaseTuple(),
    # CaseDictBlock(), CaseListBlock(), 
    # CaseListGen(),
    # CaseDictLine(), CaseListComprehension(), CaseSlice(), CaseList(), CaseCollectElem(), 
    # CaseFunCall(), CaseStructConstr(), 
    CaseMString(), CaseUnar(StrFormatter()),
    # CaseVar_(), CaseVal(), CaseString(), CaseVar(), CaseBrackets() 
]

patternMatchCasesSolid = [
    MT_Other(),
    MTVal(), MTString(), MTRegexp(), MTList(), MTTuple(), MTDict(), MTStruct(), 
]

patternMatchCasesCplx = [
    MTPtGuard(), MTMultiCase(), MTTypedVal(), MTDuaColon(), MTMultiTyped(),
]


def getCases()->list[ExpCase]:
    return expCaseList


def simpleExpr(expCase:ExpCase, elems)->Expression:
    # dprint('#simple-case:', expCase)
    return expCase.expr(elems)


def mtCases(elems:list[Elem], cases: list[ExpCase], parent:ExpCase=None)->MatchingPattern:
    # print('mtCases', [repr(cc) for cc in cases])
    if isinstance(parent, (MTList)):
        cases = pMListInnerCases
    for mtCase in cases:
        # print('mtC>', mtCase)
        if mtCase.match(elems):
            # print('mt.found>', mtCase.__class__.__name__, '', elemStr(elems))
            if mtCase.hasSubExpr():
                pattr, subElems = mtCase.split(elems)
                subExp = elems2expr(subElems)
                pattr = mtCase.setSub(pattr, subExp)
            else:
                pattr = mtCase.expr(elems)
            return pattr
    return None


def makePMatchExpr(elems:list[Elem], parent:ExpCase=None)->MatchingPattern:
    # print('#makePMatchExpr:', [(n.text, Lt.name(n.type)) for n in elems])
    # print('\n#tree-makePMatchExpr/1::', ' '.join(["'%s'"%n.text for n in elems]))
    caseList = patternMatchCasesSolid
    if not isSolidExpr(elems):
        caseList = patternMatchCasesCplx
        
    found = mtCases(elems, caseList, parent)
    if found:
        return found
    
    # print('DEBUG: No current MTCase for `%s` ' % '~'.join([n.text for n in elems]))
    raise InterpretErr('No current MTCase for `%s` ' % ''.join([n.text for n in elems]))


def complexExpr(expCase:SubCase, elems:list[Elem])->Expression:
    base, subs = expCase.split(elems)
    # print('#complex-case:', expCase.__class__.__name__, ' base:', base, subs)
    # print('#complexExpr', expCase.__class__.__name__, base, '', [elemStr(s) for s in subs])

    if not expCase.sub():
        return base
    
    if isinstance(expCase, CaseMatchCase):
        # pattern !- block
        pattern =  makePMatchExpr(subs[0])
        block = elems2expr(subs[1])
        expCase.setSub(base, [pattern, block])
        # print('complexExpr..CaseMatchCase', base)
        return base
        
    
    if not subs or not subs[0]:
        return base
    
    subExp:list[Expression] = []
    for sub in subs:
        # prels('#complexExpr1:', sub)
        texpr = elems2expr(sub)
        # if isinstance(texpr, NothingExpr):
        #     continue
        subExp.append(texpr)
    bb = expCase.setSub(base, subExp)
    if bb is not None:
        base = bb
    return base

def makeExpr(expCase:ExpCase, elems:list[Elem])->Expression:
    # dprint('makeExpr', [n.text for n in elems])
    if expCase.sub():
        return complexExpr(expCase, elems)
    return simpleExpr(expCase, elems)

def elems2expr(elems:list[Elem])->Expression:
    # print('#elems2expr:', [(n.text, Lt.name(n.type)) for n in elems])
    # print('/n#elems2expr/1::', ' '.join(["'%s'"%n.text for n in elems]))
    
    # checkSolid:
    if isSolidExpr(elems):
        # print('elems2expr/isSolidExpr', expCaseSolids)
        for expCase in expCaseSolids:
            # print('#elems2expr/2:', type(expCase).__name__, (elems))
            # print('#elems2expr/12:', type(expCase).__name__)
            if expCase.match(elems):
                # print('CaseSl found::', expCase.__class__.__name__, '', elemStr(elems), '\n')
                expr = makeExpr(expCase, elems)
                if isinstance(expr, CtrlSubExpr):
                    # print('#elems2expr/3 ', expr)
                    expr = expr.toControl()
                # print('\n#EL2EX . expr:', expr, '', elemStr(elems))
                return expr
    
    # print('elems2expr/other')
    for expCase in getCases():
        # print('#elems2expr/2:', type(expCase).__name__, (elems))
        # print('#elems2expr/2:', type(expCase).__name__)
        if expCase.match(elems):
            # print('CaseOt found::', expCase.__class__.__name__, '', elemStr(elems), '\n')
            # print('Case found::', expCase.__class__.__name__)
            expr = makeExpr(expCase, elems)
            if isinstance(expr, CtrlSubExpr):
                # print('#elems2expr/3 ', expr)
                expr = expr.toControl()
            # print('\n#EL2EX . expr:', expr, '', elemStr(elems))
            return expr
    # print('tree:DEBUG: No current ExprCase for `%s` ' % ''.join([n.text for n in elems]))
    raise InterpretErr('No current ExprCase for `%s` ' % '_'.join([n.text for n in elems]))


def line2expr(cline:CLine)-> Expression:
    ''' '''
    # types: assign, just value, definition, definition content (for struct), operator, func call, control (for, if, func, match, case), 
    try:
        # print('>> line2expr 1:', ''.join([n.text for n in cline.code]))
        expr = elems2expr(cline.code)
        # print('>> line2expr 2:', expr)
        expr.src = cline
        return expr
    except InterpretErr as ixc:
        ixc.src = cline
        raise ixc
    except Exception as exc:
        ixc = InterpretErr("Error in `line2expr`", cline, exc)
        raise ixc


def raw2done(parent:Expression, raw:RawCase)->Expression:
    ''' post-process for sub-level sub-expressions:
        match-case | expr -> expr
        struct-field | expr : expr
        dict-(key:val) | expr : expr
        etc.
    '''
    # match-case
    # print('>> raw2done', parent, raw)
    if isinstance(parent, MatchExpr) and isinstance(raw, MatchPtrCase):
        # `case` sub-expr in `match`
        res = CaseExpr()
        res.setExp(raw.left)
        if raw.right:
            # one-line case
            res.add(raw.right)
        return res
    # lambdas ...



def lex2tree(src:list[CLine]) -> Block:
    ''' '''
    root = Module()
    if len(src) == 0:
        return root
    curBlock = root
    lineNum = 0
    parents:list[Block] = []
    # dprint('~~~~~~~~~~~` start tree builder ~~~~~~~~~~~~')
    i = -1

    unclosed = None
    prev = root # expr of prev line
    expr = root
    indent = src[0].indent
    caseComment = CaseComment()
    for cline in src:
        i += 1
        # print('  -  -  - ')
        lineNum += 1
        cline.line = lineNum
        
        # print('\n(((((( == >>>>>---------- #cline-code1:', f"<{' '.join([ee.text for ee in cline.code])}>", ' ))))) curBlock:>>', repr(curBlock))
        # print('#code-src: `%s`' % cline.src.src, '$ind=',  indent, '; curInd=', curInd)
        # print('#  --- ', [(ee.text, Lt.name(ee.type)) for ee in cline.code])
        if len(cline.code) == 0:
            continue
        
        # code = cline.code
        if unclosed is not None:
            unclosed.add(cline.code, cline.src)
            # code = unclosed.elems
            # updated cline for unclosed
            cline = CLine(unclosed.src, unclosed.elems, unclosed.indent)
            # prels('unclosed: ', unclosed.elems)
        
        else:
            if caseComment.match(cline.code):
                # nothing for comment now
                continue
        
        # get expression
        prev = expr
        expr = line2expr(cline) # >>>>>>>>>>>>>>>>>>> Expression 
        
        # print( '$ind=',  indent, '; prevIndent=', prevIndent)
        
        if isinstance(expr, UnclosedExpr):
            # Start processing unclosed expressions
            expr.init(cline)
            if unclosed is None:
                unclosed = expr
                # unclosed.indent = indent
            continue
        else:
            if unclosed is not None:
                unclosed = None
        
        if isinstance(expr, CaseComment):
            # nothing for comment now
            continue
        
        prevIndent = indent
        if unclosed is None:
            indent = cline.indent
        else:
            indent = unclosed.indent

        if isinstance(expr, CtrlSubExpr):
            expr = expr.toControl()
        
        # print('lex2tree-2 expr:', repr(expr), 'prev:', repr(prev), 
            #   '; \n ^^ parents:', [repr(n) for n in parents], repr(curBlock), ('in=',  indent, '; pin=', prevIndent))
        goBack = False # if we move back from nected block
        # goBack = indent < curInd #  and (isinstance(expr, ElseExpr) and not expr.hasIf())
        goBack = indent < prevIndent
        goDeep = indent > prevIndent
        prevPar = []
        if goBack:
            stepsUp = prevIndent - indent
            for i in range(stepsUp):
                # print('------', i, repr(parents[-1]), repr(curBlock))
                prevPar.append(curBlock)
                curBlock = parents.pop()

        
        if isinstance(expr, ElseExpr): # else | else if ..
            if not prevPar or not isinstance(prevPar[-1], (IfExpr,ElsFold)):
                raise EvalErr('Incorrect `else` block after non-`if`')
            parents.append(curBlock)
            curBlock = prevPar[-1]
            # print('in Else:', repr(curBlock), repr(expr))
            curBlock.toElse(expr)
            if isinstance(curBlock, IfExpr):
                # ELSE statement
                curBlock = ElsFold(curBlock)
                # print('    Else-1', repr(curBlock))
        
            if expr.hasIf(): # else if ..
                # print('    Else-2', repr(curBlock), repr(expr))
                curBlock.setNext(expr)
            continue
            
        if goDeep and prev.add:
            # start new block
            # print('! goDeep', repr(curBlock), repr(prev), repr(expr),'is ELSE?:', isinstance(prev, (ElseExpr)))
            # prev.toBlock()
            if not isinstance(prev, (ElseExpr)):
                parents.append(curBlock)
                curBlock = prev

        if isinstance(expr, RawCase):
            expr = raw2done(curBlock, expr)
            # print('>> after raw:', expr)
        
        # if 1-line block
        if isinstance(expr, SequenceExpr):
            if expr.delim == ';':
                for subExp in expr.getSubs():
                    curBlock.add(subExp)
            continue
        
        curBlock.add(expr)

    return root
