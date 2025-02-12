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
HOLE_WIDTH, HOLE_HEIGHT = 189, 100
BACKGROUND_COLOR = (50, 50, 50)
BACKGROUND_IMAGE_PATH = f"{IMAGE_PATH}/background.png"
background_img = pygame.image.load(BACKGROUND_IMAGE_PATH)
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

LOGO_IMAGE_PATH = f"{IMAGE_PATH}/logo.png"
logo_img = pygame.image.load(LOGO_IMAGE_PATH)
logo_img = pygame.transform.scale(logo_img, (400, int(logo_img.get_height() * (400 / logo_img.get_width()))))

TEXT_COLOR = (255, 255, 255)
FPS = 60

zombie_images = []
zombie_filenames = [f for f in os.listdir(f"{IMAGE_PATH}/zombie") if "zombie" in f]
for filename in zombie_filenames:
    img = pygame.image.load(f"{IMAGE_PATH}/zombie/{filename}")
    img = pygame.transform.scale(img, (ZOMBIE_SIZE, ZOMBIE_SIZE))
    zombie_images.append(img)

HOLE_IMAGE_PATH = f"{IMAGE_PATH}/hole.png"
hole_img = pygame.image.load(HOLE_IMAGE_PATH)
hole_img = pygame.transform.scale(hole_img, (HOLE_WIDTH, HOLE_HEIGHT))

weapon_images = [pygame.image.load(f"{IMAGE_PATH}/weapons/weapon{x}.png") for x in range(1, 4)]
weapon_images = [
    pygame.transform.scale(img, (60, int(img.get_height() * (60 / img.get_width())))) 
    for img in weapon_images
]
weapon_offsets = [(15, -15), (15, 15), (15, 0)]
current_weapon = weapon_images[0]
hit_sound = pygame.mixer.Sound(f"{AUDIO_PATH}/hit.mp3")
miss_sound = pygame.mixer.Sound(f"{AUDIO_PATH}/miss.mp3")
music = pygame.mixer.music.load(f"{AUDIO_PATH}/background_music.mp3")
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Whack-a-Zombie")

font = pygame.font.Font("font/Creepster-Regular.ttf", 36)
clock = pygame.time.Clock()

def draw_text(text, x, y, font=font, color=TEXT_COLOR, surface=screen):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def instruction_screen():
    showing_instructions = True
    while showing_instructions:
        screen.blit(background_img, (0, 0))
        screen.blit(logo_img, (WIDTH // 2 - 175, HEIGHT // 2 - 150))
        draw_text('Instructions', WIDTH // 2 - 75, HEIGHT // 2 - 45)
        draw_text("1. Click on zombies to score points.", WIDTH // 2 - 245, HEIGHT // 2 + 10)
        draw_text("2. If you miss, your miss count increases.", WIDTH // 2 - 245, HEIGHT // 2 + 40)
        draw_text("3. Your weapon changes every 10 hits.", WIDTH // 2 - 245, HEIGHT // 2 + 70)
        draw_text("4. Lose if misses >= score and misses >= 5.", WIDTH // 2 - 245, HEIGHT // 2 + 100)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                showing_instructions = False

def main_menu():
    while True:
        screen.blit(background_img, (0, 0))
        screen.blit(logo_img, (WIDTH // 2 - 175, HEIGHT // 2 - 150))
        draw_text('Instructions', WIDTH // 2 - 75, HEIGHT // 2 - 45)
        draw_text('Play', WIDTH // 2 - 30, HEIGHT // 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if WIDTH // 2 - 70 <= mouse_x <= WIDTH // 2 + 110 and HEIGHT // 2 - 45 <= mouse_y <= HEIGHT // 2 - 15:
                    instruction_screen()
                if WIDTH // 2 - 30 <= mouse_x <= WIDTH // 2 + 30 and HEIGHT // 2 <= mouse_y <= HEIGHT // 2 + 30:
                    return

def update_weapon(score):
    global current_weapon
    idx = score // 10
    current_weapon = weapon_images[idx % len(weapon_images)]

main_menu()

score = 0
misses = 0
hole_pos = (random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100))
zombie_pos = (hole_pos[0] + 50, hole_pos[1] - 50)
zombie_visible = False
hole_visible = False
hole_timer = 0
time_limit = 1000
hole_delay = 500
all_delay = time_limit + hole_delay
current_zombie = random.choice(zombie_images)

hammer_angle = 0
hammer_down = False

running = True
while running:
    screen.blit(background_img, (0, 0))
    current_time = pygame.time.get_ticks()
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
                    hole_visible = False
                    hole_pos = (random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100))
                    zombie_pos = (hole_pos[0] + 50, hole_pos[1] - 50)
                    hole_timer = current_time
                    update_weapon(score)
                else:
                    misses += 1
                    miss_sound.play()
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

    if hole_visible:
        screen.blit(hole_img, hole_pos)
        if zombie_visible:
            screen.blit(current_zombie, zombie_pos)
        if current_time - hole_timer > all_delay:
            hole_visible = False
            hole_pos = (random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100))
            zombie_pos = (hole_pos[0] + 50, hole_pos[1] - 50)
            hole_timer = current_time
            zombie_visible = False
            misses += 1
            miss_sound.play()
        elif zombie_visible == False and current_time - hole_timer > hole_delay:
            current_zombie = random.choice(zombie_images)
            zombie_pos = (hole_pos[0] + 50, hole_pos[1] - 50)
            zombie_visible = True
    else: hole_visible = True

    rotated_hammer = pygame.transform.rotate(current_weapon, hammer_angle)
    weapon_index = weapon_images.index(current_weapon)
    offset_x, offset_y = weapon_offsets[weapon_index]
    hammer_rect = rotated_hammer.get_rect(center=(mouse_x + offset_x, mouse_y + offset_y))
    screen.blit(rotated_hammer, hammer_rect.topleft)

    score_text = font.render(f"Hits: {score}  Misses: {misses}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))

    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, TEXT_COLOR)
    screen.blit(fps_text, (WIDTH - fps_text.get_width() - 10, 10))

    process = psutil.Process(os.getpid())
    ram_usage = process.memory_info().rss / 1024 / 1024
    ram_text = font.render(f"RAM: {ram_usage:.2f} MB", True, TEXT_COLOR)
    screen.blit(ram_text, (WIDTH - ram_text.get_width() - 10, 50))

    pygame.display.flip()
    clock.tick(FPS)

    if misses >= 5 and misses >= score:
        draw_text("Game Over! Returning to Main Menu...", WIDTH // 2 - 225, HEIGHT // 2)
        pygame.display.flip()
        pygame.time.delay(2000)
        main_menu()
        score, misses = 0, 0

pygame.quit()
