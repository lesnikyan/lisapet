
'''
Parse source code
'''
import re

from lang import *


c_space = [' ', '\t', '\n', '\r' ]
c_esc = '\'\"ntr\\/`'
c_nums = [n for n in '1234567890']
c_oper = '+~-*/=%^&!?<>()[]:.;,|{}\\'
# single-line comment, to and of line
c_comm = '#'
# blok-comment, multiline or inline
c_opcomm = '#@'
c_ndcomm = '@#'
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
    if prev == Lt.mtcomm:
        return Lt.mtcomm
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

opers = [n for n in ('; , .. ** ++ -- += -= *= /= %=  && || == != <= >= << >> => -> <- :='
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


def splitLine(src: str, prevType:int=Lt.none) -> tuple[TLine, int]:
    '''
    prevType - for multiline cases:
    multiline string
    multiline comment
    '''
    cur = []
    res = []
    curType = prevType
    openQuote = None
    # esc = False
    print(' --- splitLine:', 'prevType=', Lt.name(prevType), '::', src)
    
    def nextRes(cur, curType, nval):
        wd = ''.join(cur)
        print('#3 >> p-cur, `%s`' % wd, ' curt = ', Lt.name(curType))
        res.append(lex(wd, Mk.lex, type=curType))
        cur = [nval]
        return [nval]
    i = -1
    slen = len(src)
    for s in src:
        i += 1
        # print('#6 ', cur, " s='%s'"%s, curType, '|')
        sType = charType(curType, s)
        # print('#stype:', sType)
        
        # close multi-comment
        if curType == Lt.mtcomm:
            cur.append(s)
            # print('>>mtc:: ', cur, ' >> ', cur[-2:])
            if ''.join(cur[-2:]) == '@#':
                cur = nextRes(cur, curType, '')
                curType = Lt.none
            continue
    
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
        
        if curType == Lt.comm and i < slen:
            if len(cur) == 1 and cur[0] + s == '#@':
                # start of multiline coment found
                cur.append(s)
                curType = Lt.mtcomm
                continue

        # ordinar case
        if sType == curType:
            cur.append(s)
            continue

        if sType == Lt.quot:
            if openQuote is None:
                # start string
                st = ''.join(cur)
                # print('#- open string', st, '; cur: ', cur, '; s=', s)
                # res.append(lex(st, Mk.lex, type=curType))
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
    return TLine(src, lexems), curType

def splitLexems(text: str) -> list[TLine]:
    lines = text.splitlines()
    res:list[TLine] = []
    lastType = Lt.none
    # TODO: 
    for s in lines:
        if not s.strip():
            continue # miss empty and spaces line
        # res.append(lex(0, Mk.line))
        # interpretator magic:
        
        if s.startswith('@intr@exit'):
            print('Interpretation exit in splitLexems()')
            exit(1);
        nextLine, endType = splitLine(s, lastType)
        print([(x.val, Lt.name(x.ltype), x.mark) for x in nextLine.lexems])
        # res.extend(nextLine)
        print('--- split res --->', [(x.val, x.ltype) for x in nextLine.lexems])
        res.append(nextLine)
        lastType = Lt.none
        if len(nextLine.lexems) == 0:
            continue
        # lastElemType = nextLine.lexems[-1].ltype
        if endType in [Lt.mtcomm, Lt.mttext]:
            lastType = endType
    # res.append(lex(0, Mk.line))
    return res


def lex2Elem(xx:lex)->Elem:
    if xx.ltype in [Lt.word, Lt.num, Lt.text]:
        return Elem(xx.ltype, xx.val)
    if xx.ltype == Lt.oper:
        return Elem(Lt.oper, xx.val)
    # TODO: other type
    # TODO: metadata from comments


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
        print('indent: cur/ base:', indLen , CLine.BaseIndent, ' = ', indLen / CLine.BaseIndent)
        ind = int(indLen / CLine.BaseIndent)

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


