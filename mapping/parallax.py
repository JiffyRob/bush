import pygame

from bush import util


class LoopedSurface(pygame.sprite.Sprite):
    def __init__(self, surface, scroll_factor, size, alpha=False):
        self.surface = surface
        self.is_anim = not isinstance(self.surface, pygame.Surface)
        self.size = size
        self.scroll_factor = scroll_factor
        self.alpha = alpha
        self.pos = pygame.Vector2(0, 0)
        super().__init__()

    @property
    def image(self):
        image = self.surface
        if self.is_anim:
            image = self.surface.image()
        return util.repeat(image, self.size, self.pos * self.scroll_factor)

    @property
    def rect(self):
        return pygame.FRect(self.pos, self.size)
