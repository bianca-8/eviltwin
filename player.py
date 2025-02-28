import pygame
from collections import deque
from attack import Attack
pygame.mixer.init()

class Player:
    def __init__(self, x, y, delay=0, lives=1, direction=1):
        self.x = x
        self.delay = delay
        self.ground_y = y
        self.y = y
        self.final_y = y + 50
        self.width = 100
        self.height = 100
        self.velo = 0
        self.roblox_face = False
        self.previous_state = "neutral"
        self.heart_image = self.load_image("Assets/heart.png")
        self.idle_images = [self.load_image("Assets/idle1.png"),
                            self.load_image("Assets/idle2.png")]
        self.running_images = [self.load_image("Assets/running1.png"),
                               self.load_image("Assets/running2.png"),
                               self.load_image("Assets/running3.png"),
                               self.load_image("Assets/running4.png"),
                               self.load_image("Assets/running5.png"),
                               self.load_image("Assets/running6.png")]
        self.shield_images = [self.load_image("Assets/shield1.png"),
                              self.load_image("Assets/shield2.png"),
                              self.load_image("Assets/shield3.png")]
        self.framecount = 0
        self.state = "neutral"  # Current state
        self.state_queue = deque(["neutral"] * (delay * 2 + 1))  # Queue for delayed states
        self.movement_queue = deque([(0, 0)] * (delay * 2 + 1))  # Queue for delayed movements
        self.lives = lives
        self.last_attack_time = 0
        self.attack_cooldown = 500
        self.direction = direction
        self.jump_velocity = -20
        self.gravity = 0.5
        self.is_jumping = False
        self.vertical_velocity = 0
        self.attack = None  # Store current attack object

    def update(self, state, movement, opponent, keys, blocks):
        # Update delayed states
        self.state_queue.append(state)
        self.state = self.state_queue.popleft()

        if self.state != self.previous_state:
            self.framecount = 0
            self.roblox_face = False
            self.previous_state = self.state
            if self.state == "block":
                pygame.mixer.Channel(2).play(pygame.mixer.Sound('shield.wav'))

        # Update delayed movement
        self.movement_queue.append(movement)
        dx, dy = self.movement_queue.popleft()
        self.velo = dx
        if 0 < self.x + dx < 1100:  #  and self.x + dx < 0 or self.x - dx    Ensure player stays within screen bounds
            self.x += dx
        else:
            self.velo = 0

        # Gravity and Jumping Logic
        if not self.is_jumping:  # Gravity when not jumping
            if not self.is_grounded(blocks):  # If not grounded, apply gravity
                self.vertical_velocity += self.gravity
            else:
                self.vertical_velocity = 0  # Stop falling when grounded
        else:  # While jumping, continue moving upward until velocity changes
            self.vertical_velocity += self.gravity

        self.y += self.vertical_velocity  # Apply vertical movement to position

        # Check ceiling collisions
        if self.vertical_velocity < 0:  # Moving upwards
            for block in blocks:
                block_rect = block.get_rect()
                player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                if player_rect.colliderect(block_rect):  # Collision with the ceiling
                    self.y = block_rect.bottom  # Position player below the ceiling
                    self.vertical_velocity = 0  # Stop upward movement
                    break

        # Check landing on ground or platforms
        if self.y >= self.ground_y:  # Ground level
            self.y = self.ground_y
            self.is_jumping = False
            self.vertical_velocity = 0
        else:  # Check platform collisions
            for block in blocks:
                block_rect = block.get_rect()
                player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
                if player_rect.colliderect(block_rect):
                    if self.vertical_velocity > 0:  # Falling
                        self.y = block_rect.top - self.height
                        self.is_jumping = False
                        self.vertical_velocity = 0

        # Trigger Jumping
        if keys[pygame.K_UP] and self.is_grounded(blocks) and not self.is_jumping:
            self.is_jumping = True
            self.vertical_velocity = self.jump_velocity

        # Attack Logic: Check if the cooldown has elapsed
        current_time = pygame.time.get_ticks()
        if self.state == "attack" and current_time - self.last_attack_time >= self.attack_cooldown:
            # Create the attack object
            a = 1 * self.direction
            b = 100 * self.direction
            self.attack = Attack(self.x + b, self.y + 25, a, "Assets/bullets.png")  # Example image path
            pygame.mixer.Channel(1).play(pygame.mixer.Sound('whoosh.mp3'))

        # Check for collision only if an attack exists
        if self.attack:
            # Update attack position
            self.attack.x += self.attack.direction * 5

            # Define attack range
            attack_start = self.attack.x
            attack_end = self.attack.x + self.attack.width
            attack_start_y = self.attack.y
            attack_end_y = self.attack.y + self.attack.height

            # Block collision
            for block in blocks:
                block_start = block.x
                block_end = block.x + block.width
                block_start_y = block.y
                block_end_y = block.y + block.height

                x_overlap = attack_end >= block_start and attack_start <= block_end
                y_overlap = attack_end_y >= block_start_y and attack_start_y <= block_end_y

                if x_overlap and y_overlap:
                    self.attack = None  # Stop the attack on block collision
                    break  # Exit the block loop

            # Define opponent range
            opponent_start = opponent.x
            opponent_end = opponent.x + opponent.width
            opponent_start_y = opponent.y
            opponent_end_y = opponent.y + opponent.height

            x_overlap = attack_end >= opponent_start and attack_start <= opponent_end
            y_overlap = attack_end_y >= opponent_start_y and attack_start_y <= opponent_end_y

            if x_overlap and y_overlap:
                current_time = pygame.time.get_ticks()
                if opponent.state != "block" and current_time - self.last_attack_time >= self.attack_cooldown:
                    opponent.lives -= 1
                    self.last_attack_time = current_time
                elif opponent.state == "block":
                    opponent.roblox_face = True

            # Remove attack if out of bounds (optional cleanup)
            if self.attack and (self.attack.x < 0 or self.attack.x > 1200):
                self.attack = None  # Reset attack when out of bounds

        if self.lives <= 0:
            self.height = 50
            self.is_jumping = True  # Enable gravity-based fall
            self.vertical_velocity += self.gravity  # Apply gravity
            self.y += self.vertical_velocity  # Update position

            if self.y >= self.ground_y:  # Land on the ground
                self.y = self.ground_y
                self.is_jumping = False  # Stop falling
                self.vertical_velocity = 0

    def get_image(self):
        try:
            # Animation frame rate control
            frame_delay = 20  # Number of game frames to wait before switching animation frames
            if self.framecount % frame_delay == 0:
                if self.lives > 0:
                    if self.state != "block":
                        if self.is_jumping or self.velo != 0:  # Use running frames during jump
                            self.current_frame = self.running_images[
                                (self.framecount // frame_delay) % len(self.running_images)]
                        else:
                            self.current_frame = self.idle_images[(self.framecount // frame_delay) % len(self.idle_images)]
                    else:
                        if self.roblox_face == False:
                            self.current_frame = self.shield_images[(self.framecount // frame_delay) % 2]
                        else:
                            self.current_frame = self.shield_images[2]
                else:
                    self.height = 50
                    self.vertical_velocity = 0  # Reset velocity
                    self.current_frame = self.load_image("Assets/dead.png")

            self.framecount += 1

            if self.direction == 1:
                return pygame.transform.scale(self.current_frame, (self.width, self.height))
            else:
                return pygame.transform.scale(pygame.transform.flip(self.current_frame, True, False),
                                              (self.width, self.height))

        except pygame.error:
            return None

    def load_image(self, path):
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, (self.width, self.height))
        except pygame.error:
            return pygame.Surface((self.width, self.height)).convert()

    def draw_lives(self, screen):
        heart_width, heart_height = 30, 27  # Heart dimensions
        spacing = 10  # Space between hearts

        # Calculate the total width of all the hearts plus spacing
        total_width = self.lives * heart_width + (self.lives - 1) * spacing

        # Calculate the starting X position to center the hearts above the player
        start_x = self.x + (self.width - total_width) // 2

        # Position the hearts above the player
        start_y = self.y - heart_height - 10  # 10 pixels above the player

        # Draw the hearts
        for i in range(self.lives):
            heart_x = start_x + i * (heart_width + spacing)
            heart_y = start_y
            scaled_heart = pygame.transform.scale(self.heart_image, (heart_width, heart_height))
            screen.blit(scaled_heart, (heart_x, heart_y))

    def draw(self, screen):
        screen.blit(self.get_image(), (self.x, self.y))

        if self.attack:
            self.attack.draw(screen)
            self.attack.x += self.attack.direction * 5

        self.draw_lives(screen)

    def is_grounded(self, blocks):
        """Checks if the player is on the ground or a platform."""
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for block in blocks:
            block_rect = block.get_rect()
            # Check if the player's feet are within the block's top surface
            if (
                    block_rect.left < player_rect.centerx < block_rect.right  # Feet are horizontally within block
                    and abs(player_rect.bottom - block_rect.top) <= 5  # Feet are close to the top surface
            ):
                return True
        return False