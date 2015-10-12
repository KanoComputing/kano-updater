
# paths.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#
# Path variables used throught the game.


import os


# game top level directory - 'flappy-judoka'
base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# setting Resources paths - fonts and images
res_path = os.path.join(base_path, 'res')
images_path = os.path.join(res_path, 'images')
fonts_path = os.path.join(res_path, 'fonts')
sounds_path = os.path.join(res_path, 'sounds')
