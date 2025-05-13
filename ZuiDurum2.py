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
# DRINK_EFFECT_DURATION = 6000  # REMOVA OU COMENTE ESTA LINHA
DRINK_SCALE_BOOST = 3.0  # Fator de aceleração do crescimento dos carros
# DRUNK_SPEED_BOOST = 1.5  # REMOVA OU COMENTE ESTA LINHA (não era utilizada diretamente para velocidade do obstáculo)
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
        # Atributos como drinks, drink_effect_active, etc., são inicializados em reset_position()

    def reset_position(self):
        self.lane = 1
        self.x = WIDTH // 2
        self.y = HEIGHT
        self.world_offset = 0
        self.target_offset = 0
        self.drinks = 5
        self.drink_effect_active = False
        self.drink_effect_start_time = 0 # Usado para a animação da onda desde a última bebida
        self.drink_scale_boost = 1.0
        self.drunk_level = 0
        self.drunk_wave_effect = 0
        self.time_multiplier = 1.0
        
    def load_image(self):
        try:
            self.image = pygame.image.load("player.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except Exception as e:
            print(f"Imagem do jogador não encontrada ou erro ao carregar: {e}")
            self.image = None
            
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
        if self.drinks > 0 and self.drunk_level < MAX_DRUNK_LEVEL:
            self.drinks -= 1
            self.drink_effect_active = True
            self.drink_effect_start_time = current_time # Define/atualiza o início do efeito visual da onda
            self.drunk_level += 1
            self.time_multiplier *= TIME_BOOST_PER_DRINK # Acelera o tempo
            # O drink_scale_boost será aplicado em update()
            return True
        return False
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.drink_effect_active:
            # Efeito de onda visual
            if self.drink_effect_start_time > 0: # Garante que o tempo foi setado
                 time_since_drink = (current_time - self.drink_effect_start_time) / 1000.0
                 self.drunk_wave_effect = self.drunk_level * math.sin(time_since_drink * 3.0) * 5.0
            else: # Fallback caso o tempo não tenha sido setado (não deve ocorrer com a lógica atual de drink())
                 self.drunk_wave_effect = self.drunk_level * math.sin(current_time / 1000.0 * 3.0) * 5.0
            
            self.drink_scale_boost = DRINK_SCALE_BOOST # Aplica o boost de escala dos obstáculos
        else:
            # Reseta os boosts e efeitos visuais quando o efeito de bebida não está ativo
            self.drink_scale_boost = 1.0
            self.drunk_wave_effect = 0
            # self.drink_effect_start_time é resetado em reset_position ou quando o efeito termina (fase/game over)
            
        # Lógica de movimento da câmera/mundo
        if abs(self.world_offset - self.target_offset) > 1:
            self.world_offset += (self.target_offset - self.world_offset) * 0.2
        else:
            self.world_offset = self.target_offset # Garante que chegue ao valor exato para evitar micro-movimentos
            self.is_moving = False
            
    def draw(self, surface):
        if self.image:
            # Aplica efeitos visuais de embriaguez se o efeito estiver ativo e houver algum nível de embriaguez
            if self.drink_effect_active and self.drunk_level > 0:
                drunk_surface = self.image.copy()
                # Cria uma superfície temporária para aplicar os efeitos de distorção e desfoque
                temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                # Efeito de onda na imagem do jogador
                for y_slice in range(0, self.height, 5):
                    # Calcula o deslocamento horizontal para a onda
                    # Combina uma onda baseada no tempo global e nível de embriaguez com a onda específica da bebida
                    offset_x_wave = (10 + self.drunk_level * 3) * math.sin(
                        y_slice * 0.05 + pygame.time.get_ticks() * 0.005 * self.drunk_level
                    )
                    offset_x = offset_x_wave + self.drunk_wave_effect # Adiciona a onda calculada em update
                    
                    # Desenha uma fatia da imagem original deslocada na superfície temporária
                    temp_surface.blit(drunk_surface, (offset_x, y_slice), (0, y_slice, self.width, 5))
                
                # Aplica um desfoque/alpha progressivo baseado no nível de embriaguez
                alpha_blur = max(0, 200 - self.drunk_level * 20) # Garante que alpha não seja negativo
                temp_surface.fill((255, 255, 255, alpha_blur), None, pygame.BLEND_RGBA_MULT)
                
                surface.blit(temp_surface, (0, 0))
            else:
                # Desenha a imagem normal do jogador se não houver efeito de bebida ativo
                surface.blit(self.image, (0, 0))

class Obstacle:
    def __init__(self, lane, world_offset=0): # Removido scale_boost como parâmetro
        self.lane = lane
        self.base_x = (WIDTH // 2) + (lane - 1) * (LANE_WIDTH)  
        self.x = self.base_x + world_offset
        self.y = 200  # Spawn mais acima
        self.base_speed = random.uniform(2.0, 3.0)
        self.base_width = 100
        self.base_height = 180
        self.scale = 0.1  # Tamanho inicial bem pequeno
        self.image = None
        self.load_image()
        self.should_render = True # Controla se o obstáculo deve ser desenhado (otimização)
        self.max_scale = 5.5
        self.min_speed = 0.2  # Velocidade mínima (nunca zera)
        # self.scale_boost não é mais um atributo do obstáculo; usa player.drink_scale_boost diretamente
        
    def load_image(self):
        try:
            self.image = pygame.image.load("carro-vindo.png").convert_alpha()
        except Exception as e:
            print(f"Imagem de obstáculo não encontrada ou erro ao carregar: {e}")
            self.image = None
            
    def update(self, player): # O jogador é passado para acessar seus atributos (drunk_level, drink_scale_boost)
        self.x = self.base_x + player.world_offset # Atualiza a posição x baseada no movimento do mundo do jogador
        self.should_render = abs(self.lane - player.lane) <= 1 # Otimização: só renderiza se próximo ao jogador

        # Calcula o progresso do obstáculo na tela para ajustar velocidade e escala
        progress = min(1.0, (self.y + 400) / (HEIGHT + 400)) # Normaliza entre 0 e 1

        # Velocidade aumenta com o nível de embriaguez do jogador
        # O código original tinha (player.drunk_level * 2), que é um aumento muito grande.
        # Se desejar um aumento mais suave (ex: 20% por nível), use player.drunk_level * 0.2
        # Mantendo o valor original do código fornecido:
        speed_multiplier = 1 + (player.drunk_level * 0.6) 
        
        # A velocidade do obstáculo também varia com sua progressão na tela (efeito de perspectiva)
        current_speed = self.base_speed * (
            self.min_speed + (1 - progress)**2 * (1 - self.min_speed)
        ) * speed_multiplier
        
        self.y += current_speed

        # A escala do obstáculo aumenta com base no progresso e no drink_scale_boost do jogador
        # Usa player.drink_scale_boost diretamente do objeto player
        scale_increase_rate = 0.01 + (0.03 * progress) # Taxa base de aumento da escala
        effective_scale_increase = scale_increase_rate * player.drink_scale_boost # Aplica o boost
        self.scale = min(self.max_scale, self.scale + effective_scale_increase)

        # Retorna False se o obstáculo atingiu a escala máxima (para ser removido)
        if self.scale >= self.max_scale:
            return False
        return True
            
    def draw(self, surface):
        if not self.should_render or not self.image: # Não desenha se não for necessário ou não houver imagem
            return
            
        current_width = int(self.base_width * self.scale)
        current_height = int(self.base_height * self.scale)
        
        # Evita erro se a escala for muito pequena ou negativa
        if current_width <= 0 or current_height <= 0:
            return

        scaled_img = pygame.transform.scale(self.image, (current_width, current_height))
        img_rect = scaled_img.get_rect(center=(self.x, self.y))
        surface.blit(scaled_img, img_rect)
    
    def is_off_screen(self):
        # Remove o obstáculo se ele saiu da parte inferior da tela
        return self.y > HEIGHT + (self.base_height * self.scale / 2) # Ajustado para considerar a altura do obstáculo
    
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
    start_button = Button(WIDTH//2 - 100, 250, 200, 50, "INICIAR", DARK_BLUE, LIGHT_BLUE, lambda: "game_start")
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

    menu_start_time = pygame.time.get_ticks()
    
    while running:
        current_time = pygame.time.get_ticks() - menu_start_time
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
    menu_result = show_main_menu()
    
    if menu_result == "quit":
        pygame.quit()
        sys.exit() # Usar sys.exit() para terminar o programa completamente
    
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
    game_started = False
    phase_start_time = 0
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        if game_started:
            # Calcula o tempo decorrido e restante na fase, considerando o multiplicador de tempo do jogador
            elapsed_time = (current_time - phase_start_time) * player.time_multiplier
            remaining_time = max(0, PHASE_DURATION - elapsed_time)
            
            # Verifica se a fase foi completada
            if not phase_complete and remaining_time <= 0:
                phase_complete = True
                player.drink_effect_active = False  # Desativa o efeito de bebida ao final da fase
                player.time_multiplier = 1.0      # Reseta o multiplicador de tempo para a próxima fase
                # O drunk_level não é resetado aqui, persiste para a próxima fase (se houver)
                # Outros efeitos (wave, scale_boost) serão resetados em player.update()
        else:
            remaining_time = PHASE_DURATION # Tempo total da fase antes de começar
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Lógica para reiniciar o jogo após Game Over
                if game_over and event.key == pygame.K_r:
                    player.reset_position() # Reseta todos os atributos do jogador (incluindo efeitos de bebida, drunk_level)
                    obstacles = []
                    score = 0 # Reinicia a pontuação
                    game_over = False
                    current_spawn_rate = INITIAL_SPAWN_RATE
                    phase_complete = False # Garante que não esteja em estado de fase completa
                    game_started = True    # O jogo reinicia imediatamente
                    phase_start_time = current_time # Define o novo tempo de início da fase
                
                # Lógica para continuar para a próxima fase (se implementado)
                elif phase_complete and event.key == pygame.K_r:
                    # Prepara para uma nova fase
                    obstacles = [] # Limpa obstáculos da fase anterior
                    # score pode continuar ou ser resetado por fase, atualmente continua
                    current_spawn_rate = INITIAL_SPAWN_RATE # Pode ajustar a dificuldade aqui
                    phase_complete = False
                    game_started = True # Continua o jogo
                    phase_start_time = current_time # Define o tempo de início da nova fase
                    # player.reset_position() NÃO é chamado aqui para manter o drunk_level
                    # player.drink_effect_active já é False e time_multiplier é 1.0
                
                # Lógica para iniciar o jogo a partir do menu ou estado inicial
                elif not game_started and menu_result == "game_start":
                    game_started = True
                    phase_start_time = current_time
                    # Processa a primeira ação do jogador que iniciou o jogo
                    if not game_over and not phase_complete: # Garante que o jogo pode receber input
                        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                            player.move_left()
                        elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                            player.move_right()
                        elif event.key == pygame.K_f or event.key == pygame.K_SPACE:
                            player.drink()
                
                # Processa input do jogador durante o jogo
                elif game_started and not game_over and not phase_complete:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        player.move_left()
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        player.move_right()
                    elif event.key == pygame.K_f or event.key == pygame.K_SPACE:
                        player.drink()
                        
        # Lógica de atualização do jogo (só roda se o jogo começou, não está em game over e a fase não terminou)
        if game_started and not game_over and not phase_complete:
            player.update() # Atualiza o estado do jogador e seus efeitos
            
            # Geração de obstáculos
            obstacle_counter += 1
            if obstacle_counter >= current_spawn_rate:
                lane = random.randint(0, LANE_COUNT - 1)
                # O scale_boost é acessado pelo obstáculo diretamente do player em seu update
                obstacles.append(Obstacle(lane, player.world_offset))
                obstacle_counter = 0
                # Aumenta a taxa de spawn baseada na pontuação (ou outro critério)
                if score > 0 and score % 10 == 0 and current_spawn_rate > MIN_SPAWN_RATE:
                    current_spawn_rate -= 5
            
            # Atualiza e verifica colisões dos obstáculos
            for i in range(len(obstacles) - 1, -1, -1): # Itera de trás para frente para remoção segura
                obstacle = obstacles[i]
                if not obstacle.update(player): # Se update retorna False (ex: max_scale atingido)
                    obstacles.pop(i)
                    score += 1 # Pontua por desviar/sobreviver ao obstáculo
                elif obstacle.is_off_screen():
                    obstacles.pop(i)
                    score += 1 # Pontua por desviar/sobreviver ao obstáculo
                elif obstacle.collides_with(player):
                    game_over = True
                    player.drink_effect_active = False # Desativa efeitos de bebida no game over
                    player.time_multiplier = 1.0     # Reseta multiplicador de tempo
                    # player.update() no próximo ciclo (se houver antes do display de game over)
                    # ou player.reset_position() no reinício cuidará de zerar os efeitos visuais.
                    break # Sai do loop de obstáculos após a primeira colisão
        
        # Renderização
        screen.fill(BLACK) # Limpa a tela com uma cor base (opcional, se a estrada cobrir tudo)

        road.draw(screen, player.world_offset, 
                  player.drink_effect_active, # Passa se o efeito de bebida está ativo
                  # Tempo para animação da estrada (usa o tempo desde a última bebida para sincronia)
                  current_time - player.drink_effect_start_time if player.drink_effect_active and player.drink_effect_start_time > 0 else 0,
                  player.drunk_level)
        
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        player.draw(screen) # Desenha o jogador com seus efeitos
        
        # Interface do Usuário (UI)
        font = pygame.font.SysFont(None, 36) # Fonte padrão para UI
        
        # Exibe o tempo restante (apenas se o jogo começou)
        if game_started:
            time_val_sec = int(remaining_time / 1000)
            time_minutes = time_val_sec // 60
            time_seconds = time_val_sec % 60
            time_text_render = font.render(f"Tempo: {time_minutes:02d}:{time_seconds:02d}", True, WHITE)
            screen.blit(time_text_render, (WIDTH - time_text_render.get_width() - 10, 50))
        # Mensagem para iniciar (se o jogo ainda não começou após o menu)
        elif menu_result == "game_start" and not game_started: 
            start_prompt_text = font.render("Pressione qualquer tecla para começar", True, WHITE)
            text_rect = start_prompt_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(start_prompt_text, text_rect)
            
        # Exibe a quantidade de bebidas restantes
        drinks_label_render = font.render("Bebidas:", True, WHITE)
        drinks_count_render = font.render(str(player.drinks), True, WHITE)
        screen.blit(drinks_label_render, (10, 10))
        screen.blit(drinks_count_render, (10 + drinks_label_render.get_width() + 5, 10))
        
        # Exibe a pontuação
        score_render = font.render(f"Pontuação: {score}", True, WHITE)
        screen.blit(score_render, (10, 50))

        # Mensagem de Fase Completa
        if phase_complete:
            complete_text_render = font.render("FASE COMPLETA! Pressione R para continuar", True, WHITE)
            text_rect = complete_text_render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(complete_text_render, text_rect)
        
        # Mensagem de Game Over
        if game_over:
            game_over_render = font.render("GAME OVER - Pressione R para reiniciar", True, WHITE)
            text_rect = game_over_render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(game_over_render, text_rect)
            
        pygame.display.flip() # Atualiza a tela inteira
        clock.tick(FPS) # Controla a taxa de quadros por segundo

if __name__ == "__main__":
    main()