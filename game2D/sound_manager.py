import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        # Load music and sounds here
        self.music_file = "game2D/Sounds/music.mp3"  # Change extension if needed

        self.rotate_sound = pygame.mixer.Sound("game2D/Sounds/rotate.mp3")
        self.clear_sound = pygame.mixer.Sound("game2D/Sounds/clear.mp3")
        self.drop_sound = pygame.mixer.Sound("game2D/Sounds/drop.mp3")
        self.gameover_sound = pygame.mixer.Sound("game2D/Sounds/gameover.mp3")

    def play_music(self):
        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_rotate(self):
        self.rotate_sound.play()

    def play_clear(self):
        self.clear_sound.play()

    def play_drop(self):
        self.drop_sound.play()

    def play_gameover(self):
        self.gameover_sound.play()
