import pygame
import math
from config import *
from utils import load_asset

class Player:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.image = None
        self.load_image()
        self.hitbox_y = HEIGHT - PLAYER_HITBOX_HEIGHT
        self.is_moving = False
        self.move_speed = 15
        self.reset_game_state()
        self.phase_count = 0  # Contador de fases completadas
        self.current_max_drunk_level = BASE_MAX_DRUNK_LEVEL  # Limite dinâmico
        self.last_phase_score = 0  # Adicione esta linha

    def reset_game_state(self):
        self.reset_position()
        self.money = INITIAL_PLAYER_MONEY
        self.drinks = INITIAL_PLAYER_DRINKS
        self.drinks_consumed_this_phase = 0
        self.drinks_consumed_total = 0 
        self.phases_completed = 0      
        self.score = 0                     

    def reset_position(self):
        self.lane = 1
        self.x = WIDTH // 2
        self.y = HEIGHT
        self.world_offset = 0
        self.target_offset = 0
        self.drink_effect_active = False
        self.drink_effect_start_time = 0
        self.drink_scale_boost = 1.0
        self.drunk_level = 0
        self.drunk_wave_effect = 0
        self.time_multiplier = 1.0
        self.drinks_consumed_this_phase = 0

    def prepare_for_new_driving_phase(self, drinks_to_carry_over):
        self.reset_position()
        self.drinks = drinks_to_carry_over
        self.phase_count += 1
        self.current_max_drunk_level = BASE_MAX_DRUNK_LEVEL + self.phase_count  # Aumenta limite a cada fase    

    def load_image(self):
        self.image = load_asset("player.png")
        if self.image:
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.image = self.image.convert_alpha()
        else:
            # Fallback quando a imagem não carrega
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 0, 0, 128), (0, 0, self.width, self.height))

    def move_left(self):
        if self.lane > 0 and not self.is_moving:
            self.lane -= 1
            self.target_offset += LANE_WIDTH
            self.is_moving = True
            return True
        return False

    def move_right(self):
        if self.lane < LANE_COUNT - 1 and not self.is_moving:
            self.lane += 1
            self.target_offset -= LANE_WIDTH
            self.is_moving = True
            return True
        return False

    def drink(self):
        current_time = pygame.time.get_ticks()
        if self.drinks > 0 and self.drunk_level < self.current_max_drunk_level:  # Usa o limite dinâmico
            self.drinks -= 1
            self.drinks_consumed_this_phase += 1
            self.drink_effect_active = True
            self.drink_effect_start_time = current_time
            self.drunk_level += 1
            self.time_multiplier *= TIME_BOOST_PER_DRINK
            return True
        return False

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.drink_effect_active:
            if self.drink_effect_start_time > 0:
                time_since_drink = (current_time - self.drink_effect_start_time) / 1000.0
                self.drunk_wave_effect = self.drunk_level * math.sin(time_since_drink * 3.0) * 5.0
            else:
                self.drunk_wave_effect = self.drunk_level * math.sin(current_time / 1000.0 * 3.0) * 5.0
            self.drink_scale_boost = DRINK_SCALE_BOOST
        else:
            self.drink_scale_boost = 1.0
            self.drunk_wave_effect = 0

        if abs(self.world_offset - self.target_offset) > 1:
            self.world_offset += (self.target_offset - self.world_offset) * 0.2
        else:
            self.world_offset = self.target_offset
            self.is_moving = False

    def draw(self, surface):
        if self.image:
            if self.drink_effect_active and self.drunk_level > 0:
                drunk_surface = self.image.copy()
                temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                for y_slice in range(0, self.height, 5):
                    offset_x_wave = (10 + self.drunk_level * 3) * math.sin(
                        y_slice * 0.05 + pygame.time.get_ticks() * 0.005 * self.drunk_level
                    )
                    offset_x = offset_x_wave + self.drunk_wave_effect
                    temp_surface.blit(drunk_surface, (offset_x, y_slice), (0, y_slice, self.width, 5))
                alpha_blur = max(0, 200 - self.drunk_level * 20)
                temp_surface.fill((255, 255, 255, alpha_blur), None, pygame.BLEND_RGBA_MULT)
                surface.blit(temp_surface, (0, 0))
            else:
                surface.blit(self.image, (0, 0))