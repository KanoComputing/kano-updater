#
# Managing the upgrade procedure
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import pip
import sys
import time

from kano.logging import logger

from kano_updater.paths import PIP_PACKAGES_LIST, SYSTEM_VERSION_FILE
from kano_updater.status import UpdaterStatus
from kano_updater.os_version import OSVersion, bump_system_version, \
    TARGET_VERSION
from kano_updater.scenarios import PreUpdate, PostUpdate
from kano_updater.apt_wrapper import apt_handle
from kano_updater.auxiliary_tasks import run_aux_tasks
from kano_updater.progress import DummyProgress, Phase
from kano_updater.utils import supress_output
from kano_updater.commands.download import download


class InstallError(Exception):
    pass


def install(progress=None):
    status = UpdaterStatus.get_instance()
    logger.debug("Installing update (updater state = {})".format(status.state))

    if not progress:
        progress = DummyProgress()

    if status.state == UpdaterStatus.INSTALLING_UPDATES:
        progress.abort(_('The install is already running'))
        return False
    elif status.state != UpdaterStatus.UPDATES_DOWNLOADED:
        progress.split(
            Phase(
                'download',
                _('Downloading updates'),
                30
            ),
            Phase(
                'install',
                _('Installing updates'),
                70
            ),
        )

        progress.start('download')
        if not download(progress):
            return False

        progress.start('install')

    do_install(progress, status)


def do_install(progress, status):
    status.state = UpdaterStatus.INSTALLING_UPDATES
    status.save()

    progress.split(
        Phase(
            'init',
            _('Starting Update'),
            10
        ),
        Phase(
            'updating-itself',
            _('Updating Itself'),
            10
        ),
        # Implement relaunch signal
        Phase(
            'preupdate',
            _('Running The Preupdate Scripts'),
            10
        ),
        Phase(
            'updating-pip-packages',
            _('Updating Pip Packages'),
            15
        ),
        Phase(
            'updating-deb-packages',
            _('Updating Deb Packages'),
            15
        ),
        Phase(
            'postupdate',
            _('Running The Postupdate Scripts'),
            10
        ),
        Phase(
            'aux-tasks',
            'Performing auxiliary tasks',
            10
        )
    )

    progress.start('init')
    apt_handle.fix_broken(progress)

    # determine the versions (from and to)
    system_version = OSVersion.from_version_file(SYSTEM_VERSION_FILE)

    msg = "Upgrading from {} to {}".format(system_version, TARGET_VERSION)
    logger.debug(msg)

    # set up the scenarios and check whether they cover updating
    # from this version
    preup = PreUpdate(system_version)
    postup = PostUpdate(system_version)
    if not (preup.covers_update() and postup.covers_update()):
        title = _('Unfortunately, your version of Kano OS is too old '
                  'to be updated through the updater.')
        description = _('You will need to download the image of the '
                        'OS and reflash your SD card.')

        msg = "{}: {}".format(title, description)
        progress.error(msg)
        raise InstallError(msg)

    old_updater = apt_handle.get_package('kano-updater')


    progress.start('updating-itself')  #  - apt updating packages here too
    apt_handle.upgrade('kano-updater', progress)

    # relaunch the process
    new_updater = apt_handle.get_package('kano-updater')
    if old_updater.installed.version != new_updater.installed.version:
        # Need to relaunch updater
        logger.debug(_('The updater has been updated, relaunching.'))
        pass

    progress.start('preupdate')  # - per script
    try:
        preup.run()
    except Exception as e:
        logger.error(_('The pre-update scenarios failed.'))
        sys.exit(e)

    install_pip_packages(progress)
    install_deb_packages(progress)

    progress.start('postupdate')  # - per script
    try:
        postup.run()
    except Exception as e:
        logger.error(_('The post-update scenarios failed.'))
        sys.exit(e)

    bump_system_version()

    progress.start('aux-tasks')
    run_aux_tasks(progress)

    # save status - available and no-updates
    status.state = UpdaterStatus.NO_UPDATES
    status.last_update = int(time.time())
    status.save()


def install_deb_packages(progress):
    progress.start('updating-deb-packages')
    apt_handle.upgrade_all(progress)


def install_pip_packages(progress):
    progress.start('updating-pip-packages')
    supress_output(pip.main, ['install', '--upgrade', '-r', PIP_PACKAGES_LIST])
