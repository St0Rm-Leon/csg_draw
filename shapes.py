import numpy as np 
import matplotlib.pyplot as plt 

class Const:
    def __init__(self, num):
        self._CONST = num

    @property
    def get(self):
        return self._CONST 

class Plane:                                   # Plane: Ax+By+Cz=D 
    def __init__(self, a, b, c, d):
        self.a = a 
        self.b = b 
        self.c = c
        self.d = d

    def is_inside(self, px0, py0, pz0):
        return (px0*self.a + py0*self.b + pz0*self.c) >= self.d  
        # We define A*px0 + B*py0 + C*pz0 > d
        # as the point (px0,py0,pz0) is INSIDE the Plane
        # IN PRACTCE:


class XPlane(Plane):                           # XPlane: Ax=D
    def __init__(self, a, d):
        super().__init__(a, 0, 0, d)
        if a == 0:
            raise ValueError("there should be an A in Ax=D")
        self.x0 = self.d/self.a

    def is_inside(self, px0, py0, pz0):
        return px0 >= self.x0


class YPlane(Plane):                           # XPlane: By=D
    def __init__(self, b, d):
        super().__init__(0, b, 0, d)
        if b == 0:
            raise ValueError("there should be an B in By=D")
        self.y0 = self.d/self.b

    def is_inside(self, px0, py0, pz0):
        return py0 >= self.y0


class ZPlane(Plane):                           # XPlane: Cz=D
    def __init__(self, c, d):
        super().__init__(0, 0, c, d)
        if c == 0:
            raise ValueError("there should be an C in Cz=D")
        self.z0 = self.c/self.d  

    def is_inside(self, px0, py0, pz0):
        return pz0 >= self.z0


class Sphere:                                  # Sphere: (x-A)^2+(y-b)^2+(z-c)^2=r^2
    def __init__(self, x0, y0, z0, r):
        self.x0 = x0 
        self.y0 = y0  
        self.z0 = z0 
        self.r = r

class OSphere(Sphere):                         # OSphere: x^2+y^2+z^2=r^2
    def __init__(self, r):
        super().__init__(0, 0, 0, r)

class XSphere(Sphere):
    def __init__(self, x0, r):
        super().__init__(x0, 0, 0, r)


