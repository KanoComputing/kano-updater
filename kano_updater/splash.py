#
# splash.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# configure boot splash

import os
from kano_updater.ui.paths import IMAGE_PATH
from kano_i18n import assets


def set_splash_interrupted():
    # This command may not exist yet, so ignore errors
    splash_path = assets.get_path(IMAGE_PATH,
                                  'update_interrupted.png')
    os.system('kano-boot-splash-cli set {}'.format(splash_path))


def clear_splash():
    # This command may not exist yet, so ignore errors
    os.system('kano-boot-splash-cli clear')
