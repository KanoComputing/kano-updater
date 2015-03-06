#
# Managing downloads of apt and pip packages for the upgrade
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import pip

from kano.network import is_internet

from kano_updater.paths import PIP_PACKAGES_LIST
from kano_updater.status import UpdaterStatus
from kano_updater.apt_wrapper import apt_handle
from kano_updater.progress import DummyProgress, Phase
from kano_updater.utils import supress_output


class DownloadError(Exception):
    pass


def download(progress=None):
    status = UpdaterStatus()

    if status.state == UpdaterStatus.UPDATES_DOWNLOADED:
        raise DownloadError(_('Updates have been downloaded already'))

    if not is_internet():
        raise DownloadError(_('Must have internet to download the updates'))

    if status.state == UpdaterStatus.DOWNLOADING_UPDATES:
        raise DownloadError(_('The download is already running'))

    if not progress:
        progress = DummyProgress()

    do_download(progress, status)


def do_download(progress, status):
    status.state = UpdaterStatus.DOWNLOADING_UPDATES
    status.save()

    progress.split(
        Phase(
            'downloading-pip-pkgs',
            'Downloading Python packages',
            10
        ),
        Phase(
            'updating-sources',
            'Updating apt sources',
            40
        ),
        Phase(
            'downloading-apt-packages',
            'Downloading apt packages',
            50
        ),
        phase_name='root'
    )

    _cache_pip_packages(progress)
    _cache_deb_packages(progress)

    status.state = UpdaterStatus.UPDATES_DOWNLOADED
    status.save()

    progress.finish('Done downloading')


def _cache_pip_packages(progress):
    """
        Downloads all updatable python modules and caches them in pip's
        internal pacakge cache.
    """

    progress.start('downloading-pip-pkgs')

    # TODO: This could be done in a thread in a way that we could read and
    #       parse the progress in real-time.

    # The `--no-install` parameter has been deprecated in pip. However, the
    # version of pip in wheezy doesn't yet support the new approach which is
    # supposed to provide the same behaviour.
    supress_output(pip.main, ['install', '--upgrade', '--no-install', '-r',
                              PIP_PACKAGES_LIST])


def _cache_deb_packages(progress):
    progress.start('updating-sources')
    apt_handle.update(progress=progress)

    progress.start('downloading-apt-packages')
    apt_handle.cache_updates(progress)
