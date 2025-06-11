from vector3d import Vector3D
from constants import GRID_SIZE
class Block:
    def __init__(self, x, y, z, color):
        self.position = Vector3D(x, y, z)
        self.color = color
    
    def get_face_vertices(self, camera):
        """獲取立方體的面頂點，按深度排序只渲染最前面的面"""
        size = GRID_SIZE // 2

        # 定義立方體的6個面
        faces = {
            'front': [
                Vector3D(self.position.x - size, self.position.y - size, self.position.z + size),
                Vector3D(self.position.x + size, self.position.y - size, self.position.z + size),
                Vector3D(self.position.x + size, self.position.y + size, self.position.z + size),
                Vector3D(self.position.x - size, self.position.y + size, self.position.z + size)
            ],
            'back': [
                Vector3D(self.position.x + size, self.position.y - size, self.position.z - size),
                Vector3D(self.position.x - size, self.position.y - size, self.position.z - size),
                Vector3D(self.position.x - size, self.position.y + size, self.position.z - size),
                Vector3D(self.position.x + size, self.position.y + size, self.position.z - size)
            ],
            'left': [
                Vector3D(self.position.x - size, self.position.y - size, self.position.z - size),
                Vector3D(self.position.x - size, self.position.y - size, self.position.z + size),
                Vector3D(self.position.x - size, self.position.y + size, self.position.z + size),
                Vector3D(self.position.x - size, self.position.y + size, self.position.z - size)
            ],
            'right': [
                Vector3D(self.position.x + size, self.position.y - size, self.position.z + size),
                Vector3D(self.position.x + size, self.position.y - size, self.position.z - size),
                Vector3D(self.position.x + size, self.position.y + size, self.position.z - size),
                Vector3D(self.position.x + size, self.position.y + size, self.position.z + size)
            ],
            'top': [
                Vector3D(self.position.x - size, self.position.y + size, self.position.z + size),
                Vector3D(self.position.x + size, self.position.y + size, self.position.z + size),
                Vector3D(self.position.x + size, self.position.y + size, self.position.z - size),
                Vector3D(self.position.x - size, self.position.y + size, self.position.z - size)
            ],
            'bottom': [
                Vector3D(self.position.x - size, self.position.y - size, self.position.z - size),
                Vector3D(self.position.x + size, self.position.y - size, self.position.z - size),
                Vector3D(self.position.x + size, self.position.y - size, self.position.z + size),
                Vector3D(self.position.x - size, self.position.y - size, self.position.z + size)
            ]
        }

        # 計算每個面的深度和法向量，只渲染面向攝像機的面
        visible_faces = []
        camera_dir = (self.position - camera.position).normalize()

        face_normals = {
            'front': Vector3D(0, 0, 1),
            'back': Vector3D(0, 0, -1),
            'left': Vector3D(-1, 0, 0),
            'right': Vector3D(1, 0, 0),
            'top': Vector3D(0, 1, 0),
            'bottom': Vector3D(0, -1, 0)
        }

        for face_name, vertices in faces.items():
            normal = face_normals[face_name]
            # 計算法向量與攝像機方向的點積
            dot_product = normal.x * camera_dir.x + normal.y * camera_dir.y + normal.z * camera_dir.z

            if dot_product < 0:  # 面向攝像機
                center = vertices[0] + vertices[1] + vertices[2] + vertices[3]
                center = Vector3D(center.x / 4, center.y / 4, center.z / 4)
                try:
                    depth = camera.project(center)[2]
                    visible_faces.append((face_name, vertices, depth))
                except:
                    continue  # 忽略投影失敗者

        return visible_faces
        
        # 計算每個面的深度和法向量，只渲染面向攝像機的面
        visible_faces = []
        camera_dir = (self.position - camera.position).normalize()
        
        face_normals = {
            'front': Vector3D(0, 0, 1),
            'back': Vector3D(0, 0, -1),
            'left': Vector3D(-1, 0, 0),
            'right': Vector3D(1, 0, 0),
            'top': Vector3D(0, 1, 0),
            'bottom': Vector3D(0, -1, 0)
        }
        
        for face_name, vertices in faces.items():
            normal = face_normals[face_name]
            # 計算法向量與攝像機方向的點積
            dot_product = normal.x * camera_dir.x + normal.y * camera_dir.y + normal.z * camera_dir.z
            
            if dot_product > 0:  # 面向攝像機
                center = vertices[0] + vertices[1] + vertices[2] + vertices[3]
                center = Vector3D(center.x/4, center.y/4, center.z/4)
                depth = camera.project(center)[2]
                visible_faces.append((face_name, vertices, depth))
        
        return visible_faces