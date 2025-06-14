import pygame
from pygame.locals import QUIT, MOUSEWHEEL
from game import Game

def main():
    pygame.init()
    game = Game()

    running = True
    in_menu = True
    game_active = False
    in_leaderboard = False

    while running:
        dt = game.clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEWHEEL:
                game.camera.handle_mouse_wheel(event)

        if in_menu:
            game.menu.draw()
            selected_option = game.menu.handle_input()
            if selected_option == 0:  # Start Game
                in_menu = False
                game_active = True
            elif selected_option == 1:  # Leaderboard
                in_menu = False
                in_leaderboard = True
            elif selected_option == 2:  # Quit
                running = False
        elif in_leaderboard:
            game.leaderboard.draw()
            if game.leaderboard.handle_input():
                in_leaderboard = False
                in_menu = True
        elif game_active:
            mouse_buttons = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()

            game.camera.handle_mouse(mouse_buttons, mouse_pos)
            game.handle_input()
            game_active = game.update(dt)
            game.draw()

            if not game_active:
                player_name = game.get_player_name()  # Prompt for player name
                game.leaderboard.save_score(player_name, game.score)  # Save score to leaderboard
                pygame.time.wait(333)
                game.reset_game()
                in_menu = True

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
