import pygame
import random
from config import *
from utils import load_asset
import math

class Obstacle:
    def __init__(self, lane, world_offset=0):
        self.lane = lane
        self.base_x = (WIDTH // 2) + (lane - 1) * (LANE_WIDTH)
        self.x = self.base_x + world_offset
        self.y = 200
        self.base_speed = random.uniform(2.0, 3.0)
        self.base_width = 100
        self.base_height = 180
        self.scale = 0.1
        self.image = None
        self.load_image()
        self.should_render = True
        self.max_scale = 5.5
        self.min_speed = 0.2

    def load_image(self):
        self.image = load_asset("carro-vindo.png")
        if self.image:
            self.image = self.image.convert_alpha()
        else:
            # Fallback
            self.image = pygame.Surface((self.base_width, self.base_height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200, 0, 0), (0, 0, self.base_width, self.base_height))
    def update(self, player):
        self.x = self.base_x + player.world_offset
        self.should_render = abs(self.lane - player.lane) <= 1
        progress = min(1.0, (self.y + 400) / (HEIGHT + 400))
        speed_multiplier = 1 + (player.drunk_level * 0.6)
        current_speed = self.base_speed * (
            self.min_speed + (1 - progress)**2 * (1 - self.min_speed)
        ) * speed_multiplier
        self.y += current_speed
        scale_increase_rate = 0.01 + (0.03 * progress)
        effective_scale_increase = scale_increase_rate * player.drink_scale_boost
        self.scale = min(self.max_scale, self.scale + effective_scale_increase)
        if self.scale >= self.max_scale:
            return False
        return True

    def draw(self, surface, drunk_level=0, effect_time=0):
        if not self.should_render or not self.image:
            return
            
        current_width = int(self.base_width * self.scale)
        current_height = int(self.base_height * self.scale)
        if current_width <= 0 or current_height <= 0:
            return
        
        # Renderização normal se não estiver bêbado
        if drunk_level <= 0:
            scaled_img = pygame.transform.scale(self.image, (current_width, current_height))
            img_rect = scaled_img.get_rect(center=(self.x, self.y))
            surface.blit(scaled_img, img_rect)
        else:
            # Efeitos de embriaguez
            temp_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
            scaled_img = pygame.transform.scale(self.image, (current_width, current_height))
            
            # Efeito de onda
            wave_intensity = 5 + drunk_level * 2
            wave_speed = 0.005 + drunk_level * 0.0015
            
            for y in range(0, current_height, 3):
                offset_x = wave_intensity * math.sin(y * 0.05 + effect_time * wave_speed)
                temp_surface.blit(scaled_img, (offset_x, y), (0, y, current_width, 3))
            
            # Desfoque
            blur_alpha = max(0, 200 - drunk_level * 30)
            temp_surface.fill((255, 255, 255, blur_alpha), None, pygame.BLEND_RGBA_MULT)
            
            # Desenha na tela
            img_rect = temp_surface.get_rect(center=(self.x, self.y))
            surface.blit(temp_surface, img_rect)

    def is_off_screen(self):
        return self.y > HEIGHT + (self.base_height * self.scale / 2)

    def collides_with(self, player):
        if self.lane != player.lane:
            return False
        obstacle_bottom = self.y + (self.base_height * self.scale) / 2
        if obstacle_bottom < 750:
            return False
        obstacle_width = self.base_width * self.scale
        player_width = LANE_WIDTH * 0.8
        player_visual_left = (WIDTH // 2) - player_width / 2
        player_visual_right = (WIDTH // 2) + player_width / 2
        obstacle_left = self.x - obstacle_width / 2
        obstacle_right = self.x + obstacle_width / 2
        return (obstacle_right > player_visual_left and obstacle_left < player_visual_right)