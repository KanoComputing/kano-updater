# download.py
#
# Copyright (C) 2015-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Managing downloads of apt packages for the upgrade


from kano.network import is_internet
from kano.logging import logger
from kano.utils import read_file_contents_as_lines, ensure_dir

from kano_updater.status import UpdaterStatus
from kano_updater.apt_wrapper import AptWrapper
from kano_updater.progress import DummyProgress, Phase
from kano_updater.utils import is_server_available, show_kano_dialog, \
    make_normal_prio
from kano_updater.commands.check import check_for_updates
import kano_updater.priority as Priority
from kano_updater.return_codes import RC, RCState


class DownloadError(Exception):
    pass


def download(progress=None, gui=True):
    status = UpdaterStatus.get_instance()
    dialog_proc = None

    if not progress:
        progress = DummyProgress()

    if status.state in [UpdaterStatus.NO_UPDATES, UpdaterStatus.UPDATES_DOWNLOADED]:
        progress.split(
            Phase(
                'checking',
                _("Checking for updates"),
                10,
                is_main=True
            ),
            Phase(
                'downloading',
                _("Downloading updates"),
                90,
                is_main=True
            )
        )
        pre_check_state = status.state
        progress.start('checking')
        check_for_updates(progress=progress)

        if status.state == UpdaterStatus.NO_UPDATES:
            if pre_check_state == UpdaterStatus.NO_UPDATES:
                msg = N_("No updates to download")
                logger.info(msg)
                progress.finish(_(msg))
                return False
            elif pre_check_state == UpdaterStatus.UPDATES_DOWNLOADED:
                err_msg = N_("Latest updates have been downloaded already")
                logger.info(err_msg)
                progress.abort(_(err_msg))
                return True

        progress.start('downloading')

    elif status.state == UpdaterStatus.DOWNLOADING_UPDATES:
        err_msg = N_("The download is already running")
        logger.error(err_msg)
        progress.abort(_(err_msg))
        return False

    if not is_internet():
        err_msg = N_("Must have internet to download the updates")
        logger.error(err_msg)
        progress.fail(_(err_msg))
        RCState.get_instance().rc = RC.NO_NETWORK
        return False

    if not is_server_available():
        err_msg = N_("Could not connect to the download server")
        logger.error(err_msg)
        progress.fail(_(err_msg))
        RCState.get_instance().rc = RC.CANNOT_REACH_KANO
        return False

    # show a dialog informing the user of an automatic urgent download
    if status.is_urgent and not gui:
        # TODO: mute notifications?
        title = _("Updater")
        description = _(
            "Kano HQ has just released a critical update that will repair"
            " some important things on your system! We'll download these"
            " automatically, and ask you to schedule the install when they finish."
        )
        buttons = _("OK:green:1")
        dialog_proc = show_kano_dialog(title, description, buttons, blocking=False)

    # If the Updater is running in recovery mode, do not update the state
    # out of the installing ones, otherwise the recovery flow will quit.
    if not status.is_recovery_needed():
        status.state = UpdaterStatus.DOWNLOADING_UPDATES
        status.save()

    priority = Priority.NONE

    if status.is_urgent:
        priority = Priority.URGENT
        logger.info("Urgent update detected, bumping to normal priority")
        make_normal_prio()

    logger.debug("Downloading with priority {}".format(priority.priority))

    try:
        success = do_download(progress, status, priority=priority, dialog_proc=dialog_proc)
    except Exception as err:
        progress.fail(err.message)
        logger.error(err.message)
        RCState.get_instance().rc = RC.UNEXPECTED_ERROR

        status.state = UpdaterStatus.UPDATES_AVAILABLE
        status.save()

        return False

    if not status.is_recovery_needed():
        status.state = UpdaterStatus.UPDATES_DOWNLOADED
        status.save()

    return success


def do_download(progress, status, priority=Priority.NONE, dialog_proc=None):
    progress.split(
        Phase(
            'updating-sources',
            _("Updating apt sources"),
            40,
            is_main=True
        ),
        Phase(
            'downloading-apt-packages',
            _("Downloading apt packages"),
            60,
            is_main=True
        )
    )

    _cache_deb_packages(progress, priority=priority)

    progress.finish(_("Done downloading"))

    # kill the dialog if it is still on
    if dialog_proc:
        dialog_proc.terminate()

    # TODO: Figure out if it has actually worked
    return True

def _cache_deb_packages(progress, priority=Priority.NONE):
    apt_handle = AptWrapper.get_instance()

    progress.start('updating-sources')
    apt_handle.update(progress=progress)

    progress.start('downloading-apt-packages')
    apt_handle.cache_updates(progress, priority=priority)
