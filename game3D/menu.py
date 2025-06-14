import pygame
from pygame.locals import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.options = ["Start Game", "Leaderboard", "Quit"]
        self.selected_option = 0

    def draw(self):
        self.screen.fill(BLACK)
        title = self.font.render("3D Tetris", True, WHITE)
        self.screen.blit(title, (400 - title.get_width() // 2, 100))

        for i, option in enumerate(self.options):
            color = WHITE if i == self.selected_option else GRAY
            text = self.font.render(option, True, color)
            self.screen.blit(text, (400 - text.get_width() // 2, 200 + i * 50))

        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[K_w]:  # Pressing 'W' moves up
            self.selected_option = (self.selected_option - 1) % len(self.options)
            pygame.time.delay(250)
        elif keys[K_s]:  # Pressing 'S' moves down
            self.selected_option = (self.selected_option + 1) % len(self.options)
            pygame.time.delay(250)
        elif keys[K_1]:  # Pressing '1' selects the first option
            self.selected_option = 0
        elif keys[K_2]:  # Pressing '2' selects the second option
            self.selected_option = 1
        elif keys[K_3]:  # Pressing '3' selects the third option
            self.selected_option = 2
        elif keys[K_RETURN]:  # Pressing 'Enter' confirms the selection
            return self.selected_option
        return None