import pygame
import sys
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 720, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zui Durum")

frame1 = pygame.image.load("frame1.png").convert_alpha()
frame2 = pygame.image.load("frame2.png").convert_alpha()
frame1 = pygame.transform.scale(frame1, (SCREEN_WIDTH, SCREEN_HEIGHT))
frame2 = pygame.transform.scale(frame2, (SCREEN_WIDTH, SCREEN_HEIGHT))
frames = [frame1, frame2]

car_image_original = pygame.image.load("carro-vindo.png").convert()
car_image_original.set_colorkey((255, 255, 255))

initial_car_width, initial_car_height = 20, 20
car_width, car_height = initial_car_width, initial_car_height
car_max_width = SCREEN_WIDTH // 1.5
car_growth_speed = 0.15

LANE_WIDTH = SCREEN_WIDTH // 3
player_lane = 1

car_x_offset = -50
car_y_offset = SCREEN_HEIGHT // 2
car_x = car_x_offset
car_y = car_y_offset

current_frame = 0
frame_timer = 0
frame_interval = 250

font = pygame.font.SysFont('Arial', 24)

clock = pygame.time.Clock()
running = True

key_delay = 200
last_key_time = 0

cars = []

def spawn_car():
    lane = random.randint(0, 2)
    return {
        'lane': lane,
        'x': lane * LANE_WIDTH + LANE_WIDTH // 2 - initial_car_width // 2,
        'y': -50,
        'width': initial_car_width,
        'height': initial_car_height,
        'growth_speed': 0.1
    }

while running:
    dt = clock.tick(60)
    frame_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if frame_timer >= frame_interval:
        current_frame = (current_frame + 1) % len(frames)
        frame_timer = 0

    if random.random() < 0.02:
        cars.append(spawn_car())

    for car in cars[:]:
        if car['height'] < car_max_width:
            car['width'] += car['growth_speed'] * dt
            car['height'] += car['growth_speed'] * dt
        else:
            car['y'] += 1

        if car['y'] > SCREEN_HEIGHT:
            cars.remove(car)

        scaled_car = pygame.transform.scale(car_image_original, (int(car['width']), int(car['height'])))
        screen.blit(scaled_car, (int(car['x']), int(car['y'])))

    if car_width < car_max_width:
        car_width += car_growth_speed * dt
        car_height += car_growth_speed * dt
    else:
        car_width, car_height = initial_car_width, initial_car_height
        car_x = car_x_offset

    car_x = player_lane * LANE_WIDTH + LANE_WIDTH // 2 - car_width // 2

    screen.blit(frames[current_frame], (0, 0))

    lane_text = font.render(f"Lane: {player_lane + 1}", True, (255, 255, 255))
    screen.blit(lane_text, (SCREEN_WIDTH // 2 - lane_text.get_width() // 2, 20))

    scaled_car = pygame.transform.scale(car_image_original, (int(car_width), int(car_height)))
    screen.blit(scaled_car, (int(car_x), int(car_y)))

    keys = pygame.key.get_pressed()
    current_time = pygame.time.get_ticks()

    if keys[pygame.K_RIGHT] and player_lane > 0 and current_time - last_key_time > key_delay:
        player_lane -= 1
        last_key_time = current_time

    if keys[pygame.K_LEFT] and player_lane < 2 and current_time - last_key_time > key_delay:
        player_lane += 1
        last_key_time = current_time

    pygame.display.flip()

pygame.quit()
sys.exit()
