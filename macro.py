import shapes as sp 


# RPP Rectangular Solid
class RPP(sp.Shape):
    def __init__(self, x0, x1, y0, y1, z0, z1):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.z0 = z0
        self.z1 = z1
    def is_positive(self, px0, py0, pz0):
        return ((px0 < self.x0) | (px0 > self.x1) |
                (py0 < self.y0) | (py0 > self.y1) |
                (pz0 < self.z0) | (pz0 > self.z1)
                )

# RCC Cylinder
class RCC(sp.Shape):
    def __init__(self, x0, y0, z0, Hx, Hy, Hz, R):
        self.x0 = x0 
        self.y0 = y0 
        self.z0 = z0 
        self.Hx = Hx 
        self.Hy = Hy 
        self.Hz = Hz 
        self.R = R 
        self.H_sq = Hx**2+Hy**2+Hz**2
        self.threshold = self.H_sq * self.R**2

    def is_positive(self, px0, py0, pz0):
        dx = px0-self.x0
        dy = py0-self.y0 
        dz = pz0-self.z0
        cross_sq = (self.Hy*dz-self.Hz*dy)**2
        cross_sq += (self.Hz*dx-self.Hx*dz)**2
        cross_sq += (self.Hx*dy-self.Hy*dx)**2
        dot = dx*self.Hx + dy*self.Hy + dz*self.Hz 
        return ((dot < 0) |
                (dot > self.H_sq) |
                (cross_sq > self.threshold)
                )

class BOX(sp.Shape):
    def __init__(self, x0, y0, z0, 
                 ax, ay, az,
                 bx, by, bz,
                 cx, cy, cz):
        self.x0 = x0
        self.y0 = y0
        self.z0 = z0 
        self.ax = ax 
        self.ay = ay 
        self.az = az 
        self.bx = bx 
        self.by = by 
        self.bz = bz
        self.cx = cx 
        self.cy = cy 
        self.cz = cz 
        self.a_sq = ax**2+ay**2+az**2
        self.b_sq = bx**2+by**2+bz**2
        self.c_sq = cx**2+cy**2+cz**2 

    def is_positive(self, px0, py0, pz0):
        dx = px0-self.x0 
        dy = py0-self.y0 
        dz = pz0-self.z0
        a_dot = dx*self.ax + dy*self.ay + dz*self.az
        b_dot = dx*self.bx + dy*self.by + dz*self.bz 
        c_dot = dx*self.cx + dy*self.cy + dz*self.cz 
        return ((a_dot < 0) | (a_dot > self.a_sq) |
                (b_dot < 0) | (b_dot > self.b_sq) |
                (c_dot < 0) | (c_dot > self.c_sq)
                )


class HEX(sp.Shape):
    def init(self, x0, y0, z0,
             hx, hy, hz,
             ax, ay, az,
             bx = None, by = None, bz = None,
             cx = None, cy = None, cz = None):
        self.x0 = x0 
        self.y0 = y0 
        self.z0 = z0 
        self.hx = hx 
        self.hy = hy 
        self.hz = hz 
        self.ax = ax 
        self.ay = ay 
        self.az = az
        if bx != None:
            self.bx = bx
        if by != None:
            self.by = by 
        if bz != None:
            self.bz = bz 
        if cx != None:
            self.cx = cx
        if cy != None:
            self.cy = cy 
        if cz != None:
            self.cz = cz
        self.h_sq = hx**2 + hy**2 + hz**2
        self.a_sq = ax**2 + ay**2 + az**2
        self.b_sq = self.bx**2 + self.by**2 + self.bz**2
        self.c_sq = self.cx**2 + self.cy**2 + self.cz**2
        # Note:
        # if bx ... == DEFAULT
        # Need Rodrigue's Rotation Formula in Parser
        
    def is_positive(self, px0, py0, pz0):
        dx = px0-self.x0 
        dy = py0-self.y0 
        dz = pz0-self.z0
        h_dot = dx*self.hx + dy*self.hy + dz*self.hz 
        a_dot = dx*self.ax + dy*self.ay + dz*self.az
        b_dot = dx*self.bx + dy*self.by + dz*self.bz 
        c_dot = dx*self.cx + dy*self.cy + dz*self.cz 
        return ((h_dot < 0) | (h_dot > self.h_sq) |
                (a_dot < -self.a_sq) | (a_dot > self.a_sq) |
                (b_dot < -self.b_sq) | (b_dot > self.b_sq) |
                (c_dot < -self.c_sq) | (c_dot > self.c_sq)
                )


class REC(sp.Shape):
    def __init__(self, x0, y0, z0,
                 hx, hy, hz,
                 ax, ay, az,
                 bx, by = None, bz = None):
        self.x0 = x0
        self.y0 = y0 
        self.z0 = z0 
        self.hx = hx 
        self.hy = hy 
        self.hz = hz 
        self.ax = ax 
        self.ay = ay 
        self.az = az 
        self.h_sq = hx**2 + hy**2 + hz**2
        self.a_sq = ax**2 + ay**2 + az**2
        self.bx = bx 
        self.b_sq = bx**2 
        self.is_b_vector = False 
        if (by != None) and (bz != None):           #by != None, therefore bz != None
            self.by = by 
            self.bz = bz 
            self.b_sq += self.by**2 + self.bz**2
            self.is_b_vector = True
            # is b a vector?
        self.b_over_a_sq = self.b_sq/self.a_sq 
        # Note:
        # if by,bz == None(DEFAULT)
        # self.bx is minor radius of the elliptic
    
    def is_positive(self, px0, py0, pz0):
        dx = px0-self.x0 
        dy = py0-self.y0 
        dz = pz0-self.z0
        d_sq = dx**2 + dy**2 + dz**2
        h_dot = dx*self.hx + dy*self.hy + dz*self.hz 
        a_dot = dx*self.ax + dy*self.ay + dz*self.az
        if self.is_b_vector:
            b_dot = dx*self.bx + dy*self.by + dz*self.bz
            b_dot_sq = b_dot**2
        else:
            b_dot_sq = ((d_sq - (h_dot**2)/self.h_sq - (a_dot**2)/self.a_sq) *
                self.b_sq) 
        return ((h_dot < 0) | (h_dot > self.h_sq) |
                (self.b_over_a_sq * (a_dot)**2 + 
                b_dot_sq/self.b_over_a_sq) > (self.a_sq*self.b_sq)
                )

