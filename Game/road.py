import pygame
import math
from config import *
from utils import load_asset

class Road:
    def __init__(self):
        self.image = None  # Inicializa o atributo image
        self.load_image()  # Carrega a imagem imediatamente

    def load_image(self):
        """Carrega a imagem da estrada com fallback caso não encontre"""
        self.image = load_asset("frame1.png")
        
        if self.image:
            self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
            self.image = self.image.convert()
        else:
            # Fallback - cria uma estrada simples programaticamente
            self.image = pygame.Surface((WIDTH, HEIGHT))
            self.image.fill(BLACK)
            
            # Desenha marcações de pista
            lane_width = WIDTH // LANE_COUNT
            for i in range(1, LANE_COUNT):
                pygame.draw.line(self.image, WHITE, 
                                (i * lane_width, 0), 
                                (i * lane_width, HEIGHT), 
                                5)

    def draw(self, surface, world_offset, drunk_effect=False, effect_time=0, drunk_level=0):
        if drunk_effect and drunk_level > 0:
            if drunk_level <= EXTRA_DRUNK_EFFECT_LEVEL:
                self._draw_drunk_effect(surface, world_offset, effect_time, drunk_level)
            else:
                self._draw_extra_drunk_effect(surface, world_offset, effect_time, drunk_level)
        else:
            self._draw_normal(surface, world_offset)

    def _draw_normal(self, surface, world_offset):
        """Desenha a estrada sem efeitos de embriaguez"""
        surface.blit(self.image, (world_offset, 0))
        if world_offset > 0:
            surface.blit(self.image, (world_offset - WIDTH, 0))
        elif world_offset < 0:
            surface.blit(self.image, (world_offset + WIDTH, 0))

    def _draw_drunk_effect(self, surface, world_offset, effect_time, drunk_level):
        """Desenha a estrada com efeitos de embriaguez"""
        drunk_surface = self.image.copy()
        temp_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        wave_intensity = 5 + drunk_level * 2
        wave_speed = 0.005 + drunk_level * 0.0015
        
        for y in range(0, HEIGHT, 5):
            offset_x = wave_intensity * math.sin(y * 0.02 + effect_time * wave_speed)
            temp_surface.blit(drunk_surface, (world_offset + offset_x, y), 
                             (0, y, WIDTH, 5))
            
            if world_offset + offset_x > 0:
                temp_surface.blit(drunk_surface, (world_offset + offset_x - WIDTH, y), 
                                 (0, y, WIDTH, 5))
            elif world_offset + offset_x < 0:
                temp_surface.blit(drunk_surface, (world_offset + offset_x + WIDTH, y), 
                                 (0, y, WIDTH, 5))
        
        blur_alpha = 200 - min(150, drunk_level * 30)
        temp_surface.fill((200, 200, 255, blur_alpha), None, pygame.BLEND_RGBA_MULT)
        surface.blit(temp_surface, (0, 0))

    def _draw_extra_drunk_effect(self, surface, world_offset, effect_time, drunk_level):
        """Efeito especial para quando passar de 5 bebidas"""
        # Efeito base (wave)
        self._draw_drunk_effect(surface, world_offset, effect_time, drunk_level)
        
        # Cria uma superfície para o efeito extra
        extra_effect = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Efeito de cor alterada (tom avermelhado)
        hue_shift = (effect_time * 0.01) % 360
        color_shift = pygame.Color(0)
        color_shift.hsva = (hue_shift, 40, 90, 30)  # Matiz variável, 40% saturação, 90% brilho, 30% alpha
        extra_effect.fill(color_shift)
        
        # Efeito de desfoque radial
        for i in range(1, 6):
            radius = int(effect_time * 0.05 % 100 + i * 20)
            alpha = 50 - i * 8
            if alpha > 0:
                blur_circle = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(blur_circle, (255, 255, 255, alpha), (radius, radius), radius)
                extra_effect.blit(blur_circle, (WIDTH//2 - radius, HEIGHT//2 - radius))
        
        surface.blit(extra_effect, (0, 0))