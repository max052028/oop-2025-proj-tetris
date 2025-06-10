import pygame
import numpy as np
import math
import random
from pygame.locals import *
from game2D.menu import Menu
from game2D.leaderboard import Leaderboard

# 初始化Pygame
pygame.init()
pygame.mixer.init()
# 常數設定
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_DEPTH = 10

# 顏色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
TRANSPARENT_BLUE = (100, 150, 255, 60)

COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]

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

class Camera:
    def __init__(self):
        self.target = Vector3D(GRID_WIDTH * GRID_SIZE / 2, GRID_HEIGHT * GRID_SIZE / 2, GRID_DEPTH * GRID_SIZE / 2)
        self.distance = 800
        self.rotation_x = -0.3  # 向下看一點
        self.rotation_y = 0.5
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        
        self.update_position()
    
    def handle_mouse_wheel(self, event):
        if event.y > 0:
            self.distance = max(100, self.distance - 50)  # 不要太近避免進入堆疊區
        elif event.y < 0:
            self.distance += 50
        self.update_position()

    def update_position(self):
        # 圍繞目標點旋轉
        x = self.distance * math.cos(self.rotation_x) * math.sin(self.rotation_y)
        y = self.distance * math.sin(self.rotation_x)
        z = self.distance * math.cos(self.rotation_x) * math.cos(self.rotation_y)
        
        self.position = Vector3D(
            self.target.x + x,
            self.target.y + y,
            self.target.z + z
        )
    
    def project(self, point):
        # 3D到2D投影
        relative = point - self.position
        
        # 計算攝像機的觀察方向
        forward = (self.target - self.position).normalize()
        up = Vector3D(0, 1, 0)
        right = Vector3D(
            forward.y * up.z - forward.z * up.y,
            forward.z * up.x - forward.x * up.z,
            forward.x * up.y - forward.y * up.x
        ).normalize()
        up = Vector3D(
            right.y * forward.z - right.z * forward.y,
            right.z * forward.x - right.x * forward.z,
            right.x * forward.y - right.y * forward.x
        ).normalize()
        
        # 轉換到攝像機座標系
        x = relative.x * right.x + relative.y * right.y + relative.z * right.z
        y = relative.x * up.x + relative.y * up.y + relative.z * up.z
        z = relative.x * forward.x + relative.y * forward.y + relative.z * forward.z
        
        if z <= 0:
            z = 0.001
        
        factor = 800 / z
        screen_x = int(x * factor + WINDOW_WIDTH // 2)
        screen_y = int(-y * factor + WINDOW_HEIGHT // 2)
        
        return (screen_x, screen_y, z)
    
    def handle_mouse(self, mouse_buttons, mouse_pos):
        if mouse_buttons[0]:  # 左鍵按下
            if not self.mouse_dragging:
                self.mouse_dragging = True
                self.last_mouse_pos = mouse_pos
            else:
                dx = mouse_pos[0] - self.last_mouse_pos[0]
                dy = mouse_pos[1] - self.last_mouse_pos[1]

                self.rotation_y -= dx * 0.01
                self.rotation_x += dy * 0.01  # 顛倒垂直旋轉

                self.rotation_x = max(-math.pi/2 + 0.1, min(math.pi/2 - 0.1, self.rotation_x))
                self.last_mouse_pos = mouse_pos
                self.update_position()
        else:
            self.mouse_dragging = False

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
        [Vector3D(0, 0, 0), Vector3D(1, 0, 0), Vector3D(0, 1, 0), Vector3D(-1, 1, 0)],
        # Z形狀
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
        4: RED,     # Z shape
        5: BLUE,    # J shape
        6: ORANGE,  # L shape
        7: WHITE,   # 3D special shape
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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("3D Tetris")
        self.clock = pygame.time.Clock()
        self.camera = Camera()
        self.menu = Menu(self.screen)
        self.leaderboard = Leaderboard(self.screen)
        self.grid = np.zeros((GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH), dtype=int)
        self.placed_blocks = []
        self.current_tetromino = Tetromino()
        self.fall_time = 0
        self.fall_speed = 500
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.keys_pressed = set()
        # Load and play background music
        pygame.mixer.music.load("game3D/background_music.mp3")  # Replace with your music file name
        pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Play the music in a loop
        
    def is_valid_position(self, tetromino):
        for offset in tetromino.shape:
            pos = tetromino.position + offset
            x, y, z = int(pos.x), int(pos.y), int(pos.z)
            
            # 檢查邊界
            if x < 0 or x >= GRID_WIDTH or y < 0 or z < 0 or z >= GRID_DEPTH:
                return False
            
            # 檢查是否與已放置的方塊重疊
            if y < GRID_HEIGHT and self.grid[x, y, z] != 0:
                return False
        
        return True
    
    def place_tetromino(self):
        for offset in self.current_tetromino.shape:
            pos = self.current_tetromino.position + offset
            x, y, z = int(pos.x), int(pos.y), int(pos.z)
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and 0 <= z < GRID_DEPTH:
                self.grid[x, y, z] = 1
                block = Block((x + 0.5) * GRID_SIZE, (y + 0.5) * GRID_SIZE, (z + 0.5) * GRID_SIZE, self.current_tetromino.color)
                self.placed_blocks.append(block)
    
    def clear_lines(self):
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if np.all(self.grid[:, y, :] == 1):
                # 清除這一層
                self.grid[:, y, :] = 0
                # 移除對應的方塊
                self.placed_blocks = [block for block in self.placed_blocks 
                                    if int(block.position.y / GRID_SIZE) != y]
                
                # 讓上面的方塊下降
                for above_y in range(y + 1, GRID_HEIGHT):
                    self.grid[:, above_y - 1, :] = self.grid[:, above_y, :]
                    self.grid[:, above_y, :] = 0
                
                # 更新方塊位置
                for block in self.placed_blocks:
                    if block.position.y > y * GRID_SIZE:
                        block.position.y -= GRID_SIZE
                
                lines_cleared += 1
        
        if lines_cleared > 0:
            self.score += lines_cleared * 100
    
    def draw_game_area_boundary(self):
        """繪製半透明的遊戲區域邊界"""
        # 創建半透明表面
        boundary_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # 繪製底面邊界
        bottom_vertices = [
            self.camera.project(Vector3D(0, 0, 0))[0:2],
            self.camera.project(Vector3D(GRID_WIDTH * GRID_SIZE, 0, 0))[0:2],
            self.camera.project(Vector3D(GRID_WIDTH * GRID_SIZE, 0, GRID_DEPTH * GRID_SIZE))[0:2],
            self.camera.project(Vector3D(0, 0, GRID_DEPTH * GRID_SIZE))[0:2]
        ]
        pygame.draw.polygon(boundary_surface, TRANSPARENT_BLUE, bottom_vertices)
        
        # 繪製邊框線
        boundary_lines = [
            # 底面邊框
            (Vector3D(0, 0, 0), Vector3D(GRID_WIDTH * GRID_SIZE, 0, 0)),
            (Vector3D(GRID_WIDTH * GRID_SIZE, 0, 0), Vector3D(GRID_WIDTH * GRID_SIZE, 0, GRID_DEPTH * GRID_SIZE)),
            (Vector3D(GRID_WIDTH * GRID_SIZE, 0, GRID_DEPTH * GRID_SIZE), Vector3D(0, 0, GRID_DEPTH * GRID_SIZE)),
            (Vector3D(0, 0, GRID_DEPTH * GRID_SIZE), Vector3D(0, 0, 0)),
            # 垂直邊框
            (Vector3D(0, 0, 0), Vector3D(0, GRID_HEIGHT * GRID_SIZE, 0)),
            (Vector3D(GRID_WIDTH * GRID_SIZE, 0, 0), Vector3D(GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE, 0)),
            (Vector3D(GRID_WIDTH * GRID_SIZE, 0, GRID_DEPTH * GRID_SIZE), Vector3D(GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE, GRID_DEPTH * GRID_SIZE)),
            (Vector3D(0, 0, GRID_DEPTH * GRID_SIZE), Vector3D(0, GRID_HEIGHT * GRID_SIZE, GRID_DEPTH * GRID_SIZE)),
        ]
        
        for start, end in boundary_lines:
            start_2d = self.camera.project(start)[0:2]
            end_2d = self.camera.project(end)[0:2]
            pygame.draw.line(boundary_surface, LIGHT_GRAY, start_2d, end_2d, 2)
        
        self.screen.blit(boundary_surface, (0, 0))
    
    def draw_block_with_faces(self, block):
        """繪製方塊的可見面"""
        visible_faces = block.get_face_vertices(self.camera)
        
        # 按深度排序
        visible_faces.sort(key=lambda x: x[2], reverse=True)
        
        for face_name, vertices, depth in visible_faces:
            # 投影頂點
            projected_vertices = [self.camera.project(v)[0:2] for v in vertices]
            
            # 計算面的顏色（添加深度陰影）
            base_color = block.color
            if face_name in ['back', 'bottom', 'left']:
                # 背面、底面、左面稍微暗一些
                shadow_factor = 0.7
                color = (
                    int(base_color[0] * shadow_factor),
                    int(base_color[1] * shadow_factor),
                    int(base_color[2] * shadow_factor)
                )
            else:
                color = base_color
            
            # 繪製面
            pygame.draw.polygon(self.screen, color, projected_vertices)
            pygame.draw.polygon(self.screen, BLACK, projected_vertices, 2)
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        directions = [K_w, K_a, K_s, K_d]
        for key in directions:
            if keys[key] and key not in self.keys_pressed:
                dir = self.get_movement_direction(key)
                dx, dz = round(dir.x), round(dir.z)
                test = Tetromino()
                test.shape = self.current_tetromino.shape[:]
                test.position = self.current_tetromino.position + Vector3D(dx, 0, dz)
                test.color = self.current_tetromino.color
                if self.is_valid_position(test):
                    self.current_tetromino.move(dx, 0, dz)

        # Q旋轉X軸，E旋轉Y軸
        if keys[K_q] and K_q not in self.keys_pressed:
            old_shape = self.current_tetromino.shape[:]
            self.current_tetromino.rotate_x()
            if not self.is_valid_position(self.current_tetromino):
                self.current_tetromino.shape = old_shape
                self.current_tetromino.blocks = self.current_tetromino.create_blocks()

        if keys[K_e] and K_e not in self.keys_pressed:
            old_shape = self.current_tetromino.shape[:]
            self.current_tetromino.rotate_y()
            if not self.is_valid_position(self.current_tetromino):
                self.current_tetromino.shape = old_shape
                self.current_tetromino.blocks = self.current_tetromino.create_blocks()

        # 空白鍵快速下降
        if keys[K_SPACE]:
            test = Tetromino()
            test.shape = self.current_tetromino.shape[:]
            test.position = self.current_tetromino.position + Vector3D(0, -1, 0)
            test.color = self.current_tetromino.color
            if self.is_valid_position(test):
                self.current_tetromino.move(0, -1, 0)

        self.keys_pressed = {key for key in [K_a, K_d, K_w, K_s, K_q, K_e] if keys[key]}
    
    def update(self, dt):
        self.fall_time += dt
        
        if self.fall_time >= self.fall_speed:
            # 嘗試讓方塊下降
            test_tetromino = Tetromino()
            test_tetromino.shape = self.current_tetromino.shape[:]
            test_tetromino.position = Vector3D(
                self.current_tetromino.position.x,
                self.current_tetromino.position.y - 1,
                self.current_tetromino.position.z
            )
            test_tetromino.color = self.current_tetromino.color
            
            if self.is_valid_position(test_tetromino):
                self.current_tetromino.move(0, -1, 0)
            else:
                # 方塊到底了，放置並創建新方塊
                self.place_tetromino()
                self.clear_lines()
                self.current_tetromino = Tetromino()
                
                # 檢查遊戲結束
                if not self.is_valid_position(self.current_tetromino):
                    return False  # 遊戲結束
            
            self.fall_time = 0
        
        return True
    
    def get_movement_direction(self, key):
        forward = (self.camera.target - self.camera.position).normalize()
        forward.y = 0
        forward = forward.normalize()
        right = Vector3D(-forward.z, 0, forward.x)  # 修正 right 為右手系（使 A 左、D 右）

        if key == K_w:
            return forward
        elif key == K_s:
            return forward * -1
        elif key == K_a:
            return right * -1
        elif key == K_d:
            return right
        return Vector3D(0, 0, 0)

    def draw(self):
        self.screen.fill(BLACK)
        
        # 繪製遊戲區域邊界
        self.draw_game_area_boundary()
        
        # 收集所有方塊並按深度排序
        all_blocks = []
        
        # 添加已放置的方塊
        for block in self.placed_blocks:
            depth = self.camera.project(block.position)[2]
            all_blocks.append((block, depth))
        
        # 添加當前方塊
        for block in self.current_tetromino.blocks:
            depth = self.camera.project(block.position)[2]
            all_blocks.append((block, depth))
        
        # 按深度排序（遠的先畫）
        all_blocks.sort(key=lambda x: x[1], reverse=True)
        
        # 繪製所有方塊
        for block, depth in all_blocks:
            self.draw_block_with_faces(block)
        
        # 繪製UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        controls_text = [
            "Controls:",
            "WASD: Move Block",
            "Q: Rotate X-axis",
            "E: Rotate Y-axis",
            "Space: Fast Drop",
            "Mouse: Drag to rotate camera"
        ]
        
        for i, text in enumerate(controls_text):
            rendered = pygame.font.Font(None, 24).render(text, True, WHITE)
            self.screen.blit(rendered, (10, 50 + i * 25))
        
        pygame.display.flip()
        
    def get_player_name(self):
        name = ""
        font = pygame.font.Font(None, 36)
        input_active = True

        while input_active:
            self.screen.fill(BLACK)
            prompt_text = font.render("Enter your name:", True, WHITE)
            self.screen.blit(prompt_text, (WINDOW_WIDTH // 2 - prompt_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))

            name_text = font.render(name, True, WHITE)
            self.screen.blit(name_text, (WINDOW_WIDTH // 2 - name_text.get_width() // 2, WINDOW_HEIGHT // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:  # Press Enter to confirm
                        input_active = False
                    elif event.key == K_BACKSPACE:  # Press Backspace to delete a character
                        name = name[:-1]
                    else:
                        name += event.unicode  # Add the typed character to the name

        return name
    
    def reset_game(self):
        self.grid = np.zeros((GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH), dtype=int)
        self.placed_blocks = []
        self.current_tetromino = Tetromino()
        self.fall_time = 0
        self.score = 0

    def run(self):
        running = True
        in_menu = True
        game_active = False
        in_leaderboard = False

        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEWHEEL:
                    self.camera.handle_mouse_wheel(event)

            if in_menu:
                self.menu.draw()
                selected_option = self.menu.handle_input()
                if selected_option == 0:  # Start Game
                    in_menu = False
                    game_active = True
                elif selected_option == 1:  # Leaderboard
                    in_menu = False
                    in_leaderboard = True
                elif selected_option == 2:  # Quit
                    running = False
            elif in_leaderboard:
                self.leaderboard.draw()
                if self.leaderboard.handle_input():
                    in_leaderboard = False
                    in_menu = True
            elif game_active:
                mouse_buttons = pygame.mouse.get_pressed()
                mouse_pos = pygame.mouse.get_pos()

                self.camera.handle_mouse(mouse_buttons, mouse_pos)
                self.handle_input()
                game_active = self.update(dt)
                self.draw()

                if not game_active:
                    player_name = self.get_player_name()  # Prompt for player name
                    self.leaderboard.save_score(player_name, self.score)  # Save score to leaderboard
                    pygame.time.wait(500)
                    self.reset_game() 
                    in_menu = True
                    
        pygame.mixer.music.stop()
        pygame.quit()
        
if __name__ == "__main__":
    game = Game()
    game.run()