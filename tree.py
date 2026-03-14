
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

from cases.matcher import *


class StrFormatter(SFormatter):
    '''parse interpret includes, eval includes, build result line'''
    
    def __init__(self):
        super().__init__()
        self.fp = FormatParser()
    
    def subExpr(self, code:str):
        tlines = splitLexems(code)
        clines:CLine = elemStream(tlines)
        # print('SFm 1:', clines)
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


# CaseMString
# CaseBrackets -> CaseBrRound, CaseBrSquare, CaseBrCurl
# CaseWord -> CaseKeyword, CaseVar, CaseVal
# CaseEndBrackets -> funcCall, collectElem, structConstr
# CaseExprLeft: ObjMember, ListExtr, FuncCurry
expCaseSolids:list[ExpCase] = [
    CaseBreak(), CaseContinue(), CaseReturn(),  CaseElse(), 
    
    CaseNumVal(), CaseVar(), CaseVar_(), 
    CaseString(), CaseGlif(), CaseRegexp(), 
    CaseDotName(), CaseRTildArroy(), 
    
    CaseListGen(), CaseBytes(), CaseBytesExplicit(),
    CaseArgExtraList(), CaseArgExtraDict(),
    CaseDictLine(), CaseListComprehension(), CaseSlice(), CaseCollectElem(), 
    CaseTuple(), CaseList(),
    
    CaseFunCall(), CaseStructConstr(),
    CaseBrackets(), CaseMString()
]

# CaseService -> empty, debug, unclosed
# CaseKeywordLeft -> definition, control, import
# CaseOperators -> lambda, bin-common, inline-control, sequence, unarLeft
#
expCaseList:list[ExpCase] = [
    CaseEmpty(), CaseDebug(),
    # CaseUnclosedBrackets(),
    CaseInlineSub(),
    
    CaseImport(), 
    CaseFuncDef(), CaseMethodDef(), # ident func, then - method
    CaseIf(), CaseElse(), CaseWhile(), CaseFor(),  CaseMatch(), CaseReturnVal(),  
    CaseMatchCase(),
    CaseStructBlockDef(), CaseStructDef(), CaseEnum(),
    
    CaseLambda(),
    CaseSemic(), CaseBinOper(), CaseCommas(),
    CaseLUnar(StrFormatter()),
]

patternMatchCasesSolid = [
    MT_Other(),
    MTVal(), MTString(), MTRegexp(), MTList(), MTTuple(), MTDict(), MTStruct(), MTObjMember(),
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
                # print('$3>', subExp)
                pattr = mtCase.setSub(pattr, subExp)
            else:
                pattr = mtCase.expr(elems)
            return pattr
    return None


def makePMatchExpr(elems:list[Elem], parent:ExpCase=None)->MatchingPattern:
    # print('#makePMatchExpr:', [(n.text, Lt.name(n.type)) for n in elems])
    # print('\n#tree-makePMatchExpr/1::', ' '.join(["'%s'"%n.text for n in elems]))
    caseList = patternMatchCasesSolid
    ok, _ = isSolidExpr(elems, skipKeywords=True)
    if not ok:
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

def subBtContext(blockContext:Expression):
    match blockContext:
        case MatchExpr():
            return CaseMatchCase()
    return None


## py -m cProfile -s tottime -m unittest

def caseMatcher():
    strLim = CaseOption(CaseStr(), [CaseRegexp(), CaseGlif(), CaseString(), CaseMString()])
    wordLim = CaseOption(CaseWord(), [CaseElse(), CaseBreak(), CaseContinue(), CaseReturn(), CaseVar_(), CaseNumVal(), CaseDebug(), CaseVar(), ])
    solidLeft = CaseOptionPrepared(
        CaseSolidLeft(), 
        [CaseFunCall(), CaseStructConstr(), CaseArgExtraList(), CaseDotName(), 
        CaseRTildArroy(), CaseSlice(), CaseCollectElem(), CaseBytesExplicit()])
    
    sqBrkLim = CaseOption(CaseBrkSquare(), [CaseListGen(), CaseBytes(), CaseListComprehension(), CaseList()])
    brkLim = CaseOption(CaseGenBrackets(), [sqBrkLim, CaseTuple(), CaseDictLine(), CaseBrackets()])
    
    solidOther = CaseOption(CaseAny(), [])

    solidLim = CaseOption(CaseSolid(), [wordLim, strLim, solidLeft, brkLim, solidOther])

    # ===
    # def match\(self, elems:list\[Elem\]\)

    servLim = CaseOption(CaseServ(), [CaseEmpty(), CaseDebug(),])
    
    kewRList = [CaseIf(), CaseElse(), CaseWhile(), CaseFor(),  CaseMatch(), CaseReturn(), CaseImport(), CaseEnum(), 
        CaseFuncDef(), CaseMethodDef(), CaseStructDef(), CaseStructBlockDef(),]
    
    keywRs = CaseOption(CaseAny(), kewRList)
    
    keyrwLim = CaseOption(
        CaseRWord(), [CaseInlineSub(), keywRs])

    operLim = CaseOptionPrepared(CaseOperLim(), [CaseLambda(), CaseBinOper(), CaseCommas(), CaseSemic(), ])

    # should apply after solid
    nonSolLim = CaseOption(NonSolid(), [servLim, CaseUnclosedBrackets(), keyrwLim, operLim, CaseLUnar(StrFormatter()),])

    fullMatcher = CaseMatchcher([solidLim, nonSolLim])
    return fullMatcher

__genMatcher = caseMatcher()


def elems2expr(elems:list[Elem], blockContext:Expression=None)->Expression:
    # print('#elems2expr:', [(n.text, Lt.name(n.type)) for n in elems])
    # print('\n--/n# elems2expr/1::', ' '.join(["'%s'"%n.text for n in elems]), 'bContext:', blockContext)
    # print('\n--tree::', elemStr(elems), 'bContext:', blockContext)
    
    foundCase = None
    
    # check context-dependent
    if blockContext:
        foundCase = subBtContext(blockContext)
    
    # # check Solid:
    # expSolid = isSolidExpr(elems)
    # # print('\ntree.solid:', expSolid)
    # if not foundCase and expSolid:
    #     # print('elems2expr/isSolidExpr', expCaseSolids)
    #     for expCase in expCaseSolids:
    #         # print('elems2expr/Solid', expCase.__class__)
    #         if expCase.match(elems):
    #             foundCase = expCase
    #             break
    
    # # check non-Solid
    # if not foundCase:
    #     for expCase in getCases():
    #         # print('elems2expr/NoSolid', expCase.__class__)
    #         if expCase.match(elems):
    #             foundCase = expCase
    #             break
    
    
    if not foundCase:
        lineInfo = CMatchInfo(elems)
        foundCase = __genMatcher.find(lineInfo)
        # ee = 55
        # if isinstance(foundCase, CaseOption):
        #     ee = (foundCase.matcher, foundCase.subs)
        # print('tr-fc', foundCase, ee)
    
    if foundCase:
        # print('.. tree/found:', repr(foundCase), '', elemStr(elems))
        expr = makeExpr(foundCase, elems)
        if isinstance(expr, CtrlSubExpr):
            expr = expr.toControl()
        # print('#post-sub:', expr, '', elemStr(elems))
        return expr
    # print('tree:DEBUG: No current ExprCase for `%s` ' % ''.join([n.text for n in elems]))
    raise InterpretErr('No current ExprCase for `%s` ' % '_'.join([n.text for n in elems]))


def line2expr(cline:CLine, blockContext:Expression=None)-> Expression:
    ''' '''
    # types: assign, just value, definition, definition content (for struct), operator, func call, control (for, if, func, match, case), 
    try:
        # print('>> line2expr 1:', ''.join([n.text for n in cline.code]))
        expr = elems2expr(cline.code, blockContext)
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



def lex2tree(src:list[CLine]) -> Block:
    ''' '''
    root = Module()
    if len(src) == 0:
        return root
    curBlock = root
    lineNum = 0
    parents:list[Block] = []
    # print('~~~~~~~~~~~` start tree builder ~~~~~~~~~~~~')
    i_src = -1

    unclosed = None
    unclosedCase = CaseUnclosedBrackets()
    prev = root # expr of prev line
    expr = root
    indent = src[0].indent
    lastInd = len(src) - 1
    caseComment = CaseComment()
    for cline in src:
        i_src += 1
        # print('  -  -  - ')
        lineNum += 1
        cline.line = lineNum
        
        # print('\n(((((( == >>>>>---------- #cline-code1:', f"<{' '.join([ee.text for ee in cline.code])}>", ' ))))) curBlock:>>', repr(curBlock))
        # print('#code-src: `%s`' % cline.src.src, '$ind=',  indent, '; curInd=', curInd)
        # print('#  --- ', [(ee.text, Lt.name(ee.type)) for ee in cline.code])
        if len(cline.code) == 0:
            continue
        
        if unclosed is not None:
            unclosed.add(cline.code, cline.src)
            # updated cline for unclosed
            cline = CLine(unclosed.src, unclosed.elems, unclosed.indent)
        else:
            if caseComment.match(cline.code):
                # nothing for comment now
                continue
        
        if unclosedCase.match(cline.code):
            # Start processing unclosed expressions
            expr = unclosedCase.expr(cline.code)
            expr.init(cline)
            if unclosed is None:
                unclosed = expr
            # print('->>', lastInd, i_src)
            if lastInd == i_src:
                raise InterpretErr('Unclosed expression in last line. Uncosed till <<%s>>' % expSrc(cline.src))
            continue
        else:
            if unclosed is not None:
                unclosed = None
        
        prevIndent = indent
        # print(i_src, '$ind=',  indent, '; prevIndent=', prevIndent)
        if unclosed is None:
            indent = cline.indent
        else:
            indent = unclosed.indent
        
        # print('lex2tree-2 expr:', repr(expr), 'prev:', repr(prev), 
            #   '; \n ^^ parents:', [repr(n) for n in parents], repr(curBlock), ('in=',  indent, '; pin=', prevIndent))
        goBack = False # if we move back from nected block
        goBack = indent < prevIndent
        goDeep = indent > prevIndent
        prevPar = []
        if goBack:
            stepsUp = prevIndent - indent
            for i in range(stepsUp):
                # print('------', i, repr(parents[-1]), repr(curBlock))
                prevPar.append(curBlock)
                curBlock = parents.pop()
        
        # resolve block by indent
        prev = expr
        if goDeep and prev.add:
            # start new block
            # print('! goDeep', repr(curBlock), repr(prev), repr(expr),'is ELSE?:', isinstance(prev, (ElseExpr)))
            if not isinstance(prev, (ElseExpr)):
                parents.append(curBlock)
                curBlock = prev
                
        # prep blockContext
        blockContext = None
        if not unclosed:
            if isinstance(curBlock, MatchExpr):
                blockContext = curBlock
        
        # get expression
        expr = line2expr(cline, blockContext) # >>>>>>>>>>>>>>>>>>> Expression 
        
        # if isinstance(expr, CaseComment):
        #     # nothing for comment now
        #     continue

        # if isinstance(expr, CtrlSubExpr):
        #     expr = expr.toControl()
        
        if isinstance(expr, ElseExpr): # else | else if ..
            if not prevPar or not isinstance(prevPar[-1], (IfExpr,ElsFold)):
                raise EvalErr('Incorrect `else` block after non-`if`')
            parents.append(curBlock)
            curBlock = prevPar[-1]
            curBlock.toElse(expr)
            if isinstance(curBlock, IfExpr):
                # ELSE statement
                curBlock = ElsFold(curBlock)
            if expr.hasIf(): # else if ..
                curBlock.setNext(expr)
            continue

        if isinstance(expr, RawCase):
            expr = raw2done(curBlock, expr)
        
        # if 1-line block
        if isinstance(expr, SequenceExpr):
            if expr.delim == ';':
                for subExp in expr.getSubs():
                    curBlock.add(subExp)
            continue
        
        curBlock.add(expr)

    return root
