# clean.py
#
# Copyright (C) 2015-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The check-in procedure of the updater that runs on every boot


from kano.logging import logger

from kano_updater.status import UpdaterStatus


def clean(dry_run=False):
    status = UpdaterStatus.get_instance()

    old_status = status.state
    msg = "The status of the updater at boot was: {}".format(status.state)
    logger.info(msg)

    if status.state == UpdaterStatus.DOWNLOADING_UPDATES:
        # The download was interrupted, go back one state
        status.state = UpdaterStatus.UPDATES_AVAILABLE

    elif status.state == UpdaterStatus.UPDATES_INSTALLED:
        # Show a dialog and change the state back to no updates
        status.state = UpdaterStatus.NO_UPDATES
        status.is_urgent = False

    if status.state != old_status:
        msg = "The status was changed to: {}".format(status.state)
        logger.info(msg)

    status.notifications_muted = False

    if not dry_run:
        status.save()

    return old_status
