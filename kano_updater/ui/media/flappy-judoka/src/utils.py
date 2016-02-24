
# utils.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# Various utilities used throught the game.


import os
import sys
import signal
import pygame

from paths import images_path, sounds_path


TMP_DIR = '/tmp/flappy'
PID_FILE = os.path.join(TMP_DIR, 'flappy.pid')

DEBUG = False


def debugger(text, fatal=False):
    if DEBUG:
        print text
        if fatal:
            print 'debugger: Fatal error, exiting..'
    elif sys.stdin.isatty():
        pass  # TODO: output to flappy.debug in TMP_DIR
    if fatal:
        sys.exit()


def is_running():
    '''
    NOTE: This function is designed to work for the RPI!
    '''
    ensure_dir(TMP_DIR)

    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as pid_file:
            old_pid = pid_file.read()

        if os.path.exists(os.path.join('/proc', old_pid)):
            return True

    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(os.getpid()))

    return False


def ensure_dir(directory):
    '''
    Checks the validity of a path, and creates it if it doesn't exist
    '''
    if not os.path.exists(directory):
        os.makedirs(directory)


def load_image(name, colorkey=None, alpha=False):
    '''
    Loads an image into memory

    Adapted from: http://www.pygame.org/wiki/FastPixelPerfect
    '''
    path = os.path.join(images_path, name)
    try:
        image = pygame.image.load(path)
    except pygame.error:
        debugger("FATAL ERROR: utils: load_image: Could not load '{}' from '{}' !"
                 .format(name, path), fatal=True)

    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image


def load_sound(name):
    '''
    '''
    path = os.path.join(sounds_path, name)
    try:
        sound = pygame.mixer.Sound(path)
    except pygame.error:
        debugger("FATAL ERROR: utils: load_sound: Could not load '{}' from '{}' !"
                 .format(name, path), fatal=True)

    return sound


def rotate_center(image, rect, angle):
    '''
    Rotate an image while keeping its center and size.
    NOTE: ONLY WORKS WITH SQUARE IMAGES!

    Adapted from https://pygame.org/wiki/RotateCenter
    '''
    rot_image = pygame.transform.rotozoom(image, angle, 1)
    rot_rect = rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image, rot_rect


def setup_window_on_top_signal():
    signal.signal(signal.SIGUSR1, give_focus_to_game)


def give_focus_to_game(signal=None, frame=None):
    '''
    NOTE: This function is designed to work for the RPI!
    '''
    try:
        os.system('wmctrl -a "Flappy Judoka" &')
    except:
        debugger('ERROR: utils: give_focus_to_game: wmctrl failed!')


def set_window_on_top(signal=None, frame=None):
    '''
    NOTE: This function is designed to work for the RPI!
    '''
    try:
        os.system('wmctrl -r "Flappy Judoka" -b add,above &')
    except:
        debugger('ERROR: utils: set_window_on_top: wmctrl failed!')
