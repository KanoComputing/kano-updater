#
# Tasks that are done with every update
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import sys
import traceback

from kano_updater.utils import update_home_folders_from_skel, run_for_every_user
from kano.utils import run_cmd_log
from kano.logging import logger

from kano_updater.progress import Phase


def run_aux_tasks(progress):
    progress.split(
        Phase('updating-home-folders',
              _('Updating home folders from template')),
        Phase('refreshing-kdesk',
              _('Refreshing the desktop')),
        Phase('expanding-rootfs',
              _('Expanding filesystem partitions')),
        Phase('prune-kano-content',
              _('Removing unnecessary kano-content entries')),
        Phase('syncing',
              _('Syncing'))
    )

    progress.start('updating-home-folders')

    try:
        update_home_folders_from_skel()
    except Exception:
        logger.error("Updating home folders failed. See the traceback bellow:")
        _type, _value, tb = sys.exc_info()
        for tb_line in traceback.format_tb(tb):
            logger.error(tb_line)

    progress.start('refreshing-kdesk')
    _refresh_kdesk()
    progress.start('expanding-rootfs')
    _expand_rootfs()
    progress.start('prune-kano-content')
    _kano_content_prune()
    progress.start('syncing')
    _sync()


def _refresh_kdesk():
    # Ignoring the return value here if the refresh fails
    run_cmd_log('kdesk -r')


def _expand_rootfs():
    # TODO: Do we care about the return value?
    run_cmd_log('/usr/bin/expand-rootfs')


def _sync():
    sync_cmd = 'kano-sync --skip-kdesk --sync --backup --upload-tracking-data -s'
    run_for_every_user(sync_cmd)


def _kano_content_prune():
    # kano-content needs to be ran as sudo
    kano_content_cmd = 'sudo kano-content prune'
    run_for_every_user(kano_content_cmd)
