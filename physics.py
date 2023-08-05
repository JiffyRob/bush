"""
physics - simple top down physics + shape primitives
"""
from collections import namedtuple

import pygame

from bush import collision, util

TYPE_STATIC = 0
TYPE_DYNAMIC = 1
TYPE_TRIGGER = 2

MAX_SPEED = 5

PhysicsData = namedtuple("PhysicsData", ("type", "collision_group"))


def optimize_for_physics(group):
    groups = (
        pygame.sprite.Group(),
        pygame.sprite.Group(),
        pygame.sprite.Group(),
    )
    rects = [None, None, None, None]
    for sprite in group.sprites():
        type = sprite.physics_data.type
        try:
            rects[type].union_ip(sprite.rect)
        except AttributeError:
            rects[type] = sprite.rect.copy()
        groups[type].add(sprite)
    for key in (TYPE_STATIC,):
        if rects[key] is None:
            continue
        megamask = pygame.Mask(rects[key].size)
        for sprite in groups[key]:
            megamask.draw(sprite.mask, sprite.rect.topleft)
            group.remove(sprite)
        new_sprite = pygame.sprite.Sprite()
        new_sprite.rect = megamask.get_rect()
        new_sprite.pos = new_sprite.rect.center
        new_sprite.mask = megamask
        new_sprite.physics_data = PhysicsData(key, group)
        group.add(new_sprite)


def dynamic_update(self, dt, stop_on_collision=False):
    checked_velocity = pygame.Vector2()
    sprite_velocity = self.velocity.copy() * dt
    callbacks = (static_collision, dynamic_collision, trigger_collision)
    for sprite in self.physics_data.collision_group:
        if sprite is self:
            continue
        callbacks[sprite.physics_data.type](self, sprite, dt, stop_on_collision)
    while checked_velocity != sprite_velocity:
        checked_velocity.move_towards_ip(sprite_velocity, MAX_SPEED)
        self.pos += checked_velocity
        self.update_rects()
        for sprite in self.physics_data.collision_group:
            if sprite is self:
                continue
            callbacks[sprite.physics_data.type](self, sprite, dt, stop_on_collision)


def resolve_collision(to_move, to_resolve):
    searcher = util.search(to_move.pos)
    collided = False
    while collision.collide_rect_mask(
        to_move.collision_rect, to_resolve.mask, to_resolve.rect.topleft
    ):
        to_move.pos = pygame.Vector2(next(searcher))
        to_move.update_rects()
        collided = True
    return collided


def static_collision(dynamic, static, dt, stop_on_collision):
    collided = resolve_collision(dynamic, static)
    if collided and stop_on_collision:
        dynamic.velocity *= 0
    if collided and hasattr(dynamic, "on_collision"):
        dynamic.on_collision(static, dt)
    if collided and hasattr(static, "on_collision"):
        static.on_collision(dynamic, dt)
    return collided


def dynamic_collision(dynamic1, dynamic2, dt, stop_on_collision):
    if dynamic1.collision_rect.colliderect(dynamic2.collision_rect):
        if hasattr(dynamic1, "on_collision"):
            print("callback", dynamic1, dynamic2)
            dynamic1.on_collision(dynamic2, dt)
        if hasattr(dynamic2, "on_collision"):
            print("callback", dynamic2, dynamic1)
            dynamic2.on_collision(dynamic1, dt)


def trigger_collision(dynamic, trigger, dt, stop_on_collision):
    if collision.collide_rect_mask(
        dynamic.collision_rect, trigger.mask, trigger.rect.topleft
    ):
        if hasattr(dynamic, "on_collision"):
            dynamic.on_collision(trigger, dt)
        if hasattr(trigger, "on_collision"):
            trigger.on_collision(dynamic, dt)
