import pygame

class Ground:
    def __init__(self, y, width, height, image_path):
        self.y = y
        self.width = width
        self.height = height
        self.image = self.load_image(image_path)

    def load_image(self, path):
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, (self.width, self.height))
        except pygame.error:
            print(f"Warning: Could not load image at {path}. Using fallback surface.")
            return pygame.Surface((self.width, self.height)).convert()

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (0, self.y))