import pygame

# Screen settings
WIDTH, HEIGHT = 800, 600
FPS = 60

# Game settings
LANE_COUNT = 3
LANE_WIDTH = (WIDTH + 400) // LANE_COUNT
INITIAL_SPAWN_RATE = 180
MIN_SPAWN_RATE = 90
OBSTACLE_MIN_SPEED = 1.5
OBSTACLE_MAX_SPEED = 3
PLAYER_HITBOX_HEIGHT = 340
MOVE_AMOUNT = 100
DRINK_SCALE_BOOST = 3.0
MAX_DRUNK_LEVEL = 5
PHASE_DURATION = 15000
TIME_BOOST_PER_DRINK = 1.2

# Economy settings
BASE_MONEY_PER_PHASE = 5
MONEY_PER_DRINK_CONSUMED = 3
COST_PER_DRINK_PURCHASE = 2
INITIAL_PLAYER_MONEY = 5
INITIAL_PLAYER_DRINKS = 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (50, 50, 200)
LIGHT_BLUE_BUTTON = (100, 150, 255)
DARK_BLUE_BUTTON = (10, 20, 40)

# Background settings
BACKGROUND_SWITCH_DELAY = 1000

# Initialize fonts
pygame.init()
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
    print(f"Warning: Arial font not found, using default Pygame font. {e}")
    FONT_DEFAULT_36 = pygame.font.Font(None, 36)
    FONT_DEFAULT_32_BOLD = pygame.font.Font(None, 38)
    FONT_DEFAULT_28_BOLD = pygame.font.Font(None, 32)
    FONT_DEFAULT_24 = pygame.font.Font(None, 24)
    FONT_LARGE_48_BOLD = pygame.font.Font(None, 52)
    FONT_MENU_TITLE = pygame.font.Font(None, 76)
    FONT_MENU_SUBTITLE = pygame.font.Font(None, 28)
    FONT_MENU_INSTRUCTIONS = pygame.font.Font(None, 20)