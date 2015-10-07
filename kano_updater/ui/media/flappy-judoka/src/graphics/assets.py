
# assets.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# A static object to load all game assets after the Display initialisation.


import pygame

from src.utils import debugger, load_image


class Assets(object):
    '''
    This class is the main object for game assets.
    Flappy, Pipe, Ground, Display get their assets from here.

    Also, since the Display instanciates this class, the final Display
    dimensions are also stored here for all users of the class.
    '''

    FLAPPY_SCALE = 0.13      # % of display height
    PIPE_TOP_SCALE = 0.16    # the very top part of the pipe
    PIPE_BODY_SCALE = 0.60   # pipe height = 60% of display height
    BACKGROUND_SCALE = 0.35  # background skyline = 30% of display height
    GROUND_SCALE = 0.12      # animated ground = 15% of display height (with + .03 for floating point precision)

    _singleton_instance = None

    def __init__(self, display_width, display_height):
        if Assets._singleton_instance:
            raise Exception('This class is a singleton!')
        else:
            Assets._singleton_instance = self

        self.display_width = display_width
        self.display_height = display_height

        self.load()
        self.resize()
        self.group()

    @staticmethod
    def get():
        return Assets._singleton_instance

    def load(self):
        debugger('Assets: load: Loading all game assets')

        self.FLAPPY_UP_IMAGE = load_image('flappy-up.png', colorkey=None, alpha=True)
        self.FLAPPY_MIDDLE_IMAGE = load_image('flappy-middle.png', colorkey=None, alpha=True)
        self.FLAPPY_DOWN_IMAGE = load_image('flappy-down.png', colorkey=None, alpha=True)

        # self.PIPE_TOP_IMAGE = load_image('pipe-top.png')
        self.PIPE_TOP_IMAGE = load_image('yellow-cable-top.png')
        # self.PIPE_BODY_IMAGE = load_image('pipe-body.png')
        self.PIPE_BODY_IMAGE = load_image('yellow-cable-body.png')

        # self.BACKGROUND_DAY_COLOR = (74, 190, 206)
        self.BACKGROUND_DAY_COLOR = (49, 64, 70)
        # self.BACKGROUND_DAY_IMAGE = load_image('background-skyline-day.png')
        self.BACKGROUND_DAY_IMAGE = load_image('background.png')
        # self.BACKGROUND_NIGHT_COLOR = (0, 134, 148)
        # self.BACKGROUND_NIGHT_IMAGE = load_image('background-skyline-night.png')

        self.GROUND_IMAGE = load_image('ground.png')

    def resize(self):
        self.FLAPPY_UP_IMAGE = self.aspect_ratio_scale(self.FLAPPY_UP_IMAGE, self.FLAPPY_SCALE, smooth=True)
        self.FLAPPY_MIDDLE_IMAGE = self.aspect_ratio_scale(self.FLAPPY_MIDDLE_IMAGE, self.FLAPPY_SCALE, smooth=True)
        self.FLAPPY_DOWN_IMAGE = self.aspect_ratio_scale(self.FLAPPY_DOWN_IMAGE, self.FLAPPY_SCALE, smooth=True)

        # assembling the pipes from TOP, BODY by stretching the body
        # the bottom pipe will be the fliped top one
        self.PIPE_TOP_IMAGE = self.aspect_ratio_scale(self.PIPE_TOP_IMAGE, self.PIPE_TOP_SCALE)
        self.PIPE_BODY_IMAGE = pygame.transform.scale(self.PIPE_BODY_IMAGE, (self.PIPE_TOP_IMAGE.get_width(), int(self.display_height * self.PIPE_BODY_SCALE)))
        pipe_top = pygame.Surface((self.PIPE_TOP_IMAGE.get_width(), self.display_height * self.PIPE_BODY_SCALE))
        pipe_top.set_colorkey((0, 0, 0))  # somehow, the alpha of pipe-body.png is ignored and is black instead
        pipe_top.blit(self.PIPE_BODY_IMAGE, (pipe_top.get_width() / 2.0 - self.PIPE_BODY_IMAGE.get_width() / 2.0, 0))
        pipe_top.blit(self.PIPE_TOP_IMAGE, (0, pipe_top.get_height() - self.PIPE_TOP_IMAGE.get_height()))
        self.PIPE_TOP_IMAGE = pipe_top
        self.PIPE_BOTTOM_IMAGE = pygame.transform.flip(pipe_top, False, True)

        self.BACKGROUND_DAY_IMAGE = self.aspect_ratio_scale(self.BACKGROUND_DAY_IMAGE, self.BACKGROUND_SCALE)
        # self.BACKGROUND_NIGHT_IMAGE = self.aspect_ratio_scale(self.BACKGROUND_NIGHT_IMAGE, self.BACKGROUND_SCALE)

        self.GROUND_IMAGE = self.aspect_ratio_scale(self.GROUND_IMAGE, self.GROUND_SCALE)

    def aspect_ratio_scale(self, image, scale_ratio, smooth=False):
        height = self.display_height * scale_ratio
        width = image.get_width() * (height / image.get_height())
        if smooth:
            return pygame.transform.smoothscale(image, (int(width), int(height)))
        return pygame.transform.scale(image, (int(width), int(height)))

    def group(self):
        self.FLAPPY_IMAGES = [
            self.FLAPPY_UP_IMAGE,
            self.FLAPPY_MIDDLE_IMAGE,
            self.FLAPPY_DOWN_IMAGE
        ]

        self.BACKGROUND_IMAGES = [
            self.BACKGROUND_DAY_IMAGE,
            # self.BACKGROUND_NIGHT_IMAGE
        ]

        self.BACKGROUND_COLORS = [
            self.BACKGROUND_DAY_COLOR,
            # self.BACKGROUND_NIGHT_COLOR
        ]
