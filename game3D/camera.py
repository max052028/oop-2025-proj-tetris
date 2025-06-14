import math
from vector3d import Vector3D
from constants import GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH, GRID_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT

class Camera:
    def __init__(self, screen_width=800, screen_height=600, target=Vector3D(GRID_WIDTH * GRID_SIZE / 2, GRID_HEIGHT * GRID_SIZE / 2, GRID_DEPTH * GRID_SIZE / 2), distance=None, rotation_x=-0.3, rotation_y=0.5):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.target = target
        # 根據解析度自動設置鏡頭距離
        self.distance = distance if distance is not None else max(screen_width, screen_height)
        self.rotation_x = rotation_x
        self.rotation_y = rotation_y
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        self.update_position()
    
    def handle_mouse_wheel(self, event):
        if event.y > 0:
            self.distance = max(100, self.distance - 50)
        elif event.y < 0:
            self.distance += 50
        self.update_position()

    def update_position(self):
        x = self.distance * math.cos(self.rotation_x) * math.sin(self.rotation_y)
        y = self.distance * math.sin(self.rotation_x)
        z = self.distance * math.cos(self.rotation_x) * math.cos(self.rotation_y)
        self.position = Vector3D(self.target.x + x, self.target.y + y, self.target.z + z)
    
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
        
        factor = self.screen_height * 1.33 / z  # 根據螢幕高度自適應
        screen_x = int(x * factor + self.screen_width // 2)
        screen_y = int(-y * factor + self.screen_height // 2)
        
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
    
    def set_screen_size(self, width, height):
        self.screen_width = width
        self.screen_height = height
        # 視窗變大時自動拉遠鏡頭
        self.distance = max(width, height)
        self.update_position()