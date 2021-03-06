# check.py
#
# Copyright (C) 2014-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Checking to see if updates exist


import time

from kano.network import is_internet
from kano.logging import logger
from kano.utils.shell import run_cmd_log

from kano_updater.apt_wrapper import AptWrapper
from kano_updater.status import UpdaterStatus
from kano_updater.progress import DummyProgress
from kano_updater.utils import is_server_available
import kano_updater.priority as Priority
from kano_updater.paths import KANO_SOURCES_LIST
from kano_updater.return_codes import RC, RCState


def check_for_updates(progress=None, priority=Priority.NONE, is_gui=False):
    status = UpdaterStatus.get_instance()

    if not progress:
        progress = DummyProgress()

    countdown = status.first_boot_countdown - int(time.time())

    # block update checks when:
    #  1) three days have NOT passed since the first boot
    #  2) and not checking for URGENT updates
    #  3) and the check is triggered from background hooks (not by user)
    if (countdown > 0) and (priority is not Priority.URGENT) and (not is_gui):
        return False

    if status.state not in [UpdaterStatus.NO_UPDATES, UpdaterStatus.UPDATES_DOWNLOADED]:
        msg = "No need to check for updates"
        logger.info(msg)

        # This was a successful check, so we need to update the timestamp.
        status.last_check = int(time.time())
        status.save()

        # Return True in all cases except when the state is UPDATES_INSTALLED
        # In that case, we've just updated and don't want to check for updates
        # again.
        return status.state != UpdaterStatus.UPDATES_INSTALLED

    if not is_internet():
        err_msg = N_("Must have internet to check for updates")
        logger.error(err_msg)
        progress.fail(_(err_msg))
        RCState.get_instance().rc = RC.NO_NETWORK

        # Not updating the timestamp. The check failed.
        return False

    if not is_server_available():
        err_msg = N_("Could not connect to the download server")
        logger.error(err_msg)
        progress.fail(_(err_msg))
        RCState.get_instance().rc = RC.CANNOT_REACH_KANO

        # Not updating the timestamp. The check failed.
        return False

    update_type = _do_check(progress, priority=priority)
    if update_type == Priority.NONE:
        # If the Updater is running in recovery mode, do not update the state
        # out of the installing ones, otherwise the recovery flow will quit.
        if not status.is_recovery_needed():
            status.state = UpdaterStatus.NO_UPDATES
        logger.info("No updates available")
        RCState.get_instance().rc = RC.NO_UPDATES_AVAILABLE
        rv = False
    else:
        if update_type == Priority.URGENT:
            status.notifications_muted = True
            status.is_urgent = True

        if not status.is_recovery_needed():
            status.state = UpdaterStatus.UPDATES_AVAILABLE
        logger.info("Updates available")
        logger.info("Found update of priority: {}".format(priority.priority))
        rv = True

    if priority <= Priority.STANDARD:
        status.last_check = int(time.time())

    # always check independent packages as NONE as urgent updates to
    # these packages are dealt with by the main updater
    status.updatable_independent_packages = get_ind_packages(Priority.NONE)

    status.last_check_urgent = int(time.time())

    status.save()

    return rv


def _do_check(progress, priority=Priority.NONE):
    '''
    Perform checks for all priorities greater than the one provided.
    '''
    apt_handle = AptWrapper.get_instance()

    apt_handle.update(progress, sources_list=KANO_SOURCES_LIST)
    logger.info("Checking urgent: {}".format(priority <= Priority.URGENT))
    logger.info("Checking standard: {}".format(priority <= Priority.STANDARD))
    run_cmd_log('apt-get --yes autoclean')

    if (
            priority <= Priority.URGENT
            and apt_handle.is_update_available(priority=Priority.URGENT)
        ):
        return Priority.URGENT

    if (
            priority <= Priority.STANDARD
            and apt_handle.is_update_available()
        ):
        return Priority.STANDARD

    return Priority.NONE


def get_ind_packages(priority=Priority.NONE):
    apt_handle = AptWrapper.get_instance()
    return apt_handle.independent_packages_available(priority)
