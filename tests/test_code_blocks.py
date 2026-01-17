'''
Blocks of code - blocks by indent
for
    code...
if expr
    code...
def func()
    code...
match
    case_code...

'''

from unittest import TestCase, main
from context import Context
from eval import rootContext, moduleContext
from tests.utils import *


class TestCodeBlocks(TestCase):
    
    
    def test_blocks(self):
        ''' test base blocks, 
        loops, def of func, 
        inline loop - if
        loop - continue
        folding if- else lf - else
        '''
        
        code = r'''
        res = ['-0']
        
        func foo(x)
            2 * x
        
        r1 = []
        for a <- [1..7]
            if a > 2 && a < 6
                r1 <- foo(a)
        
        r2 = []
        for b <- [1..5] /: if b % 2 /: r2 <- b
        
        struct A a:int
        
        func st:A foo2(x)
            st.a + x
            
        func st:A foo3(x, y)
            st.a + (x * y)
        
        a1 = A(12)
        res <- a1.foo2(5)
        res <- a1.foo3(2,3)
        
        res <- r1
        res <- r2
        
        func fooo4(x)
            r = []
            if x == 1
                111
                for n <- [1,2]
                    for m <- [1,2,3]
                        r <- n * m
            else if x == 2
                222
                for n <- [6..8]
                    for m <- [4,5,6]
                        r <- n * m
            else if x == 3
                333
                for n <- [10..13]
                    for m <- [7,8]
                        r <- n * m
            
            else
                r <- 444
            r
        
        r3 = [fooo4(1), fooo4(2), fooo4(3), fooo4(4)]
        res <- r3
        
        func foo(a:int)
            if a > 5
                return a
            else
                return - a
        1
        res <- foo(2)
        
        r5 = 0
        for i <- [1..10]
            # print(i, r5)
            if i % 2 == 0
                continue
            r5 += i
        res <- r5 
        
        # print('r1', r1, r2, r3)
        # print('res', res)
        '''
        
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        trydo(ex, ctx)
        rvar = ctx.get('res').get()
        # print('tt>>', rvar.vals())
        exv = ['-0', 17, 18, [6, 8, 10], [1, 3, 5], 
               [[1, 2, 3, 2, 4, 6], [24, 30, 36, 28, 35, 42, 32, 40, 48], [70, 80, 77, 88, 84, 96, 91, 104], [444]], -2, 25]
        self.assertEqual(exv, rvar.vals())

