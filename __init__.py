"""
Bush!

Component based engine geared toward performance and code simplicity

Named because the leaves of a bush (components of an entity) are defined seperately from the sten (entity)
But mostly because why not.

Copyright 2022 - 2023 John Robinson and Zachary Matzek
Distributed under MIT License
"""
import pygame

from bush import autotile  # TODO: get rid of this
from bush import color  # TODO: get rid of this
from bush import (
    ai,
    animation,
    asset_handler,
    collision,
    easing,
    entity,
    event_binding,
    joy_cursor,
    mapping,
    particle,
    physics,
    timer,
    util,
    util_load,
)

__all__ = (
    ai,
    animation,
    autotile,  # TODO: get rid of this
    asset_handler,
    collision,
    color,  # TODO: get rid of this
    easing,
    entity,
    event_binding,
    joy_cursor,
    particle,
    mapping,
    physics,
    timer,
    util,
    util_load,
)

pygame.init()
