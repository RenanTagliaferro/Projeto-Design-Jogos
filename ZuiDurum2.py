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
DRUNK_SPEED_BOOST = 1.5  # Fator de aceleração dos obstáculos quando bêbado
MAX_DRUNK_LEVEL = 5
PHASE_DURATION = 45000  # 45 segundos em milissegundos
TIME_BOOST_PER_DRINK = 1.2  # Fator de aceleração do tempo por drink

class Player:
    def __init__(self):
        self.reset_position()
        self.width = WIDTH 
        self.height = HEIGHT
        self.image = None
        self.load_image()
        self.hitbox_y = HEIGHT - PLAYER_HITBOX_HEIGHT
        self.is_moving = False
        self.move_speed = 15
        self.drinks = 5
        self.drink_effect_active = False
        self.drink_effect_start_time = 0
        self.drink_scale_boost = 1.0
        self.drunk_level = 0
        self.drunk_wave_effect = 0
        self.phase_start_time = 0
        self.time_multiplier = 1.0  # Fator de aceleração do tempo
        
    def reset_position(self):
        self.lane = 1
        self.x = WIDTH // 2
        self.y = HEIGHT
        self.world_offset = 0
        self.target_offset = 0
        self.drinks = 5
        self.drink_effect_active = False
        self.drink_scale_boost = 1.0
        self.drunk_level = 0  # Corrige o problema 1 - reset do nível
        self.drunk_wave_effect = 0
        self.phase_start_time = pygame.time.get_ticks()
        self.time_multiplier = 1.0
        
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
        if self.drinks > 0 and self.drunk_level < MAX_DRUNK_LEVEL:
            self.drinks -= 1
            self.drink_effect_active = True
            self.drink_effect_start_time = current_time
            self.drunk_level += 1
            self.time_multiplier *= TIME_BOOST_PER_DRINK  # Acelera o tempo
            return True
        return False
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Atualiza efeitos visuais acumulativos
        if self.drink_effect_active:
            time_since_drink = (current_time - self.drink_effect_start_time) / 1000
            self.drunk_wave_effect = self.drunk_level * math.sin(time_since_drink * 3) * 5
            
        if abs(self.world_offset - self.target_offset) > 1:
            self.world_offset += (self.target_offset - self.world_offset) * 0.2
        else:
            self.is_moving = False
        
    def draw(self, surface):
        if self.image:
            if self.drink_effect_active:
                drunk_surface = self.image.copy()
                temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                # Efeito acumulativo baseado no drunk_level
                for y in range(0, self.height, 5):
                    # Combina múltiplas ondas com intensidade progressiva
                    offset_x = (10 + self.drunk_level * 3) * math.sin(
                        y * 0.05 + pygame.time.get_ticks() * 0.005 * self.drunk_level
                    )
                    offset_x += self.drunk_wave_effect
                    temp_surface.blit(drunk_surface, (offset_x, y), (0, y, self.width, 5))
                
                # Desfoque progressivo
                alpha = 200 - self.drunk_level * 20
                temp_surface.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
                surface.blit(temp_surface, (0, 0))
            else:
                surface.blit(self.image, (0, 0))

class Obstacle:
    def __init__(self, lane, world_offset=0, scale_boost=1.0):
        self.lane = lane
        self.base_x = (WIDTH // 2) + (lane - 1) * (LANE_WIDTH)  
        self.x = self.base_x + world_offset
        self.y = 200  # Spawn mais acima
        self.base_speed = random.uniform(2.0, 3.0)  # Velocidade base
        self.base_width = 100
        self.base_height = 180
        self.scale = 0.1  # Tamanho inicial bem pequeno
        self.image = None
        self.load_image()
        self.should_render = True
        self.max_scale = 5.5  # Aumentei o tamanho máximo
        self.min_speed = 0.2  # Velocidade mínima (nunca zera)
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

        # Velocidade base com aceleração proporcional ao nível de embriaguez
        speed_multiplier = 1 + (player.drunk_level * 2)  # 20% mais rápido por nível
        current_speed = self.base_speed * (
            self.min_speed + (1 - progress)**2 * (1 - self.min_speed)
        ) * speed_multiplier
        
        self.y += current_speed

        # Escala com boost progressivo
        scale_increase = (0.01 + (0.03 * progress)) * player.drink_scale_boost
        self.scale = min(self.max_scale, self.scale + scale_increase)

        if self.scale >= self.max_scale:
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
        return self.y > 600  # Remove quando passar do novo limite
    
    def collides_with(self, player):
        # Corrige problema 3 - nova lógica de colisão
        if self.lane != player.lane:
            return False
            
        # Verifica se o obstáculo ultrapassou a linha y=450
        obstacle_bottom = self.y + (self.base_height * self.scale) / 2
        if obstacle_bottom < 750:  # 450 é a posição Y fixa da hitbox do jogador
            return False
            
        # Calcula colisão apenas na horizontal
        obstacle_width = self.base_width * self.scale
        player_width = LANE_WIDTH * 0.8  # Largura da hitbox do jogador
        
        obstacle_left = self.x - obstacle_width/2
        obstacle_right = self.x + obstacle_width/2
        player_left = player.x - player_width/2
        player_right = player.x + player_width/2
        
        return (obstacle_right > player_left and obstacle_left < player_right)
    
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
        
    def draw(self, surface, world_offset, drunk_effect=False, effect_time=0, drunk_level=0):
        if self.image:
            if drunk_effect and drunk_level > 0:
                drunk_surface = self.image.copy()
                temp_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                
                # Efeito acumulativo baseado no drunk_level (Corrige problema 2)
                wave_intensity = 5 + drunk_level * 2  # Intensidade aumenta com o nível
                wave_speed = 0.005 + drunk_level * 0.0015
                
                for y in range(0, HEIGHT, 5):
                    offset_x = wave_intensity * math.sin(y * 0.02 + effect_time * wave_speed)
                    temp_surface.blit(drunk_surface, (world_offset + offset_x, y), (0, y, WIDTH, 5))
                
                # Desfoque progressivo
                blur_alpha = 200 - min(150, drunk_level * 30)
                temp_surface.fill((200, 200, 255, blur_alpha), None, pygame.BLEND_RGBA_MULT)
                
                surface.blit(temp_surface, (0, 0))
                if world_offset > 0:
                    surface.blit(temp_surface, (world_offset - WIDTH, 0))
                elif world_offset < 0:
                    surface.blit(temp_surface, (world_offset + WIDTH, 0))
            else:
                # Desenho normal sem efeitos
                surface.blit(self.image, (world_offset, 0))
                if world_offset > 0:
                    surface.blit(self.image, (world_offset - WIDTH, 0))
                elif world_offset < 0:
                    surface.blit(self.image, (world_offset + WIDTH, 0))
        else:
            surface.fill(BLACK)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def execute_action(self):
        if self.action:
            return self.action()
        return None

def show_main_menu():
    # Cores personalizadas
    DARK_BLUE = (10, 20, 40)
    LIGHT_BLUE = (100, 150, 255)
    RED = (200, 50, 50)
    
    # Efeitos de animação
    title_y = -50
    title_target_y = 50
    title_speed = 2
    
    # Criar botões
    start_button = Button(WIDTH//2 - 100, 250, 200, 50, "INICIAR", DARK_BLUE, LIGHT_BLUE, lambda: "start")
    quit_button = Button(WIDTH//2 - 100, 320, 200, 50, "SAIR", DARK_BLUE, RED, lambda: "quit")
    
    # Carregar imagens de fundo
    try:
        bg_image = pygame.image.load("frame1.png").convert()
        bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    except:
        bg_image = None
    
    # Efeitos de estrada em movimento
    road_offset = 0
    
    # Texto de título
    title_font = pygame.font.SysFont('Arial', 72, bold=True)
    subtitle_font = pygame.font.SysFont('Arial', 24, italic=True)
    
    # Efeitos de brilho
    glow_alpha = 0
    glow_direction = 1
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo
                    if start_button.check_hover(mouse_pos):
                        return start_button.execute_action()
                    elif quit_button.check_hover(mouse_pos):
                        return quit_button.execute_action()
        
        # Atualizações
        start_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        # Animação do título
        if title_y < title_target_y:
            title_y += title_speed
        
        # Efeito de brilho pulsante
        glow_alpha += 2 * glow_direction
        if glow_alpha > 100 or glow_alpha <= 0:
            glow_direction *= -1
        
        # Efeito de estrada em movimento
        road_offset = (road_offset + 0.5) % WIDTH
        
        # Desenhar
        if bg_image:
            screen.blit(bg_image, (-road_offset, 0))
            screen.blit(bg_image, (WIDTH - road_offset, 0))
        else:
            screen.fill(DARK_BLUE)
        
        # Overlay escuro
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Título com efeito de brilho
        title_text = title_font.render("ZUI DURUM", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH//2, title_y))
        
        # Efeito de brilho
        glow_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255,255,255,glow_alpha), 
                        (0, 0, title_rect.width + 20, title_rect.height + 20), 
                        border_radius=10)
        screen.blit(glow_surface, (title_rect.x - 10, title_rect.y - 10))
        
        screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = subtitle_font.render("Não beba e dirija... ou beba e tente sobreviver!", True, WHITE)
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, title_y + 70))
        
        # Botões
        start_button.draw(screen)
        quit_button.draw(screen)
        
        # Instruções
        instructions_font = pygame.font.SysFont('Arial', 16)
        instructions = [
            "CONTROLES:",
            "A/← - Mover para esquerda",
            "D/→ - Mover para direita",
            "F/ESPAÇO - Beber"
        ]
        
        for i, line in enumerate(instructions):
            text = instructions_font.render(line, True, WHITE)
            screen.blit(text, (20, HEIGHT - 100 + i * 20))

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

def main():
    # Mostrar menu primeiro
    menu_result = show_main_menu()
    
    if menu_result == "quit":
        pygame.quit()
        return
    
    # Configuração inicial do jogo
    clock = pygame.time.Clock()
    player = Player()
    road = Road()
    obstacles = []
    obstacle_counter = 0
    score = 0
    game_over = False
    current_spawn_rate = INITIAL_SPAWN_RATE
    
    phase_complete = False
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - player.phase_start_time) * player.time_multiplier
        remaining_time = max(0, PHASE_DURATION - elapsed_time)
            
        # Verifica se completou a fase
        if not phase_complete and remaining_time <= 0:
            phase_complete = True
        
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
                if not game_over:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        player.move_left()
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        player.move_right()
                    if event.key == pygame.K_f or event.key == pygame.K_SPACE:
                        player.drink()
        
        if not game_over:
            player.update()
            
            obstacle_counter += 1
            if obstacle_counter >= current_spawn_rate:
                lane = random.randint(0, LANE_COUNT - 1)
                obstacles.append(Obstacle(lane, player.world_offset, player.drink_scale_boost))
                obstacle_counter = 0
                if score % 10 == 0 and current_spawn_rate > MIN_SPAWN_RATE:
                    current_spawn_rate -= 5
            
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
        
        road.draw(screen, player.world_offset, 
          player.drink_effect_active,
          current_time - player.drink_effect_start_time if player.drink_effect_active else 0,
          player.drunk_level)  # Passa o nível de embriaguez

        for obstacle in obstacles:
            obstacle.draw(screen)
        
        player.draw(screen)

        # UI - Adicione o contador de tempo
        font = pygame.font.SysFont(None, 36)

        # Contador de tempo (formato MM:SS)
        time_text = font.render(f"Tempo: {int(remaining_time/1000)//60:02d}:{int(remaining_time/1000)%60:02d}", True, WHITE)
        screen.blit(time_text, (WIDTH - time_text.get_width() - 10, 50))
        
        font = pygame.font.SysFont(None, 36)
        drink_label = font.render("Bebida:", True, WHITE)
        drink_count = font.render(str(player.drinks), True, WHITE)
        screen.blit(drink_label, (10, 10))
        screen.blit(drink_count, (10 + drink_label.get_width() + 5, 10))
        
        score_text = font.render(f"Pontuação: {score}", True, WHITE)
        screen.blit(score_text, (10, 50))

        if phase_complete:
            phase_text = font.render("FASE COMPLETA! Pressione R para continuar", True, WHITE)
            screen.blit(phase_text, (WIDTH//2 - phase_text.get_width()//2, HEIGHT//2))
        
        if game_over:
            game_over_text = font.render("GAME OVER - Pressione R para reiniciar", True, WHITE)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()