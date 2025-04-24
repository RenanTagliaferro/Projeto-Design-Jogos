import pygame
import random
import os
import sys

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
        
    def reset_position(self):
        self.lane = 1
        self.x = WIDTH // 2
        self.y = HEIGHT
        self.world_offset = 0
        self.target_offset = 0
        
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
        
    def update(self):
        if abs(self.world_offset - self.target_offset) > 1:
            self.world_offset += (self.target_offset - self.world_offset) * 0.2
        else:
            self.is_moving = False
        
    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (0, 0))

class Obstacle:
    def __init__(self, lane, world_offset=0):
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
        
    def load_image(self):
        try:
            self.image = pygame.image.load("carro-vindo.png").convert_alpha()
        except:
            print("Imagem de obstáculo não encontrada")
            self.image = None
        
    def update(self, player_lane, world_offset):
        self.x = self.base_x + world_offset
        self.should_render = abs(self.lane - player_lane) <= 1
        
        # Calcula progressão (0 quando longe, 1 quando perto)
        progress = min(1.0, (self.y + 400) / (HEIGHT + 400))  # Normalizado entre 0-1
        
        # Velocidade decrescente usando curva exponencial
        current_speed = self.base_speed * (self.min_speed + (1 - progress)**2 * (1 - self.min_speed))
        
        # Movimento vertical
        self.y += current_speed
        
        # Aumento do tamanho - mais rápido conforme progride
        scale_increase = 0.01 + (0.05 * progress)  # Cresce entre 0.01 e 0.06 por frame
        self.scale = min(self.max_scale, self.scale + scale_increase)
        
        # Remove quando passou muito da tela ou atingiu tamanho máximo
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
        
    def draw(self, surface, world_offset):
        if self.image:
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
        
        if not game_over:
            player.update()
            
            # Spawn de obstáculos
            obstacle_counter += 1
            if obstacle_counter >= current_spawn_rate:
                lane = random.randint(0, LANE_COUNT - 1)
                obstacles.append(Obstacle(lane, player.world_offset))
                obstacle_counter = 0
                if score % 10 == 0 and current_spawn_rate > MIN_SPAWN_RATE:
                    current_spawn_rate -= 5
            
            # Atualizar obstáculos
            for obstacle in obstacles[:]:
                if not obstacle.update(player.lane, player.world_offset):
                    obstacles.remove(obstacle)
                    score += 1
                    continue
                    
                if obstacle.is_off_screen():
                    obstacles.remove(obstacle)
                    score += 1
                elif obstacle.collides_with(player):
                    game_over = True
        
        # Desenhar
        road.draw(screen, player.world_offset)
        
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        player.draw(screen)
        
        # UI
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Pontuação: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            game_over_text = font.render("GAME OVER - Pressione R para reiniciar", True, WHITE)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()