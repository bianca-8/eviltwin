import pygame

class Attack:
    def __init__(self, x, y, direction, image_path):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 50
        self.direction = direction  # 1 for right, -1 for left
        self.image = self.load_image(image_path)

    def load_image(self, path):
        try:
            image = pygame.image.load(path)
            if self.direction == 1:
                return pygame.transform.scale(image, (self.width, self.height))
            else:
                return pygame.transform.scale(pygame.transform.flip(image, True, False), (self.width, self.height))
        except pygame.error:
            print(f"Warning: Could not load image at {path}. Using fallback surface.")
            return pygame.Surface((self.width, self.height)).convert()

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))