
'''
Parse source code
'''
import re

from lang import *


c_space = [' ', '\t', '\n', '\r' ]
c_esc = '\'\"ntr\\/`'
c_nums = [n for n in '1234567890']
c_oper = '+~-*/=%^&!?<>()[]:.;|{}\\'
c_comm = '#'
rxChar = re.compile(r'[a-zA-Z_\$@]')
c_quot = "\'\""

ext_in = {
    Lt.num: ['j', 'x', 'b', 'o',  '.', 'a', 'b', 'c', 'd', 'e', 'f']
}

pref = {
    Lt.num: []
}

def charType(prev:int, s:str) -> int:
    base = Lt.none
    if s in c_space:
        base = Lt.space
    if s in c_oper:
        base = Lt.oper
        # print('#2: ', prev, s)
        if prev == Lt.text and s == '\\':
            base = Lt.esc
    elif s in c_nums:
        base = Lt.num
    elif s in c_comm:
        base = Lt.comm
    elif rxChar.match(s):
        base = Lt.word
    elif s in c_quot:
        base = Lt.quot
        
    # type correction
    if prev == Lt.comm:
        return Lt.comm
    if prev == Lt.esc:
        if s in c_esc:
            return Lt.text
        raise ParseErr('Invalid esc symbol `%s`' % s)
    if base == Lt.quot:
        return Lt.quot # TODO: think about different quotes ' " `
    if prev == Lt.text:
        # print('#1 ', base)
        if base == Lt.esc:
            return Lt.esc
        return Lt.text # TODO: add check for types of strig opener ' , "
    if prev == Lt.num and s in ext_in[Lt.num]:
        return prev
    if prev == Lt.word and base == Lt.num:
        return prev
    
    return base

def quoting(s, curType, sType, curLex, openQuote):
    '''' '''
    finStr = False
    rType = sType
    res = []
    if openQuote == '':
        # start string
        curType = Lt.text
        res.append(curLex)
        curLex = []
    else:
        if openQuote == s:
            # close string
            st = ''.join(curLex)
            res.append(lex(st,Mk.lex))
            curLex = [s]
            rType = Lt.quot
        else:
            rType = Lt.text
    return finStr, curLex, rType

opers = [n for n in ('; .. ** ++ -- += -= *= /=  && || == != <= >= << >> => -> <- :='
' < > = + - * / | { } [ ] . , : ~ ! % ^ & * ( )').split(' ') if n]

# if i > 0 and el.text in ['-', '+', '!', '~'] and elems[i-1].type == Lt.oper and elems[i-1].text != ')'
unarOpers = '- + ! ~'

def splitOper(oper:str)->list[str]:
    res = []
    # print(opers)
    while len(oper) > 0:
        # print('#1 oper: ', oper)
        for n in opers:
            # print('`', oper, n)
            if oper.startswith(n):
                # first correct oper has been found
                res.append(n)
                oper = oper[len(n):]
                # print('#a7:', len(oper), res)
                break
    if oper:
        raise ParseErr('Incorrect operator : `%s`'% oper)
    return res

def normilizeLexems(src:list[lex])->list[lex]:
    ''' '''
    prep:list[lex] = []
    for x in src:
        # Num fix
        if x.ltype == Lt.num and x.val.find('..') > -1:
            xparts = x.val.split('..')
            print('~', xparts)
            prep.append(lex(xparts[0], Mk.lex, type=Lt.num))
            prep.append(lex('..', Mk.lex, type=Lt.oper))
            x = lex(xparts[1], Mk.lex, type=Lt.num)
        elif x.ltype == Lt.oper:
            # Fix operators
            ops = splitOper(x.val)
            # print('#a71:', ops)
            prep.extend([lex(op, Mk.lex, type=Lt.oper) for op in ops])
            continue
        prep.append(x)
    return [s for s in prep if len(s.val) > 0]


def splitLine(src: str) -> TLine:
    cur = []
    res = []
    curType = 0
    openQuote = None
    # esc = False
    
    def nextRes(cur, curType, nval):
        wd = ''.join(cur)
        # print('#3 >> p-cur, `%s`' % wd, ' st = ', curType)

        res.append(lex(wd, Mk.lex, type=curType))
        cur = [nval]
        return [nval]

    for s in src:
        # print('#6 ', cur, "'%s'"%s, curType, '|')
        sType = charType(curType, s)
        # print('#stype:', sType)
    
        if curType == Lt.esc:
            # in the string and after esc slash
            # print('## in esc')
            curType = Lt.text
            cur.append(s)
            continue
        if curType == Lt.text:
            # escape sequences
            if sType == Lt.esc:
                # print('## esc')# esc = True
                curType = Lt.esc
                continue
            # else:
            if openQuote == s:
                cur = nextRes(cur, curType, s)
                curType = Lt.quot
                cur = nextRes(cur, curType, '')
                curType = Lt.none
                openQuote = None
                continue
            # TODO: esc \n \t
            cur.append(s)
            continue 
        
        # ordinar case
        if sType == curType:
            cur.append(s)
            continue

        if sType == Lt.quot:
            if openQuote is None:
                # start string
                # print('#- open string')
                st = ''.join(cur)
                res.append(lex(st,Mk.lex, type=curType))
                # cur = []
                cur = nextRes(cur, curType, '')
                curType = Lt.text
                openQuote = s
                continue

        # finalize word
        cur = nextRes(cur, curType, s)
        curType = sType
    if cur:
        nextRes(cur, curType, None)
    
    if curType == Lt.text:
        raise ParseErr('Unclosed string in the and of line `%s`'% s)
    # print('#a3:', src)
    lexems = normilizeLexems(res)
    return TLine(src, lexems)

def splitLexems(text: str) -> list[TLine]:
    lines = text.splitlines()
    res:list[TLine] = []
    for s in lines:
        if not s.strip():
            continue # miss empty and spaces line
        # res.append(lex(0, Mk.line))
        nextLine = splitLine(s)
        # res.extend(nextLine)
        res.append(nextLine)
    # res.append(lex(0, Mk.line))
    return res


def buildLexems(lexems:list[lex]) -> list[Elem]:
    ''' From raw lexems to lang Elems
    numbers: check format, split by: .. 
    operators: longer set of chars over shorter: 1..5 -> [1(int), .., 5] 1.,0 -> [1.(float), 0]
    
    '''
    res = []
    prep:list[lex] = []
    for x in lexems:
        # TODO: prevent splitted spaces in indent
        # Num fix
        # print('#-1: ', x.val)
        if x.ltype == Lt.num and x.val.find('..') > -1:
            xparts = x.val.split('..')
            print('~', xparts)
            prep.append(lex(xparts[0], Mk.lex, type=Lt.num))
            prep.append(lex('..', Mk.lex, type=Lt.oper))
            x = lex(xparts[1], Mk.lex, type=Lt.num)
        prep.append(x)
            
    locInd = 0 # local indent
    glInd = 0 #global indent
    lastLex:lex = None
    curLex:lex = lex()  
    prLex = lex()
    for x in prep:
        # lex to Chunk
        prLex = curLex
        curLex = x
        lastLex = prLex
        if x.mark == Mk.line:
            res.append(Elem(Lt.endline, x.val))
            lastLex = x
        if lastLex.mark == Mk.line:
            print('-2:', x.val,':', Lt.name(x.ltype))
        if lastLex.mark == Mk.line:
            # here we get indent, convert indent to startBlock or endBlock
            locInd = 0
            if x.ltype == Lt.space:
                locInd = len(x.val)
            if locInd > glInd:
                # new block
                res.append(Elem(Lt.block, x.val))
            elif locInd < glInd:
                res.append(Elem(Lt.close, x.val))
            #TODO: catch and remove blank lines
            glInd = locInd
            lastLex = x
            continue
        
        if x.ltype == Lt.space:
            res.append(Elem(Lt.space, x.val))
        else:
            res.append(Elem(x.ltype, x.val))
    return res



def lex2Elem(xx:lex)->Elem:
    if xx.ltype in [Lt.word, Lt.num, Lt.text]:
        return Elem(xx.ltype, xx.val)
    if xx.ltype == Lt.oper:
        return Elem(Lt.oper, xx.val)
    # TODO: other ypes


def elemLine(src:TLine)->CLine:
    ''' '''
    prep:list[lex] = []
    ind = 0
    if len(src.lexems) == 0:
        return CLine() # or None
    # print('@@lexms:', ','.join([lx.val for lx in src.lexems]))
    # print('#@', '`%s`' % src.lexems[0].val, Lt.name(src.lexems[0].ltype))
    if src.lexems[0].ltype == Lt.space:
        # print('@@@@@@@@')
        if len(src.lexems) == 1:
            # line filled by spaces, the same as empty
            return CLine() # or None
        # TODO: walk over spaces (additional check for  several spaces in beginning of line)
        # we have an indent here
        indLen = len(src.lexems[0].val)
        if CLine.BaseIndent == 0:
            # set a base indent for whole code
            CLine.BaseIndent = indLen
        if indLen % CLine.BaseIndent > 0:
            raise ParseErr('Incorrect indent size %d with base indent = %d'% (indLen, CLine.BaseIndent))
        ind = indLen / CLine.BaseIndent
        
    # for x in src.lexems:
    #     # Num fix
    #     if x.ltype == Lt.num and x.val.find('..') > -1:
    #         xparts = x.val.split('..')
    #         print('~', xparts)
    #         prep.append(lex(xparts[0], Mk.lex, type=Lt.num))
    #         prep.append(lex('..', Mk.lex, type=Lt.oper))
    #         x = lex(xparts[1], Mk.lex, type=Lt.num)
    #     elif x.ltype == Lt.oper:
    #         # Fix operators
    #         ops = splitOper(x.val)
    #         prep.extend(ops)
    #         continue
    #     prep.append(x)
    # src.src = prep
    res:list[Elem] = []
    for lx in src.lexems:
        el = lex2Elem(lx)
        if not el:
            continue
        res.append(el)
    return CLine(src, res, ind)

def elemStream(lines:list[TLine])->list[CLine]:
    ''' '''
    res:list[CLine] = []
    for tl in lines:
        cl = elemLine(tl)
        res.append(cl)
    return res


