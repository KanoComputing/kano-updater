#
# The check-in procedure of the updater that runs on every boot
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from kano.logging import logger

from kano_updater.status import UpdaterStatus
# from kano_updater.ui.


def clean(dry_run=False):
    status = UpdaterStatus.get_instance()

    old_status = status.state
    msg = "The status of the updater at boot was: {}".format(status.state)
    logger.debug(msg)

    if status.state == UpdaterStatus.DOWNLOADING_UPDATES:
        # The download was interrupted, go back one state
        status.state = UpdaterStatus.UPDATES_AVAILABLE
    elif status.state == UpdaterStatus.INSTALLING_UPDATES:
        # The installation was interrupted, go back one state
        status.state = UpdaterStatus.UPDATES_DOWNLOADED
    elif status.state == UpdaterStatus.UPDATES_INSTALLED:
        # Show a dialog and change the state back to no updates
        status.state = UpdaterStatus.NO_UPDATES

    if status.state != old_status:
        msg = "The status was changed to: {}".format(status.state)
        logger.debug(msg)

    status.notifications_muted = False

    if not dry_run:
        status.save()

    return old_status
