import pygame

class Mustache:
    def __init__(self):
        self.width = 50
        self.height = 20
        self.direction = -1
        self.image = self.load_image("Assets/mustache.png")

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

    def draw(self, screen, x, y):
        if self.image:
            screen.blit(self.image, (x, y))