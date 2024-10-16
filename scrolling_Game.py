import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_AREA_HEIGHT = int(SCREEN_HEIGHT * 0.8)
HUD_HEIGHT = int(SCREEN_HEIGHT * 0.2)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)

# Game screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tank Shooter Game")

# Clock
clock = pygame.time.Clock()

# Player (Tank) Class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 30))  # Placeholder for tank
        self.image.fill(GREEN)  # Green color for tank
        pygame.draw.rect(self.image, BLACK, [10, 10, 30, 10])  # Turret
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = 5
        self.health = 100
        self.lives = 3

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Keep the player within the screen bounds
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width

    def shoot(self):
        projectile = Projectile(self.rect.centerx, self.rect.top)
        return projectile

    def update(self):
        self.move()

# Projectile Class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)  # Red color for projectiles
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:  # Off-screen
            self.kill()

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health, speed):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill(RED)  # Enemy tanks are red
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health = health
        self.speed = speed

    def move(self):
        self.rect.y += self.speed

    def update(self):
        self.move()

# Scoreboard and HUD Class
class Scoreboard:
    def __init__(self):
        self.score = 0
        self.level = 1

    def increase_score(self, amount):
        self.score += amount

    def reset_score(self):
        self.score = 0

    def draw(self, screen, player):
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        health_text = font.render(f"Health: {player.health}", True, WHITE)

        screen.blit(score_text, (10, GAME_AREA_HEIGHT + 10))
        screen.blit(level_text, (10, GAME_AREA_HEIGHT + 40))
        screen.blit(lives_text, (10, GAME_AREA_HEIGHT + 70))
        screen.blit(health_text, (10, GAME_AREA_HEIGHT + 100))

    def display_game_over(self, screen):
        font = pygame.font.SysFont(None, 72)
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))

    def display_play_again(self, screen):
        font = pygame.font.SysFont(None, 36)
        play_again_text = font.render("Play Again? Press Y for Yes, N for No", True, WHITE)
        screen.blit(play_again_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50))

    def display_level_up(self, screen):
        font = pygame.font.SysFont(None, 72)
        level_up_text = font.render(f"Level {self.level}", True, GREEN)
        screen.blit(level_up_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))

    def display_lives_left(self, screen, player):
        font = pygame.font.SysFont(None, 72)
        lives_left_text = font.render(f"{player.lives} Lives Left", True, WHITE)
        screen.blit(lives_left_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))

# Function to pause and display lives left
def display_lives_left_pause(screen, player, scoreboard, seconds):
    screen.fill(BLACK)
    scoreboard.draw(screen, player)
    scoreboard.display_lives_left(screen, player)
    pygame.display.flip()
    pygame.time.delay(seconds * 1000)  # Pause for the specified seconds

# User Guide Screen Function
def show_user_guide(screen):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 36)

    guide_lines = [
        "HOW TO PLAY:",
        "1. Use LEFT and RIGHT arrow keys to move the tank.",
        "2. Press 'Z' to shoot at enemies.",
        "3. If an enemy reaches the bottom, you lose a life.",
        "4. You have 3 lives. If you lose all lives, it's game over.",
        "5. Score 100 points to level up, and enemies get faster.",
        "6. Your score resets after each level.",
        "",
        "Press 'Enter' to Start the Game!"
    ]

    y_offset = 100
    for line in guide_lines:
        guide_text = font.render(line, True, WHITE)
        screen.blit(guide_text, (SCREEN_WIDTH // 2 - 300, y_offset))
        y_offset += 40

    pygame.display.flip()

    # Wait for user to press "Enter" to start the game
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False  # Exit loop and start the game

# Main Game Loop
def main():
    show_user_guide(screen)  # Display user guide before starting the game

    player = Player(SCREEN_WIDTH // 2, GAME_AREA_HEIGHT - 50)
    projectiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    scoreboard = Scoreboard()

    enemy_spawn_timer = 100  # Time between enemy spawns
    enemy_spawn_counter = 0

    enemy_speed = 2  # Initial enemy speed for level 1
    game_over = False
    display_level_up_message = False
    level_up_timer = 60  # Time to display the level-up message
    lives_lost_pause = False  # Pause after life is lost

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and not game_over:
                    projectile = player.shoot()
                    projectiles.add(projectile)

                # Handle input when game over and asking to play again
                if game_over:
                    if event.key == pygame.K_y:  # Restart game
                        main()  # Restart the game
                    elif event.key == pygame.K_n:  # Quit game
                        running = False  # Exit the game loop

        if not game_over:
            # Update player, projectiles, and enemies
            player.update()
            projectiles.update()

            # Only update enemies and spawn new ones if not paused after losing a life
            if not lives_lost_pause:
                enemies.update()

                # Check for projectile-enemy collisions
                for projectile in projectiles:
                    enemy_hit_list = pygame.sprite.spritecollide(projectile, enemies, True)
                    for enemy in enemy_hit_list:
                        scoreboard.increase_score(10)
                        projectile.kill()

                # Check if the score reaches 100 and level up
                if scoreboard.score >= 100:
                    scoreboard.level += 1
                    scoreboard.reset_score()
                    display_level_up_message = True
                    enemy_speed += 2  # Increase enemy speed with each level

                # Display the level-up message for a short time
                if display_level_up_message:
                    level_up_timer -= 1
                    if level_up_timer <= 0:
                        display_level_up_message = False
                        level_up_timer = 60

                # Spawn enemies
                if enemy_spawn_counter > enemy_spawn_timer:
                    x_pos = random.randint(0, SCREEN_WIDTH - 40)
                    enemy = Enemy(x_pos, 0, 50, enemy_speed)
                    enemies.add(enemy)
                    enemy_spawn_counter = 0
                else:
                    enemy_spawn_counter += 1

                # Check if any enemies reach the bottom
                for enemy in enemies:
                    if enemy.rect.y > GAME_AREA_HEIGHT:
                        player.lives -= 1
                        enemies.empty()  # Clear all enemies

                        if player.lives > 0:
                            display_lives_left_pause(screen, player, scoreboard, 2)
                        else:
                            game_over = True
                            display_lives_left_pause(screen, player, scoreboard, 2)

            # Drawing
            screen.fill(BLACK)

            if game_over:
                scoreboard.display_game_over(screen)
                scoreboard.display_play_again(screen)  # Ask if the player wants to play again
            else:
                # Draw the game area (80%)
                pygame.draw.rect(screen, GREEN, [0, GAME_AREA_HEIGHT, SCREEN_WIDTH, 5])  # Green bottom line
                screen.blit(player.image, player.rect)
                projectiles.draw(screen)
                enemies.draw(screen)

                # Draw the HUD (20%)
                scoreboard.draw(screen, player)

                # Display level-up message if leveling up
                if display_level_up_message:
                    scoreboard.display_level_up(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

