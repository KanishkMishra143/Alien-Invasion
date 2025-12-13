import pygame
from pygame.sprite import Sprite
import random

class Powerup(Sprite):
    """A class to represent a power-up."""

    def __init__(self, ai_game):
        """Initialize the power-up and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Create the power-up's image and rect.
        self.image = pygame.Surface([20, 20])
        self.image.fill((255, 255, 0)) # Yellow
        self.rect = self.image.get_rect()

        self.rect.x = random.randint(0, self.settings.screen_width - self.rect.width)
        self.rect.y = -self.rect.height

        # Store the power-up's position as a float.
        self.y = float(self.rect.y)

        self.speed = 1.0

    def update(self):
        """Move the power-up down the screen."""
        self.y += self.speed
        self.rect.y = self.y
