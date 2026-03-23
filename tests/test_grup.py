''' 
grup
'''


from unittest import TestCase, main

from tests.utils import *




            
class TestGrup(TestCase):


    def test_grup_blocked_outer(self):
        '''Test that items from context above of grup context 
            can't by taken directly by grup name. '''
        code = r'''
        
        res = []
        
        struct A a:int
        
        grup Ggg
            func a(x:int)
                A(x)
        
        # ok expression
        res <- Ggg.a(11)
        
        # incorrect hack
        res <- Ggg.A(22)
        
        # print('res = ', res)
        '''
        code = norm(code[1:])
        ex = tryParse(code)
        rCtx = rootContext()
        ctx = rCtx.moduleContext()
        
        with self.assertRaisesRegex(EvalErr, r"Grup Ggg doesn't have item.*") as contx:
            trydo(ex, ctx, 0)
            
        # print('>>TT err:', contx.exception)
        
        rvar = ctx.get('res').get()
        resv = resRepr(rvar.vals())
        # print(resv)
        exv = ['st@A{a: 11}']
        self.assertEqual(exv, resv)


    def test_grup_inner_var(self):
        ''' '''
        code = r'''
        
        res = []
        
        struct A a:int
        
        grup x
            
            struct B v:int
            
            enum E a:1, b, c, d
            
            func b(num:int)
                B(num)
            
            bInd=0
            
            func b()
                t = bInd
                x.bInd +=1
                B(t)
            
            word = 'item'
            
            func s(val:B)
                ~'{word}{val.v}'
        
        # test part
        res <- x.b(1).v
        
        x.bInd = 10
        res <- [x.b().v ; _ <- iter(3)]
        
        res <- x.s(x.b())
        res <- x.s(x.b())
        res <- x.s(x.b())
        
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
        exv = [1, [10, 11, 12], 'item13', 'item14', 'item15']
        self.assertEqual(exv, resv)

    def test_grup_definition(self):
        ''' '''
        code = r'''
        
        res = []
        
        struct A a:int
        
        grup Vect
            name: string = 'Vasya'
            num: int = 12345
            a1 = A(1)
            
            func chName(val:string)
                name = val
        
            func sumNum(val:int)
                num + val
        
            struct Point x:float, y:float
        
            func dist(a: Point, b: Point)
                2^/((b.x - a.x) ** 2 + (b.y - a.y) ** 2)
            
            func inst:Point dis(targ:Point)
                dist(targ, inst)
            
            func a:Point sum(b:Point)
                Point(a.x + b.x, a.y + b.y)
            
            enum en
                a = 10
                b
                c
                d
                e
                f
            
            grup Cons
                root2 = 1.4142135623730951
                root3 = 1.7320508075688772
                root5 = 2.23606797749979
            
            point0 = Point(0,0)
            point1: Point = Point(1,1)
            point100 = Point{x:100, y:100}
        
        # test part
        
        
        res <- Vect.name
        res <- Vect.num
        res <- Vect.a1
        
        Vect.chName('Petya')
        res <- Vect.name
        
        Vect.num = 23456
        v = Vect
        res <- v.num
        
        res <- v.point0
        res <- v.point1
        
        p0 = v.point0
        p1 = v.point1
        res <- v.dist(p0, p1)
        res <- p0.dis(p1)
        
        p5 = v.Point(5, -2)
        res <- p5
        
        res <- p1.sum(p5)
        
        pp0 = Vect.Point{}
        p6 = Vect.Point{x:3, y:4}
        res <- pp0.dis(p6)
        
        
        res <- Vect.en.a
        res <- Vect.Cons.root2
        
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
            'Vasya', 12345, 'st@A{a: 1}', 'Petya', 23456, 
            'st@Point{x: 0.0,y: 0.0}', 'st@Point{x: 1.0,y: 1.0}', 1.4142135623730951, 1.4142135623730951, 
            'st@Point{x: 5.0,y: -2.0}', 'st@Point{x: 6.0,y: -1.0}', 5.0, 10, 1.4142135623730951]
        self.assertEqual(exv, resv)


if __name__ == '__main__':
    main()

