import pygame
from config import *

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font=None, action=None, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        self.font = font if font else FONT_DEFAULT_32_BOLD
        self.enabled = enabled
        self.disabled_color = (100, 100, 100)

    def draw(self, surface):
        current_color = self.color
        if not self.enabled:
            current_color = self.disabled_color
        elif self.is_hovered:
            current_color = self.hover_color
        
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        if self.enabled:
            self.is_hovered = self.rect.collidepoint(pos)
            return self.is_hovered
        self.is_hovered = False
        return False

    def execute_action(self):
        if self.enabled and self.action:
            return self.action()
        return None