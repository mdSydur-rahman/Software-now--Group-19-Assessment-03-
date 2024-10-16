import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the game window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Platformer Game with Enemies and Coins")

# Set frame rate
FPS = 60  # Cap the frame rate at 60 FPS
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# Load images
try:
    player_image = pygame.image.load("hero.png").convert_alpha()  # Load hero image
    enemy_image = pygame.image.load("enemy.png").convert_alpha()  # Load enemy image
    bg_image = pygame.image.load("background.png").convert()  # Load background image
    coin_image = pygame.image.load("coin.png").convert_alpha()    # Load coin image
    platform_image = pygame.image.load("platform.png").convert_alpha()  # Load platform image
except pygame.error as e:
    print(f"Error loading image: {e}")
    sys.exit()

# Scale the images to increase the size
player_image = pygame.transform.scale(player_image, (80, 80))  # Increased player size to 80x80
enemy_image = pygame.transform.scale(enemy_image, (80, 80))    # Increased enemy size to 80x80
bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))  # Scale background
coin_image = pygame.transform.scale(coin_image, (30, 30))      # Keep coin size the same

# Define the Platform class with image
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        try:
            self.image = pygame.image.load("platform.png").convert_alpha()  # Load platform image
            self.image = pygame.transform.scale(self.image, (width, height))  # Scale to platform size
        except pygame.error:
            print("Error loading platform image, using fallback.")
            self.image = pygame.Surface((width, height))
            self.image.fill((128, 128, 128))  # Fallback color (gray) if image is not available
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2  # Speed at which platforms move to the left

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -150:  # Remove platform when it moves off the screen
            self.kill()

# Define the Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image  # Use the hero image
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = screen_height - 150
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.health = 100
        self.lives = 3
        self.score = 0

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.velocity_x = -5
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = 5
        else:
            self.velocity_x = 0

        # Jumping
        if not self.is_jumping and keys[pygame.K_SPACE]:
            self.is_jumping = True
            self.velocity_y = -15

        # Gravity effect
        self.velocity_y += 1
        
        # Update player position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Check if player collides with a platform while falling
        platform_hit = pygame.sprite.spritecollide(self, platforms, False)
        if platform_hit and self.velocity_y > 0:
            self.rect.y = platform_hit[0].rect.top - self.rect.height  # Place player on top of the platform
            self.is_jumping = False
            self.velocity_y = 0

        # Prevent player from falling through the ground
        if self.rect.y >= screen_height - 150:
            self.rect.y = screen_height - 150
            self.is_jumping = False

        # Check boundaries to keep player on screen
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > screen_width - 50:
            self.rect.x = screen_width - 50

    def shoot(self):
        if len(all_projectiles) < 5:
            projectile = Projectile(self.rect.x + 50, self.rect.y + 25)
            all_projectiles.add(projectile)
            all_sprites.add(projectile)

# Define the Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > screen_width:
            self.kill()

# Define the Enemy class with updated position to be on the same level as the coins
class Enemy(pygame.sprite.Sprite):
    def __init__(self, platform):
        super().__init__()
        self.image = enemy_image  # Use enemy image
        self.rect = self.image.get_rect()
        self.platform = platform
        self.rect.x = platform.rect.x + random.randint(50, 100)  # Set enemy on the platform horizontally

        # Place the enemy slightly above the platform like the coins
        self.rect.y = platform.rect.y - 80  # Adjust Y position so enemy is on top of platform like the coins

        self.appearance_delay = random.randint(60, 120)  # Delay appearance (1-2 seconds)
        self.appeared = False

    def update(self):
        if not self.appeared:
            self.appearance_delay -= 1
            if self.appearance_delay <= 0:
                self.appeared = True  # After delay, the enemy appears

        if self.appeared:
            # Move the enemy with the platform
            self.rect.x = self.platform.rect.x + 50
            if self.rect.x < -50:  # Remove if off-screen
                self.kill()

# Define the Coin class, appearing on the platforms
class Coin(pygame.sprite.Sprite):
    def __init__(self, platform, enemy_positions):
        super().__init__()
        self.image = coin_image  # Use the coin image
        self.rect = self.image.get_rect()
        self.platform = platform
        
        # Ensure the coin doesn't spawn where an enemy is
        while True:
            self.rect.x = platform.rect.x + random.randint(50, 100)  # Set coin on the platform
            self.rect.y = platform.rect.y - 30  # Coin slightly above the platform

            # Check if the coin's position overlaps with any enemy
            overlap = any(abs(self.rect.x - ex) < 40 for ex in enemy_positions)
            if not overlap:
                break  # Break loop if no overlap with enemy

    def update(self):
        self.rect.x -= 2  # Move left with the platform
        if self.rect.x < -50:
            self.kill()

        # Check if player collects the coin
        if pygame.sprite.collide_rect(self, player):
            player.score += 10  # Increase score when coin is collected
            self.kill()  # Remove coin once collected

# Scroll the background
def scroll_background(bg_x, speed):
    screen.blit(bg_image, (bg_x, 0))
    screen.blit(bg_image, (bg_x + screen_width, 0))
    bg_x -= speed
    if bg_x <= -screen_width:
        bg_x = 0
    return bg_x

# Game Over function
def game_over():
    font = pygame.font.SysFont(None, 75)
    text = font.render('Game Over', True, RED)
    screen.blit(text, (screen_width // 2 - 150, screen_height // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

# Initialize sprite groups
all_sprites = pygame.sprite.Group()
all_projectiles = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_coins = pygame.sprite.Group()
platforms = pygame.sprite.Group()  # Platform group for jumping

# Create the player
player = Player()
all_sprites.add(player)

# Main game loop
bg_x = 0  # Initial background x position
platform_spawn_timer = 0
running = True
while running:
    clock.tick(FPS)  # Ensure the game runs at 60 FPS

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:  # Shoot with 'X'
                player.shoot()

    # Background motion
    bg_x = scroll_background(bg_x, 2)

    # Spawn platforms, enemies, and coins (with reduced frequency)
    platform_spawn_timer += 1
    if platform_spawn_timer > 120:  # Slightly reduced frequency of new platforms
        platform_spawn_timer = 0
        new_platform = Platform(screen_width, random.randint(300, 500), 150, 20)
        platforms.add(new_platform)
        all_sprites.add(new_platform)

        # Track enemy positions to prevent coin overlap
        enemy_positions = []

        # Spawn enemies with delay on the platform
        if random.random() < 0.5:  # 50% chance to spawn an enemy on the platform
            new_enemy = Enemy(new_platform)
            enemy_positions.append(new_enemy.rect.x)  # Store enemy position
            all_enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # Spawn coins without overlapping enemies
        if random.random() < 0.4:  # Slightly lower chance to spawn a coin on the platform
            new_coin = Coin(new_platform, enemy_positions)
            all_coins.add(new_coin)
            all_sprites.add(new_coin)

    # Update all sprites
    all_sprites.update()

    # Check collisions between projectiles and enemies
    for projectile in all_projectiles:
        enemy_hit = pygame.sprite.spritecollide(projectile, all_enemies, True)
        if enemy_hit:
            player.score += 50  # Add score for each enemy defeated
            projectile.kill()

    # Check collisions between player and enemies (lose health)
    if pygame.sprite.spritecollide(player, all_enemies, True):
        player.health -= 10
        if player.health <= 0:
            player.lives -= 1
            player.health = 100
            if player.lives == 0:
                game_over()

    # Drawing
    all_sprites.draw(screen)

    # Display health, lives, and score
    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f'Health: {player.health}', True, WHITE)
    lives_text = font.render(f'Lives: {player.lives}', True, WHITE)
    score_text = font.render(f'Score: {player.score}', True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(score_text, (10, 70))

    # Update display
    pygame.display.flip()

# Exit Pygame
pygame.quit()
sys.exit()












