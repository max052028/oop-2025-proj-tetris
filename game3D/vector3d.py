import math

class Vector3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    
    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector3D(self.x/length, self.y/length, self.z/length)
        return Vector3D(0, 0, 0)
    
    def rotate_x(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector3D(
            self.x,
            self.y * cos_a - self.z * sin_a,
            self.y * sin_a + self.z * cos_a
        )
    
    def rotate_y(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector3D(
            self.x * cos_a + self.z * sin_a,
            self.y,
            -self.x * sin_a + self.z * cos_a
        )
        
    def rotate_z(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        return Vector3D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a,
            self.z
        )