import pygame
import sys
import random
from config import *
from player import Player
from obstacle import Obstacle
from road import Road
from button import Button
from scenes.intermission import draw_intermission_scene
from scenes.main_menu import show_main_menu
from scenes.game_over import draw_game_over_scene
from audio import audio

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Direção em Primeira Pessoa")
    clock = pygame.time.Clock()

    # Inicializa objetos
    player = Player()
    road = Road()
    obstacles = []
    obstacle_counter = 0
    current_spawn_rate = INITIAL_SPAWN_RATE

    #inicializa sons
    audio.load_sound("caue", "caueta_voice.mp3",0.8)
    audio.load_sound("gameover", "death-scream.mp3",0.9)
    audio.load_sound("carcrash", "car-crash.mp3",0.9)
    audio.load_sound("carropassando", "car-pass-by.mp3",0.2)


    # Game state
    game_state = "START_PROMPT"
    effective_elapsed_time = 0.0
    last_frame_ticks = 0
    phase_duration = BASE_PHASE_DURATION
    remaining_time = phase_duration

    # Backgrounds
    current_background = "background1"
    last_background_switch_time = pygame.time.get_ticks()

    # Tela entre as fases
    money_earned_this_phase_surface = None
    drinks_bought_for_next_phase = 0
    beverages_leftover = 0

    # Botões
    intermission_buy_drink_button = Button(
        WIDTH // 2 - 150, HEIGHT - 150, 300, 50,
        f"Comprar Bebida (${COST_PER_DRINK_PURCHASE})",
        DARK_BLUE_BUTTON, LIGHT_BLUE_BUTTON, FONT_DEFAULT_24
    )
    intermission_continue_button = Button(
        WIDTH // 2 - 100, HEIGHT - 80, 200, 50,
        "Continuar", GREEN, LIGHT_BLUE_BUTTON, FONT_DEFAULT_32_BOLD
    )

    # Main menu
    menu_result = show_main_menu(screen)
    if menu_result == "quit":
        pygame.quit()
        sys.exit()

    running = True
    while running:
        current_frame_ticks = pygame.time.get_ticks()
        if last_frame_ticks == 0:
            last_frame_ticks = current_frame_ticks
        delta_ticks = current_frame_ticks - last_frame_ticks
        last_frame_ticks = current_frame_ticks

        mouse_pos = pygame.mouse.get_pos()

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if game_state == "START_PROMPT":
                    game_state = "PLAYING"
                    player.reset_position()
                    effective_elapsed_time = 0.0
                    last_frame_ticks = pygame.time.get_ticks()
                    phase_duration = BASE_PHASE_DURATION
                    remaining_time = phase_duration

                elif game_state == "PLAYING":
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT: 
                        player.move_left()
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT: 
                        player.move_right()
                    elif event.key == pygame.K_f or event.key == pygame.K_SPACE: 
                        player.drink()

                elif game_state == "GAME_OVER" and event.key == pygame.K_r:
                    player.reset_game_state()
                    obstacles = []
                    current_spawn_rate = INITIAL_SPAWN_RATE
                    effective_elapsed_time = 0.0
                    last_frame_ticks = pygame.time.get_ticks()
                    phase_duration = BASE_PHASE_DURATION
                    remaining_time = phase_duration
                    drinks_bought_for_next_phase = 0
                    beverages_leftover = 0
                    game_state = "PLAYING"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "INTERMISSION":
                    if intermission_buy_drink_button.check_hover(mouse_pos) and intermission_buy_drink_button.enabled:
                        audio.play("caue",loops=2)
                        if player.money >= COST_PER_DRINK_PURCHASE:
                            player.money -= COST_PER_DRINK_PURCHASE
                            drinks_bought_for_next_phase += 1

                    elif intermission_continue_button.check_hover(mouse_pos):
                        player.prepare_for_new_driving_phase(drinks_bought_for_next_phase)
                        obstacles = []
                        effective_elapsed_time = 0.0
                        last_frame_ticks = pygame.time.get_ticks()
                        phase_duration = BASE_PHASE_DURATION + (player.phases_completed * PHASE_DURATION_INCREMENT)
                        remaining_time = phase_duration
                        money_earned_this_phase_surface = None
                        beverages_leftover = 0
                        drinks_bought_for_next_phase = 0
                        game_state = "PLAYING"

        # Updates
        if game_state == "PLAYING":
            effective_delta_ticks = delta_ticks * player.time_multiplier
            effective_elapsed_time += effective_delta_ticks
            remaining_time = max(0, phase_duration - effective_elapsed_time)

            if remaining_time <= 0:
                game_state = "INTERMISSION"
                beverages_leftover = player.drinks
                drinks_bought_for_next_phase = beverages_leftover
                player.drink_effect_active = False
                player.time_multiplier = 1.0
                player.drunk_level = 0
                player.phases_completed += 1
                player.drinks_consumed_total += player.drinks_consumed_this_phase

                money_earned_this_phase_surface = FONT_DEFAULT_36.render(
                    f"Total fase: ${player.score - player.last_phase_score}", 
                    True, 
                    GREEN
                )
                player.last_phase_score = player.score
                player.drinks_consumed_this_phase = 0
                last_background_switch_time = pygame.time.get_ticks()

            player.update()
            obstacle_counter += 1
            if obstacle_counter >= current_spawn_rate:
                lane = random.randint(0, LANE_COUNT - 1)
                obstacles.append(Obstacle(lane, player.world_offset))
                obstacle_counter = 0
                if player.score > 0 and player.score % 10 == 0 and current_spawn_rate > MIN_SPAWN_RATE:
                    current_spawn_rate = max(MIN_SPAWN_RATE, current_spawn_rate - 5)

            for i in range(len(obstacles) - 1, -1, -1):
                obstacle = obstacles[i]
                
                if not obstacle.update(player):
                    if obstacle.scale >= obstacle.max_scale:
                        audio.play("carropassando")
                        # Sistema de pontos/dinheiro progressivo
                        if player.drunk_level == 0:
                            points = 1
                        elif 2 <= player.drunk_level < 5:
                            points = 3
                        elif player.drunk_level >= 5:
                            points = 5
                        
                        player.score += points
                        player.money += points  # Dinheiro = Pontos
                    obstacles.pop(i)
                elif obstacle.collides_with(player):
                    game_state = "GAME_OVER"
                    audio.play("gameover",loops=1)
                    audio.play("carcrash",loops=1)
                    player.drink_effect_active = False
                    player.time_multiplier = 1.0
                    player.drunk_level = 0
                    break

        elif game_state == "INTERMISSION":
            intermission_buy_drink_button.check_hover(mouse_pos)
            intermission_continue_button.check_hover(mouse_pos)
            intermission_buy_drink_button.enabled = player.money >= COST_PER_DRINK_PURCHASE

        # Renders
        screen.fill(BLACK)

        if game_state == "START_PROMPT":
            road.draw(screen, player.world_offset)
            player.draw(screen)
            prompt_text = FONT_DEFAULT_36.render("Pressione qualquer tecla para começar!", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(prompt_text, prompt_rect)

        elif game_state == "PLAYING":
            road.draw(screen, player.world_offset, player.drink_effect_active and player.drunk_level > 0,
                     current_frame_ticks, player.drunk_level)
            for obstacle in obstacles: 
                obstacle.draw(screen, player.drunk_level if player.drink_effect_active else 0, 
                 current_frame_ticks)
            player.draw(screen)

            # UI
            progress = effective_elapsed_time / phase_duration
            distance = int((1 - progress) * BASE_DISTANCE)
            distance = int(distance * (1 - (progress * DISTANCE_CURVE_FACTOR)))
            drunk_speed_boost = 1.0 + (player.drunk_level * DRUNK_SPEED_BOOST_PER_LEVEL)
            distance = int(distance * (1.0 / drunk_speed_boost))
            distance = max(0, distance)
            
            distance_text = FONT_DEFAULT_36.render(
                f"Fase {player.phases_completed+1} | Dist: {distance}m", 
                True, 
                WHITE
            )
            screen.blit(distance_text, (WIDTH - distance_text.get_width() - 10, 10))

            drinks_text = FONT_DEFAULT_36.render(f"Bebidas: {player.drinks}", True, WHITE)
            screen.blit(drinks_text, (10, 10))

            score_text = FONT_DEFAULT_36.render(f"Pontos: {player.score}", True, WHITE)
            screen.blit(score_text, (10, 50))

            money_text = FONT_DEFAULT_36.render(f"Dinheiro: ${player.money}", True, WHITE)
            screen.blit(money_text, (10, 90))

            drunk_limit_text = FONT_DEFAULT_24.render(
                f"Bebidas: {player.drunk_level}/{player.current_max_drunk_level}", 
                True, 
                WHITE)
            screen.blit(drunk_limit_text, (10, 130))

        elif game_state == "INTERMISSION":
            current_background, last_background_switch_time = draw_intermission_scene(
                screen, player, drinks_bought_for_next_phase,
                money_earned_this_phase_surface,
                intermission_continue_button, intermission_buy_drink_button,
                current_background, last_background_switch_time
            )

        elif game_state == "GAME_OVER":
            draw_game_over_scene(screen, player, road, obstacles, player.world_offset)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()