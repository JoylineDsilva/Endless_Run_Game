from video_preview import main as play_videos
play_videos()
import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Endless Runner")

# Player
player_width = 100
player_height = 100
player_x = 50
player_y = screen_height - player_height - 50  # Adjusted to be on the road
player_velocity_y = 0
player_jump = False
player_speed = 2  # Reduced player speed
jump_height = 100
jump_velocity = 8
falling = False
fall_duration = 3  # 3 seconds freeze duration
invincible_duration = 3  # 3 seconds invincible duration
dead = False

# Load player images for running animation
player_images = [
    pygame.image.load("player_1.png"),
    pygame.image.load("player_2.png"),
    pygame.image.load("player_3.png"),
    pygame.image.load("player_4.png")
]
player_images = [pygame.transform.scale(img, (player_width, player_height)) for img in player_images]
player_image_fall = pygame.image.load("falling.png")
player_image_fall = pygame.transform.scale(player_image_fall, (player_width, player_height))
player_image_dead = pygame.image.load("dying.png")
player_image_dead = pygame.transform.scale(player_image_dead, (player_width, player_height))

# Animation settings
animation_frame = 0
animation_speed = 0.1  # Speed of animation (frames per tick)

# Background
bg_x = 0
bg_y = 0
bg_speed = 3  # Increased background speed
bg_image = pygame.image.load("background.png")
bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))

# Obstacles
obstacle_width = 60
obstacle_height = 60
obstacle_speed = 5  # Increased obstacle speed

# Load obstacle images
can_image = pygame.image.load("can.png")
can_image = pygame.transform.scale(can_image, (obstacle_width, obstacle_height))
waste_image = pygame.image.load("waste.png")
waste_image = pygame.transform.scale(waste_image, (obstacle_width, obstacle_height))

# Load car obstacle images
car_width = 140  # Increased car width
car_height = 150  # Increased car height
car_images = [
    pygame.image.load("car_1.png"),
    pygame.image.load("car_2.png"),
    pygame.image.load("car_3.png"),
    pygame.image.load("car_4.png")
]
car_images = [pygame.transform.scale(img, (car_width, car_height)) for img in car_images]

# Coins
coin_width = 40
coin_height = 40
coin_speed = 5
coin_image = pygame.image.load("coin.png")
coin_image = pygame.transform.scale(coin_image, (coin_width, coin_height))
special_coin_image = pygame.image.load("special_coin.png")
special_coin_image = pygame.transform.scale(special_coin_image, (coin_width, coin_height))

# Obstacles and coins list
obstacles = []
coins = []

# Clock
clock = pygame.time.Clock()

# Score
score = 0
font = pygame.font.Font(None, 36)

# Freeze and invincible state
frozen = False
invincible = False
freeze_start_time = 0
invincible_start_time = 0

# Minimum distance between obstacles, coins
min_distance = 200

# Pause state
paused = False

# Load pause button image
pause_button_image = pygame.image.load("pause_button.png")
pause_button_image = pygame.transform.scale(pause_button_image, (50, 50))  # Make pause button smaller
pause_button_rect = pause_button_image.get_rect()
pause_button_rect.topleft = (screen_width - pause_button_rect.width - 10, 10)

# Load pause menu image and resize it to be bigger
pause_menu_image = pygame.image.load("pause_menu.png")
pause_menu_image = pygame.transform.scale(pause_menu_image, (1000, 1000))  # Make the menu bigger
pause_menu_rect = pause_menu_image.get_rect(center=(screen_width // 2, screen_height // 2))

# Load pause menu buttons and resize to fit inside the pause menu
button_width = 300  # Adjusted width
button_height = 100  # Adjusted height
resume_button_image = pygame.image.load("play_button.png")
resume_button_image = pygame.transform.scale(resume_button_image, (button_width, button_height))
resume_button_rect = resume_button_image.get_rect(center=(screen_width // 2, screen_height // 2 + 10))
restart_button_image = pygame.image.load("restart_button.png")
restart_button_image = pygame.transform.scale(restart_button_image, (button_width, button_height))
restart_button_rect = restart_button_image.get_rect(center=(screen_width // 2, screen_height // 2 + 90))
quit_button_image = pygame.image.load("quit_button.png")
quit_button_image = pygame.transform.scale(quit_button_image, (button_width, button_height))
quit_button_rect = quit_button_image.get_rect(center=(screen_width // 2, screen_height // 2 + 150))

# Load start button image
start_button_image = pygame.image.load("start.png")
start_button_image = pygame.transform.scale(start_button_image, (button_width + 150, button_height + 100))  # Make the button bigger
start_button_rect = start_button_image.get_rect(center=(screen_width // 2, screen_height // 2))

class CarSprite(pygame.sprite.Sprite):
    def __init__(self, images, x, y):
        super().__init__()
        self.images = images
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_speed = 0.1
        self.animation_counter = 0

    def update(self):
        self.animation_counter += self.animation_speed
        if self.animation_counter >= len(self.images):
            self.animation_counter = 0
        self.image_index = int(self.animation_counter)
        self.image = self.images[self.image_index]
        self.rect.x -= obstacle_speed

def does_intersect(rect1, rect2):
    """Check if two rectangles intersect."""
    return not (rect1['x'] > rect2['x'] + rect2['width'] or
                rect1['x'] + rect1['width'] < rect2['x'] or
                rect1['y'] > rect2['y'] + rect2['height'] or
                rect1['y'] + rect1['height'] < rect2['y'])

def handle_pause():
    global paused
    paused = not paused

def reset_game():
    global player_y, player_velocity_y, player_jump, falling, frozen, invincible, freeze_start_time, invincible_start_time, score
    global obstacles, coins, animation_frame, dead, car_sprites

    player_y = screen_height - player_height - 50
    player_velocity_y = 0
    player_jump = False
    falling = False
    frozen = False
    invincible = False
    freeze_start_time = 0
    invincible_start_time = 0
    score = 0
    obstacles = []
    coins = []
    animation_frame = 0
    dead = False
    car_sprites.empty()

def display_message(message, x, y, size=36, color=(255, 255, 255)):
    font = pygame.font.Font(None, size)
    text = font.render(message, True, color)
    screen.blit(text, (x, y))

def main():
    global running, frozen, invincible, freeze_start_time, invincible_start_time, falling, player_jump, player_velocity_y, player_y, score
    global bg_x, bg_speed, obstacles, coins, animation_frame, paused, dead
    global car_sprites

    running = True
    car_sprites = pygame.sprite.Group()
    game_started = False  # Flag to indicate if the game has started

    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and game_started:
                    handle_pause()
                elif event.key == pygame.K_SPACE and not player_jump and not frozen and not paused and not dead and game_started:
                    player_jump = True
                elif event.key == pygame.K_r and dead:
                    reset_game()
                elif event.key == pygame.K_q and dead:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_button_rect.collidepoint(event.pos) and game_started:
                    handle_pause()
                elif paused:
                    if resume_button_rect.collidepoint(event.pos):
                        handle_pause()
                    elif restart_button_rect.collidepoint(event.pos):
                        reset_game()
                        handle_pause()
                    elif quit_button_rect.collidepoint(event.pos):
                        running = False
                elif dead:
                    if restart_button_rect.collidepoint(event.pos):
                        reset_game()
                    elif quit_button_rect.collidepoint(event.pos):
                        running = False
                elif start_button_rect.collidepoint(event.pos) and not game_started:
                    game_started = True

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and not player_jump and not frozen and not paused and not dead and game_started:
            player_jump = True

        if not game_started:
            # Draw background and start button before the game starts
            screen.blit(bg_image, (bg_x, bg_y))
            screen.blit(start_button_image, start_button_rect.topleft)
            pygame.display.flip()
            clock.tick(60)
            continue

        if paused:
            screen.blit(pause_menu_image, pause_menu_rect.topleft)
            screen.blit(resume_button_image, resume_button_rect.topleft)
            screen.blit(restart_button_image, restart_button_rect.topleft)
            screen.blit(quit_button_image, quit_button_rect.topleft)
            pygame.display.flip()
            clock.tick(60)
            continue

        if falling:
            if current_time - freeze_start_time >= fall_duration:
                falling = False
                frozen = False
                invincible = True
                invincible_start_time = current_time
        elif invincible:
            if current_time - invincible_start_time >= invincible_duration:
                invincible = False

        if not frozen and not dead:
            # Update player position
            if not falling:
                if player_jump:
                    if player_y > screen_height - player_height - 50 - jump_height:
                        player_velocity_y = -jump_velocity
                    else:
                        player_jump = False

                player_y += player_velocity_y

                # Apply gravity
                if player_y < screen_height - player_height - 50:
                    player_velocity_y += 1
                else:
                    player_y = screen_height - player_height - 50
                    player_velocity_y = 0

                # Update background position
                bg_x -= bg_speed
                if bg_x <= -screen_width:
                    bg_x = 0

                # Generate obstacles
                if random.randint(0, 100) < 3:
                    new_obstacle = {
                        'x': screen_width,
                        'y': screen_height - obstacle_height - 50,
                        'width': obstacle_width,
                        'height': obstacle_height,
                        'image': random.choice([can_image, waste_image])
                    }
                    if not obstacles or new_obstacle['x'] - obstacles[-1]['x'] >= min_distance:
                        obstacles.append(new_obstacle)

                if random.random() < 0.010 and (len(obstacles) == 0 or obstacles[-1]['x'] < screen_width - min_distance):
                    car_y = screen_height - car_height - 50
                    car_sprite = CarSprite(car_images, screen_width, car_y)
                    car_sprites.add(car_sprite)

                # Generate coins
                if random.randint(0, 100) < 3:
                    new_coin = {
                        'x': screen_width,
                        'y': random.choice([screen_height - coin_height - 50, screen_height - coin_height - 100]),
                        'width': coin_width,
                        'height': coin_height,
                        'image': random.choice([coin_image, special_coin_image])
                    }
                    if not coins or new_coin['x'] - coins[-1]['x'] >= min_distance:
                        coins.append(new_coin)

                # Update obstacles
                for obstacle in obstacles:
                    obstacle['x'] -= obstacle_speed

                # Update coins
                for coin in coins:
                    coin['x'] -= coin_speed

                # Ensure obstacles and coins do not overlap
                all_rects = obstacles + coins
                for i in range(len(all_rects)):
                    for j in range(i + 1, len(all_rects)):
                        if does_intersect(all_rects[i], all_rects[j]):
                            if 'image' in all_rects[j]:
                                coins.remove(all_rects[j])
                            else:
                                obstacles.remove(all_rects[j])

                # Check for collision with obstacles
                player_rect = {'x': player_x, 'y': player_y, 'width': player_width, 'height': player_height}
                for obstacle in obstacles:
                    if does_intersect(player_rect, obstacle):
                        if not invincible:
                            frozen = True
                            falling = True
                            freeze_start_time = current_time
                            break

                # Check for collision with cars
                for car in car_sprites:
                    if car.rect.colliderect(pygame.Rect(player_x, player_y, player_width, player_height)):
                        if player_y == screen_height - player_height - 50:
                            dead = True

                # Check for collision with coins
                for coin in coins:
                    if does_intersect(player_rect, coin):
                        if coin['image'] == coin_image:
                            score += 5
                        elif coin['image'] == special_coin_image:
                            score += 15
                        coins.remove(coin)
                        break

                # Remove off-screen obstacles and coins
                obstacles = [obstacle for obstacle in obstacles if obstacle['x'] + obstacle['width'] > 0]
                coins = [coin for coin in coins if coin['x'] + coin['width'] > 0]

                # Update animation frame
                animation_frame += animation_speed
                if animation_frame >= len(player_images):
                    animation_frame = 0

                # Update car sprites
                car_sprites.update()

        # Draw background
        screen.blit(bg_image, (bg_x, bg_y))
        screen.blit(bg_image, (bg_x + screen_width, bg_y))

        # Draw player
        if frozen and falling:
            screen.blit(player_image_fall, (player_x, player_y))
        elif dead:
            screen.blit(player_image_dead, (player_x, player_y))
        else:
            screen.blit(player_images[int(animation_frame)], (player_x, player_y))

        # Draw obstacles
        for obstacle in obstacles:
            screen.blit(obstacle['image'], (obstacle['x'], obstacle['y']))

        # Draw coins
        for coin in coins:
            screen.blit(coin['image'], (coin['x'], coin['y']))

        # Draw car sprites
        car_sprites.draw(screen)

        # Draw score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        # Draw pause button
        if game_started:
            screen.blit(pause_button_image, pause_button_rect.topleft)

        # Check if player is dead
        if dead:
            display_message("Game Over!", screen_width // 2 - 100, screen_height // 2 - 50, size=72, color=(255, 0, 0))
            final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
            screen.blit(final_score_text, (screen_width // 2 - 100, screen_height // 2 + 20))
            screen.blit(restart_button_image, restart_button_rect.topleft)
            screen.blit(quit_button_image, quit_button_rect.topleft)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
