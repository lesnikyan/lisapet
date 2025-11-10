'''
Regexp functions for LISAPET
'''

import re


_flagMap = {
    'a' : re.ASCII, 
    'i': re.IGNORECASE, 
    'L': re.LOCALE, 
    'm': re.MULTILINE, 
    's': re.DOTALL, 
    'u': re.UNICODE, 
    'x': re.VERBOSE
}


def str2flags(src:str) -> list[int]:
    ''' '''
    return [_flagMap[s] for s in src if s in _flagMap]


def combineFlags(nums:list[int])->int:
    fr = 0
    for f in nums:
        fr = fr | f
    return fr


def compile(src:str, flags:list=0):
    prepFlags = re.RegexFlag.NOFLAG
    if isinstance(flags, (list, tuple)):
        prepFlags = combineFlags(flags)
    elif isinstance(flags, (int, re.RegexFlag)):
        prepFlags = flags
        
    rgx = re.compile(src, prepFlags)
    return rgx
