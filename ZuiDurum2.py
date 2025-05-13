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
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (50, 50, 200)
LIGHT_BLUE_BUTTON = (100, 150, 255) # Cor para hover de botão
DARK_BLUE_BUTTON = (10, 20, 40)    # Cor normal de botão

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
DRINK_SCALE_BOOST = 3.0  # Fator de aceleração do crescimento dos carros
MAX_DRUNK_LEVEL = 5
PHASE_DURATION = 15000  # Aumentei um pouco para dar tempo de jogar (15 segundos)
TIME_BOOST_PER_DRINK = 1.2  # Fator de aceleração do tempo por drink

# --- NOVAS CONFIGURAÇÕES DE ECONOMIA ---
BASE_MONEY_PER_PHASE = 5
MONEY_PER_DRINK_CONSUMED = 3
COST_PER_DRINK_PURCHASE = 2
INITIAL_PLAYER_MONEY = 5 # Começa com um pouco para poder comprar
INITIAL_PLAYER_DRINKS = 2 # Começa com algumas bebidas

beverages_leftover = 0  # Bebidas não consumidas na fase anterior

current_spawn_rate = INITIAL_SPAWN_RATE

# Carregar imagens para a cena de alternância
try:
    BACKGROUND_IMAGE_1 = pygame.image.load("background1.jpg").convert()
    BACKGROUND_IMAGE_1 = pygame.transform.scale(BACKGROUND_IMAGE_1, (WIDTH, HEIGHT))
except FileNotFoundError:
    BACKGROUND_IMAGE_1 = pygame.Surface((WIDTH, HEIGHT))
    BACKGROUND_IMAGE_1.fill((50, 50, 150))
    print("Erro: 'background1.jpg' não encontrado. Usando cor sólida.")

try:
    BACKGROUND_IMAGE_2 = pygame.image.load("background2.jpg").convert()
    BACKGROUND_IMAGE_2 = pygame.transform.scale(BACKGROUND_IMAGE_2, (WIDTH, HEIGHT))
except FileNotFoundError:
    BACKGROUND_IMAGE_2 = pygame.Surface((WIDTH, HEIGHT))
    BACKGROUND_IMAGE_2.fill((100, 50, 100))
    print("Erro: 'background2.jpg' não encontrado. Usando cor sólida.")

BACKGROUND_SWITCH_DELAY = 1000  # 1 segundo

# --- Fontes ---
try:
    FONT_DEFAULT_36 = pygame.font.SysFont('Arial', 36)
    FONT_DEFAULT_32_BOLD = pygame.font.SysFont('Arial', 32, bold=True)
    FONT_DEFAULT_28_BOLD = pygame.font.SysFont('Arial', 28, bold=True)
    FONT_DEFAULT_24 = pygame.font.SysFont('Arial', 24)
    FONT_LARGE_48_BOLD = pygame.font.SysFont('Arial', 48, bold=True)
    FONT_MENU_TITLE = pygame.font.SysFont('Arial', 72, bold=True)
    FONT_MENU_SUBTITLE = pygame.font.SysFont('Arial', 24, italic=True)
    FONT_MENU_INSTRUCTIONS = pygame.font.SysFont('Arial', 16)
except Exception as e:
    print(f"Aviso: Fonte Arial não encontrada, usando fonte padrão do Pygame. {e}")
    FONT_DEFAULT_36 = pygame.font.Font(None, 36)
    FONT_DEFAULT_32_BOLD = pygame.font.Font(None, 38) # একটু বড়ো
    FONT_DEFAULT_28_BOLD = pygame.font.Font(None, 32) # একটু বড়ো
    FONT_DEFAULT_24 = pygame.font.Font(None, 24)
    FONT_LARGE_48_BOLD = pygame.font.Font(None, 52) # একটু বড়ো
    FONT_MENU_TITLE = pygame.font.Font(None, 76)
    FONT_MENU_SUBTITLE = pygame.font.Font(None, 28)
    FONT_MENU_INSTRUCTIONS = pygame.font.Font(None, 20)


class Player:
    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.image = None
        self.load_image()
        self.hitbox_y = HEIGHT - PLAYER_HITBOX_HEIGHT
        self.is_moving = False
        self.move_speed = 15
        self.reset_game_state() # Chama um reset completo no início

    def reset_game_state(self): # Reset para início de jogo ou game over completo
        self.reset_position()
        self.money = INITIAL_PLAYER_MONEY
        self.drinks = INITIAL_PLAYER_DRINKS # Bebidas iniciais para a primeira fase
        self.drinks_consumed_this_phase = 0 # Novo: rastreia consumo para dinheiro

    def reset_position(self): # Reset para o início de uma fase de condução
        self.lane = 1
        self.x = WIDTH // 2
        self.y = HEIGHT
        self.world_offset = 0
        self.target_offset = 0
        # self.drinks é definido por prepare_for_new_driving_phase ou reset_game_state
        # self.money persiste entre fases
        self.drink_effect_active = False
        self.drink_effect_start_time = 0
        self.drink_scale_boost = 1.0
        self.drunk_level = 0
        self.drunk_wave_effect = 0
        self.time_multiplier = 1.0
        self.drinks_consumed_this_phase = 0 # Importante resetar aqui também

    def prepare_for_new_driving_phase(self, drinks_to_carry_over):
        self.reset_position() # Reseta a maioria dos estados da fase
        self.drinks = drinks_to_carry_over # Define as bebidas para a nova fase

    def load_image(self):
        try:
            self.image = pygame.image.load("player.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except Exception as e:
            print(f"Imagem do jogador não encontrada ou erro ao carregar: {e}")
            self.image = None # Permite que o jogo continue sem a imagem

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
            self.drinks_consumed_this_phase += 1 # Rastreia para ganho de dinheiro
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
            # self.drink_effect_start_time é resetado em reset_position ou quando o efeito termina

        if abs(self.world_offset - self.target_offset) > 1:
            self.world_offset += (self.target_offset - self.world_offset) * 0.2
        else:
            self.world_offset = self.target_offset
            self.is_moving = False

    def draw(self, surface):
        if self.image:
            if self.drink_effect_active and self.drunk_level > 0:
                # ... (código de efeito de embriaguez inalterado) ...
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
        # else: Se não houver imagem, não desenha nada (evita erro)

class Obstacle:
    # ... (código do Obstacle inalterado) ...
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

    def load_image(self):
        try:
            self.image = pygame.image.load("carro-vindo.png").convert_alpha()
        except Exception as e:
            print(f"Imagem de obstáculo não encontrada ou erro ao carregar: {e}")
            self.image = None

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

    def draw(self, surface):
        if not self.should_render or not self.image: 
            return
        current_width = int(self.base_width * self.scale)
        current_height = int(self.base_height * self.scale)
        if current_width <= 0 or current_height <= 0:
            return
        scaled_img = pygame.transform.scale(self.image, (current_width, current_height))
        img_rect = scaled_img.get_rect(center=(self.x, self.y))
        surface.blit(scaled_img, img_rect)

    def is_off_screen(self):
        return self.y > HEIGHT + (self.base_height * self.scale / 2)

    def collides_with(self, player):
        if self.lane != player.lane:
            return False
        obstacle_bottom = self.y + (self.base_height * self.scale) / 2
        if obstacle_bottom < 750: # Ajustado para corresponder à lógica anterior
             return False
        obstacle_width = self.base_width * self.scale
        player_width = LANE_WIDTH * 0.8 # Largura efetiva do jogador na pista
        player_visual_left = (WIDTH // 2) - player_width / 2
        player_visual_right = (WIDTH // 2) + player_width / 2
        obstacle_left = self.x - obstacle_width / 2
        obstacle_right = self.x + obstacle_width / 2
        return (obstacle_right > player_visual_left and obstacle_left < player_visual_right)

class Road:
    # ... (código da Road inalterado) ...
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
                wave_intensity = 5 + drunk_level * 2
                wave_speed = 0.005 + drunk_level * 0.0015
                for y in range(0, HEIGHT, 5):
                    offset_x = wave_intensity * math.sin(y * 0.02 + effect_time * wave_speed)
                    temp_surface.blit(drunk_surface, (world_offset + offset_x, y), (0, y, WIDTH, 5))
                    if world_offset + offset_x > 0 :
                        temp_surface.blit(drunk_surface, (world_offset + offset_x - WIDTH, y), (0, y, WIDTH, 5))
                    elif world_offset + offset_x < 0:
                            temp_surface.blit(drunk_surface, (world_offset + offset_x + WIDTH, y), (0, y, WIDTH, 5))
                blur_alpha = 200 - min(150, drunk_level * 30)
                temp_surface.fill((200, 200, 255, blur_alpha), None, pygame.BLEND_RGBA_MULT)
                surface.blit(temp_surface, (0,0))
            else:
                surface.blit(self.image, (world_offset, 0))
                if world_offset > 0:
                    surface.blit(self.image, (world_offset - WIDTH, 0))
                elif world_offset < 0:
                    surface.blit(self.image, (world_offset + WIDTH, 0))
        else:
            surface.fill(BLACK)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font=None, action=None, enabled=True): # Adicionado 'enabled'
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        self.font = font if font else FONT_DEFAULT_32_BOLD # Usar fonte passada ou padrão
        self.enabled = enabled # Novo: para desabilitar o botão visualmente e funcionalmente
        self.disabled_color = (100, 100, 100) # Cor para botão desabilitado

    def draw(self, surface):
        current_color = self.color
        if not self.enabled:
            current_color = self.disabled_color
        elif self.is_hovered:
            current_color = self.hover_color
        
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10) # Borda

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        if self.enabled: # Só permite hover se habilitado
            self.is_hovered = self.rect.collidepoint(pos)
            return self.is_hovered
        self.is_hovered = False
        return False

    def execute_action(self):
        if self.enabled and self.action: # Só executa se habilitado
            return self.action()
        return None

def show_main_menu():
    title_y = -50
    title_target_y = 50
    title_speed = 2
    start_button = Button(WIDTH//2 - 100, 250, 200, 50, "INICIAR", DARK_BLUE_BUTTON, LIGHT_BLUE_BUTTON, FONT_DEFAULT_32_BOLD, lambda: "game_start")
    quit_button = Button(WIDTH//2 - 100, 320, 200, 50, "SAIR", DARK_BLUE_BUTTON, RED, FONT_DEFAULT_32_BOLD, lambda: "quit")
    try:
        bg_image = pygame.image.load("frame1.png").convert()
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

# --- NOVA FUNÇÃO PARA A CENA DE TRANSIÇÃO (INTERMISSION) ---
def draw_intermission_scene(player, drinks_bought_for_next, money_earned_msg_surface, btn_continue, btn_buy_drink):
    global current_background, last_background_switch_time # Globais para alternar background
    current_time_ticks = pygame.time.get_ticks()

    if current_time_ticks - last_background_switch_time > BACKGROUND_SWITCH_DELAY:
        current_background = BACKGROUND_IMAGE_2 if current_background == BACKGROUND_IMAGE_1 else BACKGROUND_IMAGE_1
        last_background_switch_time = current_time_ticks
    screen.blit(current_background, (0, 0))

    # Overlay escuro para legibilidade
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150)) # Um pouco de transparência
    screen.blit(overlay, (0,0))

    # Título "FASE CONCLUÍDA!"
    title_surf = FONT_LARGE_48_BOLD.render("FASE CONCLUÍDA!", True, WHITE)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_surf, title_rect)

    # Mensagem de dinheiro ganho
    if money_earned_msg_surface:
        msg_rect = money_earned_msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 60))
        screen.blit(money_earned_msg_surface, msg_rect)

    # Informações de UI
    money_text = FONT_DEFAULT_36.render(f"Seu Dinheiro: ${player.money}", True, WHITE)
    money_rect = money_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    screen.blit(money_text, money_rect)

    drinks_bought_text = FONT_DEFAULT_28_BOLD.render(f"Bebidas para próxima fase: {drinks_bought_for_next}", True, WHITE)
    drinks_bought_rect = drinks_bought_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    screen.blit(drinks_bought_text, drinks_bought_rect)
    
    # Desenhar botões
    btn_buy_drink.draw(screen)
    btn_continue.draw(screen)


def main():
    global current_background, last_background_switch_time # Necessário para draw_intermission_scene
    global current_spawn_rate
    # beverages_leftover is now primarily used to initialize drinks_bought_for_next_phase
    # It holds the drinks the player *had* at the end of the phase.
    global beverages_leftover 

    menu_result = show_main_menu()
    if menu_result == "quit":
        pygame.quit()
        sys.exit()

    clock = pygame.time.Clock()
    player = Player() # Player agora tem dinheiro e bebidas iniciais
    road = Road()
    obstacles = []
    obstacle_counter = 0
    score = 0 # Pontuação por desviar, não relacionada a dinheiro diretamente

    # Estados do jogo
    game_state = "PLAYING" # Pode ser "PLAYING", "INTERMISSION", "GAME_OVER", "START_PROMPT"

    if menu_result == "game_start": # Se saiu do menu com "INICIAR"
        game_state = "START_PROMPT"

    effective_elapsed_time = 0.0
    last_frame_ticks = 0
    remaining_time = PHASE_DURATION

    current_background = BACKGROUND_IMAGE_1
    last_background_switch_time = pygame.time.get_ticks()

    # --- Variáveis para a cena de Intermission ---
    money_earned_this_phase_surface = None
    # This variable now tracks the *total* drinks for the next phase: leftovers + purchases
    drinks_bought_for_next_phase = 0 
    beverages_leftover = 0 # Initialize leftover count

    # --- Botões para a cena de Intermission (definidos uma vez) ---
    intermission_buy_drink_button = Button(
        WIDTH // 2 - 150, HEIGHT - 150, 300, 50,
        f"Comprar Bebida (${COST_PER_DRINK_PURCHASE})",
        DARK_BLUE_BUTTON, LIGHT_BLUE_BUTTON, FONT_DEFAULT_24
    )
    intermission_continue_button = Button(
        WIDTH // 2 - 100, HEIGHT - 80, 200, 50,
        "Continuar", GREEN, LIGHT_BLUE_BUTTON, FONT_DEFAULT_32_BOLD
    )

    running = True
    while running:
        current_frame_ticks = pygame.time.get_ticks()
        if last_frame_ticks == 0: # Primeira frame
            last_frame_ticks = current_frame_ticks
        delta_ticks = current_frame_ticks - last_frame_ticks
        last_frame_ticks = current_frame_ticks

        mouse_pos = pygame.mouse.get_pos() # Pega a posição do mouse uma vez por frame

        # --- LÓGICA DE EVENTOS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if game_state == "START_PROMPT":
                    game_state = "PLAYING"
                    player.reset_position() # Garante que o jogador está pronto
                    effective_elapsed_time = 0.0 # Reseta timers da fase
                    last_frame_ticks = pygame.time.get_ticks()
                    remaining_time = PHASE_DURATION

                elif game_state == "PLAYING":
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT: player.move_left()
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT: player.move_right()
                    elif event.key == pygame.K_f or event.key == pygame.K_SPACE: player.drink() # drink() agora afeta player.drinks directly

                elif game_state == "GAME_OVER" and event.key == pygame.K_r:
                    player.reset_game_state() # Reset completo do jogador (dinheiro, bebidas iniciais)
                    obstacles = []
                    score = 0
                    current_spawn_rate = INITIAL_SPAWN_RATE # Restaurar para o original
                    effective_elapsed_time = 0.0
                    last_frame_ticks = pygame.time.get_ticks()
                    remaining_time = PHASE_DURATION
                    drinks_bought_for_next_phase = 0 # Reset carryover count on game over
                    beverages_leftover = 0 # Reset leftovers on game over
                    game_state = "PLAYING" # Volta a jogar

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "INTERMISSION":
                    # drinks_bought_for_next_phase already holds leftovers from phase end
                    if intermission_buy_drink_button.check_hover(mouse_pos) and intermission_buy_drink_button.enabled:
                        if player.money >= COST_PER_DRINK_PURCHASE:
                            player.money -= COST_PER_DRINK_PURCHASE
                            drinks_bought_for_next_phase += 1 # Add purchased drink to carryover count
                            # Update button text to reflect cost/purchase status if needed,
                            # but for now, just the count updates.

                    elif intermission_continue_button.check_hover(mouse_pos):
                        # Prepare player for the next driving phase with the accumulated drinks
                        player.prepare_for_new_driving_phase(drinks_bought_for_next_phase)
                        obstacles = []
                        # current_spawn_rate pode ser mantido ou resetado (vou manter para progressão)
                        effective_elapsed_time = 0.0
                        last_frame_ticks = pygame.time.get_ticks()
                        remaining_time = PHASE_DURATION
                        money_earned_this_phase_surface = None # Limpa a mensagem
                        beverages_leftover = 0 # Reset leftover count for the *next* intermission
                        drinks_bought_for_next_phase = 0 # Reset carryover count for the *next* intermission setup
                        game_state = "PLAYING"


        # --- LÓGICA DE ATUALIZAÇÃO DE ESTADO ---
        if game_state == "PLAYING":
            effective_delta_ticks = delta_ticks * player.time_multiplier
            effective_elapsed_time += effective_delta_ticks
            remaining_time = max(0, PHASE_DURATION - effective_elapsed_time)

            if remaining_time <= 0: # Fase de condução concluída
                game_state = "INTERMISSION"
                # Capture unconsumed drinks at the end of the phase
                beverages_leftover = player.drinks 
                # Initialize the carryover count for the NEXT phase with the leftovers
                drinks_bought_for_next_phase = beverages_leftover 
                player.drink_effect_active = False # Para efeitos visuais
                player.time_multiplier = 1.0      # Reseta multiplicador de tempo
                player.drunk_level = 0            # Reset drunk level for next phase

                # Calcular dinheiro ganho e preparar para intermission
                money_earned = BASE_MONEY_PER_PHASE + (player.drinks_consumed_this_phase * MONEY_PER_DRINK_CONSUMED)
                player.money += money_earned
                money_earned_this_phase_surface = FONT_DEFAULT_36.render(f"Você ganhou: ${money_earned}", True, GREEN)

                player.drinks_consumed_this_phase = 0 # Reset consumption for next phase tracking
                last_background_switch_time = pygame.time.get_ticks() # Para a cena de intermission


            player.update()
            obstacle_counter += 1
            if obstacle_counter >= current_spawn_rate:
                lane = random.randint(0, LANE_COUNT - 1)
                obstacles.append(Obstacle(lane, player.world_offset))
                obstacle_counter = 0
                # Aumento de dificuldade (spawn rate)
                if score > 0 and score % 10 == 0 and current_spawn_rate > MIN_SPAWN_RATE:
                        current_spawn_rate = max(MIN_SPAWN_RATE, current_spawn_rate - 5)


            for i in range(len(obstacles) - 1, -1, -1):
                obstacle = obstacles[i]
                if not obstacle.update(player):
                    # Obstacle reached maximum scale, player avoided collision
                    obstacles.pop(i)
                    score += 1 # Reward for avoiding? Or only when off screen? Let's keep it for now.
                elif obstacle.is_off_screen():
                    # Obstacle went off screen without collision
                    obstacles.pop(i)
                    # score += 1 # Maybe only score here? Let's stick to the scale logic score.
                elif obstacle.collides_with(player):
                    game_state = "GAME_OVER"
                    player.drink_effect_active = False
                    player.time_multiplier = 1.0
                    player.drunk_level = 0 # Reset drunk level on game over
                    break # Exit the loop immediately on collision


        elif game_state == "INTERMISSION":
            intermission_buy_drink_button.check_hover(mouse_pos)
            intermission_continue_button.check_hover(mouse_pos)
            # Habilitar/desabilitar botão de compra
            intermission_buy_drink_button.enabled = player.money >= COST_PER_DRINK_PURCHASE


        # --- SEÇÃO DE DESENHO ---
        screen.fill(BLACK)

        if game_state == "START_PROMPT":
            road.draw(screen, player.world_offset) # Desenha um fundo inicial
            player.draw(screen) # Jogador pode ser visível
            prompt_text_surf = FONT_DEFAULT_36.render("Pressione qualquer tecla para começar!", True, WHITE)
            prompt_rect = prompt_text_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(prompt_text_surf, prompt_rect)

        elif game_state == "PLAYING":
            # Pass correct drunk state info to road drawing
            road.draw(screen, player.world_offset, player.drink_effect_active and player.drunk_level > 0,
                     current_frame_ticks, # Use current_frame_ticks for smoother animation time
                     player.drunk_level)
            for obstacle in obstacles: obstacle.draw(screen)
            player.draw(screen)

            # UI do Jogo
            time_val_sec = int(remaining_time / 1000)
            time_minutes = time_val_sec // 60
            time_seconds = time_val_sec % 60
            time_text_render = FONT_DEFAULT_36.render(f"Tempo: {time_minutes:02d}:{time_seconds:02d}", True, WHITE)
            screen.blit(time_text_render, (WIDTH - time_text_render.get_width() - 10, 10)) # Movido para cima

            # Display the drinks player currently HAS in this phase
            drinks_label_render = FONT_DEFAULT_36.render("Bebidas:", True, WHITE)
            drinks_count_render = FONT_DEFAULT_36.render(str(player.drinks), True, WHITE) 
            screen.blit(drinks_label_render, (10, 10))
            screen.blit(drinks_count_render, (10 + drinks_label_render.get_width() + 5, 10))

            score_render = FONT_DEFAULT_36.render(f"Pontos: {score}", True, WHITE) # "Pontos" em vez de "Pontuação"
            screen.blit(score_render, (10, 50))

            money_ingame_render = FONT_DEFAULT_36.render(f"Dinheiro: ${player.money}", True, WHITE)
            screen.blit(money_ingame_render, (10, 90))


        elif game_state == "INTERMISSION":
            # draw_intermission_scene now correctly uses drinks_bought_for_next_phase
            # which includes leftovers + purchases
            draw_intermission_scene(player, drinks_bought_for_next_phase,
                                    money_earned_this_phase_surface,
                                    intermission_continue_button, intermission_buy_drink_button)

        elif game_state == "GAME_OVER":
            # Pode desenhar a cena do jogo parada no fundo
            road.draw(screen, player.world_offset)
            for obstacle in obstacles: obstacle.draw(screen)
            player.draw(screen)
            # Overlay e texto de Game Over
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            screen.blit(overlay, (0,0))
            game_over_render = FONT_LARGE_48_BOLD.render("GAME OVER", True, RED)
            text_rect = game_over_render.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            screen.blit(game_over_render, text_rect)
            restart_render = FONT_DEFAULT_36.render("Pressione R para reiniciar", True, WHITE)
            restart_rect = restart_render.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(restart_render, restart_rect)


        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Initial global setup before main runs
    current_background = BACKGROUND_IMAGE_1
    last_background_switch_time = pygame.time.get_ticks() # Ensure this is initialized
    beverages_leftover = 0 # Initial state
    main()