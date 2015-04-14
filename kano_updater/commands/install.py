#
# Managing the upgrade procedure
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import time

from kano.logging import logger
from kano.utils import read_file_contents_as_lines
from kano.network import is_internet

from kano_updater.paths import PIP_PACKAGES_LIST, SYSTEM_VERSION_FILE
from kano_updater.status import UpdaterStatus
from kano_updater.os_version import OSVersion, bump_system_version, \
    TARGET_VERSION
from kano_updater.scenarios import PreUpdate, PostUpdate
from kano_updater.apt_wrapper import apt_handle
from kano_updater.auxiliary_tasks import run_aux_tasks
from kano_updater.progress import DummyProgress, Phase, Relaunch
from kano_updater.utils import run_pip_command
from kano_updater.commands.download import download


class InstallError(Exception):
    pass


def install(progress=None):
    status = UpdaterStatus.get_instance()
    logger.debug("Installing update (updater state = {})".format(status.state))

    if not progress:
        progress = DummyProgress()

    if status.state == UpdaterStatus.INSTALLING_UPDATES:
        msg = 'The install is already running'
        logger.warn(msg)
        progress.abort(_(msg))
        return False
    elif status.state != UpdaterStatus.UPDATES_DOWNLOADED:
        logger.debug('Updates weren\'t downloaded, running download first.')
        progress.split(
            Phase(
                'download',
                _('Downloading updates'),
                40,
                is_main=True
            ),
            Phase(
                'install',
                _('Installing updates'),
                60,
                is_main=True
            ),
        )

        progress.start('download')
        if not download(progress):
            logger.error('Downloading updates failed, cannot update.')
            return False

        progress.start('install')

    try:
        return do_install(progress, status)
    except Relaunch as err:
        raise
    except Exception as err:
        # Reset the state back to the previous one, so the updater
        # doesn't get stuck in 'installing' forever.
        status.state = UpdaterStatus.UPDATES_DOWNLOADED
        status.save()

        logger.error(err.message)
        progress.fail(err.message)

        return False


def do_install(progress, status):
    status.state = UpdaterStatus.INSTALLING_UPDATES
    status.save()

    progress.split(
        Phase(
            'init',
            _('Starting Update'),
            10,
            is_main=True
        ),
        Phase(
            'updating-itself',
            _('Updating Itself'),
            10,
            is_main=True
        ),
        Phase(
            'preupdate',
            _('Running The Preupdate Scripts'),
            10,
            is_main=True
        ),
        Phase(
            'updating-pip-packages',
            _('Updating Pip Packages'),
            15,
            is_main=True
        ),
        Phase(
            'updating-deb-packages',
            _('Updating Deb Packages'),
            15,
            is_main=True
        ),
        Phase(
            'postupdate',
            _('Running The Postupdate Scripts'),
            10,
            is_main=True
        ),
        Phase(
            'aux-tasks',
            'Performing auxiliary tasks',
            10,
            is_main=True
        )
    )

    progress.start('init')
    apt_handle.clear_cache()
    apt_handle.fix_broken(progress)

    # determine the versions (from and to)
    system_version = OSVersion.from_version_file(SYSTEM_VERSION_FILE)

    msg = "Upgrading from {} to {}".format(system_version, TARGET_VERSION)
    logger.info(msg)

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
        logger.error("Updating from a version that is no longer supported" + \
                     "()".format(system_version))
        progress.error(msg)
        raise InstallError(msg)

    old_updater = apt_handle.get_package('kano-updater').installed.version

    progress.start('updating-itself')
    apt_handle.upgrade('kano-updater', progress)

    # relaunch if the updater has changed
    new_updater = apt_handle.get_package('kano-updater')
    if old_updater != new_updater.installed.version:
        # Remove the installation in progress status so it doesn't
        # block the start of the new instance.
        status.state = UpdaterStatus.UPDATES_DOWNLOADED
        status.save()

        logger.info(_('The updater has been updated, relaunching.'))
        progress.relaunch()
        return False

    progress.start('preupdate')
    try:
        preup.run()
    except Exception as e:
        logger.error('The pre-update scenarios failed.')
        logger.error(str(e))
        progress.abort(_('The pre-update tasks failed.'))
        raise

    logger.debug('Updating pip packages')
    progress.start('updating-pip-packages')
    install_pip_packages(progress)

    logger.debug('Updating deb packages')
    progress.start('updating-deb-packages')
    install_deb_packages(progress)

    progress.start('postupdate')
    try:
        postup.run()
    except Exception as e:
        logger.error('The post-update scenarios failed.')
        logger.error(str(e))
        progress.abort(_('The post-update tasks failed.'))
        raise

    bump_system_version()

    # We don't care too much when these fail
    progress.start('aux-tasks')
    run_aux_tasks(progress)

    status.state = UpdaterStatus.UPDATES_INSTALLED
    status.last_update = int(time.time())
    status.save()

    progress.finish('Update completed')
    return True


def install_deb_packages(progress):
    apt_handle.upgrade_all(progress)


def install_pip_packages(progress):
    phase_name = progress.get_current_phase().name

    packages = read_file_contents_as_lines(PIP_PACKAGES_LIST)
    progress.init_steps(phase_name, len(packages))

    for pkg in packages:
        progress.next_step(phase_name, "Installing {}".format(pkg))

        success = run_pip_command("install --upgrade {}".format(pkg))

        if not success:
            msg = "Installing the '{}' pip package failed".format(pkg)
            logger.error(msg)
            if not is_internet():
                msg="Network is down, aborting PIP install"
                logger.error(msg)
                raise IOError(msg)
