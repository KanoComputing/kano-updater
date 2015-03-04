#
# Tasks that are done with every update
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


from kano_updater.utils import update_home_folders_from_skel
from kano.utils import run_cmd_log


def run_aux_tasks():
    # TODO: We might want to keep this in install()
    update_home_folders_from_skel()

    _refresh_kdesk()
    _expand_rootfs()


def _refresh_kdesk():
    # Ignoring the return value here if the refresh fails
    run_cmd_log('kdesk -r')


def _expand_rootfs():
    # TODO: Do we care about the return value?
    run_cmd_log('/usr/bin/expand-rootfs')
