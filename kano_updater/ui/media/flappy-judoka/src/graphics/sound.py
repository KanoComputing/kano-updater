
# sound.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# This is Sound effects class responsible for all sound playbacks.


import pygame

from src.actors.flappy import Flappy
from src.core.gamestate import Gamestate, FlappyFlyingState
from src.graphics.assets import Assets
from src.utils import debugger


class Sound(object):
    '''
    This class contains all the sound effect playbacks.

    It gets the sound objects from the Assets class and implements various
    interfaces within the game logic to receive notifications about the
    events that require sounds to play.
    '''

    def __init__(self):

        self.game_over_sound = Assets.get().GAME_OVER_SOUND
        self.start_game_sound = Assets.get().START_GAME_SOUND
        self.flappy_flap_sound = Assets.get().FLAPPY_FLAP_SOUND
        self.gained_point_sound = Assets.get().GAINED_POINT_SOUND

    def setup(self):
        '''
        This method is called by the Gameloop in order to initialise the Sound class.

        It provides the implementation of the state change listener
        such that it can play various sounds specific to state transitions.
        '''

        # check that the platform supports sound playback
        # if it doesn't, then it won't implement any listeners
        initialised = pygame.mixer.get_init()
        if initialised:
            debugger("Sound: __init__: Mixer is available and is initialised:" \
                     " frequency = {}, format = {}, channels = {}"
                     .format(initialised[0], initialised[1], initialised[2]))

            Gamestate.get().add_gamestate_change_listener(self.mGamestateChangeListener(self))
        else:
            debugger("Sound: __init__: Mixer is not available! Game will not have sounds!")

    # Implements
    class mGamestateChangeListener(Gamestate.GamestateChangeListener):
        def __init__(self, parent):
            self.parent = parent

        def on_intro(self):
            debugger("Sound: mGamestateChangeListener: on_intro: Playing start_game_sound")
            self.parent.start_game_sound.play()

        def on_new_game(self):
            pass

        def on_flappy_flying(self):
            debugger("Sound: mGamestateChangeListener: on_flappy_flying: Setting ScoreChangedListener and FlappyFlapListener")
            Gamestate.get().current_state.flappy.add_flappy_flap_listener(self.parent.mFlappyFlapListener(self.parent))
            Gamestate.get().current_state.add_score_changed_listener(self.parent.mScoreChangedListener(self.parent))

        def on_game_over(self, score):
            debugger("Sound: mGamestateChangeListener: on_game_over: Playing game_over_sound")
            self.parent.game_over_sound.play()

    # Implements
    class mScoreChangedListener(FlappyFlyingState.ScoreChangedListener):
        def __init__(self, parent):
            self.parent = parent

        def on_score_changed(self, score):
            debugger("Sound: mScoreChangedListener: on_score_changed: Playing gained_point_sound")
            self.parent.gained_point_sound.play()

    # Implements
    class mFlappyFlapListener(Flappy.FlappyFlapListener):
        def __init__(self, parent):
            self.parent = parent

        def on_flappy_flap(self):
            debugger("Sound: mFlappyFlapListener: on_flappy_flap: Playing flappy_flap_sound")
            self.parent.flappy_flap_sound.play()
