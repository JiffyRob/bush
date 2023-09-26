"""
entity
 - basic entity class
 - entity container group
"""
from copy import deepcopy

import pygame

from bush import animation, util


class Entity(pygame.sprite.Sprite):
    """Basic Entity"""

    registry_groups = ("main",)
    id_handler = util.IDHandler()

    def __init__(
        self,
        pos,
        surface=None,
        groups=(),
        id=None,
        layer=None,
        topleft=False,
        no_debug=False,
        drawable=True,
    ):
        if id is None:
            id = self.id_handler.get_next()
        self._id = id
        super().__init__(groups)
        self.image = surface
        self.anim = None
        self.drawable = drawable
        if isinstance(surface, animation.Animation):
            self.anim = surface
            self.image = self.anim.image()
        if surface is None:
            self.image = pygame.Surface((0, 0))
        try:
            self._pos = pygame.Vector3(pos)
        except ValueError:
            self._pos = pygame.Vector3(pos[0], pos[1], 0)
        self.rect = self.image.get_rect()
        if topleft:
            self.rect.topleft = self._pos.xy
            self._pos.update(*self.rect.center, self._pos.z)
        else:
            self.rect.center = self._pos.xy
        self._layer = 1
        if layer is not None:
            self._layer = layer
        self.no_debug = no_debug

    @property
    def pos(self):
        return pygame.Vector2(self._pos.xy)

    @pos.setter
    def pos(self, new_val):
        self._pos.xy = new_val

    @property
    def pos3(self):
        return self._pos

    @pos3.setter
    def pos3(self, value):
        self._pos.update(value)

    def get_id(self):
        return deepcopy(self._id)

    def limit(self, map_rect):
        pass  # Static Entities don't move

    def update(self, dt):
        self.rect.center = self.pos.xy
        if self.anim:
            self.image = self.anim.image()


class Actor(Entity):
    def __init__(
        self, pos, surface=None, groups=(), id=None, layer=None, topleft=False
    ):
        super().__init__(pos, surface, groups, id, layer, topleft=topleft)
        self.velocity = pygame.Vector3()

    def update_rects(self):
        self.rect.center = self.pos

    def pos_after_limiting(self, map_rect):
        pos = self.pos
        difference = max(map_rect.top - self.rect.top, 0)
        pos.y += difference
        difference = min(map_rect.bottom - self.rect.bottom, 0)
        pos.y += difference
        difference = max(map_rect.left - self.rect.left, 0)
        pos.x += difference
        difference = min(map_rect.right - self.rect.right, 0)
        pos.x += difference
        return pos

    def limit(self, map_rect):
        old_pos = self.pos
        new_pos = self.pos_after_limiting(map_rect)
        for i in range(1):
            if old_pos[i] != new_pos[i]:
                self.velocity[i] = 0
        self.pos = new_pos
        self.update_rects()
        return new_pos == old_pos
