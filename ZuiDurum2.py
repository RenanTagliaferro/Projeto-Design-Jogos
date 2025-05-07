import pygame
import random
import os
import sys
import math

# Inicializar pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Direção em Primeira Pessoa")

# Cores para debug
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Configurações do jogo
FPS = 60
LANE_COUNT = 3
LANE_WIDTH = (WIDTH + 400) // LANE_COUNT
INITIAL_SPAWN_RATE = 180
MIN_SPAWN_RATE = 90
OBSTACLE_MIN_SPEED = 1.5
OBSTACLE_MAX_SPEED = 3
PLAYER_HITBOX_HEIGHT = 340
MOVE_AMOUNT = 100  # Quantidade de movimento lateral
DRINK_EFFECT_DURATION = 6000  # 6 segundos em milissegundos
DRINK_SCALE_BOOST = 3.0  # Fator de aceleração do crescimento dos carros

class Player:
    def __init__(self):
        self.reset_position()
        self.width = WIDTH 
        self.height = HEIGHT
        self.image = None
        self.load_image()
        self.hitbox_y = HEIGHT - PLAYER_HITBOX_HEIGHT
        self.is_moving = False
        self.move_speed = 15  # Velocidade de movimento aumentada
        self.drinks = 5  # Quantidade de bebidas inicial
        self.drink_effect_active = False
        self.drink_effect_start_time = 0
        self.drink_scale_boost = 1.0  # Fator normal de escala
        
    def reset_position(self):
        self.lane = 1
        self.x = WIDTH // 2
        self.y = HEIGHT
        self.world_offset = 0
        self.target_offset = 0
        self.drinks = 5  # Resetar bebidas ao reiniciar
        self.drink_effect_active = False
        self.drink_scale_boost = 1.0
        
    def load_image(self):
        try:
            self.image = pygame.image.load("player.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            print("Imagem do jogador não encontrada")
            self.image = None
        
    def move_left(self):
        if self.lane > 0 and not self.is_moving:
            self.lane -= 1
            self.target_offset += LANE_WIDTH  # Agora move exatamente uma faixa
            self.is_moving = True
            return True
        return False
        
    def move_right(self):
        if self.lane < LANE_COUNT - 1 and not self.is_moving:
            self.lane += 1
            self.target_offset -= LANE_WIDTH  # Agora move exatamente uma faixa
            self.is_moving = True
            return True
        return False
        
    def drink(self):
        current_time = pygame.time.get_ticks()
        # Só ativa se tiver bebidas e não estiver já sob efeito
        if self.drinks > 0 and not self.drink_effect_active:
            self.drinks -= 1
            self.drink_effect_active = True
            self.drink_effect_start_time = current_time
            self.drink_scale_boost = DRINK_SCALE_BOOST
            return True
        return False
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Verifica se o efeito da bebida acabou
        if self.drink_effect_active and current_time - self.drink_effect_start_time > DRINK_EFFECT_DURATION:
            self.drink_effect_active = False
            self.drink_scale_boost = 1.0
        
        if abs(self.world_offset - self.target_offset) > 1:
            self.world_offset += (self.target_offset - self.world_offset) * 0.2
        else:
            self.is_moving = False
        
    def draw(self, surface):
        if self.image:
            if self.drink_effect_active:
                # Cria uma cópia da imagem para aplicar efeitos
                drunk_surface = self.image.copy()
                
                # Efeito de ondulação (distorção)
                current_time = pygame.time.get_ticks()
                time_factor = (current_time - self.drink_effect_start_time) / 1000.0
                
                # Cria uma surface temporária
                temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                # Aplica ondulação
                for y in range(0, self.height, 5):
                    offset_x = 10 * math.sin(y * 0.05 + time_factor * 5)
                    temp_surface.blit(drunk_surface, (offset_x, y), (0, y, self.width, 5))
                
                # Aplica ofuscamento (alpha reduzido)
                temp_surface.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)
                
                surface.blit(temp_surface, (0, 0))
            else:
                surface.blit(self.image, (0, 0))

class Obstacle:
    def __init__(self, lane, world_offset=0, scale_boost=1.0):
        self.lane = lane
        self.base_x = LANE_WIDTH * lane
        self.x = self.base_x + world_offset
        self.y = 100  # Spawn mais acima
        self.base_speed = random.uniform(2.0, 3.0)  # Velocidade base
        self.base_width = 100
        self.base_height = 180
        self.scale = 0.1  # Tamanho inicial bem pequeno
        self.image = None
        self.load_image()
        self.should_render = True
        self.max_scale = 7.0  # Aumentei o tamanho máximo
        self.min_speed = 0.3  # Velocidade mínima (nunca zera)
        self.scale_boost = scale_boost  # Fator de aceleração do crescimento
        
    def load_image(self):
        try:
            self.image = pygame.image.load("carro-vindo.png").convert_alpha()
        except:
            print("Imagem de obstáculo não encontrada")
            self.image = None
        
    def update(self, player):
        self.x = self.base_x + player.world_offset
        self.should_render = abs(self.lane - player.lane) <= 1

        progress = min(1.0, (self.y + 400) / (HEIGHT + 400))

        current_speed = self.base_speed * (self.min_speed + (1 - progress)**2 * (1 - self.min_speed))
        self.y += current_speed

        # Escala baseada no boost atual do jogador
        scale_increase = (0.01 + (0.05 * progress)) * player.drink_scale_boost
        self.scale = min(self.max_scale, self.scale + scale_increase)

        if self.y > 300 or self.scale >= self.max_scale:
            return False
        return True

        
    def draw(self, surface):
        if not self.should_render:
            return
            
        current_width = int(self.base_width * self.scale)
        current_height = int(self.base_height * self.scale)
        
        if self.image:
            scaled_img = pygame.transform.scale(self.image, (current_width, current_height))
            img_rect = scaled_img.get_rect(center=(self.x, self.y))
            surface.blit(scaled_img, img_rect)
    
    def is_off_screen(self):
        return self.y > 300  # Remove quando passar do novo limite
    
    def collides_with(self, player):
        if self.lane != player.lane:
            return False
            
        # Verifica se está na área de colisão (parte inferior)
        if self.y < player.hitbox_y:
            return False
            
        # Calcula raios para colisão circular usando o tamanho atual do obstáculo
        obstacle_radius = (self.base_width * self.scale) / 2 * 0.8  # 80% da largura para hitbox mais justa
        player_radius = player.width / 3  # Raio do jogador
        
        # Distância horizontal entre os centros
        distance = abs(self.x - player.x)
        
        return distance < (obstacle_radius + player_radius)

class Road:
    def __init__(self):
        self.image = None
        self.load_image()
        
    def load_image(self):
        try:
            self.image = pygame.image.load("frame1.png").convert()
            self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        except:
            print("Imagem da estrada não encontrada")
            self.image = None
        
    def draw(self, surface, world_offset, drunk_effect=False, effect_time=0):
        if self.image:
            if drunk_effect:
                # Cria uma cópia para aplicar efeitos
                drunk_surface = self.image.copy()
                
                # Efeito de ondulação mais suave na estrada
                temp_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                wave_intensity = 5 * math.sin(effect_time * 0.005)
                
                for y in range(0, HEIGHT, 5):
                    offset_x = wave_intensity * math.sin(y * 0.02 + effect_time * 0.01)
                    temp_surface.blit(drunk_surface, (world_offset + offset_x, y), (0, y, WIDTH, 5))
                
                # Aplica desfoque e ofuscamento
                temp_surface.fill((200, 200, 255, 200), None, pygame.BLEND_RGBA_MULT)
                
                surface.blit(temp_surface, (0, 0))
                if world_offset > 0:
                    surface.blit(temp_surface, (world_offset - WIDTH, 0))
                elif world_offset < 0:
                    surface.blit(temp_surface, (world_offset + WIDTH, 0))
            else:
                surface.blit(self.image, (world_offset, 0))
                if world_offset > 0:
                    surface.blit(self.image, (world_offset - WIDTH, 0))
                elif world_offset < 0:
                    surface.blit(self.image, (world_offset + WIDTH, 0))
        else:
            surface.fill(BLACK)

def main():
    clock = pygame.time.Clock()
    player = Player()
    road = Road()
    obstacles = []
    obstacle_counter = 0
    score = 0
    game_over = False
    current_spawn_rate = INITIAL_SPAWN_RATE
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_over:
                    player.reset_position()
                    obstacles = []
                    score = 0
                    game_over = False
                    current_spawn_rate = INITIAL_SPAWN_RATE
                # Movimento apenas no KEYDOWN (não no pressionamento contínuo)
                if not game_over:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        player.move_left()
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        player.move_right()
                    # Beber com F ou Espaço
                    if event.key == pygame.K_f or event.key == pygame.K_SPACE:
                        player.drink()
        
        if not game_over:
            player.update()
            
            # Spawn de obstáculos com o fator de escala atual
            obstacle_counter += 1
            if obstacle_counter >= current_spawn_rate:
                lane = random.randint(0, LANE_COUNT - 1)
                obstacles.append(Obstacle(lane, player.world_offset, player.drink_scale_boost))
                obstacle_counter = 0
                if score % 10 == 0 and current_spawn_rate > MIN_SPAWN_RATE:
                    current_spawn_rate -= 5
            
            # Atualizar obstáculos
            for obstacle in obstacles[:]:
                if not obstacle.update(player):
                    obstacles.remove(obstacle)
                    score += 1
                    continue
                    
                if obstacle.is_off_screen():
                    obstacles.remove(obstacle)
                    score += 1
                elif obstacle.collides_with(player):
                    game_over = True
        
        # Desenhar
        road.draw(screen, player.world_offset, player.drink_effect_active, 
                 current_time - player.drink_effect_start_time if player.drink_effect_active else 0)
        
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        player.draw(screen)
        
        # UI
        font = pygame.font.SysFont(None, 36)
        
        # Desenhar contador de bebidas
        drink_label = font.render("Bebida:", True, WHITE)
        drink_count = font.render(str(player.drinks), True, WHITE)
        
        # Posiciona no canto superior esquerdo
        screen.blit(drink_label, (10, 10))
        screen.blit(drink_count, (10 + drink_label.get_width() + 5, 10))
        
        # Pontuação abaixo do contador de bebidas
        score_text = font.render(f"Pontuação: {score}", True, WHITE)
        screen.blit(score_text, (10, 50))
        
        # Mostrar tempo restante do efeito se ativo
        if player.drink_effect_active:
            remaining_time = (DRINK_EFFECT_DURATION - (current_time - player.drink_effect_start_time)) // 1000
            effect_text = font.render(f"Efeito: {remaining_time}s", True, WHITE)
            screen.blit(effect_text, (WIDTH - effect_text.get_width() - 10, 10))
        
        if game_over:
            game_over_text = font.render("GAME OVER - Pressione R para reiniciar", True, WHITE)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()