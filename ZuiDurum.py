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

    screen.blit(frames[current_frame], (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()
