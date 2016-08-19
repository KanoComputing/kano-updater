
# pipe.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# This class encompasses the game logic for single Pipe object.


import random
import pygame

from src.graphics.collision import get_alpha_hitmask
from src.graphics.assets import Assets
from src.utils import debugger


class Pipe(pygame.sprite.Sprite):
    '''
    This class encompasses the game logic for single Pipe object.

    It can be defined as a top or bottom pipe in order to set the appropriate assets.
    Its update method simply moves the pipe from right to left.

    Notably, the moving speed here is also scaled accordingly with the display
    resolution (similar to Flappy).
    '''

    # determines how fast the pipes move
    MOVING_SPEED = 4.5

    def __init__(self, position, is_top=False):
        super(Pipe, self).__init__()
        self.position = position

        # use different images for top and bottom pipes
        if is_top:
            self.image = Assets.get().PIPE_TOP_IMAGE
        else:
            self.image = Assets.get().PIPE_BOTTOM_IMAGE

        # scaling speed with display resolution
        self.MOVING_SPEED *= self.image.get_width()

        self.rect = self.image.get_rect()
        self.hitmask = get_alpha_hitmask(self.image, self.rect)

    def update(self, delta_t):
        '''
        This method is called by PipeManager as part of the update
        for the entire pipe "system".

        It moves the pipe from right to left.
        '''
        x, y = self.position

        # moving the pipe with a distance proportional to the time between 2 frames
        x -= delta_t * self.MOVING_SPEED
        x = round(x, 2)  # normalization with 2 decimal points precision

        self.position = (x, y)
        self.rect.center = self.position


class PipeManager(object):
    '''
    This class is the top level manager for the "system" of pipes.
    It is used both by the individual gamestates and the Display for rendering.

    It defines how the pipe heights are randomised, as well as how the continuous
    pipe barrier effect is achieved.

    The system is configurable through the class constants below, which also
    scale accordingly with the Display resolution.
    '''

    # parameters to configure pipe positions
    # the values are percentages of Display resolution
    PIPE_INIT_X = 1.3             # from which X the pipes start
    PIPE_MIN_SPACING_X = 0.28     # highest difficulty: distance between two pipes in X
    PIPE_MIN_SPACING_Y = 0.28     # highest difficulty: distance between top pipe and bottom pipe
    PIPE_MAX_SPACING_X = 0.40     # lowest difficulty: distance between two pipes in X
    PIPE_MAX_SPACING_Y = 0.40     # lowest difficulty: distance between top pipe and bottom pipe
    PIPE_SPACING_DECREASE = 0.02  # how much spacing decreases with difficulty

    # range in display height percentage for the pipe spacing center
    SPACING_FROM_Y = 0.25
    SPACING_TO_Y = 0.60

    # the number of pipes needed to fall off the screen in order to increase difficulty
    DIFFICULTY_CHANGE = 10

    def __init__(self):
        self.display_width = Assets.get().display_width
        self.display_height = Assets.get().display_height

        # scaling parameters with display resolution
        self.PIPE_INIT_X = int(self.PIPE_INIT_X * self.display_width)
        self.PIPE_MIN_SPACING_X = int(self.PIPE_MIN_SPACING_X * self.display_height)
        self.PIPE_MIN_SPACING_Y = int(self.PIPE_MIN_SPACING_Y * self.display_height)
        self.PIPE_MAX_SPACING_X = int(self.PIPE_MAX_SPACING_X * self.display_height)
        self.PIPE_MAX_SPACING_Y = int(self.PIPE_MAX_SPACING_Y * self.display_height)
        self.PIPE_SPACING_DECREASE = int(self.PIPE_SPACING_DECREASE * self.display_height)

        self.pipe_spacing_x = self.PIPE_MAX_SPACING_X
        self.pipe_spacing_y = self.PIPE_MAX_SPACING_Y

        self.pipe_width, self.pipe_height = Assets.get().PIPE_BOTTOM_IMAGE.get_size()
        debugger("PipeManager: __init__: pipe_width = {}, pipe_height = {}".format(self.pipe_width, self.pipe_height))

        # initialising parameters for randomizing top/bottom pipe y positions
        self.rand_from = int(self.display_height * self.SPACING_FROM_Y)
        self.rand_to = int(self.display_height * self.SPACING_TO_Y)
        debugger("PipeManager: __init__: (rand_from, rand_to) = {}".format((self.rand_from, self.rand_to)))

        # calculate the number of pipes needed and generate them
        self.no_of_pipes = self.display_width / (self.pipe_width + self.PIPE_MIN_SPACING_X) + 2
        debugger("PipeManager: __init__: no_of_pipes = {}".format(self.no_of_pipes))
        self.pipes_list = self.generate_pipes()
        self.pipes_group = pygame.sprite.RenderUpdates(self.pipes_list)

        self.difficulty_counter = self.no_of_pipes

    def clear(self, display, background):
        '''
        This method clears the pipes from the background and is
        called by the Display update when drawing drawables.
        '''
        self.pipes_group.clear(display, background)

    def draw(self, display):
        '''
        This method draws the pipes onto the Display surface and is
        called by the Display update when drawing drawables.
        '''
        return self.pipes_group.draw(display)

    def update(self, delta_t):
        '''
        This method updates the entire pipe "system" and is called
        by each individual game state when appropriate.

        It calls the update for each Pipe and moves the first two pipes to
        the back when they fall off the display to the left.
        '''

        # call the update function of every Pipe sprite
        for pipe in self.pipes_list:
            pipe.update(delta_t)

        # if the first two pipes fall off the screen completely
        if self.pipes_list[0].position[0] < -self.pipe_width / 2:
            debugger("PipeManager: update: A pipe object fell off the screen")

            # remove the first pipes (by X) top/bottom
            first_top_pipe = self.pipes_list.pop(0)
            first_bottom_pipe = self.pipes_list.pop(0)

            # calculate X to move first pipes to last, equally spaced
            # when the top/bottom pipes are moved to the back, randomize Y positions
            new_last_pipe_x = self.pipes_list[-1].position[0] + self.pipe_spacing_x + self.pipe_width
            new_last_pipe_top_y, new_last_pipe_bottom_y = self.randomize_pipe_y_positions()

            # first pipe (by X) becomes the last
            first_top_pipe.position = (new_last_pipe_x, new_last_pipe_top_y)
            first_bottom_pipe.position = (new_last_pipe_x, new_last_pipe_bottom_y)

            # add the pipes to the end of the list
            self.pipes_list.append(first_top_pipe)
            self.pipes_list.append(first_bottom_pipe)

            self.update_difficulty()

    def generate_pipes(self):
        # TODO: why does this take ages on the RPI?
        pipe_list = list()

        for i in xrange(self.no_of_pipes):
            x = self.PIPE_INIT_X + i * (self.PIPE_MAX_SPACING_X + self.pipe_width)
            top_y, bottom_y = self.randomize_pipe_y_positions()

            top_pipe = Pipe((x, top_y), is_top=True)
            bottom_pipe = Pipe((x, bottom_y), is_top=False)

            pipe_list.append(top_pipe)
            pipe_list.append(bottom_pipe)

        return pipe_list

    def reset_pipes(self):
        '''
        This method resets the positions of all pipes and is called
        by GameOverState when its set.

        It avoids having to create a new instance of the PipeManager
        which would generate_pipes again. For some reason, the said method
        takes a good couple of seconds!
        '''

        self.pipe_spacing_x = self.PIPE_MAX_SPACING_X
        self.pipe_spacing_y = self.PIPE_MAX_SPACING_Y

        for i in xrange(0, len(self.pipes_list), 2):
            x = self.PIPE_INIT_X + i / 2 * (self.PIPE_MAX_SPACING_X + self.pipe_width)
            top_y, bottom_y = self.randomize_pipe_y_positions()

            self.pipes_list[i].position = (x, top_y)
            self.pipes_list[i + 1].position = (x, bottom_y)

        self.difficulty_counter = self.no_of_pipes

    def update_difficulty(self):
        self.difficulty_counter += 1

        if self.difficulty_counter == self.DIFFICULTY_CHANGE:
            self.difficulty_counter = 0

            # increase the difficulty by making the spacing between the pipes smaller
            if self.pipe_spacing_x > self.PIPE_MIN_SPACING_X:
                self.pipe_spacing_x -= self.PIPE_SPACING_DECREASE
                self.pipe_spacing_y -= self.PIPE_SPACING_DECREASE
                debugger("PipeManager: update_difficulty: Making spacing smaller X = {}, Y = {}"
                         .format(self.pipe_spacing_x, self.pipe_spacing_y))
            else:
                debugger("PipeManager: update_difficulty: Highest difficulty reached! WOOHOO! Keep going!")

    def randomize_pipe_y_positions(self):
        spacing_center_y = random.randint(self.rand_from, self.rand_to)

        top_y = spacing_center_y - self.pipe_spacing_y / 2 - self.pipe_height / 2
        bottom_y = spacing_center_y + self.pipe_spacing_y / 2 + self.pipe_height / 2

        return top_y, bottom_y

    def get_flappys_next_pipes(self):
        '''
        This method returns the two pipes just in front of Flappy.
        It is called by FlappyFlyingState in its update_state method.
        '''
        for i in xrange(0, len(self.pipes_list), 2):
            # TODO: better way of using flappy's position (.. > s.d_w * 0.1)
            if self.pipes_list[i].position[0] > self.display_width * 0.2 - Assets.get().FLAPPY_UP_IMAGE.get_width():
                return self.pipes_list[i], self.pipes_list[i + 1]
