# paths.py
#
# Copyright (C) 2015-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Paths to UI assets


import os


PACKAGE_PATH = os.path.dirname(__file__)
MEDIA_PATH = os.path.join(PACKAGE_PATH, 'media')

IMAGE_PATH = os.path.join(MEDIA_PATH, 'images')
CSS_PATH = os.path.join(MEDIA_PATH, 'css')
FLAPPY_PATH = os.path.join(MEDIA_PATH, 'flappy-judoka', 'bin', 'flappy-judoka')

ICON_SYS_PATH = '/usr/share/icons/Kano/66x66/apps/kano-updater.png'

if os.path.exists(ICON_SYS_PATH):
    ICON_PATH = ICON_SYS_PATH
else:
    ICON_PATH = os.path.abspath(
        os.path.join(PACKAGE_PATH, '../../icon/kano-updater.png'))

WEBPAGE_URL = os.path.join(PACKAGE_PATH, 'changes_page/index.html')
