# recovery.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# System recovery strategies in case of inderrupted update.


from kano_init.utils import enable_console_autologin, set_ldm_autologin, \
    enable_ldm_autostart, reconfigure_autostart_policy
from kano.utils.user import get_user_unsudoed
from kano.logging import logger

from kano_updater.splash import set_splash_interrupted, clear_splash


def enable_system_recovery_flow():
    """Configure the system to start in recovery mode on next bootup.

    This sets up a few things:

    1. Replaces the normal bootup splash animation with another for recovery.
    2. Configures LightDM autologin for multi-user systems since the Updater
       runs under the user.

    Returns:
        bool - Whether the operation was successful
    """
    logger.info('Configuring recovery stategy for next boot')
    successful = True

    # Set the recovery bootup splash and replace normal bootup one.
    set_splash_interrupted()

    # Configure the system to autologin for multi-user systems. This is due
    # to the Updater process running under the user.
    try:
        user = get_user_unsudoed()
        if user:
            # TODO: Create a single function for these in kano_init.
            enable_console_autologin(user)
            set_ldm_autologin(user)
            enable_ldm_autostart()
        else:
            successful = False
    except:
        logger.error('Could not configure autologin for update recovery!')
        successful = False

    return successful


def cancel_system_recovery_flow():
    """Restore the normal bootup configuration from the recovery one.

    This essentially reverts the config made with :func:`.enable_system_recovery_flow`.

    Note:
        Be sure to reliably call this after the aforementioned function
        in order to prevent recovery boot loops.
    """
    logger.info('Aborting recovery for next boot')

    # Restore the normal bootup splash animation.
    clear_splash()

    # Reset the autologin policy and configure for normal usage.
    reconfigure_autostart_policy()
