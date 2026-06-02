from abc import ABC, abstractmethod
import numpy as np

class SignedShape:
    def __init__(self, sign:int, shape:'Shape'):
        self.sign = sign
        self.shape = shape


class Shape(ABC):
    @abstractmethod
    def is_positive(self, px0, py0, pz0):
        pass
    # this is an abstract method,
    # class Shape does not mean to define its usage
    def __neg__(self):
        return SignedShape(-1, self)
    def __pos__(self):
        return SignedShape(1, self)


# Planes
class Plane(Shape):                                   # Plane: Ax+By+Cz=D 
    def __init__(self, a, b, c, d):
        self.a = a 
        self.b = b 
        self.c = c
        self.d = d

    def is_positive(self, px0, py0, pz0):
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

    def is_positive(self, px0, py0, pz0):
        return px0 >= self.x0


class YPlane(Plane):                           # XPlane: By=D
    def __init__(self, b, d):
        super().__init__(0, b, 0, d)
        if b == 0:
            raise ValueError("there should be an B in By=D")
        self.y0 = self.d/self.b

    def is_positive(self, px0, py0, pz0):
        return py0 >= self.y0


class ZPlane(Plane):                           # XPlane: Cz=D
    def __init__(self, c, d):
        super().__init__(0, 0, c, d)
        if c == 0:
            raise ValueError("there should be an C in Cz=D")
        self.z0 = self.d/self.c  

    def is_positive(self, px0, py0, pz0):
        return pz0 >= self.z0


class Sphere(Shape):                                  # Sphere: (x-x0)^2+(y-y0)^2+(z-z0)^2=r^2
    def __init__(self, x0, y0, z0, r):
        self.x0 = x0 
        self.y0 = y0  
        self.z0 = z0 
        self.r = r
        self.r_sq = r**2

    def is_positive(self, px0, py0, pz0):
        return ((self.x0-px0)**2+(self.y0-py0)**2+(self.z0-pz0)**2) > self.r_sq
        # We define INSIDE as inside the real spherical surface


# Spheres
class OSphere(Sphere):                         # OSphere: x^2+y^2+z^2=r^2
    def __init__(self, r):
        super().__init__(0, 0, 0, r)

    def is_positive(self, px0, py0, pz0):
        return (px0**2+py0**2+pz0**2) > self.r_sq


class XSphere(Sphere):                         # XSphere: (x-x0)^2+y^2+z^2=r^2
    def __init__(self, x0, r):
        super().__init__(x0, 0, 0, r)

    def is_positive(self, px0, py0, pz0):
        return ((self.x0-px0)**2+py0**2+pz0**2) > self.r_sq 


class YSphere(Sphere):
    def __init__(self, y0, r):
        super().__init__(0, y0, 0, r)

    def is_positive(self, px0, py0, pz0):
        return (px0**2+(self.y0-py0)**2+pz0**2) > self.r_sq


class ZSphere(Sphere):
    def __init__(self, z0, r):
        super().__init__(0, 0, z0, r)

    def is_positive(self, px0, py0, pz0):
        return (px0**2+py0**2+(self.z0-pz0)**2) > self.r_sq


# Cylinders
class XCylinder(Shape):
    def __init__(self, y0, z0, r):
        self.y0 = y0
        self.z0 = z0
        self.r = r
        self.r_sq = r**2

    def is_positive(self, px0, py0, pz0):
        return ((self.y0-py0)**2+(self.z0-pz0)**2) > self.r_sq 


class YCylinder(Shape):
    def __init__(self, x0, z0, r):
        self.x0 = x0 
        self.z0 = z0
        self.r = r
        self.r_sq = r**2

    def is_positive(self, px0, py0, pz0):
        return ((self.x0-px0)**2+(self.z0-pz0)**2) > self.r_sq 


class ZCylinder(Shape): 
    def __init__(self, x0, y0, r):
        self.x0 = x0 
        self.y0 = y0
        self.r = r
        self.r_sq = r**2

    def is_positive(self, px0, py0, pz0):
        return ((self.x0-px0)**2+(self.y0-py0)**2) > self.r_sq 


# Cones, K/X, K/Y, K/Z 
# KX, KY, KZ are just special K/* 
class Cone(Shape):
    def __init__(self, x0, y0, z0, t_sq, k=1):
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0 
        self.t_sq = t_sq
        self.k = k
        self.t = t_sq ** 0.5
    @abstractmethod
    def is_positive(self, px0, py0, pz0):
        pass

class XCone(Cone):
    def __init__(self, x0, y0, z0, t_sq, k=1):
        super().__init__(x0, y0, z0, t_sq, k)
    def is_positive(self, px0, py0, pz0):
        lsq = (self.y0-py0)**2+(self.z0-pz0)**2 
        ursq = (self.t*(self.x0-px0))**2
        srsq = self.k*self.t*(self.x0-px0)
        return ( (srsq < 0) | ( (srsq>=0) & (ursq > lsq)))

class YCone(Cone):
    def __init__(self, x0, y0, z0, t_sq, k=1):
        super().__init__(x0, y0, z0, t_sq, k)
    def is_positive(self, px0, py0, pz0):
        lsq = (self.x0-px0)**2+(self.z0-pz0)**2 
        ursq = (self.t*(self.y0-py0))**2
        srsq = self.k*self.t*(self.y0-py0)
        return ( (srsq < 0) | ( (srsq>=0) & (ursq > lsq)))

class ZCone(Cone):
    def __init__(self, x0, y0, z0, t_sq, k=1):
        super().__init__(x0, y0, z0, t_sq, k)
    def is_positive(self, px0, py0, pz0):
        lsq = (self.x0-px0)**2+(self.y0-py0)**2 
        ursq = (self.t*(self.z0-pz0))**2
        srsq = self.k*self.t*(self.z0-pz0)
        return ( (srsq < 0) | ((srsq>=0) & (ursq > lsq)))

# Ellipse, Hyperboloid, Paraboloid...
class Ellipse(Shape):
    def __init__(self, A, B, C, D, E, F, G, x0, y0, z0):
        self.A = A
        self.B = B 
        self.C = C 
        self.D = D 
        self.E = E
        self.F = F
        self.G = G
        self.x0 = x0 
        self.y0 = y0 
        self.z0 = z0 

    def is_positive(self, px0, py0, pz0):
        dx = self.x0-px0
        dy = self.y0-py0
        dz = self.z0-pz0
        return (
                self.A*dx**2 + self.B*dy**2 + self.C*dz**2 +
                2*self.D*dx + 2*self.E*dy + 2*self.F*dz + self.G >0
                )

# universal func
class General(Shape):
    def __init__(self, A, B, C, D, E, F, G, H, J, K):
        self.A = A
        self.B = B 
        self.C = C 
        self.D = D 
        self.E = E
        self.F = F
        self.G = G
        self.H = H  
        self.J = J  
        self.K = K 

    def is_positive(self, px0, py0, pz0):
        return (
                self.A*px0**2 + self.B*py0**2 + self.C*pz0**2 +
                self.D*px0*py0 + self.E*py0*pz0 +self.F*px0*pz0 +
                self.G*px0 + self.H*py0 + self.J*pz0 +self.K > 0
                )


# Torus
class Torus(Shape):
    def __init__(self, x0, y0, z0, A, B, C):
        self.x0 = x0
        self.y0 = y0 
        self.z0 = z0
        self.A = A
        self.B = B
        self.C = C
    @abstractmethod
    def is_positive(self, px0, py0, pz0):
        pass 

class XTorus(Torus):
    def __init__(self, x0, y0, z0, A, B, C):
        super().__init__(x0, y0, z0, A, B, C)

    def is_positive(self, px0, py0, pz0):
        dx_sq = (self.x0-px0) ** 2
        dy_sq = (self.y0-py0) ** 2
        dz_sq = (self.z0-pz0) ** 2
        B_sq = self.B ** 2
        C_sq = self.C ** 2 
        return dx_sq/B_sq + (np.sqrt(dy_sq+dz_sq)-self.A)**2/C_sq - 1 > 0 

class YTorus(Torus):
    def __init__(self, x0, y0, z0, A, B, C):
        super().__init__(x0, y0, z0, A, B, C)

    def is_positive(self, px0, py0, pz0):
        dx_sq = (self.x0-px0) ** 2
        dy_sq = (self.y0-py0) ** 2
        dz_sq = (self.z0-pz0) ** 2
        B_sq = self.B ** 2
        C_sq = self.C ** 2 
        return dy_sq/B_sq + (np.sqrt(dx_sq+dz_sq)-self.A)**2/C_sq - 1 > 0

class ZTorus(Torus):
    def __init__(self, x0, y0, z0, A, B, C):
        super().__init__(x0, y0, z0, A, B, C)

    def is_positive(self, px0, py0, pz0):
        dx_sq = (self.x0-px0) ** 2
        dy_sq = (self.y0-py0) ** 2
        dz_sq = (self.z0-pz0) ** 2
        B_sq = self.B ** 2
        C_sq = self.C ** 2 
        return dz_sq/B_sq + (np.sqrt(dx_sq+dy_sq)-self.A)**2/C_sq - 1 > 0 

# Surfaces expressed by equations are OVER.
