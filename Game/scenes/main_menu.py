import pygame
from config import *
from button import Button
from utils import load_asset

def show_main_menu(screen):
    title_y = -50
    title_target_y = 50
    title_speed = 2
    start_button = Button(WIDTH//2 - 100, 250, 200, 50, "INICIAR", DARK_BLUE_BUTTON, LIGHT_BLUE_BUTTON, FONT_DEFAULT_32_BOLD, lambda: "game_start")
    quit_button = Button(WIDTH//2 - 100, 320, 200, 50, "SAIR", DARK_BLUE_BUTTON, RED, FONT_DEFAULT_32_BOLD, lambda: "quit")
    
    try:
        bg_image = load_asset("frame1.png")
        if bg_image:
            bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    except:
        bg_image = None
        
    road_offset = 0
    glow_alpha = 0
    glow_direction = 1
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if start_button.check_hover(mouse_pos):
                        return start_button.execute_action()
                    elif quit_button.check_hover(mouse_pos):
                        return quit_button.execute_action()
                        
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        if title_y < title_target_y: title_y += title_speed
        glow_alpha += 2 * glow_direction
        if glow_alpha > 100 or glow_alpha <= 0: glow_direction *= -1
        road_offset = (road_offset + 0.5) % WIDTH

        if bg_image:
            screen.blit(bg_image, (-road_offset, 0))
            screen.blit(bg_image, (WIDTH - road_offset, 0))
        else:
            screen.fill(DARK_BLUE_BUTTON)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title_text = FONT_MENU_TITLE.render("ZUI DURUM", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH//2, title_y))
        glow_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255,255,255,glow_alpha), (0, 0, title_rect.width + 20, title_rect.height + 20), border_radius=10)
        screen.blit(glow_surface, (title_rect.x - 10, title_rect.y - 10))
        screen.blit(title_text, title_rect)

        subtitle_text = FONT_MENU_SUBTITLE.render("Não beba e dirija... ou beba e tente sobreviver!", True, WHITE)
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, title_y + 70))
        start_button.draw(screen)
        quit_button.draw(screen)

        instructions = [
            "CONTROLES:", "A/← - Mover para esquerda", "D/→ - Mover para direita", "F/ESPAÇO - Beber"
        ]
        for i, line in enumerate(instructions):
            text = FONT_MENU_INSTRUCTIONS.render(line, True, WHITE)
            screen.blit(text, (20, HEIGHT - 100 + i * 20))
            
        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    return "quit"