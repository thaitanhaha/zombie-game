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
        draw_text("4. Lose if misses >= 10.", WIDTH // 2 - 245, HEIGHT // 2 + 100)
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
                    global score, misses, holes_pos, zombies_pos, alives, current_zombies
                    score = 0
                    misses = 0
                    holes_pos, zombies_pos, alives, current_zombies = generate_positions()
                    return

def update_weapon(score):
    global current_weapon
    idx = score // 10
    current_weapon = weapon_images[idx % len(weapon_images)]

def generate_positions(score=0, min_distance=200, WIDTH=WIDTH, HEIGHT=HEIGHT):
    def generate_hole():
        return (random.randint(150, WIDTH - 150), random.randint(150, HEIGHT - 150))

    if score >= 0 and score <= 5:
        num_holes = 1
    elif score > 5 and score <= 20:
        num_holes = 2
    elif score > 20 and score <= 50:
        num_holes = 3
    else:
        num_holes = 4
        min_distance = 100
    holes_pos = []
    while len(holes_pos) < num_holes:
        new_hole = generate_hole()
        too_close = False
        for hole in holes_pos:
            distance = ((new_hole[0] - hole[0]) ** 2 + (new_hole[1] - hole[1]) ** 2) ** 0.5
            if distance < min_distance:
                too_close = True
                break
        if not too_close: holes_pos.append(new_hole)
    zombies_pos = [(hole[0] + 50, hole[1] - 50) for hole in holes_pos]
    alives = [True for _ in holes_pos]
    current_zombies = [random.choice(zombie_images) for _ in holes_pos]
    return holes_pos, zombies_pos, alives, current_zombies


main_menu()

score = 0
misses = 0
holes_pos, zombies_pos, alives, current_zombies = generate_positions()
zombies_visible = False
holes_visible = False
holes_timer = 0
time_limit = 1000
holes_delay = 500
all_delay = time_limit + holes_delay

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
            if zombies_visible:
                check = False
                for i in range(len(zombies_pos)):
                    zx, zy = zombies_pos[i]
                    if zx < mouse_x < zx + ZOMBIE_SIZE and zy < mouse_y < zy + ZOMBIE_SIZE:
                        score += 1
                        hit_sound.play()
                        alives[i] = False
                        check = True
                        update_weapon(score)
                if not check:
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

    if holes_visible:
        for i in range(len(holes_pos)):
            screen.blit(hole_img, holes_pos[i])
            if zombies_visible:
                if alives[i]: screen.blit(current_zombies[i], zombies_pos[i])
            if current_time - holes_timer > all_delay:
                holes_visible = False
                holes_timer = current_time
                zombies_visible = False
                check = False
                for j in range(len(alives)):
                    if alives[j] == True:
                        check = True
                        misses += 1
                if check: miss_sound.play()
                holes_pos, zombies_pos, alives, current_zombies = generate_positions(score)
            elif zombies_visible == False and current_time - holes_timer > holes_delay:
                zombies_pos[i] = (holes_pos[i][0] + 50, holes_pos[i][1] - 50)
                zombies_visible = True
    else: holes_visible = True

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

    if misses >= 10:
        draw_text("Game Over! Returning to Main Menu...", WIDTH // 2 - 225, HEIGHT // 2)
        pygame.display.flip()
        pygame.time.delay(2000)
        main_menu()
        score, misses = 0, 0

pygame.quit()
