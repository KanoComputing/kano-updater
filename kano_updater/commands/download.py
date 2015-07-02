#
# Managing downloads of apt and pip packages for the upgrade
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from kano.network import is_internet
from kano.logging import logger
from kano.utils import read_file_contents_as_lines, ensure_dir

from kano_updater.paths import PIP_PACKAGES_LIST
from kano_updater.status import UpdaterStatus
from kano_updater.apt_wrapper import apt_handle
from kano_updater.progress import DummyProgress, Phase
from kano_updater.utils import run_pip_command, is_server_available
from kano_updater.commands.check import check_for_updates


class DownloadError(Exception):
    pass


def download(progress=None):
    status = UpdaterStatus.get_instance()

    if not progress:
        progress = DummyProgress()

    if status.state == UpdaterStatus.NO_UPDATES:
        progress.split(
            Phase(
                'checking',
                _('Checking for updates'),
                10,
                is_main=True
            ),
            Phase(
                'downloading',
                _('Downloading updates'),
                90,
                is_main=True
            )
        )
        progress.start('checking')
        check_for_updates(progress=progress)
        if status.state == UpdaterStatus.NO_UPDATES:
            progress.finish(_('No updates to download'))
            return False

        progress.start('downloading')

    elif status.state == UpdaterStatus.UPDATES_DOWNLOADED:
        err_msg = _('Updates have been downloaded already')
        logger.error(err_msg)
        progress.abort(err_msg)
        return True

    elif status.state == UpdaterStatus.DOWNLOADING_UPDATES:
        err_msg = _('The download is already running')
        logger.error(err_msg)
        progress.abort(err_msg)
        return False

    elif status.state == UpdaterStatus.INSTALLING_UPDATES:
        err_msg = _('Updates are already being installed')
        logger.error(err_msg)
        progress.abort(err_msg)
        return False

    if not is_internet():
        err_msg = _('Must have internet to download the updates')
        logger.error(err_msg)
        progress.fail(err_msg)
        return False

    if not is_server_available():
        err_msg = _('Could not connect to the download server')
        logger.error(err_msg)
        progress.fail(err_msg)
        return False

    status.state = UpdaterStatus.DOWNLOADING_UPDATES
    status.save()

    try:
        success = do_download(progress, status)
    except Exception as err:
        progress.fail(err.message)
        logger.error(err.message)

        status.state = UpdaterStatus.UPDATES_AVAILABLE
        status.save()

        return False

    status.state = UpdaterStatus.UPDATES_DOWNLOADED
    status.save()

    return success


def do_download(progress, status):
    progress.split(
        Phase(
            'downloading-pip-pkgs',
            'Downloading Python packages',
            10,
            is_main=True
        ),
        Phase(
            'updating-sources',
            'Updating apt sources',
            40,
            is_main=True
        ),
        Phase(
            'downloading-apt-packages',
            'Downloading apt packages',
            50,
            is_main=True
        )
    )

    _cache_pip_packages(progress)
    _cache_deb_packages(progress)

    progress.finish('Done downloading')
    # TODO: Figure out if it has actually worked
    return True


def _cache_pip_packages(progress):
    """
        Downloads all updatable python modules and caches them in pip's
        internal pacakge cache.
    """

    phase_name = 'downloading-pip-pkgs'
    progress.start(phase_name)

    pip_cache = '/var/cache/kano-updater/pkg_cache'

    ensure_dir(pip_cache)

    packages = read_file_contents_as_lines(PIP_PACKAGES_LIST)
    progress.init_steps(phase_name, len(packages))

    for pkg in packages:
        progress.next_step(phase_name, "Downloading {}".format(pkg))

        # The `--no-install` parameter has been deprecated in pip. However, the
        # version of pip in wheezy doesn't yet support the new approach which
        # is supposed to provide the same behaviour.
        args = "install --upgrade --download '{}' '{}'".format(pip_cache, pkg)
        success = run_pip_command(args)

        # TODO: abort the install?
        if not success:
            msg = "Downloading the '{}' pip package failed.".format(pkg)
            logger.error(msg)


def _cache_deb_packages(progress):
    progress.start('updating-sources')
    apt_handle.update(progress=progress)

    progress.start('downloading-apt-packages')
    apt_handle.cache_updates(progress)
