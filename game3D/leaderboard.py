import pygame
from pygame.locals import *
import json
import os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Update the path to store the JSON file in the game3D directory
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")

class Leaderboard:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)

    def load_scores(self):
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)

    def save_score(self, name, score):
        scores = self.load_scores()
        scores.append({"name": name, "score": score})
        scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
        with open(LEADERBOARD_FILE, "w") as file:
            json.dump(scores, file)

    def draw(self):
        self.screen.fill(BLACK)
        title = self.font.render("Leaderboard", True, WHITE)
        self.screen.blit(title, (400 - title.get_width() // 2, 50))

        scores = self.load_scores()
        for i, entry in enumerate(scores):
            text = self.font.render(f"{i + 1}. {entry['name']} - {entry['score']}", True, WHITE)
            self.screen.blit(text, (400 - text.get_width() // 2, 100 + i * 30))

        back_text = self.font.render("Press B to go back", True, WHITE)
        self.screen.blit(back_text, (400 - back_text.get_width() // 2, 550))
        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[K_b]:
            return True
        return False