
'''
Parse source code
'''
import re

from lang import *


c_space = [' ', '\t', '\n', '\r' ]
c_esc = '\'\"ntr\\/`'
c_esc_map = {'n':'\n', 't':'\t', 'r':'\r', '\\':'\\', '/':'/', '\'':'\'', '\"':'\"', '`':'`'}
c_nums = [n for n in '1234567890']
c_oper = '+~-*/=%^&!?<>()[]:.;,|{}\\'
# single-line comment, to and of line
c_comm = '#'
# blok-comment, multiline or inline
c_opcomm = '#@'
c_ndcomm = '@#'
c_mlines = '\'\'\' """ ```'.split(' ')
rxChar = re.compile(r'[a-zA-Z_\$@]')
c_quot = "\'\"`"
c_regex = '| / % '

ext_in = {
    Lt.num: ['j', 'x', 'b', 'o', 'a', 'b', 'c', 'd', 'e', 'f']
}

pref = {
    Lt.num: []
}

def charType(prevs:int, s:str) -> int:
    prevChars, prev = prevs
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
    if prev == Lt.text or prev == Lt.mttext:
        # print('#1 ', s, ' prev / base', Lt.name(prev),  Lt.name(base))
        if base == Lt.esc:
            return Lt.esc
        return prev # TODO: add check for types of strig opener ' , "
    # print(' >> ', Lt.name(prev), Lt.name(base))
    if prev == Lt.num and s in ext_in[Lt.num]:
        if s == '.' and s in prevChars:
            # here we found second dot `.` in number
            # print('Num correction 2')
            if prevChars[-1] != '.':
                # wrong syntax
                raise ParseErr('incorrect sequence of input: %s ' % ''.join(prevChars + [s]))
            # returned tuple is a sygnal that we have change of expected type
            return (prevChars[:-1], ['.','.'], Lt.oper)
            
        return prev
    if prev == Lt.word and base == Lt.num:
        return prev
    
    return base


opers = [n for n in ('; , ... .. ** ++ -- += -= *= /= %=  && || == != <= >= << >> => ?> -> <- := ?:'
# ' """ \'\'\' ``` '
' < > = + - * / | \\ { } [ ] . , : ? ~ ! % ^ & * ( )').split(' ') if n]

# if i > 0 and el.text in ['-', '+', '!', '~'] and elems[i-1].type == Lt.oper and elems[i-1].text != ')'
unarOpers = '- + ! ~'

def splitOper(oper:str)->list[str]:
    res = []
    # print(opers)
    def findOper(oper):
        for n in opers:
            # print('>> ', oper, n)
            if oper.startswith(n):
                # first correct oper has been found
                res.append(n)
                oper = oper[len(n):]
                # print('#a7:', len(oper), res)
                return oper
        raise ParseErr('Incorrect operator (not found) : `%s`'% oper)
    
    while len(oper) > 0:
        # print('#1 oper: ', oper)
        oper = findOper(oper)
    if oper:
        raise ParseErr('Incorrect operator (left in the end) : `%s`'% oper)
    return res

_numOnlyRx = re.compile(r'^[0-9]+$')
_numDotRx = re.compile(r'^[0-9]+\.$')

def normilizeLexems(src:list[lex])->list[lex]:
    ''' '''
    prep:list[lex] = []
    # print('normLexLine 1::', [n.val for n in src])
    i = -1
    # split opers
    for x in src:
        i += 1
        if not x.val:
            continue

        if x.ltype == Lt.oper:
            # fix dec num
            # Fix operators
            ops = splitOper(x.val)
            # print('#a71:', ops)
            prep.extend([lex(op, Mk.lex, type=Lt.oper) for op in ops])
            continue
        prep.append(x)
    src = prep
    prep = []
    
    # post-opers part
    # print('normLexLine 2::', [n.val for n in src])
    i = -1
    for x in src:
        i += i
        # print('# x', x.val, ':>', Lt.name(x.ltype))
        
        if prep and x.ltype == Lt.oper and x.val == '.':
            prev = prep[-1]
            # print('#// prev1', prev.val)
            if prev.ltype == Lt.num and _numOnlyRx.match(prev.val):
                # looks like it`s dot of decimal / float
                prep[-1].val += '.'
                continue

        if prep and x.ltype == Lt.num and _numOnlyRx.match(x.val):
            prev = prep[-1]
            # print('#// prev2', prev.val)
            if prev.ltype == Lt.num and _numDotRx.match(prev.val):
                # 2-nd part of decimal / float
                prep[-1].val += x.val
                continue
        prep.append(x)
    return [s for s in prep if len(s.val) > 0]


def splitLine(src: str, prevType:int=Lt.none, **kw) -> tuple[TLine, int]:
    '''
    prevType - for multiline cases:
    multiline string
    multiline comment
    '''
    cur = []
    res = []
    curType = prevType
    openQuote = None
    openMultStr = None # ''' """ ``` 
    if 'open_m_str' in kw:
        openMultStr = kw['open_m_str']
        
    escMod = False # if escape case
    # qMod = '' # if in qutes (string)
    # rxMod = '' # if native regexp
    # inRaw = False # for feature `raw string`
    print(' --- splitLine:', 'prevType=', Lt.name(prevType), '::', src)
    # print(' --- splitLine:', '::', src)
    def nextRes(cur, curType, nval):
        wd = ''.join(cur)
        # print('#3 >> p-cur, `%s`' % wd, ' curt = ', Lt.name(curType), '; next=', nval)
        res.append(lex(wd, Mk.lex, type=curType))
        cur = [nval]
        return [nval]
    
    if curType == Lt.mttext:
        src = '\n' + src

    i = -1
    slen = len(src)
    for s in src:
        i += 1
        # print('#6 ', cur, " s='%s'"%s, curType, '|', 'esc:', escMod)
        
        if escMod:
            if s not in c_esc_map:
                raise ParseErr('Not currect escape sequence: `%s` ' % src[i-1: i + 1])
        

        sType = charType((cur, curType), s)
        
        if isinstance(sType, tuple):
            # unexpected changing of prev type
            donePart, nextPart, nextType = sType
            nextRes(donePart, curType, '')
            cur, curType = nextPart, nextType
            continue
        # print('#stype:', Lt.name(sType), '>>', s)
        
        # close multi-comment
        if curType == Lt.mtcomm:
            cur.append(s)
            # print('>>mtc:: ', cur, ' >> ', cur[-2:])
            if ''.join(cur[-2:]) == '@#':
                cur = nextRes(cur, curType, '')
                curType = Lt.none
            continue
    
        
        # TODO: use `` and ``` ``` quotes as raw string (no any escapes, instead of \`)
        if curType in [Lt.text, Lt.mttext]:
            
            if escMod:
                # in the string and after esc slash
                print('## in esc' ,  'multi:', openMultStr , '; cur:', cur, 's:', s)
                if s not in c_esc_map:
                    raise ParseErr('Incorrect escape sequence: `\\%s`' % s)
                cur.append(c_esc_map[s])
                escMod = False
                # cur = nextRes(cur, curType, '')
                continue
        
            # escape sequences
            if s == '\\': # sType == Lt.esc:
                print('## esc ', s)# esc = True
                # curType = Lt.esc
                escMod = True
                continue

            if curType == Lt.text and openQuote == s:
                cur = nextRes(cur, curType, s)
                curType = Lt.quot
                cur = nextRes(cur, curType, '')
                curType = Lt.none
                openQuote = None
                continue
            
            if i > 1 and curType == Lt.mttext and sType == Lt.quot:
                # print('MTEXT Quot', src[i-2: i+1], ' open:', openMultStr)
                if src[i-2: i+1] == openMultStr:
                    cur = nextRes(cur[:-2], curType, src[i-2: i+1])
                    curType = Lt.quot
                    cur = nextRes(cur, curType, '')
                    curType = Lt.none
                    openMultStr = None
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

        # ' asd ' , '' , '''  
        if sType == Lt.quot:
            if openQuote is None:
                # start string
                if i > 1 and src[i-2: i+1] in c_mlines:
                    # starting multiline string, prev in '', "", ``
                    openMultStr = src[i-2: i+1]
                    cur = [openMultStr] # like: ['"""']
                    # print('Start multiline ', openMultStr )
                    del res[-1]
                    cur = nextRes(cur, Lt.mttext, '')
                    curType = Lt.mttext
                    continue
                    
                cur = nextRes(cur, curType, '')
                curType = Lt.text
                openQuote = s
                continue

        # finalize word
        cur = nextRes(cur, curType, s)
        curType = sType
    if cur:
        nextRes(cur, curType, None)
    
    if curType == Lt.text and openMultStr is None:
        raise ParseErr('Unclosed string in the and of line `%s`'% s)
    # print('#a3:', src)
    lexems = normilizeLexems(res)
    res3 = {}
    if openMultStr is not None:
        res3['open_m_str'] = openMultStr
    return TLine(src, lexems), curType, res3


def splitLexems(text: str) -> list[TLine]:
    lines = text.splitlines()
    res:list[TLine] = []
    lastType = Lt.none
    # TODO: 
    extArg = {}
    for s in lines:
        if not s.strip():
            continue # miss empty and spaces line
        # res.append(lex(0, Mk.line))
        # interpretator magic:
        
        if s.startswith('@intr@exit'):
            print('Interpretation exit in splitLexems()')
            exit(1);
        nextLine, endType, r3 = splitLine(s, lastType, **extArg)
        extArg = r3
        print('splLex..', [(x.val, Lt.name(x.ltype), x.mark) for x in nextLine.lexems])
        # res.extend(nextLine)
        # print('--- split res --->', [(x.val, x.ltype) for x in nextLine.lexems])
        if res and lastType in [Lt.mtcomm, Lt.mttext] and endType == lastType:
            # join cure line to prev
            lasTLine = res[-1]
            lasTLine.lexems.extend(nextLine.lexems)
            lasTLine.src += nextLine.src
            res[-1] = lasTLine
            continue
        
        if len(nextLine.lexems) == 0:
            continue
        res.append(nextLine)
        lastType = Lt.none
        # lastElemType = nextLine.lexems[-1].ltype
        if endType in [Lt.mtcomm, Lt.mttext]:
            lastType = endType
    # res.append(lex(0, Mk.line))
    return res


def lex2Elem(xx:lex)->Elem:
    # print(':::', xx)
    # if isinstance(xx, (list, tuple)):
    #     for subxx in xx:
    #         print('lex2Elem..subxx:', subxx.val, ':', Lt.name(subxx.ltype))
    #     raise ParseErr(';!!')
    # else:
    #     print('lex2Elem..subxx:', xx.val, ':', Lt.name(xx.ltype))
    
    if xx.ltype in [Lt.word, Lt.num, Lt.text, Lt.mttext]:
        return Elem(xx.ltype, xx.val)
    if xx.ltype == Lt.oper:
        return Elem(Lt.oper, xx.val)
    # TODO: other type
    # TODO: metadata from comments


def elemLine(src:TLine)->CLine:
    ''' '''
    # prep:list[lex] = []
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
        # print('indent: cur/ base:', indLen , CLine.BaseIndent, ' = ', indLen / CLine.BaseIndent)
        ind = int(indLen / CLine.BaseIndent)

    res:list[Elem] = []
    for lx in src.lexems:
        el = lex2Elem(lx)
        if not el:
            continue
        
        res.append(el)
    # print('================>>>> ', res)
    return CLine(src, res, ind)

def elemStream(lines:list[TLine])->list[CLine]:
    ''' '''
    res:list[CLine] = []
    CLine.BaseIndent = 0
    for tl in lines:
        cl = elemLine(tl)
        res.append(cl)
    return res
