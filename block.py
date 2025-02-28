import pygame

class Block:
    def __init__(self, x, y, width, height, path):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = self.load_image(path)

    def load_image(self, path):
        try:
            image = pygame.image.load(path)
            return pygame.transform.scale(image, (self.width, self.height))
        except pygame.error:
            print(f"Warning: Could not load image at {path}. Using fallback surface.")
            return pygame.Surface((self.width, self.height)).convert()

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))