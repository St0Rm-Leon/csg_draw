class HEX:
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
            
