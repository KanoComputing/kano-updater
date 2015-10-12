
# display.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# This is the main Game View, the game rendering window.


import random
import pygame

from src.core.gamestate import Gamestate
from src.graphics.hud import IntroHUD, NewGameHUD, FlappyFlyingHUD, GameOverHUD
from src.graphics.assets import Assets
from src.utils import debugger


class Display(object):
    '''
    This is the main Game View, the game rendering window.
    It presents the running Gamestate to the player.

    It sets the pygame display mode and screen resolution, listens for notifications
    from Gamestate by implementing the interface, composes and draws the background,
    and renders on each frame the drawables it's given, as well as the HUD on top.

    The frame by frame rendering unfortunately does not make use of DirtySprite
    with LayeredDirty grouping due to pygame on the RPI - different implementations?

    The drawables are esentially objects which need to have
    clear() and draw() methods - See pygame.sprite.RenderUpdates.
    '''

    # default values for the Display resolution
    # these may be overriden by parameters cmdline args in bin/flappy-judoka: main()
    WIDTH = 0.52
    HEIGHT = 0.65

    GAME_TITLE = 'Flappy Judoka'

    def __init__(self):

        # if the resolution was not changed through cmdline args, use the default scaling
        if self.WIDTH < 1 and self.HEIGHT < 1:
            monitor_info = pygame.display.Info()
            debugger('Display: __init__: Monitor resolution is {}x{}'.format(monitor_info.current_w, monitor_info.current_h))
            self.WIDTH = int(self.WIDTH * monitor_info.current_w)
            self.HEIGHT = int(self.HEIGHT * monitor_info.current_h)

        debugger('Display: __init__: Setting game resolution {}x{}'.format(self.WIDTH, self.HEIGHT))
        self.display = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption(self.GAME_TITLE)

        # TODO: remove this if font sizes in HUDs are scaled
        if self.HEIGHT < 400:
            debugger('WARNING: flappy-judoka: main: Height resolution is below the recommended value 400!')

        # initialising and loading assets based on screen resolution
        Assets(self.WIDTH, self.HEIGHT)

        # compose and draw the background
        self.randomise_background()
        self.draw_background()

    def setup(self):
        '''
        This method is called by the Gameloop in order to initialise the Display.

        It provides the implementation of the state change listener
        such that the Display can react on specific state transitions.
        '''
        Gamestate.get().add_gamestate_change_listener(self.mGamestateChangeListener(self))

    def randomise_background(self):
        # pick a random background from the list
        index = random.randint(0, len(Assets.get().BACKGROUND_IMAGES) - 1)
        background_image = Assets.get().BACKGROUND_IMAGES[index]
        background_color = Assets.get().BACKGROUND_COLORS[index]

        # compose the background by filling the surface with a color
        self.background = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.background.fill(background_color)

        # and draw as many background assets one after another as needed
        no_of_background_images = int(self.WIDTH / background_image.get_width()) + 1
        y = self.HEIGHT * 0.88 - background_image.get_width() / 2.0
        for i in xrange(no_of_background_images):
            x = int(i * background_image.get_width())
            self.background.blit(background_image, (x, y))

    def draw_background(self):
        # draw the background over the display, effectively clearing everything on it
        self.display.blit(self.background, (0, 0))

    def update(self, drawables, fps):
        '''
        This is the games main rendering method.
        Each time it is called, a new frame gets drawn on the screen.

        It is called in the Gameloop as long as the game is running.
        '''
        for drawable in drawables:
            # instead of drawing the background every time, clear just the rects
            # that have changed, and draw the updates on top
            drawable.clear(self.display, self.background)
            drawable.draw(self.display)

        # draw the HUD on top of everything
        self.hud.update(fps)

        # update the entire screen
        pygame.display.update()  # TODO: improve the drawing pipeline

    # Implements
    class mGamestateChangeListener(Gamestate.GamestateChangeListener):
        def __init__(self, parent):
            self.parent = parent

        def on_intro(self):
            debugger('Display: mGamestateChangeListener: on_intro: Setting the IntroHUD')
            self.parent.hud = IntroHUD(self.parent.display)

        def on_new_game(self):
            debugger('Display: mGamestateChangeListener: on_new_game: Redrawing background')
            self.parent.randomise_background()
            self.parent.draw_background()
            self.parent.hud = NewGameHUD(self.parent.display)

        def on_flappy_flying(self):
            debugger('Display: mGamestateChangeListener: on_flappy_flying: Redrawing background')
            self.parent.draw_background()
            self.parent.hud = FlappyFlyingHUD(self.parent.display, self.parent.background)

        def on_game_over(self, score):
            debugger('Display: mGamestateChangeListener: on_game_over: Redrawing background')
            self.parent.draw_background()
            self.parent.hud = GameOverHUD(self.parent.display, score)
