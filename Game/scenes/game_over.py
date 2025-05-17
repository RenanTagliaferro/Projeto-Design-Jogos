import pygame
from config import *

def draw_game_over_scene(screen, player, road, obstacles, world_offset):
    """
    Desenha a cena de Game Over com todas as informações necessárias
    
    Args:
        screen: Superfície do Pygame onde desenhar
        player: Instância do jogador
        road: Instância da estrada
        obstacles: Lista de obstáculos
        world_offset: Offset do mundo para posicionamento correto
    """
    # Desenha o estado atual do jogo como fundo
    road.draw(screen, world_offset)
    for obstacle in obstacles:
        obstacle.draw(screen)
    player.draw(screen)
    
    # Overlay escuro para melhor legibilidade
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Texto de Game Over
    game_over_text = FONT_LARGE_48_BOLD.render("GAME OVER", True, RED)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(game_over_text, game_over_rect)
    
    # Instruções para reiniciar
    restart_text = FONT_DEFAULT_36.render("Pressione R para reiniciar", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(restart_text, restart_rect)
    
    # Estatísticas do jogador
    stats_y = HEIGHT // 2 + 70
    stats_lines = [
        f"Pontuação Final: {player.score}",
        f"Bebidas consumidas: {player.drinks_consumed_total}",
        f"Fases completas: {player.phases_completed}"
    ]
    
    for i, line in enumerate(stats_lines):
        stat_text = FONT_DEFAULT_24.render(line, True, WHITE)
        stat_rect = stat_text.get_rect(center=(WIDTH // 2, stats_y + i * 30))
        screen.blit(stat_text, stat_rect)