import pygame
import sys

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
car_max_width = SCREEN_WIDTH // 1.2
car_growth_speed = 0.15

car_x_offset = SCREEN_WIDTH // 3  # Starting position in the left-middle
car_y_offset = SCREEN_HEIGHT // 2
car_x = car_x_offset
car_y = car_y_offset

current_frame = 0
frame_timer = 0
frame_interval = 250

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)
    frame_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if frame_timer >= frame_interval:
        current_frame = (current_frame + 1) % len(frames)
        frame_timer = 0

    if car_width < car_max_width:
        car_width += car_growth_speed * dt
        car_height += car_growth_speed * dt
    else:
        car_width, car_height = initial_car_width, initial_car_height
        car_x = car_x_offset  # Reset the car's position once it reaches the max size

    scaled_car = pygame.transform.scale(car_image_original, (int(car_width), int(car_height)))

    screen.blit(frames[current_frame], (0, 0))
    screen.blit(scaled_car, (int(car_x - car_width // 2), int(car_y - car_height // 2)))  # Center the car

    pygame.display.flip()

pygame.quit()
sys.exit()
