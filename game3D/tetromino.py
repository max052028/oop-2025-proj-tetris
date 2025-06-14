import random
import math
from vector3d import Vector3D
from block import Block
from constants import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH
from constants import CYAN, YELLOW, PURPLE, GREEN, BLUE, ORANGE, WHITE

class Tetromino:
    # 定義不同的俄羅斯方塊形狀（3D版本）
    SHAPES = [
        # I形狀
        [Vector3D(0, 0, 0), Vector3D(0, 1, 0), Vector3D(0, 2, 0), Vector3D(0, 3, 0)],
        # O形狀
        [Vector3D(0, 0, 0), Vector3D(1, 0, 0), Vector3D(0, 1, 0), Vector3D(1, 1, 0)],
        # T形狀
        [Vector3D(0, 0, 0), Vector3D(-1, 0, 0), Vector3D(1, 0, 0), Vector3D(0, 1, 0)],
        # S形狀
        [Vector3D(0, 0, 0), Vector3D(-1, 0, 0), Vector3D(0, 1, 0), Vector3D(1, 1, 0)],
        # J形狀
        [Vector3D(0, 0, 0), Vector3D(0, 1, 0), Vector3D(0, 2, 0), Vector3D(-1, 2, 0)],
        # L形狀
        [Vector3D(0, 0, 0), Vector3D(0, 1, 0), Vector3D(0, 2, 0), Vector3D(1, 2, 0)],
        # 3D特殊形狀
        [Vector3D(0, 0, 0), Vector3D(1, 0, 0), Vector3D(0, 1, 0), Vector3D(0, 0, 1)],
    ]
    
    SHAPE_COLORS = {
        0: CYAN,    # I shape
        1: YELLOW,  # O shape
        2: PURPLE,  # T shape
        3: GREEN,   # S shape
        4: BLUE,    # J shape
        5: ORANGE,  # L shape
        6: WHITE,   # 3D special shape
    }
    
    def __init__(self):
        shape_index = random.randint(0, len(self.SHAPES) - 1)
        self.shape = self.SHAPES[shape_index]
        self.position = Vector3D(
            (GRID_WIDTH - 1) // 2,  # 對齊格線中心（支援奇數寬度）
            GRID_HEIGHT - 1,
            (GRID_DEPTH - 1) // 2
        )
        self.color = self.SHAPE_COLORS[shape_index]
        self.blocks = self.create_blocks()
    
    def create_blocks(self):
        blocks = []
        for offset in self.shape:
            pos = self.position + offset
            blocks.append(Block((pos.x + 0.5) * GRID_SIZE, (pos.y + 0.5) * GRID_SIZE, (pos.z + 0.5) * GRID_SIZE, self.color))
        return blocks
    
    def move(self, dx, dy, dz):
        self.position = self.position + Vector3D(dx, dy, dz)
        self.blocks = self.create_blocks()
        
    def rotate_x(self):
        new_shape = []
        for offset in self.shape:
            rotated = offset.rotate_x(math.pi / 2)
            new_shape.append(Vector3D(round(rotated.x), round(rotated.y), round(rotated.z)))
        self.shape = new_shape
        self.blocks = self.create_blocks()
    
    def rotate_y(self):
        new_shape = []
        for offset in self.shape:
            rotated = offset.rotate_y(math.pi / 2)
            new_shape.append(Vector3D(round(rotated.x), round(rotated.y), round(rotated.z)))
        self.shape = new_shape
        self.blocks = self.create_blocks()
        
    def rotate_z(self):
        new_shape = []
        for offset in self.shape:
            rotated = offset.rotate_z(math.pi / 2)
            new_shape.append(Vector3D(round(rotated.x), round(rotated.y), round(rotated.z)))
        self.shape = new_shape
        self.blocks = self.create_blocks()
