import pygame
from pygame.locals import *
import json
import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

DEFAULT_SETTINGS = {
    "screen_width": 800,
    "screen_height": 600,
    "mouse_sensitivity_x": 1.0,
    "mouse_sensitivity_y": 1.0,
    "volume": 0.5,
    "key_bindings": {
        "move_left": "a",
        "move_right": "d",
        "move_forward": "s",
        "move_backward": "w",
        "rotate_left": "q",
        "rotate_right": "e",
        "drop": "space"
    }
}

class Settings:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                self.settings.update(json.load(f))

    def save(self):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

class SettingsMenu:
    def __init__(self, screen, settings: Settings):
        self.screen = screen
        self.settings = settings
        self.font = pygame.font.Font(None, 40)
        self.options = [
            "Screen width", "Screen height", "Horizontal Sensetivity", "Vertical Sensetivity", "Volume", "Customize Keyboard", "Save and Return"
        ]
        self.selected = 0
        self.editing = False
        self.input_text = ""
        # 只包含實際有用到的控制項
        self.key_binding_keys = [
            ("move_left", "Move Left"),
            ("move_right", "Move Right"),
            ("move_forward", "Move Forward"),
            ("move_backward", "Move Backward"),
            ("rotate_left", "Rotate Left"),
            ("rotate_right", "Rotate Right"),
            ("drop", "Fast Drop"),
            ("Back to Settings", "Back to Settings")
        ]
        self.key_binding_index = 0
        self.in_key_binding_menu = False
        self.key_binding_editing = False

    def draw(self):
        self.screen.fill(BLACK)
        if self.in_key_binding_menu:
            self.draw_key_binding_menu()
            return
        title = self.font.render("Settings", True, WHITE)
        self.screen.blit(title, (400 - title.get_width() // 2, 60))
        for i, option in enumerate(self.options):
            color = WHITE if i == self.selected else GRAY
            text = self.font.render(option, True, color)
            y = 150 + i * 50
            self.screen.blit(text, (100, y))
            # 顯示目前設定值
            if option == "Screen width":
                val = str(self.settings.get("screen_width"))
            elif option == "Screen height":
                val = str(self.settings.get("screen_height"))
            elif option == "Horizontal Sensetivity":
                val = str(self.settings.get("mouse_sensitivity_x"))
            elif option == "Vertical Sensetivity":
                val = str(self.settings.get("mouse_sensitivity_y"))
            elif option == "Volume":
                val = str(self.settings.get("volume"))
            elif option == "Customize Keyboard":
                # 只在不是 'Back to Settings' 時顯示鍵值
                kb_idx = self.key_binding_index
                kb_key, kb_label = self.key_binding_keys[kb_idx]
                if kb_key != "Back to Settings":
                    val = kb_label + ": " + self.settings.settings["key_bindings"].get(kb_key, "")
                else:
                    val = ""
            else:
                val = ""
            # 修正：編輯時顯示 input_text 並高亮顏色
            if self.editing and i == self.selected:
                show_val = self.input_text if self.input_text else val
                val_color = (255, 255, 0)  # 黃色高亮
            else:
                show_val = val
                val_color = LIGHT_GRAY
            if show_val:
                val_text = self.font.render(show_val, True, val_color)
                self.screen.blit(val_text, (500, y))
        pygame.display.flip()

    def draw_key_binding_menu(self):
        self.screen.fill(BLACK)  # 清除畫面，避免標題重疊
        title = self.font.render("Customize Keyboard", True, WHITE)
        self.screen.blit(title, (400 - title.get_width() // 2, 60))
        for i, (key, label) in enumerate(self.key_binding_keys):
            color = WHITE if i == self.key_binding_index else GRAY
            text = self.font.render(label, True, color)
            y = 150 + i * 50
            self.screen.blit(text, (100, y))
            if key != "Back to Settings":
                val = self.settings.settings["key_bindings"].get(key, "")
                val_color = LIGHT_GRAY
                val_text = self.font.render(val, True, val_color)
                self.screen.blit(val_text, (500, y))
        pygame.display.flip()

    def handle_input(self, events):
        if self.in_key_binding_menu:
            for event in events:
                if self.key_binding_editing:
                    if event.type == pygame.KEYDOWN:
                        if event.key == K_RETURN:
                            self.key_binding_editing = False
                        else:
                            key, _ = self.key_binding_keys[self.key_binding_index]
                            if key != "Back to Settings":
                                self.settings.settings["key_bindings"][key] = pygame.key.name(event.key)
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key in (K_w, K_UP):
                        self.key_binding_index = (self.key_binding_index - 1) % len(self.key_binding_keys)
                    elif event.key in (K_s, K_DOWN):
                        self.key_binding_index = (self.key_binding_index + 1) % len(self.key_binding_keys)
                    elif event.key == K_RETURN:
                        key, _ = self.key_binding_keys[self.key_binding_index]
                        if key == "Back to Settings":
                            self.in_key_binding_menu = False
                        else:
                            self.key_binding_editing = True
            return None
        # ...existing code for normal settings menu...
        for event in events:
            if self.editing:
                if event.type == pygame.KEYDOWN:
                    if event.key == K_RETURN:
                        self.apply_edit()
                        # 如果是自訂鍵位，顯示所有控制列表
                        if self.options[self.selected] == "Customize Keyboard":
                            self.show_key_bindings()
                        self.editing = False
                        self.input_text = ""
                    elif event.key == K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.key == K_ESCAPE:
                        self.editing = False
                        self.input_text = ""
                    else:
                        if len(self.input_text) < 10:
                            self.input_text += event.unicode
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (K_w, K_UP):
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key in (K_s, K_DOWN):
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == K_RETURN:
                    if self.options[self.selected] == "Save and Return":
                        self.settings.save()
                        self.settings.load()  # 立即重新載入設定，讓 key_bindings 變更即時生效
                        # 請在主程式收到 True 後呼叫 game.apply_settings(self.settings.settings)
                        return True
                    elif self.options[self.selected] == "Customize Keyboard":
                        self.in_key_binding_menu = True
                        self.key_binding_index = 0
                    else:
                        self.editing = True
                        self.input_text = ""
        return None

    def apply_edit(self):
        option = self.options[self.selected]
        if option == "Screen width":
            try:
                self.settings.set("screen_width", int(self.input_text))
            except ValueError:
                pass
        elif option == "Screen height":
            try:
                self.settings.set("screen_height", int(self.input_text))
            except ValueError:
                pass
        elif option == "Horizontal Sensetivity":
            try:
                self.settings.set("mouse_sensitivity_x", float(self.input_text))
            except ValueError:
                pass
        elif option == "Vertical Sensetivity":
            try:
                self.settings.set("mouse_sensitivity_y", float(self.input_text))
            except ValueError:
                pass
        elif option == "Volume":
            try:
                v = float(self.input_text)
                if 0.0 <= v <= 1.0:
                    self.settings.set("volume", v)
            except ValueError:
                pass
        elif option == "Customize Keyboard":
            key = self.key_binding_keys[self.key_binding_index][0]
            self.settings.settings["key_bindings"][key] = self.input_text

    def show_key_bindings(self):
        # 彈出一個簡單的鍵位說明視窗
        info = [
            "Key Bindings:",
            f"Move Left: {self.settings.settings['key_bindings'].get('move_left', 'a')}",
            f"Move Right: {self.settings.settings['key_bindings'].get('move_right', 'd')}",
            f"Move Down: {self.settings.settings['key_bindings'].get('move_down', 's')}",
            f"Rotate (Q/E): {self.settings.settings['key_bindings'].get('rotate_y', 'q')}/{self.settings.settings['key_bindings'].get('rotate_x', 'e')}",
            f"Rotate Z: {self.settings.settings['key_bindings'].get('rotate_z', 'r')}",
            f"Fast Drop: {self.settings.settings['key_bindings'].get('drop', 'space')}",
            "Press any key to continue..."
        ]
        popup = pygame.Surface((600, 350))
        popup.fill((30, 30, 30))
        font = pygame.font.Font(None, 36)
        for i, line in enumerate(info):
            text = font.render(line, True, (255, 255, 0) if i == 0 else (255, 255, 255))
            popup.blit(text, (30, 30 + i * 40))
        self.screen.blit(popup, (self.screen.get_width()//2 - 300, self.screen.get_height()//2 - 175))
        pygame.display.flip()
        # 等待任意鍵
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
