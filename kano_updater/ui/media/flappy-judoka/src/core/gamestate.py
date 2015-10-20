
# gamestate.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# The heart of the game logic is in a form of a Finite State Machine.
# The running gamestate is managed by the central (singleton) class - Gamestate.
# The Gamestate communicates events to the Display through notifications (interface).
#
# Each individual state has its own controls and actors it updates.
# Ultimately, each individual state dictates what actors the Display renders.
#
# The FSM is: IntroState > NewGameState > FlappyFlyingState > GameOverState > NewGameState > ...


import pygame

from src.actors.flappy import Flappy
from src.actors.pipe import PipeManager
from src.actors.ground import GroundManager
from src.graphics.collision import check_collision
from src.utils import debugger

from kano_profile.tracker import track_data


class Gamestate(object):
    '''
    This is the central Gamestate class, a singleton.

    It runs the current state, manages state transitions (as well as the game exit
    condition), and notifies any listeners of game state changes.
    '''

    class GamestateChangeListener(object):
        def on_intro(self):
            pass

        def on_new_game(self):
            pass

        def on_flappy_flying(self):
            pass

        def on_game_over(self):
            pass

    _singleton_instance = None

    def __init__(self):
        if Gamestate._singleton_instance:
            raise Exception('This class is a singleton!')
        else:
            Gamestate._singleton_instance = self

        self.gamestate_change_listeners = list()

    def setup(self):
        '''
        This method is called by the gameloop in order to initialise the gamestate.
        '''
        self.current_state = IntroState()
        self._is_running = True  # flag for the gameloop to determine when to exit

    @staticmethod
    def get():
        if not Gamestate._singleton_instance:
            debugger('FATAL ERROR: Gamestate: get: Gamestate was not initialised!', fatal=True)
        return Gamestate._singleton_instance

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        self._current_state = new_state

        if isinstance(new_state, IntroState):
            debugger('Gamestate: current_state.setter: Setting state to IntroState')
            self.call_gamestate_change_listeners_on_intro()
        elif isinstance(new_state, NewGameState):
            debugger('Gamestate: current_state.setter: Setting state to NewGameState')
            self.call_gamestate_change_listeners_on_new_game()
        elif isinstance(new_state, FlappyFlyingState):
            debugger('Gamestate: current_state.setter: Setting state to FlappyFlyingState')
            self.call_gamestate_change_listeners_on_flappy_flying()
        elif isinstance(new_state, GameOverState):
            debugger('Gamestate: current_state.setter: Setting state to GameOverState')
            self.call_gamestate_change_listeners_on_game_over(self.current_state.score)
        else:
            debugger('FATAL ERROR: Gamestate: current_state.setter: Given state is not valid!', fatal=True)

    def add_gamestate_change_listener(self, listener):
        if not isinstance(listener, self.GamestateChangeListener):
            debugger('FATAL ERROR: Gamestate: set_gamestate_change_listener:'
                     ' Given listener is not an instance of GamestateChangeListener!', fatal=True)
        self.gamestate_change_listeners.append(listener)

    def call_gamestate_change_listeners_on_intro(self):
        for listener in self.gamestate_change_listeners:
            listener.on_intro()

    def call_gamestate_change_listeners_on_new_game(self):
        for listener in self.gamestate_change_listeners:
            listener.on_new_game()

    def call_gamestate_change_listeners_on_flappy_flying(self):
        for listener in self.gamestate_change_listeners:
            listener.on_flappy_flying()

    def call_gamestate_change_listeners_on_game_over(self, score):
        for listener in self.gamestate_change_listeners:
            listener.on_game_over(score)

    def update(self, delta_t):
        '''
        This is the entry point into updating the game logic.
        It calls the update method of the currently running gamestate.

        It is called in the Gameloop as long as the game is running.
        '''
        drawables = self.current_state.update(delta_t)
        return drawables

    @property
    def is_running(self):
        '''
        This method is used by the Gameloop in order to determine
        whether or not to quit the game.
        '''
        return self._is_running

    def quit(self):
        debugger('Gamestate: quit: Setting _is_running to False')
        self._is_running = False


class GamestateTemplate(object):
    '''
    This is the base class for an individual game state.

    The update method encapsulates the gamestate update mechanics.
    First, update the controls. Second, update the actors and score.
    '''

    # the keys used to Quit the game
    QUIT_KEYS = [
        pygame.K_ESCAPE,
        pygame.K_q
    ]

    def __init__(self):
        self.state_instance = Gamestate.get()

    def update(self, delta_t):
        '''
        The central Gamestate class will call this method
        in order to update the individual state.
        '''
        drawables = list()

        for event in pygame.event.get():
            if not hasattr(event, 'key') or event.type is not pygame.KEYDOWN:
                continue

            # these controls apply to all states that subclass the template
            elif event.key in self.QUIT_KEYS:
                debugger('GamestateTemplate: update: Pressed a QUIT key')
                self.state_instance.quit()

            else:
                # update controls specific to the individial state
                # the stop flag is used to avoid drawing if the state changes
                stop = self.state_controls(event)
                if stop:
                    return drawables

        # update the individual state
        drawables = self.state_update(delta_t)
        return drawables

    def state_controls(self, event):
        pass  # Subclasses: implement this!

    def state_update(self):
        pass  # Subclasses: implement this!


class IntroState(GamestateTemplate):
    '''
    This is the first state the game starts into.
    From here, the game moves into a NewGameState.

    It serves as an introduction/banner state.
    It features a banner HUD, flappy idle animation, and ground animation.
    NOTE: The HUD is setup by the Display as it's listening for gamestate changes.
    '''

    # the keys used to go from IntroState to NewGameState
    START_KEYS = [
        pygame.K_SPACE,
        pygame.K_UP
    ]

    def __init__(self):
        super(IntroState, self).__init__()

        self.flappy = Flappy(0.5, 0.65)  # passing X, Y to Flappy
        self.flappy_group = pygame.sprite.RenderUpdates(self.flappy)
        self.ground = GroundManager()

        # create the pipes here to avoid generation (stutter) in FlappyFlying State
        self.pipes = PipeManager()

    # @Override
    def state_controls(self, event):
        if event.key in self.START_KEYS:
            debugger('IntroState: state_controls: Pressed a START key')
            self.state_instance.current_state = NewGameState(self.pipes)
            return True  # state has changed, do not call state_update
        return False

    # @Override
    def state_update(self, delta_t):
        self.flappy.idle_animation(delta_t)
        self.ground.update(delta_t)

        # returning what we actually want to draw
        return [self.flappy_group, self.ground]


class NewGameState(GamestateTemplate):
    '''
    This is the second state in which the game runs.
    From here, the game moves into a FlappyFlyingState.

    It moves Flappy to his default position in an idle animation.
    The HUD displays the state (New Game) and the controls to get started.
    '''

    # the keys used to go from NewGameState to FlappyFlyingState
    START_KEYS = [
        pygame.K_SPACE,
        pygame.K_UP
    ]

    def __init__(self, pipes):
        super(NewGameState, self).__init__()
        self.pipes = pipes

        self.flappy = Flappy(0.2, 0.4)  # passing X, Y to Flappy
        self.flappy_group = pygame.sprite.RenderUpdates(self.flappy)

        self.ground = GroundManager()

    # @Override
    def state_controls(self, event):
        if event.key in self.START_KEYS:
            debugger('NewGameState: state_controls: Pressed a START key')
            self.state_instance.current_state = FlappyFlyingState(self.flappy, self.pipes, self.ground)
            return True  # state has changed, do not call state_update
        return False

    # @Override
    def state_update(self, delta_t):
        self.flappy.idle_animation(delta_t)
        self.ground.update(delta_t)

        # returning what we actually want to draw
        return [self.flappy_group, self.ground]


class FlappyFlyingState(GamestateTemplate):
    '''
    This is the third and most important state in which the game runs.
    From here, the game moves into a GameOverState.

    The controls allow the user to make Flappy fly. The state update here involves
    updating the pipes and ground animations as well as simulating gravity for Flappy.

    It also checks for collisions with pipes and ground, handling Flappy's death
    differently in each case. The score is also calculated in the state update and
    the Display is notified through the interface.
    '''

    class ScoreChangedListener(object):
        def on_score_changed(self, score):
            pass

    # the keys used to make flappy flap
    FLAP_KEYS = [
        pygame.K_SPACE,
        pygame.K_UP
    ]

    def __init__(self, flappy, pipes, ground):
        super(FlappyFlyingState, self).__init__()
        self.flappy = flappy
        self.pipes = pipes
        self.ground = ground

        self.flappy_group = pygame.sprite.RenderUpdates(self.flappy)

        self.flappy_hit_pipe = False  # flag to allow for falling animation after pipe smash
        self.score = 0                # the number of pipes flappy passed through
        self.counted_pipe = None      # pipe we are currently going through

        self.score_changed_listeners = list()

    # @Override
    def state_controls(self, event):
        if event.key in self.FLAP_KEYS:
            debugger('FlappyFlyingState: state_controls: Pressed a FLAP key')
            if not self.flappy_hit_pipe:
                self.flappy.flap()

    # @Override
    def state_update(self, delta_t):
        # keep moving the pipes and ground as long as flappy did not crash
        if not self.flappy_hit_pipe:
            self.pipes.update(delta_t)
            self.ground.update(delta_t)

        # update flappy's Y position, simulating gravity
        self.flappy.update(delta_t)
        self.update_score()

        # checking if flappy smashed into the 2 pipes in front of him
        for pipe in self.pipes.get_flappys_next_pipes():
            if check_collision(self.flappy, pipe):
                self.flappy_hit_pipe = True

        # checking if flappy hit the ground right underneath him
        # switch to GameOver only when Flappy hits the ground
        if check_collision(self.flappy, self.ground.get_ground_under_flappy()):
            self.state_instance.current_state = GameOverState(self.pipes, self.score)

        # returning what we actually want to draw
        return [self.flappy_group, self.pipes, self.ground]

    def update_score(self):
        for i in xrange(0, len(self.pipes.pipes_list), 2):
            flappy_to_pipe = self.flappy.default_position[0] - self.pipes.pipes_list[i].position[0]
            if flappy_to_pipe > 0 and flappy_to_pipe < self.pipes.pipe_width:
                if id(self.pipes.pipes_list[i]) != self.counted_pipe:
                    self.counted_pipe = id(self.pipes.pipes_list[i])
                    self.score += 1
                    self.call_score_changed_listeners()
                    break
            else:
                break

    def add_score_changed_listener(self, listener):
        if not isinstance(listener, self.ScoreChangedListener):
            debugger('FATAL ERROR: PipeManager: add_score_changed_listener:'
                     ' Given listener is not an instance of ScoreChangedListener!', fatal=True)
        self.score_changed_listeners.append(listener)

    def call_score_changed_listeners(self):
        for listener in self.score_changed_listeners:
            listener.on_score_changed(self.score)


class GameOverState(GamestateTemplate):
    '''
    This is the forth and final state in which the game runs.
    From here, the game moves into NewGameState.

    It features a GameOverHUD which displays the score achieved.
    '''

    # the keys used to go from GameOverState to NewGameState
    START_KEYS = [
        pygame.K_SPACE,
        pygame.K_UP
    ]

    def __init__(self, pipes, score):
        super(GameOverState, self).__init__()
        self.pipes = pipes
        self.score = score

        self.pipes.reset_pipes()

        try:
            # TODO: track best score as well
            track_data('updater-flappy-judoka', {
                'score': score
            })
        except:
            debugger('ERROR: GameOverState: __init__: Tracking the users score failed!')

    # @Override
    def state_controls(self, event):
        if event.key in self.START_KEYS:
            debugger('GameOverState: state_controls: Pressed a START key')
            self.state_instance.current_state = NewGameState(self.pipes)
            return True  # state has changed, do not call state_update
        return False

    # @Override
    def state_update(self, delta_t):
        # no actors to draw during GameOver
        return list()
