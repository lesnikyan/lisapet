''' '''


from unittest import TestCase, main
from context import Context
from eval import rootContext, moduleContext
from tests.utils import *


class TestBytes(TestCase):
    ''' '''
    


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
        
        res <- 0b[1 10 11 100 101 110 111 1000][-4:-1]
        
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
        
        bb2 = 0b[10 01 1111 1000 10101010 10000000 11111111 00000000]
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
            (2, 8), '0x[02 01 0f 08 aa 80 ff 00]', 
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


