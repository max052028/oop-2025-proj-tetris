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
        "move_down": "s",
        "rotate_x": "w",
        "rotate_y": "q",
        "rotate_z": "e",
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
        self.key_binding_index = 0
        self.key_binding_keys = list(self.settings.settings["key_bindings"].keys())

    def draw(self):
        self.screen.fill(BLACK)
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
                val = self.key_binding_keys[self.key_binding_index] + ": " + self.settings.settings["key_bindings"][self.key_binding_keys[self.key_binding_index]]
            else:
                val = ""
            if val:
                val_text = self.font.render(val, True, LIGHT_GRAY)
                self.screen.blit(val_text, (500, y))
        pygame.display.flip()

    def handle_input(self, events):
        for event in events:
            if self.editing:
                if event.type == pygame.KEYDOWN:
                    if event.key == K_RETURN:
                        self.apply_edit()
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
                        return True
                    elif self.options[self.selected] == "Customize Keyboard":
                        self.editing = True
                        self.input_text = ""
                    else:
                        self.editing = True
                        self.input_text = ""
                elif self.options[self.selected] == "Customize Keyboard":
                    if event.key == K_a:
                        self.key_binding_index = (self.key_binding_index - 1) % len(self.key_binding_keys)
                    elif event.key == K_d:
                        self.key_binding_index = (self.key_binding_index + 1) % len(self.key_binding_keys)
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
            key = self.key_binding_keys[self.key_binding_index]
            self.settings.settings["key_bindings"][key] = self.input_text
