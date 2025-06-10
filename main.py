import pygame
import sys
from game import Game
from colors import Colors
from leaderboard import add_score
from menu import Menu
from sound_manager import SoundManager

pygame.init()
screen = pygame.display.set_mode((500, 600))  # Standard dimensions
pygame.display.set_caption("Python Tetris")

clock = pygame.time.Clock()
small_font = pygame.font.Font(None, 30)

game = Game()
menu = Menu(screen)
sound_manager = SoundManager()
sound_manager.play_music()

state = "menu"  # menu, playing, leaderboard, paused
input_active = False
player_name = ""

GAME_UPDATE = pygame.USEREVENT
pygame.time.set_timer(GAME_UPDATE, 200)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    state = "playing"
                    game.reset()
                elif event.key == pygame.K_2:
                    state = "leaderboard"
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()

        elif state == "leaderboard":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "menu"

        elif state == "paused":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state = "playing"

        elif state == "playing":
            if game.game_over and not input_active:
                input_active = True
                sound_manager.play_gameover()

            if input_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and player_name:
                        add_score(player_name, game.score)
                        player_name = ""
                        input_active = False
                        state = "menu"
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif len(player_name) < 10 and event.unicode.isprintable():
                        player_name += event.unicode
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    state = "paused"
                elif event.key == pygame.K_LEFT:
                    game.move_left()
                elif event.key == pygame.K_RIGHT:
                    game.move_right()
                elif event.key == pygame.K_DOWN:
                    game.move_down()
                    game.update_score(0, 1)
                    sound_manager.play_drop()
                elif event.key == pygame.K_UP:
                    game.rotate()
                    sound_manager.play_rotate()

            if event.type == GAME_UPDATE and not game.game_over and not input_active:
                game.move_down()

    # Drawing
    screen.fill(Colors.blue)  # Clear the screen before drawing
    if state == "menu":
        menu.draw_main_menu()
    elif state == "leaderboard":
        menu.draw_leaderboard()
    elif state == "paused":
        menu.draw_game_ui(game)
        menu.draw_pause_screen()
    elif state == "playing":
        menu.draw_game_ui(game)
        game.draw(screen)

        if game.game_over and input_active:
            input_surface = small_font.render("Enter Name: " + player_name, True, Colors.white)
            screen.blit(input_surface, (320, 460))

    pygame.display.update()
    clock.tick(60)


