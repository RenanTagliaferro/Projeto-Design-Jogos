import pygame
from config import *
from utils import load_asset

def draw_intermission_scene(screen, player, drinks_bought_for_next, money_earned_msg_surface, 
                          btn_continue, btn_buy_drink, current_background, last_background_switch_time):
    current_time = pygame.time.get_ticks()
    
    # Só alterna o background após o delay definido
    if current_time - last_background_switch_time > BACKGROUND_SWITCH_DELAY:
        last_background_switch_time = current_time
        current_background = "background2" if current_background == "background1" else "background1"
    
    # Carrega o background atual uma única vez por frame
    bg_file = "background2.jpg" if current_background == "background2" else "background1.jpg"
    bg_image = load_asset(bg_file)
    
    if bg_image:
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
        screen.blit(bg_image, (0, 0))
    else:
        screen.fill(DARK_BLUE_BUTTON)  # Fallback
    
    # Overlay escuro para legibilidade
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Ajuste a opacidade aqui
    screen.blit(overlay, (0, 0))

    # Título "FASE CONCLUÍDA!"
    title_surf = FONT_LARGE_48_BOLD.render("FASE CONCLUÍDA!", True, WHITE)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_surf, title_rect)

    # Mensagem de dinheiro ganho
    if money_earned_msg_surface:
        msg_rect = money_earned_msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 60))
        screen.blit(money_earned_msg_surface, msg_rect)

    # Informações de UI
    money_text = FONT_DEFAULT_36.render(f"Seu Dinheiro: ${player.money}", True, WHITE)
    money_rect = money_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    screen.blit(money_text, money_rect)

    drinks_text = FONT_DEFAULT_28_BOLD.render(f"Bebidas para próxima fase: {drinks_bought_for_next}", True, WHITE)
    drinks_rect = drinks_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    screen.blit(drinks_text, drinks_rect)
    
    # Desenhar botões
    btn_buy_drink.draw(screen)
    btn_continue.draw(screen)

    return current_background, last_background_switch_time