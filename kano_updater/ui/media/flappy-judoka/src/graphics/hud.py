
# hud.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


import os
import pygame

from src.core.gamestate import Gamestate, FlappyFlyingState
from src.graphics.assets import Assets
from src.utils import debugger, DEBUG
from src.paths import fonts_path


class TemplateHUD(object):
    '''
    '''

    # font size parameters
    # TODO: scale these based on display resolution
    BANNER_FONT_SIZE = 90
    SCORE_FONT_SIZE = 80
    TITLE_FONT_SIZE = 60
    HINT_FONT_SIZE = 30

    # defining colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)
    ORANGE = (255, 132, 42)

    # parameters defining the Y position of the texts
    CONTROLS_HINT_X = 0.03
    CONTROLS_HINT_Y = 0.915

    def __init__(self, display):
        self.display = display
        self.display_width = Assets.get().display_width
        self.display_height = Assets.get().display_height

        # Font downloaded from: http://www.fontsaddict.com/font/zx-spectrum-7-bold.html
        self.font_path = os.path.join(fonts_path, 'zx_spectrum-7_bold.ttf')
        self.setup_fonts()

        self.controls_hint_text = self.hint_renderer.render('[SPACE] or [UP] to Jump', 1, self.WHITE)
        self.controls_hint_text_x = self.display_width * self.CONTROLS_HINT_X
        self.controls_hint_text_y = self.display_height * self.CONTROLS_HINT_Y

        self.quit_hint_text = self.hint_renderer.render('[ESC] or [Q] to Quit', 1, self.WHITE)
        self.quit_hint_text_x = self.display_width * self.CONTROLS_HINT_X
        self.quit_hint_text_y = self.display_height * self.CONTROLS_HINT_Y + 20

    def setup_fonts(self):
        # setting up the font renderers
        self.score_renderer = pygame.font.Font(self.font_path, self.SCORE_FONT_SIZE)
        self.banner_renderer = pygame.font.Font(self.font_path, self.BANNER_FONT_SIZE)
        self.title_renderer = pygame.font.Font(self.font_path, self.TITLE_FONT_SIZE)
        self.hint_renderer = pygame.font.Font(self.font_path, self.HINT_FONT_SIZE)
        self.fps_renderer = pygame.font.SysFont('Bariol', 30)

    def update(self, fps):
        '''
        '''

        # on every frame, all subclasses will draw the controls + quit hints
        self.display.blit(self.controls_hint_text, (self.controls_hint_text_x, self.controls_hint_text_y))
        self.display.blit(self.quit_hint_text, (self.quit_hint_text_x, self.quit_hint_text_y))

        # draw the fps if we are in debugging mode (not for production)
        if DEBUG:
            fps_text = self.fps_renderer.render('{}'.format(round(fps, 3)), 1, self.ORANGE)
            self.display.blit(fps_text, (self.display_width * 0.93, self.display_height * 0.93))

        # update the HUD specific to the individual state
        self.state_update()

    def state_update(self):
        pass  # Subclasses: implement this!


class IntroHUD(TemplateHUD):
    '''
    '''

    # parameters defining the Y position of the texts
    BANNER_Y = 0.25
    HINT_Y = 0.4

    def __init__(self, display):
        super(IntroHUD, self).__init__(display)

        self.banner_text = self.banner_renderer.render('FlappyJudoka', 1, self.ORANGE)
        self.hint_text = self.hint_renderer.render('Press [SPACE] to start!', 1, self.GRAY)

        self.banner_text_x = self.display_width / 2.0 - self.banner_text.get_width() / 2.0  # centered
        self.banner_text_y = self.display_height * self.BANNER_Y

        self.hint_text_x = self.display_width / 2.0 - self.hint_text.get_width() / 2.0  # centered
        self.hint_text_y = self.display_height * self.HINT_Y

    def state_update(self):
        '''
        '''
        self.display.blit(self.banner_text, (self.banner_text_x, self.banner_text_y))
        self.display.blit(self.hint_text, (self.hint_text_x, self.hint_text_y))


class NewGameHUD(TemplateHUD):
    '''
    '''

    # parameters defining the Y position of the texts
    TITLE_Y = 0.2
    HINT_Y = 0.5

    def __init__(self, display):
        super(NewGameHUD, self).__init__(display)

        self.title_text = self.title_renderer.render('New Game', 1, self.WHITE)
        self.hint_text = self.hint_renderer.render('Press [SPACE] to start!', 1, self.GRAY)

        self.title_text_x = self.display_width / 2.0 - self.title_text.get_width() / 2.0  # centered
        self.title_text_y = self.display_height * self.TITLE_Y

        self.hint_text_x = self.display_width / 2.0 - self.hint_text.get_width() / 2.0  # centered
        self.hint_text_y = self.display_height * self.HINT_Y

    def state_update(self):
        '''
        '''
        self.display.blit(self.title_text, (self.title_text_x, self.title_text_y))
        self.display.blit(self.hint_text, (self.hint_text_x, self.hint_text_y))


class FlappyFlyingHUD(TemplateHUD):
    '''
    '''

    # parameters defining the Y position of the texts
    SCORE_Y = 0.1

    def __init__(self, display, background):
        super(FlappyFlyingHUD, self).__init__(display)
        self.background = background

        # the score needs to be cleared and drawn everytime it updates
        self.score_text_sprite = pygame.sprite.Sprite()
        self.score_text_group = pygame.sprite.Group(self.score_text_sprite)
        self.update_score(0)

        # implement the onScoreChanged interface of FlappyFlyingState
        Gamestate.get().current_state.add_score_changed_listener(self.mScoreChangedListener(self))

    def state_update(self):
        '''
        '''
        self.score_text_group.draw(self.display)

    def update_score(self, score):
        # clear the old score
        self.score_text_group.clear(self.display, self.background)

        # render the new score and draw it on the screen
        score_text = self.score_renderer.render(str(score), 1, self.WHITE)
        self.score_text_sprite.image = score_text
        self.score_text_sprite.rect = score_text.get_rect()

        score_text_x = self.display_width / 2.0 - score_text.get_width() / 2.0  # centered
        score_text_y = self.display_height * self.SCORE_Y
        self.score_text_sprite.rect.center = (score_text_x, score_text_y)

    class mScoreChangedListener(FlappyFlyingState.ScoreChangedListener):
        def __init__(self, parent):
            self.parent = parent

        def on_score_changed(self, score):
            self.parent.update_score(score)


class GameOverHUD(TemplateHUD):
    '''
    '''

    # parameters defining the Y position of the texts
    TITLE_Y = 0.2
    SCORE_Y = 0.35
    HINT_Y = 0.5

    def __init__(self, display, score):
        super(GameOverHUD, self).__init__(display)

        self.title_text = self.title_renderer.render('Game Over', 1, self.ORANGE)
        self.score_text = self.title_renderer.render('Score {}'.format(score), 1, self.WHITE)
        self.hint_text = self.hint_renderer.render('Press [SPACE] to play again!', 1, self.GRAY)

        self.title_text_x = self.display_width / 2.0 - self.title_text.get_width() / 2.0  # centered
        self.title_text_y = self.display_height * self.TITLE_Y

        self.score_text_x = self.display_width / 2.0 - self.score_text.get_width() / 2.0  # centered
        self.score_text_y = self.display_height * self.SCORE_Y

        self.hint_text_x = self.display_width / 2.0 - self.hint_text.get_width() / 2.0  # centered
        self.hint_text_y = self.display_height * self.HINT_Y

    def state_update(self):
        '''
        '''
        self.display.blit(self.title_text, (self.title_text_x, self.title_text_y))
        self.display.blit(self.score_text, (self.score_text_x, self.score_text_y))
        self.display.blit(self.hint_text, (self.hint_text_x, self.hint_text_y))
