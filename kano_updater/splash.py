# splash.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Configure boot splash.


import os


def set_splash_interrupted():
    """Change the bootup splash to Recovery Mode for next boot."""

    # TODO: Use kano_i18n.assets to grab the locale of the image used in
    # the services below.
    os.system('systemctl disable boot-splash-start.service')
    os.system('systemctl enable recovery-boot-splash.service')


def clear_splash():
    """Change the bootup splash to the default one for next boot."""

    # TODO: Use kano_i18n.assets to grab the locale of the image used in
    # the services below.
    os.system('systemctl disable recovery-boot-splash.service')
    os.system('systemctl enable boot-splash-start.service')
