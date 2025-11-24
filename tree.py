
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
from strformat import  *


class CaseDebug(ExpCase):
    def match(self, elems:list[Elem])-> bool:
        prels('--DEbug', elems)
        return len(elems) > 0 and elems[0].text == '@debug'
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' return base expression, Sub(elems) '''
        return DebugExpr(' '.join([e.text for e in elems]))


class UnclosedExpr:
    ''' '''
    def __init__(self, elems, indent=0):
        # super().__init__('')
        self.elems:list = elems
        self.indent = indent

    def add(self, part):
        prels('Uncl.add: ', part)
        self.elems.extend(part)


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
        dprint('SFm 1:', clines)
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


expCaseList = [ 
    CaseEmpty(), CaseComment(), CaseDebug(),
    CaseUnclosedBrackets(),
    CaseImport(),
    CaseInlineSub(),
    CaseFuncDef(), CaseReturn(), CaseMathodDef(),
    CaseBreak(), CaseContinue(), CaseRegexp(),
    CaseIf(), CaseElse(), CaseWhile(), CaseFor(),  CaseMatch(), 
    CaseLambda(), CaseMatchCase(),
    CaseStructBlockDef(), CaseStructDef(),
    CaseSemic(), CaseBinOper(), CaseCommas(),
    CaseTuple(),
    CaseDictBlock(), CaseListBlock(), CaseListGen(),
    CaseDictLine(), CaseListComprehension(), CaseSlice(), CaseList(), CaseCollectElem(), 
    CaseFunCall(), CaseStructConstr(), CaseLambda(),
    CaseVar_(), CaseVal(), CaseString(), CaseMString(), CaseVar(), CaseBrackets(), CaseUnar(StrFormatter())]

patternMatchCases = [
    MT_Other(), MTPtGuard(), MTMultiCase(), MTTypedVal(), MTDuaColon(),
    MTVal(), MTString(), MTRegexp(), MTList(), MTTuple(), MTDict(), MTStruct(), 
]


def getCases()->list[ExpCase]:
    return expCaseList


def simpleExpr(expCase:ExpCase, elems)->Expression:
    dprint('#simple-case:', expCase)
    return expCase.expr(elems)


def makePMatchExpr(elems:list[Elem], parent:ExpCase=None)->MatchingPattern:
    # print('#makePMatchExpr:', [(n.text, Lt.name(n.type)) for n in elems])
    # print('\n#tree-makePMatchExpr/1::', ' '.join(["'%s'"%n.text for n in elems]))
    cases: list[ExpCase] = patternMatchCases
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
    # print('DEBUG: No current MTCase for `%s` ' % '~'.join([n.text for n in elems]))
    raise InterpretErr('No current MTCase for `%s` ' % ''.join([n.text for n in elems]))


def complexExpr(expCase:SubCase, elems:list[Elem])->Expression:
    base, subs = expCase.split(elems)
    # print('#complex-case:', expCase.__class__.__name__, ' base:', base, subs)
    # print('#complexExpr', expCase.__class__.__name__, base, [elemStr(s) for s in subs])
    # if isinstance(subs, list):
    #     for ee in subs:
            # prels('#cml-exp1:', ee)
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
    # print('#elems2expr/1::', ' '.join(["'%s'"%n.text for n in elems]))
    for expCase in getCases():
        # print('#elems2expr/2:', type(expCase).__name__, (elems))
        # print('#elems2expr/2:', type(expCase).__name__)
        if expCase.match(elems):
            # if expCase.sub():
            #     return complexExpr(expCase, elems)
            # print('Case found::', expCase.__class__.__name__, '', elemStr(elems), '\n')
            # print('Case found::', expCase.__class__.__name__)
            expr = makeExpr(expCase, elems)
            if isinstance(expr, CtrlSubExpr):
                # print('#elems2expr/3 ', expr)
                expr = expr.toControl()
            # print('#EL2EX . expr:', expr)
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
    dprint('>> raw2done', parent, raw)
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
    curBlock = root
    lineNum = 0
    parents:list[Block] = []
    curInd = 0 # indent
    elifDeps = []
    parByInd:dict[int, int] = {} # indent : index in parents 
    dprint('~~~~~~~~~~~` start tree builder ~~~~~~~~~~~~')
    i = -1

    unclosed = None
    for cline in src:
        i += 1
        dprint('  -  -  - ')
        lineNum += 1
        cline.line = lineNum
        if unclosed is None:
            indent = cline.indent
        else:
            indent = unclosed.indent
        # print('#code-src: `%s`' % cline.src.src, '$ind=',  indent, '; curInd=', curInd)
        # prels('#cline-code1:', cline.code)
        # dprint('#cline-code2:', [(ee.text, Lt.name(ee.type)) for ee in cline.code])
        if len(cline.code) == 0:
            continue
        
        if unclosed is not None:
            # unclosed = None
            unclosed.add(cline.code)
            cline.code = unclosed.elems
            prels('unclosed: ', unclosed.elems)
        
        # get expression
        expr = line2expr(cline)
        
        if isinstance(expr, UnclosedExpr):
            if unclosed is None:
                unclosed = expr
                unclosed.indent = indent
            continue
        else:
            if unclosed is not None:
                unclosed = None

        # dprint('lex2tree-14:', expr, expr.__class__.__name__, type(expr))
        if isinstance(expr, CaseComment):
            # nothing for comment now
            continue
        
        if isinstance(expr, CtrlSubExpr):
            # print('#tree 011', expr)
            expr = expr.toControl()
        # print('#tree 012', expr)
            
        
        # print('lex2tree-2 expr:', expr, '; parents:', [type(n) for n in parents], curBlock)
        # dprint(dir(expr))
        # elDep = 0 # diff nest depth - indent. for `if else` case depth > indent
        goBack = False # if we move back from nected block
        goBack = indent < curInd #  and (isinstance(expr, ElseExpr) and not expr.hasIf())
        # TODO except else if, but if not last else in `if` tree
        if goBack:
            # end of block
            stepsUp = curInd - indent
            dprint('-- ind:', curInd, indent)
            if isinstance(expr, ElseExpr):

                # the same indent/parent level as `if` opener
                # parInd = parByInd[curInd]
                # backPart = len(parents) - parInd
                # elDep = backPart #  elifDeps.pop() #[len(elifDeps) - 1]
                
                stepsUp -= 1
                
            dprint('lex2tree-3#stepsUp=', stepsUp, parents)
            # dprint('lex2tree-33=', parByInd)
            for _ in range(stepsUp):
                curBlock = parents.pop()
                # curInd -= 1
                dprint('lex2tree-pop parents =', parents)
                dprint('lex2tree-pop curBlock =', curBlock)
            curInd -= stepsUp
        if isinstance(expr, RawCase):
            expr = raw2done(curBlock, expr)
            dprint('>> after raw:', expr)
            
        if isinstance(expr, ElseExpr):
            # dprint('in Else:', curBlock, expr)
            curBlock.toElse(expr)
            if isinstance(curBlock, IfExpr):
                # ELSE statement
                # ifEx: IfExpr = curBlock
                curBlock = ElsFold(curBlock)
                # TODO: for `else if` case we need additional logic with parent and nested `if` expr
                dprint('Else-1')
        
            if expr.hasIf():
                dprint('  Else-2')
                curBlock.setNext(expr)
                # parents.append(ifEx)
                # elEx:ElseExpr = expr
                # curBlock = elEx.subIf
                # elifDeps[len(elifDeps) - 1] += 1
            continue
        dprint('>> lex2tree-4:', expr, expr.__class__.__name__, type(expr), 'isBlock:' , expr.isBlock())
        stepBlock = expr.isBlock()

        
            
        if isinstance(expr, IfExpr):
            # first else in if
            dprint('*add new to elifDeps: ', elifDeps)
            elifDeps.append(0)
            parByInd[curInd] = len(parents)

        if stepBlock:
            # start new sub-level
            # if definition of func, type: add to upper level context

            dprint('!! in-block', parents, curBlock, expr)
            curBlock.add(expr)
            parents.append(curBlock)
            curBlock = expr
            curInd += 1
            dprint('-=-= indent cur:', curInd)
            continue
        # if 1-line block
        if isinstance(expr, SequenceExpr):
            if expr.delim == ';':
                for subExp in expr.getSubs():
                    curBlock.add(subExp)
            continue
        
        curBlock.add(expr)

    return root
