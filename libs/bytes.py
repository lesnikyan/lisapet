''' 
features of bytes type
'''

from lang import *
from vars import *
from context import Context



def zeroFill(bb:bytearray, size):
    diff = size - len(bb)
    res = bytearray([0 for _ in range(diff)]) + bb
    return bytearray2(res)


def operPrep(a, b):
    da, db = a.val, b.val
    alen, blen =  len(da), len(db)
    if alen > blen:
        db = zeroFill(db, alen)
    elif alen < blen:
        da = zeroFill(da, blen)
    return da, db


def bit_and(_, a:BytesVal, b:BytesVal) -> BytesVal:
    '''
    bytes & bytes
    '''
    da, db = operPrep(a, b)
    clen = len(da)
    r = [da[i] & db[i] for i in range(clen)]
    # print('', r)
    return BytesVal(bytearray2(r))


def bit_or(_, a:BytesVal, b:BytesVal) -> BytesVal:
    '''
    bytes & bytes
    '''
    da, db = operPrep(a, b)
    clen = len(da)
    r = [da[i] | db[i] for i in range(clen)]
    return BytesVal(bytearray2(r))


def bit_xor(_, a:BytesVal, b:BytesVal) -> BytesVal:
    '''
    bytes & bytes
    '''
    da, db = operPrep(a, b)
    clen = len(da)
    r = [da[i] ^ db[i] for i in range(clen)]
    return BytesVal(bytearray2(r))