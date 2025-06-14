import pygame
from colors import Colors
from leaderboard import load_leaderboard

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.Font(None, 60)
        self.menu_font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 30)

    def draw_main_menu(self):
        self.screen.fill(Colors.dark_blue)

        title = self.title_font.render("Python Tetris", True, Colors.white)
        start_2d = self.menu_font.render("1. Start 2D Tetris", True, Colors.light_blue)
        leaderboard = self.menu_font.render("2. View Leaderboard", True, Colors.light_blue)
        quit_game = self.menu_font.render("3. Quit", True, Colors.light_blue)

        self.screen.blit(title, (120, 100))
        self.screen.blit(start_2d, (150, 220))
        self.screen.blit(leaderboard, (150, 270))
        self.screen.blit(quit_game, (150, 320))

    def draw_leaderboard(self):
        self.screen.fill(Colors.dark_blue)
        title = self.title_font.render("Leaderboard", True, Colors.white)
        self.screen.blit(title, (140, 50))

        scores = load_leaderboard()
        for i, entry in enumerate(scores[:5]):
            line = self.small_font.render(f"{i+1}. {entry['name']} - {entry['score']}", True, Colors.light_blue)
            self.screen.blit(line, (120, 120 + i * 40))

        back_text = self.small_font.render("Press ESC to return to menu", True, Colors.white)
        self.screen.blit(back_text, (100, 550))

    def draw_game_ui(self, game):
        score_surface = self.menu_font.render("Score", True, Colors.white)
        score_value_surface = self.menu_font.render(str(game.score), True, Colors.white)

        score_rect = pygame.Rect(320, 55, 170, 60)

        self.screen.fill(Colors.dark_blue)
        self.screen.blit(score_surface, (365, 20))
        pygame.draw.rect(self.screen, Colors.light_blue, score_rect, 0, 10)
        self.screen.blit(score_value_surface, score_value_surface.get_rect(centerx=score_rect.centerx, centery=score_rect.centery))

        game.draw(self.screen)

        if game.game_over:
            leaderboard = load_leaderboard()
            y_offset = 500
            self.screen.blit(self.small_font.render("Leaderboard:", True, Colors.white), (320, y_offset))
            for i, entry in enumerate(leaderboard[:5]):
                entry_surface = self.small_font.render(f"{entry['name']}: {entry['score']}", True, Colors.white)
                self.screen.blit(entry_surface, (320, y_offset + (i + 1) * 25))

    def draw_pause_screen(self):
        pause_text = self.menu_font.render("Paused - Press P to resume", True, Colors.white)
        self.screen.blit(pause_text, (100, 300))
