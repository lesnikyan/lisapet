'''
Base types.
'''

import re

# TODO: add config
FullPrint = 0

def dprint(*args):
    if FullPrint:
        print(*args)

class ParseErr(ValueError):
    def __init__(self, msg, src=None, parent=None):
        # super().__init__(*args)
        self.msg = msg
        self.src:TLine = src
        self.parent:Exception = parent


class Mk:
    empty = 0
    lex = 1 # any lexem
    start = 2 # start of block
    fin = 3 # end of block
    line = 4 # start line


class lex:
    def __init__(self, val=None, mark=None, **kw):
        self.val = val if type(val) is str else None
        # dprint('#4 ', type(val), '|', self.val)
        self.mark = mark if mark in [1,2,3, 4] else Mk.empty
        self.ltype = kw['type'] if 'type' in kw else 0


# lexType:
class Lt:
    none = 0
    space = 1 #white space
    word = 2
    lang = 3 # special words
    num = 4
    oper = 5
    comm = 6
    text = 7
    quot = 8
    esc = 9
    block = 11 # open block. start of block if more than shift of prev line
    close = 12 # close block
    endline = 13
    indent = 14 # set of spaces, 4-th by default,
    mtcomm = 15 # multiline comment
    mttext = 16 # multiline string
    
    _names:str = 'none space word lang num oper comm text quot esc . block close endline indent mtcomm mttext'
    
    @classmethod
    def name(c, val):
        ''' get str name of Lt-values '''
        ns = Lt._names.split(' ')
        if val >= 0 and  val < len(ns):
            return ns[val]
        return 'bad#val'


class Elem:
    '''Code elem'''
    def __init__(self, type:Lt, text:str):
        self.type:Lt = type
        self.text:str = text


class TLine:
    ''' Text line '''
    def __init__(self, src:str, lexems:list[lex]):
        self.src = src
        self.lexems:list[lex] = lexems
        # dprint('#a4:', [n.val for n in self.lexems])


class CLine:
    ''' Code line '''
    
    BaseIndent = 0 # Base count of spaces  in the one indent  in the start of line.
    
    def __init__(self, src:TLine=None, code:list[Elem]=[], indent:int=0):
        self.src:TLine = src
        self.code:list[Elem] = code
        self.indent = indent
        self.line = 0


# KEYWORDS = '''
# import
# const
# for if do while func
# case match 
# '''

KEYWORDS = re.split(r'\s+',
    '''
import
const
for while break continue 
func return
if else case match
struct list dict tuple
''')

TYPES = 'num int float bool str list dict struct any null callab'
