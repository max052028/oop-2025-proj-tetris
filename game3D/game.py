import pygame
import numpy as np
from pygame.locals import *
from vector3d import Vector3D
from block import Block
from menu import Menu
from leaderboard import Leaderboard
from camera import Camera
from tetromino import Tetromino
from constants import WINDOW_HEIGHT, WINDOW_WIDTH, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH
from constants import BLACK, WHITE, LIGHT_GRAY, TRANSPARENT_BLUE, RED, GREEN, BLUE

class Game:
    def __init__(self, settings=None):
        if settings:
            width = settings.get("screen_width", 800)
            height = settings.get("screen_height", 600)
            volume = settings.get("volume", 0.5)
        else:
            width = WINDOW_WIDTH
            height = WINDOW_HEIGHT
            volume = 0.5
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("3D Tetris")
        self.clock = pygame.time.Clock()
        self.camera = Camera(screen_width=width, screen_height=height)
        self.menu = Menu(self.screen)
        self.leaderboard = Leaderboard(self.screen)
        self.grid = np.zeros((GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH), dtype=int)
        self.placed_blocks = []
        self.current_tetromino = Tetromino()
        self.fall_time = 0
        self.fall_speed = 750
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.keys_pressed = set()
        # Load and play background music
        pygame.mixer.music.load("game3D/background_music.mp3")  # Replace with your music file name
        pygame.mixer.music.set_volume(volume)  # Set volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Play the music in a loop
        self.settings = settings

    def apply_settings(self, settings):
        width = settings.get("screen_width", 800)
        height = settings.get("screen_height", 600)
        volume = settings.get("volume", 0.5)
        self.screen = pygame.display.set_mode((width, height))
        pygame.mixer.music.set_volume(volume)
        self.camera.set_screen_size(width, height)
        self.settings = settings
    
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
    
    def draw_axes(self):
        """Draw the X, Y, and Z axes for orientation."""
        axis_length = GRID_SIZE * max(GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH)

        # Define the axes
        axes = {
            "X": (Vector3D(0, 0, 0), Vector3D(axis_length, 0, 0), RED),
            "Y": (Vector3D(0, 0, 0), Vector3D(0, axis_length, 0), GREEN),
            "Z": (Vector3D(0, 0, 0), Vector3D(0, 0, axis_length), BLUE),
        }

        for axis, (start, end, color) in axes.items():
            # Project the start and end points of the axis
            start_2d = self.camera.project(start)[0:2]
            end_2d = self.camera.project(end)[0:2]

            # Draw the axis line
            pygame.draw.line(self.screen, color, start_2d, end_2d, 2)

            # Draw the axis label
            label_position = self.camera.project(end)[0:2]
            font = pygame.font.Font(None, 24)
            label = font.render(axis, True, color)
            self.screen.blit(label, (label_position[0] - 10, label_position[1] - 10))
    
    def get_ghost_tetromino(self, grid):
        # 複製目前方塊
        ghost = Tetromino()
        ghost.shape = self.current_tetromino.shape[:]
        ghost.position = Vector3D(
            self.current_tetromino.position.x,
            self.current_tetromino.position.y,
            self.current_tetromino.position.z
        )
        ghost.color = (180, 180, 180)  # 用灰色顯示預置
        # 一直往下移動直到不能再下
        while True:
            test = Tetromino()
            test.shape = ghost.shape[:]
            test.position = Vector3D(ghost.position.x, ghost.position.y - 1, ghost.position.z)
            test.color = ghost.color
            if self.is_valid_position(test):
                ghost.position.y -= 1
            else:
                break
        ghost.blocks = ghost.create_blocks()
        return ghost

    def draw(self):
        self.screen.fill(BLACK)
        # Draw the game area boundary
        self.draw_game_area_boundary()
        # Draw the XYZ axes
        self.draw_axes()
        # Collect and sort all blocks by depth
        all_blocks = []
        # Add placed blocks
        for block in self.placed_blocks:
            depth = self.camera.project(block.position)[2]
            all_blocks.append((block, depth))
        # Add ghost tetromino blocks
        ghost = self.get_ghost_tetromino(self.grid)
        for block in ghost.blocks:
            depth = self.camera.project(block.position)[2]
            all_blocks.append((block, depth, True))  # True 代表 ghost
        # Add current tetromino blocks
        for block in self.current_tetromino.blocks:
            depth = self.camera.project(block.position)[2]
            all_blocks.append((block, depth, False))
        # Sort blocks by depth (farther blocks first)
        all_blocks.sort(key=lambda x: x[1], reverse=True)
        # Draw all blocks
        for item in all_blocks:
            if len(item) == 3:
                block, depth, is_ghost = item
            else:
                block, depth = item
                is_ghost = False
            if is_ghost:
                self.draw_block_with_faces(block, ghost=True)
            else:
                self.draw_block_with_faces(block)
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        controls_text = [
            "Controls:",
            "WASD: Move Block",
            "Q: Rotate X-axis",
            "E: Rotate Y-axis",
            "R: Rotate Z-axis",
            "Space: Fast Drop",
            "Mouse: Drag to rotate camera"
        ]
        for i, text in enumerate(controls_text):
            rendered = pygame.font.Font(None, 24).render(text, True, WHITE)
            self.screen.blit(rendered, (10, 50 + i * 25))
        pygame.display.flip()

    def draw_block_with_faces(self, block, ghost=False):
        """繪製方塊的可見面"""
        visible_faces = block.get_face_vertices(self.camera)
        visible_faces.sort(key=lambda x: x[2], reverse=True)
        for face_name, vertices, depth in visible_faces:
            projected_vertices = [self.camera.project(v)[0:2] for v in vertices]
            base_color = block.color
            color = (200, 200, 200) if ghost else base_color
            if face_name in ['back', 'bottom', 'left']:
                shadow_factor = 0.7
                color = (
                    int(color[0] * shadow_factor),
                    int(color[1] * shadow_factor),
                    int(color[2] * shadow_factor)
                )
            if ghost:
                # 半透明繪製 ghost
                ghost_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                pygame.draw.polygon(ghost_surface, (color[0], color[1], color[2], 80), projected_vertices)
                self.screen.blit(ghost_surface, (0, 0))
                pygame.draw.polygon(self.screen, (180, 180, 180), projected_vertices, 1)
            else:
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

        # Q/E 基於鏡頭朝向的左右旋轉
        if (keys[K_q] or keys[K_e]) and (K_q not in self.keys_pressed and K_e not in self.keys_pressed):
            # 取得鏡頭 forward 向量
            forward = (self.camera.target - self.camera.position).normalize()
            # 判斷鏡頭主要朝向哪個軸
            abs_x, abs_y, abs_z = abs(forward.x), abs(forward.y), abs(forward.z)
            if abs_x >= abs_y and abs_x >= abs_z:
                # 朝向X軸，Q/E繞X旋轉
                if forward.x > 0:
                    if keys[K_q]:
                        self.try_rotate('x', 1)
                    elif keys[K_e]:
                        self.try_rotate('x', -1)
                else:
                    if keys[K_q]:
                        self.try_rotate('x', -1)
                    elif keys[K_e]:
                        self.try_rotate('x', 1)
            elif abs_z >= abs_x and abs_z >= abs_y:
                # 朝向Z軸，Q/E繞Z旋轉
                if forward.z > 0:
                    if keys[K_q]:
                        self.try_rotate('z', 1)
                    elif keys[K_e]:
                        self.try_rotate('z', -1)
                else:
                    if keys[K_q]:
                        self.try_rotate('z', -1)
                    elif keys[K_e]:
                        self.try_rotate('z', 1)
            else:
                # 朝向Y軸，Q/E繞Y旋轉
                if forward.y > 0:
                    if keys[K_q]:
                        self.try_rotate('y', 1)
                    elif keys[K_e]:
                        self.try_rotate('y', -1)
                else:
                    if keys[K_q]:
                        self.try_rotate('y', -1)
                    elif keys[K_e]:
                        self.try_rotate('y', 1)
        # 空白鍵快速下降
        if keys[K_SPACE]:
            test = Tetromino()
            test.shape = self.current_tetromino.shape[:]
            test.position = self.current_tetromino.position + Vector3D(0, -1, 0)
            test.color = self.current_tetromino.color
            if self.is_valid_position(test):
                self.current_tetromino.move(0, -1, 0)
                self.score += 1
        self.keys_pressed = {key for key in [K_a, K_d, K_w, K_s, K_q, K_e, K_r] if keys[key]}
    
    def try_rotate(self, axis, direction):
        old_shape = self.current_tetromino.shape[:]
        # 修正旋轉方向，將 direction 取反
        direction = -direction
        if axis == 'x':
            if direction == 1:
                self.current_tetromino.rotate_x()
            else:
                for _ in range(3):
                    self.current_tetromino.rotate_x()
        elif axis == 'y':
            if direction == 1:
                self.current_tetromino.rotate_y()
            else:
                for _ in range(3):
                    self.current_tetromino.rotate_y()
        elif axis == 'z':
            if direction == 1:
                self.current_tetromino.rotate_z()
            else:
                for _ in range(3):
                    self.current_tetromino.rotate_z()
        if not self.is_valid_position(self.current_tetromino):
            self.current_tetromino.shape = old_shape
            self.current_tetromino.blocks = self.current_tetromino.create_blocks()
    
    def update(self, dt):
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            # 嘗試讓方塊下降一層
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
                # 只有在嘗試下移一層失敗時才固定方塊，允許玩家極限嵌入
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

