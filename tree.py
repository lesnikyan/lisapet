
"""
"""

import re

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex

from cases.tcases import *
from cases.control import *
from cases.oper import *
from cases.collection import *

from nodes import *
from nodes.tnodes import *
from nodes.oper_nodes import *
from nodes.control import *
from cases.structs import *
from cases.funcs import *


class CaseDebug(ExpCase):
    def match(self, elems:list[Elem])-> bool:
        prels('--DEbug', elems)
        return len(elems) > 0 and elems[0].text == '@debug'
    
    def expr(self, elems:list[Elem])-> Expression:
        ''' return base expression, Sub(elems) '''
        return DebugExpr(' '.join([e.text for e in elems]))

expCaseList = [ 
    CaseEmpty(), CaseComment(), CaseDebug(),
    CaseFuncDef(), CaseReturn(), CaseMathodDef(),
    CaseIf(), CaseElse(), CaseWhile(), CaseFor(),  CaseMatch(), CaseArrowR(), # CaseIterOper(),
    CaseStructBlockDef(), CaseStructDef(),
    CaseAssign(), CaseBinAssign(), CaseSemic(), CaseBinOper(), 
    CaseTuple(),
    CaseDictBlock(), CaseListBlock(), CaseListGen(),
    # CaseStructBlockConstr(),
    CaseDictLine(), CaseListComprehension(), CaseSlice(), CaseList(), CaseCollectElem(), CaseFunCall(), CaseStructConstr(),
    # CaseDotOper(),
    CaseVar_(), CaseVal(), CaseVar(), CaseBrackets(), CaseUnar()]

def getCases()->list[ExpCase]:
    return expCaseList

def simpleExpr(expCase:ExpCase, elems)->Expression:
    # print('#simple-case:', expCase)
    return expCase.expr(elems)

def complexExpr(expCase:SubCase, elems:list[Elem])->Expression:
    base, subs = expCase.split(elems)
    print('#complex-case:', expCase)
    print('#complexExpr', base, [elemStr(s) for s in subs])
    # if isinstance(subs, list):
    #     for ee in subs:
            # prels('#cml-exp1:', ee)
    if not expCase.sub():
        return base
    if not subs or not subs[0]:
        return base
    subExp:list[Expression] = []
    for sub in subs:
        # prels('#complexExpr1:', sub)
        texpr = elems2expr(sub)
        subExp.append(texpr)
    expCase.setSub(base, subExp)
    return base

def makeExpr(expCase:ExpCase, elems:list[Elem])->Expression:
    # print('#b2', [n.text for n in elems])
    if expCase.sub():
        return complexExpr(expCase, elems)
    return simpleExpr(expCase, elems)

def elems2expr(elems:list[Elem])->Expression:
    print('#elems2expr:', [(n.text, Lt.name(n.type)) for n in elems])
    for expCase in getCases():
        if expCase.match(elems):
            # if expCase.sub():
            #     return complexExpr(expCase, elems)
            print('Case found::', expCase.__class__.__name__, '', elemStr(elems))
            expr = makeExpr(expCase, elems)
            # print('#b5', expr)
            return expr
    raise InterpretErr('No current ExprCase for `%s` ' % '_'.join([n.text for n in elems]))


def line2expr(cline:CLine)-> Expression:
    ''' '''
    # types: assign, just value, definition, definition content (for struct), operator, func call, control (for, if, func, match, case), 
    expr = elems2expr(cline.code)
    return expr

def raw2done(parent:Expression, raw:RawCase)->Expression:
    ''' post-process for sub-level sub-expressions:
        match-case | expr -> expr
        struct-field | expr : expr
        dict-(key:val) | expr : expr
        etc.
    '''
    # match-case
    print('>> raw2done', parent, raw)
    if isinstance(parent, MatchExpr) and isinstance(raw, ArrOper):
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
    parents:list[Block] = []
    curInd = 0 # indent
    print('~~~~~~~~~~~` start tree builder ~~~~~~~~~~~~')
    for cline in src:
        print('  -  -  -')
        indent = cline.indent
        print('#code-src: `%s`' % cline.src.src, '$ind=',  indent, '; curInd=', curInd)
        prels('#cline-code:', cline.code)
        if len(cline.code) == 0:
            continue
        expr = line2expr(cline)
        
        
        # print('lex2tree-14:', expr, expr.__class__.__name__, type(expr))
        if isinstance(expr, CaseComment):
            # nothing for comment now
            continue
        print('lex2tree-2 expr:', expr, '; parents:', parents, curBlock)
        # print(dir(expr))
        if indent < curInd:
            # end of block
            stepsUp = curInd - indent
            print('-- ind:', curInd, indent)
            if isinstance(expr, ElseExpr):
                # the same indent/parent level as `if` opener
                stepsUp -= 1
            print('lex2tree-3#stepsUp=', stepsUp, parents)
            for _ in range(stepsUp):
                curBlock = parents.pop()
                curInd -= 1
                print('lex2tree-pop parents =', parents)
                print('lex2tree-pop curBlock =', curBlock)
                
        if isinstance(expr, RawCase):
            expr = raw2done(curBlock, expr)
            print('>> after raw:', expr)
            
        if isinstance(curBlock, IfExpr) and isinstance(expr, ElseExpr):
            # ELSE statement
            curBlock.toElse(expr)
            # TODO: for `else if` case we need additional logic with parent and nested `if` expr
            continue
        print('lex2tree-4:', expr, expr.__class__.__name__, type(expr), 'isBlock:' , expr.isBlock())
        stepBlock = expr.isBlock()
        # if stepBlock:
        #     if isinstance(expr, CaseExpr):
        #         # can be 1-line
        #         # if 1-line, it just will be reset by next case line 
        #         if not expr.block.isEmpty():
        #             stepBlock = False
        
        if stepBlock:
            
            # start new sub-level
            # if definition of func, type: add to upper level context
            # if isinstance(expr, ElseExpr):
            #     # specific `else` case.
                
            #     # `else if` case need additional logic
            #     continue
            # print('!! in-block', parents, curBlock, expr)
            curBlock.add(expr)
            parents.append(curBlock)
            curBlock = expr
            curInd += 1
            print('-=-= indent cur:', curInd)
            continue
        curBlock.add(expr)
        # curBlock.ctx.add(ctx)
        # context?
    return root
