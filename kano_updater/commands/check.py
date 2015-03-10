#
# Checking to see if updates exist
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import time

from kano.logging import logger

from kano_updater.apt_wrapper import apt_handle
from kano_updater.status import UpdaterStatus
from kano_updater.progress import DummyProgress

KANO_SOURCES_LIST = '/etc/apt/sources.list.d/kano.list'


def check_for_updates(min_time_between_checks=0, progress=None):
    status = UpdaterStatus.get_instance()

    # FIXME: FOR DEBUGGING ONLY
    status.state = UpdaterStatus.UPDATES_AVAILABLE
    status.last_check = int(time.time())
    status.save()
    return True

    if not progress:
        progress = DummyProgress()

    if status.state != UpdaterStatus.NO_UPDATES:
        progress.abort(_('No need to check for updates'))
        return True

    if min_time_between_checks:
        target_delta = float(min_time_between_checks) * 60 * 60

        time_now = time.time()
        delta = time_now - status.last_check

        if delta > target_delta:
            logger.info(_('Time check passed, doing update check!'))
        else:
            msg = _('Not enough time passed for a new update check!')
            logger.info(msg)
            progress.abort(msg)
            return False

    if _do_check(progress):
        status.state = UpdaterStatus.UPDATES_AVAILABLE
        rv = True
    else:
        status.state = UpdaterStatus.NO_UPDATES
        rv = False

    status.last_check = int(time.time())
    status.save()

    return rv


def _do_check(progress):
    apt_handle.update(progress, sources_list=KANO_SOURCES_LIST)
    return apt_handle.is_update_avaliable()
