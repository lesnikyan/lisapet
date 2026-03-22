'''

'''

from lang import *
from vars import *
from vals import isDefConst, elem2val, isLex


'''
oper group replacement:
`1` >=> ,
'''



_hexType = [Lt.word, Lt.num]
rxHex = re.compile(r'[0-9a-f]+', flags=re.I)

def isHexBytes(elems:list[Elem]):
    if len(elems) < 2:
        return False
    for el in elems:
        if el.type not in _hexType or not rxHex.match(el.text):
            return False
    return True


operPrior = ('( ) [ ] { } , . , ~> , ... , -x ! ~ , ** ^/ , * / % , + - ,'
' << >> , =~ ?~ /~, < <= > >= !> ?> !?>, == != , &, ^ , | , ::, && , || , \\ , ->, $, ?: , : , ?, `1`, .. , <- , = += -= *= /= %= , ; , !: :? => , /: ')

unaryOperators = '- ! ~ +'.split(' ')

SPEC_WORDS = 'func if for while match enum struct else import return'.split(' ')

def getOperPriors():
    return [raw.replace('`1`', ',') for raw in operPrior.split(',')]


def isGetValExpr(elems:list[Elem]):
    ''' If solid  expressions 
    of var, func call, obj member, collection elem, etc '''

    inBr = 0
    obr = [s for s in '([{']
    cbr = [s for s in ')]}']
    lem = len(elems)
    
    if lem < 1 :
        return False
    varOpers = '([{}]).'
    for i in range(0, lem):
        ee = elems[i]
        
        # close br
        if isLex(ee, Lt.oper, cbr):
            inBr -= 1
        
        #open br
        if isLex(ee, Lt.oper, obr):
            inBr += 1
        
        if inBr > 0:
            continue
        
        # not in br
        if ee.type == Lt.word or (ee.type == Lt.oper and ee.text in varOpers):
            # just valid var, or func call, or collectio[elem], or obj.field 
            continue
        # print('utils.geVar4: ', ee.text, ' __ ', inBr)
        # any other lexem means that whole expression not what we expect
        return False
    return True

def isBrPair(elems:list[Elem], opn, cls):
    return isLex(elems[0], Lt.oper, opn) and isLex(elems[-1], Lt.oper, cls)

def el_text(elems:list[Elem]):
    return [n.text for n in elems]

def prels(pref, elems:list[Elem], *args, **kwargs):
    ''' Print list of elems '''
    if not (FullPrint or ('show' in kwargs and kwargs['show'])):
        return
    if not elems:
        # print(pref, '-empty-')
        return
    
    # list[list[Elem]]
    if isinstance(elems[0], (list, tuple)):
        # print(pref, end='')
        for subel in elems:
            print(el_text(subel), end=' $$ ', sep = ' ')
        print('')
        return

    # list[Elem]
    print(pref, el_text(elems), *args)


def elemStr(elems:list[Elem], delim=' '):
    # dprint('debug elemStr', elems)
    return delim.join([ee.text for ee in elems])

_rArrCh = '->'
_commaCh = ','


class OperSplitter:
    
    __politon = {}
    
    def __init__(self, priors=None):
        priorSrc = operPrior
        self.defPrior = True
        if priors:
            priorSrc = priors
            self.defPrior = False
        # print('utils.OperSplitter:', priorSrc)
        priorGroups = [raw.replace('`1`', ',') for raw in priorSrc.split(',')]
        self.priorGroups = [[ n for n in g.split(' ') if n.strip()] for g in priorGroups]
        self.opers = [oper for nn in self.priorGroups[:] for oper in nn]
        self.unarIndex = -111
        if self.defPrior:
            self.unarIndex = [gi for gi in range(len(self.priorGroups)) if '-x' in self.priorGroups[gi]].pop()
            
        self.brbr = ('([{',
                ')]}')
        self.backAssoc = ['/:']

    @classmethod
    def getInst(cl, priors=None):
        # print('getInst', priors)
        key = 0
        if key is None:
            priors = None
        else:
            key = priors
        inst = None
        if key not in cl.__politon:
            inst = OperSplitter(priors)
            cl.__politon[key] = inst
        else:
            inst = cl.__politon[key]
        return inst


    def mainOper(self, elems:list[Elem], lesser=None)-> int:
        '''
        Find the main operator in the string.
        First operator with lowest priority from the end will be returned.
        e.g. + or - for math expressions with + - / *
        or || for logical expressions. 
        '''
        
        # print('u-unar', unarIndex, self.priorGroups[unarIndex])
        # print('~- OperSplitter', len(elems))
        # prels('~~ OperSplitter', elems, show=1)
        
        lem = len(elems)
        if lem < 2:
            return -1
        
        lowestPrior = len(self.priorGroups) - 1
        leftOfRarr = False # [\] word [, word]
        passed = False
        
        for prior in range(lowestPrior, -1, -1):
            if lesser is not None:
                if passed:
                    # It means that the expected operator hasn't been found
                    # print('~')
                    return -1
                if lesser in self.priorGroups[prior]:
                    passed = True
            curPos = lem
            # obr='([{'
            # cbr = ')]}'
            cbrInd = 1
            obrInd = 0
            # if len(self.priorGroups) < 500:
            #     print('prior=', prior, self.priorGroups[prior] )
            step = -1
            elIter = range(lem - 1, -1, -1)
            if self.priorGroups[prior][0] in self.backAssoc:
                # means that all opers in group have the same direction of assoc
                # print('OperSplitter. back-assoc', self.priorGroups[prior])
                step = 1
                curPos = -1
                elIter = range(0, lem)
                # cbr='([{'
                # obr = ')]}'
                cbrInd = 0
                obrInd = 1
            inBrs = [] # brackets which was opened from behind
            # print('$prior: ', self.priorGroups[prior])
            leftOfRarr = False
            # lamLef = []
            for i in elIter:
                curPos += step
                if curPos < 0 : # or curPos >= lem
                    return curPos # Nothing was found
                el = elems[i]
                etx = el.text
                # if self.priorGroups[prior][0] in backAssoc:
                #     print('spl1:', i, el.text, Lt.name(el.type), (el.text in self.priorGroups[prior]), ' pos =', curPos, inBrs)
                
                # counting brackets from tne end, closed is first
                # dprint('ue:', i, ':', etx, '>>', '`'.join(inBrs))
                # if etx and (etx in cbr):
                if etx and (etx in self.brbr[cbrInd]):
                    inBrs.append(etx)
                    # print('inbr append: ', '>>', inBrs)
                    continue
                lebr = len(inBrs)
                if etx and (etx in self.brbr[obrInd]):
                    if lebr:
                        last = inBrs.pop() # change br stack
                        lebr = len(inBrs)
                    if i == 0 and etx in self.priorGroups[prior]:
                        # print('end of prior / open', obr)
                        return 0
                    continue
                # print('@#', etx, 'br:', inBrs)
                    # TODO: check equality of brackets pairs (not actual for valid code, because [(]) is invalid )
                if lebr > 0:
                    continue
                # if self.priorGroups[prior][0] in backAssoc:
                    # print('>>>>>>>> DEBUG 1')
                if el.type != Lt.oper:
                    continue
                if el.text not in self.opers:
                    continue

                if leftOfRarr:
                    if el.text != _commaCh and i > 0:
                        leftOfRarr = False
                    else:
                        continue
                if el.text == _rArrCh:
                    leftOfRarr = True

                # if el.text in ['-', '+', '!', '~']:
                if el.text in unaryOperators:
                    if i > 0 and elems[i-1].type == Lt.oper and elems[i-1].text not in self.brbr[1]:
                        # unary case found, skip current pos
                        # print(' >> == unary case found:', i, el.text)
                        continue
                    if i == 0 and prior != self.unarIndex:
                        # print(' >> == unary case in 0:', i, el.text)
                        continue
                if el.text in self.priorGroups[prior]:
                    # we found current split item
                    # print('oper-found> [%d ? %d]' % (i, curPos), '`%s`' % src, elemStr(elems[0:i]), '<(%s)>' % elems[i].text, elemStr(elems[i+1:]))

                    return curPos # The main Result
        if isLex(elems[0], Lt.oper, unaryOperators):
            # print('oper-found> unary [0 : %s]' % elems[0].text ) 
            return 0
        return -1 # debug output, won't happened in real case



def flatOpers():
    opers = getOperPriors()[4:]
    # print(opers)
    fopers = []
    for oops in opers:
        # print(oops.split(' '))
        fopers.extend([n for n in oops.split(' ') if n and  n not in ' .'])
    return fopers

_noSolidOpers = flatOpers()

# _keyWords = (
#     'func if else while for struct import match enum @debug'
# ).split(' ')

KEYWORDS_R = {n:0 for n in ['func','if','else','for','return','struct','match','enum','while','import', 'grup']}
KEYR_RX = re.compile('func|if|for|while|match|enum|grup|struct|else|import|return')
rSolOpers = ['.','~>', '...']
_bpairs = {'(':')', '[':']', '{':'}'}
_rob = list('}])')
_rcb = list('([{')


def isSolidExpr(elems:list[Elem], getLast=None, skipKeywords = False):
    ''' single varName or chain of fields, subelem, call 
    
        getLast - get pos of lastsubpart like word after dot, brackets
    '''
    # print('isSolid #1', elemStr(elems))
    elen = len(elems)
    if elen == 0:
        return False, -1
    
    if elen == 1 and elems[0].type in [Lt.word, Lt.text, Lt.num]:
        return True, 0
    # print('%')
    # print('isSolid #2', f"<{elems[0].text}>", elems[0].text in KEYWORDS_R)
    if not skipKeywords and  elems[0].type == Lt.word:
        if KEYR_RX.match(elems[0].text):
        # if elems[0].text in KEYWORDS_R:
            return False, -1
    
    if isHexBytes(elems):
        return False, -1

    fopers = _noSolidOpers
    # print('solid-fopers', fopers)
    opened = [] # brackets openede from right
    # # cbr = []
    # rob = list('}])')
    # rcb = list('([{')
    # print('ss:', end=' ')
    found = -1
    for i in range(elen-1, -1, -1):
        el = elems[i]
        etx = el.text
        # print('=>', '', etx, end=' ')
        # print('=>', '', etx)
        # et = el.type
        if isLex(el, Lt.oper, _rob):
            # open brackets from right
            opened.append(el.text)
            continue
        if isLex(el, Lt.oper, _rcb):
            # close brackets
            if len(opened) == 0:
                # posibly multiline expr
                # print('No-solid?', len(opened))
                return False, -1
            lastObr = opened.pop()
            if _bpairs[etx] != lastObr:
                # incorrect brackets pair in closing
                raise InterpretErr(f"incorrect brackets pair in closing `{etx}{_bpairs[etx]}`")
                # return False, -1
            if len(opened) == 0 and getLast:
                # last closed part found in solidExpr
                if found == -1:
                    found = i
                # return True
            continue
        # print('2>>')
        if opened:
            continue
        if getLast and isLex(el, Lt.oper, rSolOpers):
            if found == -1:
                found = i
            # return True
        # print('back-i:%d'%i, 'No Solid because of ', etx)
        # return False
        if isLex(el, Lt.oper, fopers):
            # any operator has been found not in brackets a + b, excepr [. ~>]
            # print('back-i:%d'%i, 'No Solid because of ', etx)
            return False, -1
        # elif isLex(el, Lt.word, KEYWORDS_R):
        #     return False
    # print('\n>> ', opened, ' //')
    res = (not opened)
    # if getLast:
    #     return res, found
    # print('isSolid-11', res, found)
    return res, found

def isFuncCall(elems:list[Elem]):
    ''' solid expr with func call in the end
        a()
        a(args)
        a.b()
        a[0]()
        a()()
        a.b()()
    '''

def isField(elems:list[Elem]):
    ''' solid expr with `.fieldName` in the end 
        a.b
        a().b
        a.b().c
        a.b[0].c
    '''
    if not isLex(elems[-2], Lt.oper, '.'):
        return False
    
    return elems[-1].type == Lt.word and elems[-1].text

def isSeqElem(elems:list[Elem]):
    ''' solid expr with square brackets in the end
        a[0]
        a.b[0]
        a()[0]
        
    '''
