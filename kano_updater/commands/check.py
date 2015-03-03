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

KANO_SOURCES_LIST = '/etc/apt/sources.list.d/kano.list'

def check_for_updates(min_time_between_checks=None):
    status = UpdaterStatus()

    if status.state != 'no-updates':
        return

    if min_time_between_checks:
        target_delta = float(min_time_between_checks) * 60 * 60

        time_now = time.time()
        delta = time_now - status.last_check

        if delta > target_delta:
            logger.info(_('Time check passed, doing update check!'))
        else:
            logger.info(_('Not enough time passed for a new update check!'))
            return

    apt_handle.update(sources_list=KANO_SOURCES_LIST)
    status.last_check = int(time.time())

    if apt_handle.is_update_avaliable():
        status.state = 'updates-available'
    else:
        status.state = 'no-updates'

    status.save()
