
import re

from lang import dprint
from parser import ParseErr
# from tree import line2expr
from nodes.expression import ValExpr, Expression
from base import Val
from vars import StringVal
from typex import TypeString
from context import Context


class subLex:
    def __init__(self, s):
        self.s = s
        self.expr = ''
        self.options = ''
        self.split()
    
    def split(self):
        src = self.s
        if ':' in src:
            # has format options
            cInd = src.find(':')
            self.expr = src[:cInd]
            self.options = src[cInd:]
        else:
            self.expr = self.s
    
    def __str__(self):
        return 's{%s}' % self.s

    def __repr__(self):
        return self.__str__()
        
    

class Fc:
    ''' Format constants '''
    ALIGN_D = 0 # default
    ALIGN_L = 1 # <
    ALIGN_R = 2 # >
    ALIGN_C = 4 # ^ Center


class FmtOption:
    def __init__(self, suff=''):
        # d:int, x:hex, o:oct, b:bin, f: float, s:str, 
        self.type = 's'
        self.shift = 0
        self.zeroLead = False
        self.minSize = 0
        self.signed = False # show sign for positive numbers
        self.toStr = False
        self.decimDigits = -1 # means - any
        self.align = Fc.ALIGN_D

class FmtOptParser:
    def __init__(self, suff=''):
        '''  '''
        self.drx = re.compile(r'\d')

    def parseSuff(self, src:str):
        formatTypes = 'x,b,o,d,f,e,s'.split(',')
        res = FmtOption()
        tKey = 's'
        if src.startswith(':'):
            if len(src) < 2:
                return
            fmo = src[1:] # :2.3.f -> 2.3f
            tKey = fmo[-1]
            if tKey not in formatTypes:
                raise ParseErr(f'Incorrect option (type) for string formatting: `{src}` ')
            res.type = tKey
            # zero count , point, decimal digits. For float and decimal-int only
            # :N.DT : N - zeros before, D - digits after dot, T - data type:: d, f
            # :2d -> 0012 ; :.2f -> 12.12 ; :2.5.f -> 0012.12345
        # fmr = [0,0,0,0,'s']
        # if tKey in 'xbodfe':
            self.parseDigits(fmo, res)
        return res
        
            
    def parseDigits(self, fmo:str, fmr:FmtOption):
            # fmr = [False, 0, -1, tKey] # format res: [+-sign:false(- only), zero-lead count:0, decimal-digits:any(-1), type:s]
            oInd = 0 # index left-side options, starts with 0
            # sign = False
            # zero = False
            msize = 0
            ddig = -1
            if fmo[oInd] in '<>^':
                # align
                match fmo[0]:
                    case '<': fmr.align = Fc.ALIGN_L
                    case '>': fmr.align = Fc.ALIGN_R
                    case '^': fmr.align = Fc.ALIGN_C
                oInd += 1
                
            if fmo[oInd] in '+-':
                fmr.signed = fmo[oInd] == '+'
                oInd += 1
            if len(fmo) > 1 + oInd:
                if fmo[oInd] == '0':
                    # zero-lead digit
                    fmr.zeroLead = True
                    oInd += 1
            if len(fmo) > 1 + oInd:
                if self.drx.match(fmo[oInd]):
                    # min size option
                    # sizeNum = fmo[oInd: fmo.find]
                    szrx = re.compile('\\d+')
                    szres = szrx.search(fmo[oInd:])
                    szSt, szEn = szres.span()
                    # dprint('sz.span', fmo[oInd+szSt: oInd+szEn])
                    msize = int(fmo[oInd+szSt: oInd+szEn])
                    oInd += szEn
            match fmr.type:
                case 'f':
                    if '.' in fmo:
                        pInd = fmo.find('.')
                        if len(fmo) < pInd + 3:
                            raise ParseErr('Incorrect option (type) for string formatting: '
                                           f'decim point without precision: `{fmo}` ')
                        pStr = fmo[pInd+1]
                        if not self.drx.match(pStr):
                            raise ParseErr('Incorrect option (type) for string formatting: '
                                           f'decimal precision not a number: `{pStr}` from opts: `{fmo}` ')
                        ddig = int(pStr)
            fmr.minSize = msize
            fmr.decimDigits = ddig
            
    def parseStr(self, fmo:str, tKey):
        ''' strings options: shift, crop, ... '''
            
    # def parseObj(self, fmo:str, tKey):
    #     ''' str format for  '''
    #     pass


class Formatter:

    def format(self, val, opt:FmtOption):
        res = ''
        isNum = opt.type in 'fdboxe'
        # dprint(opt.type)
        match opt.type:
            case 'x': res = self.toHex(val)
            case 'd': res = self.toDec(val)
            case 'b': res = self.toBin(val)
            case 'o': res = self.toOct(val)
            case 'f': res = self.toFloat(val)
            case 'e': res = self.toExp(val)
            case 's': res = self.toStr(val)
        # shift
        # if opt.shift > 0:
        #     res = ' ' * opt.shift + res
        # dprint('rowr', res)
        
        shiftR = 0
        numSign = ''
        if isNum:
            if val < 0:
                numSign = '-'
                res = res[1:]
            elif opt.signed:
                numSign = '+'
        
        if opt.type == 'f' and opt.decimDigits > -1:
            pInd = res.find('.')
            ddg = len(res) - pInd - 1 # decamal digits before correction
            if ddg > opt.decimDigits:
                # cut
                res = res[: (pInd + 1 + opt.decimDigits)]
            elif ddg < opt.decimDigits:
                # fill
                res += '0' * (opt.decimDigits - ddg)

        # if isNum and opt.signed and val > 0:
        #     res = '+' + res

        sgLen = len(numSign)
        if opt.minSize > 0:
            rlen = len(res)
            if rlen < opt.minSize:
                # dprint('--', rlen)
                fillN = opt.minSize - rlen
                pre, post = 0, 0
                match opt.align:
                    case Fc.ALIGN_D | Fc.ALIGN_R: pre = fillN
                    case Fc.ALIGN_L: post = fillN
                    case Fc.ALIGN_C: 
                        pre = int(fillN / 2)
                        post = fillN - pre
                res = ' ' * pre + res + ' ' * post
                shiftR = pre
        
        # zero-lead
        if isNum and opt.align in (Fc.ALIGN_D, Fc.ALIGN_R) and opt.zeroLead:
            res = res.replace(' ', '0', shiftR)
        
        # sign
        # '   -12.100' '    12.100'
        # '   -12.100' '   +12.100'
        # '000-12.100' '000012.100'
        # '-00012.100' '+00012.100'
        # dprint('#1:', res, ' shift:', shiftR)
        if isNum and numSign:
            # maybe we need to move sign to the res[0]
            if opt.zeroLead:
                postf = res
                if shiftR:
                    postf = res[1:]
                res = numSign + postf
            else:
                if shiftR:
                    res = res[:shiftR-1] + numSign + res[shiftR:]
                else:
                    res = numSign + res
        
        return res

    def toHex(self, num):
        return f'{num:x}'
    
    def toDec(self, num):
        return str(num)
    
    def toBin(self, num):
        return f'{num:b}'
    
    def toOct(self, num):
        return f'{num:o}'
    
    def toFloat(self, num):
        return str(num)
    
    def toStr(self, s):
        return str(s)
    
    def toExp(self, num):
        return f'{num:e}'
    
    # TODO: other needed formats
    
    # def toHex(self, num):
    #     return ''
    
    # def toHex(self, num):
    #     return ''
    

def toString(val, ptrn):
    if isinstance(val, str):
        return val


class ExprFormat(Expression):
    ''' eval expr and format result '''

    def __init__(self, expr, format:FmtOption=None):
        # super().__init__()
        self.expr = expr
        if format is None:
            format = FmtOption()
        self.opt = format
        self.res = None
    
    def do(self, ctx:Context):
        self.expr.do(ctx)
        val = self.expr.get().getVal()
        fmt = Formatter()
        fval = fmt.format(val, self.opt)
        self.res = StringVal(fval)
    
    def get(self):
        return self.res


class StrJoinExpr(Expression):
    ''' Upper Level Expression object of formatting string operator `~`
        add: add next str part
        do: Join parts of formatted string '''

    def __init__(self, parts):
        super().__init__(None, '')
        self.parts:list[Expression] = []
        if parts:
            for pp in parts:
                # dprint('SJE.init:', pp)
                self.add(pp)
        self.res = None

    def add(self, exp:Expression):
        self.parts.append(exp)

    def do(self, ctx:Context):
        ss = []
        for pp in self.parts:
            pp.do(ctx)
            tres = pp.get()
            # dprint('SJEx.do1:', pp, tres)
            s = tres.getVal()
            ss.append(s)
        rval = ''.join(ss)
        self.res = StringVal(rval)

    def get(self):
        return self.res


class FormatParser:
    """  
    parse string to next interpretation 
    ' Empty: {} escaped brackets: {{}} int: {var:d} str {var:s} default(str): {var}  '
    ' list or dict {var[key]}  struct.field {var.member} func {foo(arg1, arg2)} method {obj.foo(arg)} '
    ' operators {a + b} ternar: {a < 5 ? "aaa" : "bbb"} nullOr {var1 ?: var2} '
    
    """
    
    def __init__(self):
        self.brx = re.compile(r'(\{+|\}+)')
        self.irx = re.compile(r'[^\{]?\{([^\{\}]+)\}[^\}]?')
    
    def parse(self, src):
        ''' "text {expr}" '''
        parts = [] # text parts
        # incs = [] # expr parts
        bparts = self.brx.split(src)
        # dprint('SF:', bparts)
        inExp = False
        for bb in bparts:
            tbr = ''
            bbl = len(bb)
            hflen = int(bbl / 2)
            if bb.startswith('{'):
                if len(bb) % 2 == 0:
                    # escaped brackets
                    tbr = bb[:hflen]
                else:
                    # hlen = int((len(bb) -1) / 2)
                    tbr = bb[:hflen]
                    # next elem is expr
                    inExp = True
                if tbr:
                    parts.append(tbr)
                continue
            if bb.endswith('}'):
                if len(bb) % 2 == 0:
                    # escaped brackets
                    tbr = bb[:hflen]
                else:
                    tbr = bb[:hflen]
                    # close expr
                if inExp:
                    inExp = False
                if tbr:
                    parts.append(tbr)
                continue
            if inExp:
                parts.append(subLex(bb))
                continue
            parts.append(bb)
        return parts


# class StrFormatter:
#     '''parse interpret includes, eval includes, build result line'''
#     def subExpr(self, code:str):
#         tlines = splitLexems(code)
#         clines:CLine = elemStream(tlines)
#         return line2expr(clines)

#     def partsToExpr(self, parts:str|subLex)->list[Expression]:
#         expp = []
#         fmOpPar = FmtOptParser()
#         for ss in parts:
#             if isinstance(ss, subLex):
#                 valExpr = self.subExpr(ss.expr)
#                 format = fmOpPar.parseSuff(ss.options)
#                 expr = ExprFormat
#                 expp.append(expr)
#             else:
#                 expp.append(ValExpr(ss))
#         rr = StrJoinExpr(expp)
#         return rr


# def fstring(self, src:str):
#     ''' convers src string to expression '''
#     fp = FormatParser()
#     sf = StrFormatter()
#     parts = fp.parse(src)
#     return sf.partsToExpr(parts)

