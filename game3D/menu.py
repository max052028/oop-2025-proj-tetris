import pygame
from pygame.locals import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.options = ["Start Game", "Leaderboard", "Settings", "Quit"]
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

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (K_w, K_UP):
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key in (K_s, K_DOWN):
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == K_1:
                    self.selected_option = 0
                elif event.key == K_2:
                    self.selected_option = 1
                elif event.key == K_3:
                    self.selected_option = 2
                elif event.key == K_RETURN:
                    return self.selected_option
        return None