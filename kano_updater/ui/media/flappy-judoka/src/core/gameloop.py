
# gameloop.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# Keeping the game in a running loop.
#
# The class starts by setting up the game logic and the display.
# Then the loop does three things:
#    - gets the time between the drawing of two frames
#    - updates the game logic: actors, collisions, score
#    - updates the display: draws the gamestate's representation


import pygame

from src.core.gamestate import Gamestate
from src.graphics.display import Display
from src.graphics.sound import Sound
from src.utils import debugger


class Gameloop(object):
    '''
    This class is used by the binary 'bin/flappy-judoka'.

    It ticks the time, updates the game logic, and draws a new frame.
    '''

    # the maximum fps the game will be running at
    FRAMES_PER_SECOND = 60

    def __init__(self):
        self.clock = pygame.time.Clock()

        self.setup()

    def setup(self):
        self.display = Display()
        self.sound = Sound()
        self.gamestate = Gamestate()

        # given that there is some iteraction between the game view
        # and the game logic, separate the setup for both
        self.display.setup()
        self.sound.setup()
        self.gamestate.setup()

    def run(self):
        debugger('Gameloop: run: Starting gameloop')

        while self.gamestate.is_running:
            # get the elapsed time since last tick and cap the fps
            delta_t_ms = self.clock.tick(self.FRAMES_PER_SECOND)
            delta_t_sec = delta_t_ms / 1000.0
            fps = self.clock.get_fps()

            drawables = self.gamestate.update(delta_t_sec)
            self.display.update(drawables, fps)

        debugger('Gameloop: run: Exiting gameloop')
