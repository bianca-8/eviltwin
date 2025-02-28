import asyncio
import pygame
import sys
import time
from player import Player
from mustache import Mustache
from block import Block

# Initialize Pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.Channel(0).play(pygame.mixer.Sound('music.mp3'))

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
GROUND_Y = SCREEN_HEIGHT - 50
FPS = 120

background_image = pygame.image.load("Assets/background.jpg")
scaled_background = pygame.transform.scale(background_image, (1200, 800))

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Evil Twin")
clock = pygame.time.Clock()

# Create objects
player1 = Player(100, GROUND_Y - 100)
player2 = Player(1000, GROUND_Y - 100, delay=0, lives=5, direction=-1)  # Delayed input
mustache = Mustache()
ground = Block(0, 750, 1200, 50, "Assets/block.png")
block1 = Block(600, 400, 500, 60, "Assets/block.png")
block2 = Block(50, 300, 150, 60, "Assets/block.png")
block3 = Block(350, 600, 300, 300, "Assets/block.png")
block4 = Block(400, 200, 200, 60, "Assets/block.png")
blocks = [block1, block2, block3, block4, ground]

# title and instructions
title = pygame.image.load('Assets/title.png')
scaled_title = pygame.transform.scale(title, (380, 300))
title_size = scaled_title.get_rect().size
centered_title = [(SCREEN_WIDTH - title_size[0]) / 2, (SCREEN_HEIGHT - title_size[1]) / 2]

instructions = pygame.image.load('Assets/instructions.png')
scaled_instructions = pygame.transform.scale(instructions, (300, 220))
instructions_size = scaled_instructions.get_rect().size
centered_instructions = [800, 50]

async def main():

    # title fade in
    while pygame.key.get_pressed():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for i in range(255):
            scaled_title.set_alpha(i)
            screen.blit(scaled_title, centered_title)
            pygame.display.update()
            time.sleep(0.001)

        time.sleep(1.5)

        for i in range(255, 0, -1):
            scaled_title.set_alpha(i)
            screen.blit(scaled_title, centered_title)
            pygame.display.update()
            time.sleep(0.001)
        break

    # Game loop
    running = True
    while running:
        # Blit the scaled image to the screen at (0, 0)
        screen.blit(scaled_background, (0, 0))
        screen.blit(scaled_instructions, centered_instructions)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if player1.lives > 0 and player2.lives > 0:
            # Input handling for player1
            keys = pygame.key.get_pressed()
            player1_movement = (0, 0)
            if keys[pygame.K_LEFT]:  # Move left
                player1_movement = (-3, 0)
                player1.direction = -1
            if keys[pygame.K_RIGHT]:  # Move right
                player1_movement = (3, 0)
                player1.direction = 1

            if keys[pygame.K_f]:  # Block
                player1.update("block", player1_movement, player2, keys, blocks)
            elif keys[pygame.K_SPACE]:  # Attack
                player1.update("attack", player1_movement, player2, keys, blocks)
            else: # Neutral
                player1.update("neutral", player1_movement, player2, keys, blocks)

            # Input handling for player2
            player2_movement = (0, 0)
            if keys[pygame.K_LEFT]:  # Move left (mirrored)
                player2_movement = (3, 0)
                player2.direction = 1
                mustache.direction = -1
            if keys[pygame.K_RIGHT]:  # Move right (mirrored)
                player2_movement = (-3, 0)
                player2.direction = -1
                mustache.direction = 1

            if keys[pygame.K_f]:  # Block (mirrored)
                player2.update("block", player2_movement, player1, keys, blocks)
            elif keys[pygame.K_SPACE]:  # Attack (mirrored)
                player2.update("attack", player2_movement, player1, keys, blocks)
            else:
                player2.update("neutral", player2_movement, player1, keys, blocks)

            # Draw everything
            ground.draw(screen)
            player1.draw(screen)
            player2.draw(screen)

            if player2.lives > 0:
                mustache.draw(screen, player2.x + 25, player2.y + 40)

            for block in blocks:
                block.draw(screen)

            # Update display and tick
            pygame.display.flip()
            clock.tick(FPS)

        else:
            screen.blit(scaled_background, (0, 0))
            font = pygame.font.SysFont('Comic Sans MS', 30)

            if player1.lives <= 0:
                lose = pygame.image.load("Assets/lose.png")
                scaled_endgame = pygame.transform.scale(lose, (600, 200))
            else:
                win = pygame.image.load("Assets/win.png")
                scaled_endgame = pygame.transform.scale(win, (600, 200))

            screen.blit(scaled_endgame, (300, 200))

            restart = pygame.image.load("Assets/restart.png")
            scaled_restart = pygame.transform.scale(restart, (150, 75))
            Quit = pygame.image.load("Assets/quit.png")
            scaled_Quit = pygame.transform.scale(Quit, (150, 75))

            screen.blit(scaled_restart, (300, 600))
            screen.blit(scaled_Quit, (725, 600))

            await asyncio.sleep(0)
            pygame.display.flip()

            # wait for quit/restart
            wait = True
            while wait:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        wait = False
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        if 300 < x < 450 and 600 < y < 675:  # click restart button
                            player1.lives = 1
                            player2.lives = 5
                            player1.x, player1.y = 100, GROUND_Y - 100
                            player2.x, player2.y = 1000, GROUND_Y - 100
                            player1.state = "neutral"
                            player1.height = 100
                            player2.height = 100
                            player2.state = "neutral"
                            pygame.mixer.Channel(0).play(pygame.mixer.Sound('music.mp3'))
                            wait = False
                        elif 725 < x < 875 and 600 < y < 675:  # click quit button
                            wait = False
                            running = False

asyncio.run(main())

pygame.quit()
sys.exit()