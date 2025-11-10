'''
Operators defined as text-word:
return
break
continue

'''

from lang import *
from vars import *
from vals import isLex

from cases.tcases import *
import math


class CaseReturn(SubCase):
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) > 0:
            if isLex(elems[0], Lt.word, 'return'):
                return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' We have to 
        1. store result of next after return expr
        2. stop execution next lines'''
        subs = [elems[1:]]
        exp = ReturnExpr()
        return exp, subs
    
    def setSub(self, base:ReturnExpr, subs:list[Expression])->Expression:
        base.setSub(subs[0])
        return base



class CaseBreak(SubCase):
    ''' break '''
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) > 0:
            if isLex(elems[0], Lt.word, 'break'):
                return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        ''' ''' 
        # subs = [elems[1:]]
        exp = BreakExpr()
        return exp, []
    
    def setSub(self, base:BreakExpr, subs:list[Expression])->Expression:
        # base.setSub(subs[0])
        return base


class CaseContinue(SubCase):
    ''' continue '''
    
    def match(self, elems:list[Elem])-> bool:
        if len(elems) > 0:
            if isLex(elems[0], Lt.word, 'continue'):
                return True
        return False
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        exp = ContinueExpr()
        return exp, []
    
    def setSub(self, base:ContinueExpr, subs:list[Expression])->Expression:
        # base.setSub(subs[0])
        return base


class CaseRegexp(SubCase):
    ''' re`pattern`, re'...', re"123"
        `` quotes most useful for pattern without escape sequences
        re`abc`/`imu` : regexp with flags in string
        re`abc`/flags : regexp with flags in variable
        re`abc`imu : regexp with flags
        re`abc`{flags} : regexp with flags in variable
        re`abs`/flags =~ src : matching - bool
        re`abs`/flags /~ src : replace - string
        re`abs`/flags ?~ src : search - list[list]
        
        think about:
        re {patternVar} {flagsVar}
    '''
    
    def match(self, elems:list[Elem])-> bool:
        # re`abc`: 2
        # re`abc`imu: 3
        # re`abc`{flags}: 2
        if not isLex(elems[0], Lt.word, 're'):
            return False
        elen = len(elems)
        if elen not in [2,3,5]:
            return False
        res = True
        if elen > 1:
            # print('r-match:', Lt.name(elems[1].type), 'len=', elen)
            # print('r-match:', elemStr(elems, ','))
            res &= elems[1].type in (Lt.text, Lt.mttext)
        if res and elen == 3:
            # if native flags
            res &= elems[2].type == Lt.word and math.prod([s in 'aiLmsux' for s in elems[2].text])
        if res and elen > 4:
            # if flags in var
            # print('r-match:5len', elemStr(elems, ','))
            res &= (isLex(elems[2], Lt.oper, '{') 
                and isLex(elems[4], Lt.oper, '}')
                and elems[3].type == Lt.word)
        return res
    
    def split(self, elems:list[Elem])-> tuple[Expression, list[list[Elem]]]:
        # elems[0]: re
        patt = elems[1].text
        flags = ''
        elen = len(elems)
        match elen:
            case 3:
                # re`..`sum
                flags = elems[2].text
            case 5:
                # re`..`{var}
                flags = VarExpr(Var(elems[3].text, TypeString()))
        
        exp = RegexpExpr(patt, flags, src=elems)
        return exp, []
    
    def setSub(self, base:ContinueExpr, subs:list[Expression])->Expression:
        # base.setSub(subs[0])
        return base


