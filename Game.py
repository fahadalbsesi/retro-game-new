import pygame
import random
import sys
import os

pygame.init()

WIDTH, HEIGHT = 640, 480
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Space Invaders")

# Load images
player_img = pygame.image.load(os.path.join("images", "player.png")).convert_alpha()
enemy_img = pygame.image.load(os.path.join("images", "enemy.png")).convert_alpha()
bullet_img = pygame.image.load(os.path.join("images", "bullet.png")).convert_alpha()

# Load sounds
shoot_sound = pygame.mixer.Sound(os.path.join("sounds", "shoot.wav"))
enemy_hit_sound = pygame.mixer.Sound(os.path.join("sounds", "enemy_hit.wav"))
death_sound = pygame.mixer.Sound(os.path.join("sounds", "death.wav"))

# Resize images
player_img = pygame.transform.scale(player_img, (40, 24))
enemy_img = pygame.transform.scale(enemy_img, (30, 30))
bullet_img = pygame.transform.scale(bullet_img, (5, 10))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH - self.rect.width)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

def show_message(message, color, font_size, x, y):
    font = pygame.font.Font(None, font_size)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(x, y))
    window.blit(text, text_rect)

def reset_game():
    player.rect.centerx = WIDTH // 2
    player.rect.bottom = HEIGHT - 10

def write_error_to_file(error_message):
    with open("error_log.txt", "a") as file:
        file.write(error_message + "\n")

def restart_game():
    global game_over, score

    # Reset game over and score
    game_over = False
    score = 0  # Reset the score to 0

    # Reset the player position
    player.rect.centerx = WIDTH // 2
    player.rect.bottom = HEIGHT - 10

    # Clear existing bullets on the screen
    for bullet in bullets:
        bullet.kill()
    bullets.empty()

    # Clear existing enemies and spawn new ones
    enemies.empty()
    for _ in range(10):
        enemy = Enemy()
        enemies.add(enemy)
        all_sprites.add(enemy)

    game_over = False

def main():
    try:
        global player, enemies, bullets, all_sprites, game_over  # Declare all relevant variables as global

        clock = pygame.time.Clock()
        all_sprites = pygame.sprite.Group()

        player = Player()
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()

        all_sprites.add(player)

        score = 0
        font = pygame.font.Font(None, 30)

        game_over = False
        game_over_time = 0

        restart_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 40, 100, 50)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not game_over:
                        bullet = Bullet(player.rect.centerx, player.rect.top)
                        all_sprites.add(bullet)
                        bullets.add(bullet)
                        shoot_sound.play()

                    if event.key == pygame.K_r and game_over:
                        restart_game()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if game_over and restart_button_rect.collidepoint(event.pos):
                        restart_game()

            if not game_over:
                all_sprites.update()

                # Check for collisions between bullets and enemies
                hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
                for bullet, enemy_list in hits.items():
                    score += len(enemy_list)
                    enemy_hit_sound.play()

                # Spawn new enemies
                while len(enemies) < 10:
                    enemy = Enemy()
                    enemies.add(enemy)
                    all_sprites.add(enemy)

                # Check for collisions between player and enemies
                if pygame.sprite.spritecollide(player, enemies, True):
                    death_sound.play()
                    game_over = True
                    game_over_time = pygame.time.get_ticks()

            window.fill((0, 0, 0))
            all_sprites.draw(window)

            # Draw score
            score_text = font.render("Score: {}".format(score), True, (255, 255, 255))
            window.blit(score_text, (10, 10))

            if game_over:
                game_over_text = font.render("Game Over", True, (255, 0, 0))
                window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
                show_message("Press R to Restart", (255, 255, 255), 24, WIDTH // 2, HEIGHT // 2 + 40)

            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        write_error_to_file(error_message)

if __name__ == "__main__":
    main()