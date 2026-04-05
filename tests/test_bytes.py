''' '''


from unittest import TestCase, main
from context import Context
from eval import rootContext, moduleContext
from tests.utils import *


class TestBytes(TestCase):
    ''' 0x[ff 00 12 ab] '''


    
    def test_bytes_gen(self):
        '''
        test comprehension generator of bytes
        0x[byte(); n <- src ; ? ]
        '''
        code = r'''
        res = []
        
        # simplest
        ss1 = [1..8]
        r1 = 0x[ n ; n <- ss1]
        res <- r1
        
        
        # by list of bytes
        ss2 = [0x[11 22], 0x[33 44], 0x[aa bb], 0x[ee ff]]
        r2 = 0x[ n ; n <- ss2]
        res <- r2
        
        # by iter gen
        ss3 = [0xff8 .. 0xfff]
        r3 = 0x[n % 255 ; n <- ss3]
        res <- r3
        
        # 2 loops + assign
        ss4 = [(4, 1), (2,205), (4, 64), (4, 252)]
        r4 = 0x[ x ; n, v <- ss4 ; k <- iter(n) ; x = v + k]
        res <- r4
        
        # filter
        nn5 = [128 .. 144]
        r5 = 0x[n ; n <- nn5 ; n % 2 != 0 && n % 3 != 0]
        res <- r5
        
        # filter by func call
        func f6(x, nums)
            for n <- nums
                if x % n == 0
                    return false
            return true
        
        nn6 = [145 .. 196]
        div = [2,3,5,7, 11, 13, 17, 19, 23]
        r6 = 0x[n ; n <- nn6 ; f6(n, div)]
        res <- r6
        
        # by bytes
        bb7 = 0x[1 2 3 4 5 6 7 8 9 a b c d e f]
        r7 = 0x[xb + b ; b <- bb7 ; xb = b * 16 ; b > 7]
        res <- r7
        
        # blocks by bytes
        bb8 = bytes('ABCDEFGHIJKLMNOP')
        r8 = 0x[bytes([c + 32, 0x20]) ; c <- bb8]
        s8 = r8.string()
        res <- r8
        res<- s8
        
        # from struct fields
        struct A nn:list, tt:tuple
        
        a9 = A(
            [1,2,3,4], 
            (bytes('a'), bytes('h'), bytes('m'), bytes('x') ))
        # res <- [0x[ y ; y <- [ n + 0x30,  b]] ; n, bb <- a9.nn, a9.tt ; b = bb[0]]
        
        r9 = 0x[ 0x[ y ; y <- [ n + 0x30,  b]] ; n, bb <- a9.nn, a9.tt ; b = bb[0]]
        res <- r9
        res <- r9.string()
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            '0x[01 02 03 04 05 06 07 08]', 
            '0x[11 22 33 44 aa bb ee ff]', 
            '0x[08 09 0a 0b 0c 0d 0e 0f]', 
            '0x[01 02 03 04 cd ce 40 41 42 43 fc fd fe ff]', 
            '0x[83 85 89 8b 8f]', 
            '0x[95 97 9d a3 a7 ad b3 b5 bf c1]', 
            '0x[88 99 aa bb cc dd ee ff]', 
            '0x[61 20 62 20 63 20 64 20 65 20 66 20 67 20 68 20 69 20 6a 20 6b 20 6c 20 6d 20 6e 20 6f 20 70 20]', 
            'a b c d e f g h i j k l m n o p ', 
            '0x[31 61 32 68 33 6d 34 78]', 
            '1a2h3m4x']
        self.assertEqual(exv, resv)

    def test_bytes_oper_bitwize(self):
        ''' '''
        code = r'''
        res = [-556]
        
        # AND &
        bb1 = [f0 f0]
        bb2 = [ff 00]
        res <- (bb1 & bb2)
        
        # bin
        res <- 0b[1100 1100] & 0b[0000 1111]
        
        # diff len
        res <- [ff 00 ff 11] & [e5 ff]
        res <- 0x[17] & [ff 00 11 ff]
        
        # OR |
        
        bb11 = 0x[f0 f1 00 01 00]
        bb12 = 0x[03 00 49 e2 de]
        res <- bb11 | bb12
        
        # bin
        res <- 0b[1111 0000 1100 1100] | 0b [1001 0001 0001]
        
        # diff len
        res <- 0x[3c] | [f4 12 00]
        res <- [e1 b2 c3 f6 22 00] | 0x[15 de]
        
        # XOR ^
        
        bb21 = [ff ff]
        bb22 = [0f f0]
        res <- bb21 ^ bb22
        
        # bin
        res <- 0b[1111 0000 1010 0101] ^ 0b[0000 0011 1111 0000]
        
        # diff len
        res <- 0x[15] ^ [ee 07 00]
        res <- [ff 05 00] ^ 0x[12 41]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [-556, 
            '0x[f0 00]', '0x[0c]', '0x[00 00 e5 11]', '0x[00 00 00 17]', 
            '0x[f3 f1 49 e3 de]', '0x[f9 dd]', '0x[f4 12 3c]', '0x[e1 b2 c3 f6 37 de]', 
            '0x[f0 0f]', '0x[f3 55]', '0x[ee 07 15]', '0x[ff 17 41]']
        self.assertEqual(exv, resv)

    def test_bytes_builtin_split_method(self):
        ''' split bytes by separator '''
        code = r'''
        res = [-553]
        
        bb1 = 0x[ff 00 11 00 f1 00 ae de 00 33]
        res <- bb1.split(0x[00])
        
        bb2 = 0d[1 2 111 3 4 111 5 6 7 8 111 123 145]
        res <- bb2.split(0d[111]).map(
            p -> p.nums(1))
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [-553, 
               ['0x[ff]', '0x[11]', '0x[f1]', '0x[ae de]', '0x[33]'], 
               [[1, 2], [3, 4], [5, 6, 7, 8], [123, 145]]]
        self.assertEqual(exv, resv)

    def test_bytes_builtin_dividing_methods(self):
        ''' '''
        code = r'''
        res = [-552]
        
        # .blocks
        bb1 = [a0 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f]
        res <- bb1.blocks(1)
        res <- bb1.blocks(2)
        res <- bb1.blocks(4)
        res <- bb1.blocks(3)
        res <- bb1.blocks(5)
        
        # .nums
        
        # int32
        bb2 =  [00 00 00 01 00 00 f0 00]
        bb2 <- [00 00 00 ff 00 00 ff ff]
        bb2 <- [00 ff ff ff ff ff ff ff]
        # res <- bb2.nums(4)
        
        # byte (int8)
        bb3 = [00 01 02 09 10 f0 ff]
        res <- bb3.nums(1)
        
        # short (int16)
        bb4 = [00 01 00 08 00 10 01 00 00 ff ff 00]
        res <- bb4.nums(2)
        
        # long (int64)
        bb5 =  [00 10 00 00 00 00 00 00]
        bb5 <- [10 00 00 00 00 00 00 00]
        res <- bb5.nums(8)
        
        # sined int
        bb6 = [01 00 7f ff 80 01 ff ff]
        res <- bb6.nums(2, true)
        
        # .bits
        
        bb11 = [01 04]
        res <- bb11.bits()
        res <- 0x[80].bits()
        res <- 0b[11110000 01010101].bits()
        
        res <- 0x[ff00 1234 0000 0001 1000].blocks(2)
        res <- 0x[ff00 1234 0000 0001 1000].blocks(2).map(b -> b.bits())
        res <- 0x[1234]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = [
            -552,
            ['0x[a0]', '0x[01]', '0x[02]', '0x[03]', '0x[04]', '0x[05]', '0x[06]', '0x[07]', '0x[08]', '0x[09]', '0x[0a]', '0x[0b]', '0x[0c]', '0x[0d]', '0x[0e]', '0x[0f]'], 
            ['0x[a0 01]', '0x[02 03]', '0x[04 05]', '0x[06 07]', '0x[08 09]', '0x[0a 0b]', '0x[0c 0d]', '0x[0e 0f]'], 
            ['0x[a0 01 02 03]', '0x[04 05 06 07]', '0x[08 09 0a 0b]', '0x[0c 0d 0e 0f]'], 
            ['0x[00 00 a0]', '0x[01 02 03]', '0x[04 05 06]', '0x[07 08 09]', '0x[0a 0b 0c]', '0x[0d 0e 0f]'], 
            ['0x[00 00 00 00 a0]', '0x[01 02 03 04 05]', '0x[06 07 08 09 0a]', '0x[0b 0c 0d 0e 0f]'], 
            [0, 1, 2, 9, 16, 240, 255], [1, 8, 16, 256, 255, 65280], [4503599627370496, 1152921504606846976], [256, 32767, -32767, -1], 
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1], 
            ['0x[ff 00]', '0x[12 34]', '0x[00 00]', '0x[00 01]', '0x[10 00]'], 
            [
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
                [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 
            '0x[12 34]']
        self.assertEqual(exv, resv)

    def test_bytes_builtin_methods(self):
        ''' '''
        code = r'''
        res = []
        
        # .map
        
        bb = [10 0d 00 ff]
        
        f1 = x -> x + 1
        res <- bb.map(f1)
        
        res <- 0d[1 2 4 8 16 32].map(x -> x << 1)
        
        # .each
        
        bb3 = [1 2 3 4 5 6 7 8]
        
        r3 = []
        func evenInk(x)
            r3 <- (x % 2 == 0) ? x + 1 : x - 1
        
        bb3.each(evenInk)
        res <- r3
        
        # .reverse
        
        bb4 = [0 1 2 3 4 16 27 f8]
        res <- bb4.reverse()
        
        # .fold
        
        # sum
        res <- [0 1 0 1 0 1].fold(0, (s, v) -> s + v)
        # prod
        res <- [3 3 3].fold(1, (s, v) -> s * v)
        # fill list
        res <- [1 2 3 4 5].fold([], (s, v) -> (s <- v + 1000; s))
        
        # .replace
        
        bb6 = [1 2 3 2 4 5 7 1 2 9]
        res <- bb6.replace([1 2], [1f f5])
        
        res <- 0x[1 0 11 10 1 0 12 13].replace([1 0], [0 f])
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            '0x[11 0e 01 00]', '0x[02 04 08 10 20 40]', 
            [0, 3, 2, 5, 4, 7, 6, 9], '0x[f8 27 16 04 03 02 01 00]', 
            3, 27, [1001, 1002, 1003, 1004, 1005], 
            '0x[1f f5 03 02 04 05 07 1f f5 09]', '0x[00 0f 11 10 00 0f 12 13]']
        resv = resRepr(rvar.vals())
        # print(resv)
        self.assertEqual(exv, resv)

    def test_bytes_slice(self):
        ''' '''
        code = r'''
        res = []
        
        bb = [ff 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f]
        
        res <- bb[7:]
        
        res <- bb[:4]
        
        res <- bb[:]
        
        res <- bb[10:-1]
        
        a,b = 5,8
        res <- bb[a:b]
        
        res <- 0x[1 2 3 4 5 6 7 8][1:4]
        
        res <- 0b[00010010 00000101 00000110 00000111 00001000][-4:-1]
        
        res <- 0d[1 2 3 4 5 6 7 8][:]
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            '0x[06 07 08 09 0a 0b 0c 0d 0e 0f]', 
            '0x[ff 00 01 02]', 
            '0x[ff 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f]',
            '0x[09 0a 0b 0c 0d 0e]', '0x[04 05 06]',
            '0x[02 03 04]', '0x[05 06 07]', '0x[01 02 03 04 05 06 07 08]']
        resv = resRepr(rvar.vals())
        self.assertEqual(exv, resv)

    def test_bytes_no_spaces(self):
        ''' ob[11110000], 0x[ff00ffa8] '''
        code = r'''
        res = [-551]
        
        # bin
        res <- 0b[1111111100000000]
        res <- 0b[1111 0000 1010 0011]
        
        #hex
        res <- 0x[ff00]
        res <- 0x[1234 5678 ffff 0005]
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        exv = [
            -551,
            '0x[ff 00]', '0x[f0 a3]',
            '0x[ff 00]', '0x[12 34 56 78 ff ff 00 05]']
        resv = resRepr(rvar.vals())
        # for n in resv : print(n)
        self.assertEqual(exv, resv)

    def test_bytes_other_num_bases(self):
        ''' 0x[10] 0b[10], 0o[10], 0d[10] '''
        code = r'''
        res = [-555]
        
        bb16 = 0x[10 01 f0 0f ff 00]
        res <- (16, len(bb16))
        res <- bb16 
        
        bb = [10 01 00 ff]
        res <- (16, len(bb))
        res <- bb
        
        bb2 = 0b[00000001 00000010 00001111 00001000 10101010 10000000 11111111 00000000]
        res <- (2, len(bb2))
        res <- bb2
        
        
        bb8 = 0o[1 2 3 4 5 6 7 10 11 17 20 27 70 71 377 0]
        res <- (8, len(bb8))
        res <- bb8
        
        bb10 = 0d[1 2 3 4 9 11 12 19 20 21 29 80 81 90 100 109 110 111 199 200 240 250 255 0]
        res <- (10, len(bb10))
        res <- bb10
        
        # res.each(n -> print(~'{n[1]}'))
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        exv = [
            -555,
            (16, 6), '0x[10 01 f0 0f ff 00]', 
            (16, 4), '0x[10 01 00 ff]', 
            (2, 8), '0x[01 02 0f 08 aa 80 ff 00]', 
            (8, 16), '0x[01 02 03 04 05 06 07 08 09 0f 10 17 38 39 ff 00]', 
            (10, 24), '0x[01 02 03 04 09 0b 0c 13 14 15 1d 50 51 5a 64 6d 6e 6f c7 c8 f0 fa ff 00]']
        resv = resRepr(rvar.vals())
        self.assertEqual(exv, resv)

    def test_bytes_usage(self):
        ''' '''
        code = r'''
        res = []
        
        bb = [10 0d 00 ff]
        
        # iter by indexes
        res <- bb
        for i <- iter(4)
            res <- bb[i]
        
        # iter by sequence
        r1 = []
        for n <- bb
            r1 <- n
        
        res <- r1
        
        bigbytes = [
            00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f
            10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f
            20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f
            30 31 32 33 34 35 36 37 38 39 3a 3b 3c 3d 3e 3f
            40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f
            50 51 52 53 54 55 56 57 58 59 5a 5b 5c 5d 5e 5f
            60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 6e 6f
            70 71 72 73 74 75 76 77 78 79 7a 7b 7c 7d 7e 7f
            80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f
            90 91 92 93 94 95 96 97 98 99 9a 9b 9c 9d 9e 9f
            a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 aa ab ac ad ae af
            b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ba bb bc bd be bf
            c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 ca cb cc cd ce cf
            d0 d1 d2 d3 d4 d5 d6 d7 d8 d9 da db dc dd de df
            e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 ea eb ec ed ee ef
            f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 fa fb fc fd fe ff
        ]
        
        # diagonal from 0,0
        rbg1 = 0x[]
        # print(rbg1)
        # @debug before loop
        for i <- iter(16)
            rbg1 <- bigbytes[i*17]
        res <- rbg1
        
        # diagonal from 0,f
        rbg2 = 0x[]
        for i <- iter(1, 17)
            rbg2 <- bigbytes[i * 15]
        res <- rbg2
        
        # append bytes to bytes
        bbg2 = 0x[]
        for i <- iter(16)
            bbg2 <- 0x[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
        res <- ('bbg2-len', len(bbg2))
        
        # change bytes
        bbc = [00 00 00]
        for i <- iter(3)
            bbc[i] = 12 + 3 * i
        res <- bbc
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        exv = [
            '0x[10 0d 00 ff]', 16, 13, 0, 255, [16, 13, 0, 255],
            '0x[00 11 22 33 44 55 66 77 88 99 aa bb cc dd ee ff]', 
            '0x[0f 1e 2d 3c 4b 5a 69 78 87 96 a5 b4 c3 d2 e1 f0]', 
            ('bbg2-len', 256), '0x[0c 0f 12]']
        resv = resRepr(rvar.vals())
        self.assertEqual(exv, resv)

    def test_bytes_declaration(self):
        ''' '''
        # making test data
        # for i in range (16):
        #     print(' '.join([f'{(i*16+j):02x}' for j in range(16)]))
        
        code = r'''
        res = []
        
        # sugar - no prefix if many bytes
        bb = [10 0d 00 ff]
        
        # 1byte
        b1 = 0x[0]
        res <- b1
        
        # empty byte set
        res <- 0x[]
        
        # explicit declaration with prefix
        res <- 0x[1 2 3 4 5 6 7 8 9 a b c d e f ]
        
        # long byte field 16 x 16
        bigbytes = [
            00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f
            10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f
            20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f
            30 31 32 33 34 35 36 37 38 39 3a 3b 3c 3d 3e 3f
            40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f
            50 51 52 53 54 55 56 57 58 59 5a 5b 5c 5d 5e 5f
            60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 6e 6f
            70 71 72 73 74 75 76 77 78 79 7a 7b 7c 7d 7e 7f
            80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f
            90 91 92 93 94 95 96 97 98 99 9a 9b 9c 9d 9e 9f
            a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 aa ab ac ad ae af
            b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ba bb bc bd be bf
            c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 ca cb cc cd ce cf
            d0 d1 d2 d3 d4 d5 d6 d7 d8 d9 da db dc dd de df
            e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 ea eb ec ed ee ef
            f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 fa fb fc fd fe ff
        ]
        
        res <- ('bb-len', len(bigbytes))
        
        res <- bigbytes
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)

        # self.assertEqual(0, rvar.getVal())
        rvar = ctx.get('res').get()
        exv = [
            '0x[00]', '0x[]', '0x[01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f]', ('bb-len', 256), 
            ('0x['
                '00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f '
                '10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f '
                '20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f '
                '30 31 32 33 34 35 36 37 38 39 3a 3b 3c 3d 3e 3f '
                '40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f '
                '50 51 52 53 54 55 56 57 58 59 5a 5b 5c 5d 5e 5f '
                '60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 6e 6f '
                '70 71 72 73 74 75 76 77 78 79 7a 7b 7c 7d 7e 7f '
                '80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f '
                '90 91 92 93 94 95 96 97 98 99 9a 9b 9c 9d 9e 9f '
                'a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 aa ab ac ad ae af '
                'b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ba bb bc bd be bf '
                'c0 c1 c2 c3 c4 c5 c6 c7 c8 c9 ca cb cc cd ce cf '
                'd0 d1 d2 d3 d4 d5 d6 d7 d8 d9 da db dc dd de df '
                'e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 ea eb ec ed ee ef '
                'f0 f1 f2 f3 f4 f5 f6 f7 f8 f9 fa fb fc fd fe ff]')
            ]
        resv = resRepr(rvar.vals())
        self.assertEqual(exv, resv)


if __name__ == '__main__':
    main()


