import pygame
from pygame.locals import QUIT, MOUSEWHEEL
from game import Game
from settings_menu import Settings, SettingsMenu

def main():
    pygame.init()
    settings = Settings()
    game = Game(settings=settings)

    running = True
    in_menu = True
    game_active = False
    in_leaderboard = False
    in_settings = False
    settings_menu = SettingsMenu(game.screen, settings)

    while running:
        dt = game.clock.tick(60)
        events = pygame.event.get()  # 取得所有事件
        for event in events:
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEWHEEL:
                game.camera.handle_mouse_wheel(event)

        if in_menu:
            game.menu.draw()
            selected_option = game.menu.handle_input(events)  # 傳入事件列表
            if selected_option == 0:  # Start Game
                in_menu = False
                game_active = True
            elif selected_option == 1:  # Leaderboard
                in_menu = False
                in_leaderboard = True
            elif selected_option == 2:  # Settings
                in_menu = False
                in_settings = True
            elif selected_option == 3:  # Quit
                running = False
        elif in_leaderboard:
            game.leaderboard.draw()
            if game.leaderboard.handle_input():
                in_leaderboard = False
                in_menu = True
        elif in_settings:
            settings_menu.draw()
            if settings_menu.handle_input(events):
                in_settings = False
                in_menu = True
                # 重新套用設定
                game.apply_settings(settings)
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
