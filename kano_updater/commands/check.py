#
# Checking to see if updates exist
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import time

from kano.network import is_internet
from kano.logging import logger

from kano_updater.apt_wrapper import apt_handle
from kano_updater.status import UpdaterStatus
from kano_updater.progress import DummyProgress
from kano_updater.utils import is_server_available
import kano_updater.priority as Priority

KANO_SOURCES_LIST = '/etc/apt/sources.list.d/kano.list'


def check_for_updates(progress=None):
    status = UpdaterStatus.get_instance()

    # FIXME: FOR DEBUGGING ONLY
    #status.state = UpdaterStatus.UPDATES_AVAILABLE
    #status.last_check = int(time.time())
    #status.save()
    #return True

    if not progress:
        progress = DummyProgress()

    if status.state != UpdaterStatus.NO_UPDATES:
        msg = _('No need to check for updates')
        logger.info(msg)

        # This was a successful check, so we need to update the timestamp.
        status.last_check = int(time.time())
        status.save()

        # Return True in all cases except when the state is UPDATES_INSTALLED
        # In that case, we've just updated and don't want to check for updates
        # again.
        return status.state != UpdaterStatus.UPDATES_INSTALLED

    if not is_internet():
        err_msg = _('Must have internet to check for updates')
        logger.error(err_msg)
        progress.fail(err_msg)

        # Not updating the timestamp. The check failed.
        return False

    if not is_server_available():
        err_msg = _('Could not connect to the download server')
        logger.error(err_msg)
        progress.fail(err_msg)

        # Not updating the timestamp. The check failed.
        return False


    update_type = _do_check(progress)
    if update_type == Priority.NONE:
        status.state = UpdaterStatus.NO_UPDATES
        logger.debug('No updates available')
        rv = False
    else:
        if update_type == Priority.URGENT:
            status.is_urgent = True

        status.state = UpdaterStatus.UPDATES_AVAILABLE
        logger.debug('Updates available')
        rv = True

    status.last_check = int(time.time())
    status.save()

    return rv


def _do_check(progress):
    apt_handle.update(progress, sources_list=KANO_SOURCES_LIST)

    if apt_handle.is_update_avaliable(priority=Priority.URGENT):
        return Priority.URGENT

    if apt_handle.is_update_avaliable():
        return Priority.STANDARD

    return Priority.NONE
