
# ground.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# This class encompasses the game logic for single Ground object.


import pygame

from src.graphics.collision import get_full_hitmask
from src.graphics.assets import Assets
from src.utils import debugger


class Ground(pygame.sprite.Sprite):
    '''
    This class encompasses the game logic for single Ground object.

    Notably, the moving speed here is also scaled accordingly with the display
    resolution (similar to Flappy).
    '''

    # determines how fast the ground sprites move
    MOVING_SPEED = 4.5  # TODO: make sure this and pipe MOVING_SPEED are the same

    def __init__(self, position):
        super(Ground, self).__init__()
        self.position = position

        # scaling speed with display resolution
        self.MOVING_SPEED *= Assets.get().PIPE_TOP_IMAGE.get_width()

        self.image = Assets.get().GROUND_IMAGE

        self.rect = self.image.get_rect()
        self.hitmask = get_full_hitmask(self.image, self.rect)

    def update(self, delta_t):
        '''
        This method is called by GroundManager as part of the update
        for the entire "floor" animation.
        '''
        x, y = self.position

        # moving the ground with a distance proportional to the time between 2 frames
        x -= delta_t * self.MOVING_SPEED
        x = round(x, 2)  # normalization with 2 decimal points precision

        self.position = (x, y)
        self.rect.center = self.position


class GroundManager(object):
    '''
    This class is the top level manager for the "floor assembly".

    It composes the ground out of as many Ground objects as needed in order to
    fill the Display. Similar to PipeManager, as soon as a Ground sprite falls
    off the Dispaly to the left, it is moved at the end for continuous animation.
    '''

    GROUND_Y = 0.945

    def __init__(self):
        self.display_width = Assets.get().display_width
        self.display_height = Assets.get().display_height

        # scaling ground position with display resolution
        self.GROUND_Y *= self.display_height
        debugger("GroundManager: __init__: GROUND_Y = {}".format(self.GROUND_Y))

        self.ground_width = Assets.get().GROUND_IMAGE.get_width()
        debugger("GroundManager: __init__: ground_width = {}".format(self.ground_width))

        # calculate the number of ground sprites needed and generate them
        self.no_of_grounds = self.display_width / self.ground_width + 2
        debugger("GroundManager: __init__: no_of_grounds = {}".format(self.no_of_grounds))
        self.ground_list = self.generate_ground()
        self.ground_group = pygame.sprite.RenderUpdates(self.ground_list)

    def clear(self, display, background):
        '''
        This method clears the ground sprites from the background and is
        called by the Display update when drawing drawables.
        '''
        self.ground_group.clear(display, background)

    def draw(self, display):
        '''
        This method draws the ground sprites onto the Display surface and is
        called by the Display update when drawing drawables.
        '''
        return self.ground_group.draw(display)

    def update(self, delta_t):
        '''
        This method updates the entire "floor assembly" and is called
        by each individual game state when appropriate.

        It calls the update for each Ground object and moves the first Ground
        when it falls off the display to the left.
        '''
        # call the update function of every Ground sprite
        for ground in self.ground_list:
            ground.update(delta_t)

        # if the first ground sprite falls off the screen completely, move it to the back
        if self.ground_list[0].position[0] < -self.ground_width / 2:
            first_ground = self.ground_list.pop(0)

            new_last_ground_x = self.ground_list[-1].position[0] + self.ground_width
            first_ground.position = (new_last_ground_x, first_ground.position[1])

            self.ground_list.append(first_ground)

    def generate_ground(self):
        ground_list = list()

        for i in xrange(self.no_of_grounds):
            x = i * self.ground_width
            ground_list.append(Ground((x, self.GROUND_Y)))

        return ground_list

    def get_ground_under_flappy(self):
        '''
        This method returns the Ground object that is directly under Flappy.
        It is called by FlappyFlyingState in its update_state method.
        '''
        for ground in self.ground_list:
            # TODO: better way of using flappy's position (.. > s.d_w * 0.2)
            if ground.position[0] + Assets.get().GROUND_IMAGE.get_width() / 2.0 > self.display_width * 0.2:
                return ground
        debugger("FATAL ERROR: GroundManager: get_ground_under_flappy:" \
                 " Did not find any ground under Flappy!", fatal=True)
