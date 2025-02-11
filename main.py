import pygame
import random
import os
import time
import psutil

pygame.init()

IMAGE_PATH = "images"
AUDIO_PATH = "audio"
WIDTH, HEIGHT = 800, 600
ZOMBIE_SIZE = 100
BACKGROUND_COLOR = (50, 50, 50)
BACKGROUND_IMAGE_PATH = f"{IMAGE_PATH}/background.png"
HOLE_IMAGE_PATH = f"{IMAGE_PATH}/hole.png"
background_img = pygame.image.load(BACKGROUND_IMAGE_PATH)
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
TEXT_COLOR = (255, 255, 255)
FPS = 60

zombie_images = []
zombie_filenames = [f for f in os.listdir(f"{IMAGE_PATH}/zombie") if "zombie" in f]
for filename in zombie_filenames:
    img = pygame.image.load(f"{IMAGE_PATH}/zombie/{filename}")
    img = pygame.transform.scale(img, (ZOMBIE_SIZE, ZOMBIE_SIZE))
    zombie_images.append(img)

hole_img = pygame.image.load(HOLE_IMAGE_PATH)
hole = pygame.transform.scale(hole_img, (ZOMBIE_SIZE, ZOMBIE_SIZE))

hammer_img = pygame.image.load(f"{IMAGE_PATH}/woodhammer.png")
hammer_img = pygame.transform.scale(hammer_img, (60, 60))

hit_sound = pygame.mixer.Sound(f"{AUDIO_PATH}/hit.mp3")
miss_sound = pygame.mixer.Sound(f"{AUDIO_PATH}/miss.mp3")
music = pygame.mixer.music.load(f"{AUDIO_PATH}/background_music.mp3")
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Whack-a-Zombie")

font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def main_menu():
    while True:
        screen.blit(background_img, (0, 0))
        draw_text('Whack-a-Zombie', font, TEXT_COLOR, screen, WIDTH // 2 - 100, HEIGHT // 2 - 100)
        draw_text('Play', font, TEXT_COLOR, screen, WIDTH // 2 - 30, HEIGHT // 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if WIDTH // 2 - 30 <= mouse_x <= WIDTH // 2 + 30 and HEIGHT // 2 <= mouse_y <= HEIGHT // 2 + 30:
                    return

main_menu()

score = 0
misses = 0
zombie_pos = (random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100))
hole_pos = (zombie_pos[0] - 120, zombie_pos[1])
zombie_visible = True
zombie_timer = 0
time_limit = 1000
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
current_zombie = random.choice(zombie_images)

hammer_angle = 0
hammer_down = False

running = True
while running:
    screen.blit(background_img, (0, 0))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if zombie_visible:
                zx, zy = zombie_pos
                if zx < mouse_x < zx + ZOMBIE_SIZE and zy < mouse_y < zy + ZOMBIE_SIZE:
                    score += 1
                    hit_sound.play()
                    zombie_visible = False
                else:
                    misses += 1
                    miss_sound.play()
            hammer_down = True

        if event.type == pygame.MOUSEBUTTONUP:
            hammer_down = False

    if hammer_down:
        hammer_angle = 30
    else:
        hammer_angle = 0

    if zombie_visible:
        screen.blit(hole_img, hole_pos)
        screen.blit(current_zombie, zombie_pos)
        zombie_timer += clock.get_time()
        if zombie_timer > time_limit:
            zombie_visible = False
            misses += 1
            miss_sound.play()
    else:
        zombie_pos = (random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100))
        hole_pos = (zombie_pos[0] - 120, zombie_pos[1])
        current_zombie = random.choice(zombie_images)
        zombie_visible = True
        zombie_timer = 0

    rotated_hammer = pygame.transform.rotate(hammer_img, hammer_angle)
    hammer_rect = rotated_hammer.get_rect(center=(mouse_x, mouse_y))
    screen.blit(rotated_hammer, hammer_rect.topleft)

    score_text = font.render(f"Hits: {score}  Misses: {misses}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))

    # Get the current FPS and render it as text
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, TEXT_COLOR)
    screen.blit(fps_text, (WIDTH - fps_text.get_width() - 10, 10))

    # Get the current RAM usage and render it as text
    process = psutil.Process(os.getpid())
    ram_usage = process.memory_info().rss / 1024 / 1024  # Convert to MB
    ram_text = font.render(f"RAM: {ram_usage:.2f} MB", True, TEXT_COLOR)
    screen.blit(ram_text, (WIDTH - ram_text.get_width() - 10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
