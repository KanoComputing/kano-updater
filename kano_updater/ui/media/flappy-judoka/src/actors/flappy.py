
# flappy.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# This class encompasses the game logic for Flappy - from physics, to animations.


import pygame

from src.graphics.collision import get_alpha_hitmask
from src.graphics.assets import Assets
from src.utils import debugger, rotate_center


class Flappy(pygame.sprite.Sprite):
    '''
    This class encompasses the game logic for Flappy - from physics, to animations.
    It is used in most of the individual gamestates where appropriate.

    It defines idle, flap, and dive animations which are used in the update method.
    The animations are completely controled by the class constants below and can
    be tweaked without braking anything (within reason).

    Notably, the physics (jump velocity, acceleration, max velocity, etc) scale
    accordingly with respect to the screen resolution, and is completely controled by
    the class constants below.
    '''

    # physics constants
    ACCELERATION = 2.5      # defines the gravity's strength
    MAX_VELOCITY = 0.95     # defines the max speed with which Flappy can fall
    JUMP_VELOCITY = -0.75   # defines the power with which Flappy jumps

    # animation constants
    JUMP_TILT_ANGLE = 20          # degrees - think trigonometric circle
    MAX_DIVE_TILT_ANGLE = -40     # degrees (= 320 degrees)
    IDLE_ANIMATION_MAX_Y = 0.015  # the Y offset from the default position
    IDLE_ANIMATION_SPEED = 0.06   # how fast the idle animation behaves
    FLAP_ANIMATION_SEC = 0.120    # time (120 ms) for each animation frame

    def __init__(self, scale_pos_x, scale_pos_y):
        super(Flappy, self).__init__()
        self.display_width = Assets.get().display_width
        self.display_height = Assets.get().display_height

        self.default_position = (int(scale_pos_x * self.display_width),
                                 int(scale_pos_y * self.display_height))
        debugger('Flappy: __init__: default_position = {}'.format(self.default_position))

        # scaling physics with display resolution
        self.ACCELERATION *= self.display_height
        self.MAX_VELOCITY *= self.display_height
        self.JUMP_VELOCITY *= self.display_height
        self.IDLE_ANIMATION_MAX_Y *= self.display_height
        self.IDLE_ANIMATION_SPEED *= self.display_height

        # loading flappy assets
        self.FLAPPY_UP_IMAGE = Assets.get().FLAPPY_UP_IMAGE
        self.FLAPPY_IMAGES = Assets.get().FLAPPY_IMAGES

        # the actual image that gets rendered and collision detection mask
        self.image = self.FLAPPY_IMAGES[0]
        self.rect = self.image.get_rect()
        self.hitmask = get_alpha_hitmask(self.image, self.rect)

        # setting Flappy's default values
        self.position = self.default_position
        self.velocity = 0
        self.idle_direction = -1
        self.animation_ms = 0

    def idle_animation(self, delta_t):
        '''
        This is the update method used by IntroState and NewGameState.

        It simply moves Flappy up and down.
        '''
        x, y = self.position

        # raise or lower flappy
        y += self.idle_direction * delta_t * self.IDLE_ANIMATION_SPEED
        y = round(y, 2)  # normalization with 2 decimal points precision

        self.flap_animation(delta_t)

        # change direction to UP/DOWN
        if y <= self.default_position[1] - self.IDLE_ANIMATION_MAX_Y:
            self.idle_direction = 1  # switch to going down on Y
        elif y >= self.default_position[1] + self.IDLE_ANIMATION_MAX_Y:
            self.idle_direction = -1  # switch to going up on Y

        self.position = (x, y)
        self.rect.center = self.position

    def update(self, delta_t):
        '''
        This is the update method used by FlappyFlyingState.

        It simulates gravity and performs flap and dive animations.
        '''
        x, y = self.position

        # simplistic simulation of gravity
        y += delta_t * self.velocity  # time based flappy Y position update
        y = round(y, 2)  # normalization with 2 decimal points precision
        self.velocity += delta_t * self.ACCELERATION  # time based velocity update
        self.velocity = min(self.velocity, self.MAX_VELOCITY)  # truncate velocity

        # perform the flap and dive animation
        # these can be turned OFF by simply commenting the lines below
        self.flap_animation(delta_t)
        self.dive_animation()

        self.position = (x, y)
        self.rect.center = self.position

    def flap_animation(self, delta_t):
        # keep track of the time passed in order to determine the animation image
        self.animation_ms = (self.animation_ms + delta_t) % \
                            (len(self.FLAPPY_IMAGES) * self.FLAP_ANIMATION_SEC)
        self.image = self.get_current_flappy_image()

    def get_current_flappy_image(self):
        index = int(self.animation_ms / self.FLAP_ANIMATION_SEC)
        return self.FLAPPY_IMAGES[index]

    def dive_animation(self):
        # TODO: performance optimisations
        # TODO: update self.hitmask when a rotation is performed?
        if self.velocity <= 0:
            # tilt flappy to the jump angle as long as he is gaining altitude
            self.image, self.rect = rotate_center(self.get_current_flappy_image(), self.rect, self.JUMP_TILT_ANGLE)
        else:
            # as soon as flappy starts falling, calculate the tilt angle (range [jump, max_dive] )
            # corresponding to the current velocity, i.e. half of max velocity = mid-angle between [jump, max_dive]
            tilt_angle = (self.velocity / self.MAX_VELOCITY) * \
                         (self.MAX_DIVE_TILT_ANGLE - self.JUMP_TILT_ANGLE) + self.JUMP_TILT_ANGLE
            self.image, self.rect = rotate_center(self.FLAPPY_UP_IMAGE, self.rect, tilt_angle)

    def flap(self):
        '''
        This method is used by FlappyFlyingState's controls and is
        called whenever the player presses the apropriate key.
        '''
        # staying alive, staying alive, flap flap flap flap
        if self.position[1] > 0:  # do not go above screen
            self.velocity = self.JUMP_VELOCITY
