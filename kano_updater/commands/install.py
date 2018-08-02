# install.py
#
# Copyright (C) 2015-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Managing the upgrade procedure


import time

from kano.logging import logger
from kano.utils.disk import get_free_space
from kano.utils.file_operations import read_file_contents_as_lines
from kano.utils.shell import run_cmd, run_cmd_log
from kano.network import is_internet

from kano_updater.status import UpdaterStatus
from kano_updater.os_version import bump_system_version, get_target_version, \
    get_system_version, OSVersion
from kano_updater.scenarios import PreUpdate, PostUpdate
from kano_updater.apt_wrapper import AptWrapper
from kano_updater.auxiliary_tasks import run_aux_tasks
from kano_updater.disk_requirements import SPACE_BUFFER, MIN_REQ_SPACE, UPGRADE_3_8_0_SPACE
from kano_updater.progress import DummyProgress, Phase, Relaunch
from kano_updater.commands.download import download
from kano_updater.commands.check import get_ind_packages
import kano_updater.priority as Priority
from kano_updater.utils import track_data_and_sync
from kano_updater.return_codes import RC, RCState


class InstallError(Exception):
    pass


def install(progress=None, gui=True):
    progress.split(
        Phase(
            'checks',
            _('Checking system'),
            1,
            is_main=True
        ),
        Phase(
            'download',
            _("Downloading updates"),
            39,
            is_main=True
        ),
        Phase(
            'install',
            _("Installing updates"),
            60,
            is_main=True
        ),
    )

    progress.start('checks')
    status = UpdaterStatus.get_instance()
    logger.debug("Installing update (updater state = {})".format(status.state))

    if not progress:
        progress = DummyProgress()

    priority = Priority.NONE

    if status.is_urgent:
        priority = Priority.URGENT

    run_cmd('sudo kano-empty-trash')
    enough_space, space_msg = check_disk_space(priority)
    if not enough_space:
        logger.error(space_msg)
        progress.abort(_(space_msg))
        RCState.get_instance().rc = RC.NOT_ENOUGH_SPACE
        return False

    logger.debug("Downloading any new updates that might be available.")
    progress.start('download')
    if not download(progress):
        logger.error("Downloading updates failed, cannot update.")
        return False

    progress.start('install')

    logger.debug("Installing with priority {}".format(priority.priority))

    try:
        return do_install(progress, status, priority=priority)
    except Relaunch as err:
        raise
    except Exception as err:
        # Reset the state back to the previous one, so the updater
        # doesn't get stuck in 'installing' forever.
        status.state = UpdaterStatus.UPDATES_DOWNLOADED
        status.save()

        logger.error(err.message)
        progress.fail(err.message)
        RCState.get_instance().rc = RC.UNEXPECTED_ERROR
        return False


def do_install(progress, status, priority=Priority.NONE):
    status.state = UpdaterStatus.INSTALLING_UPDATES
    status.save()

    track_data_and_sync('update-install-started', dict())

    if priority == Priority.URGENT:
        install_urgent(progress, status)
    else:
        install_standard(progress, status)

    run_cmd_log('apt-get --yes autoremove')
    run_cmd_log('apt-get --yes clean')

    status.state = UpdaterStatus.UPDATES_INSTALLED

    # Clear the list of independent packages.
    # They should all have been updated by the full update.
    status.updatable_independent_packages = []

    status.last_update = int(time.time())
    status.is_scheduled = False
    status.save()

    progress.finish(_("Update completed"))
    track_data_and_sync('update-install-finished', dict())

    return True


def install_ind_package(progress, package):
    status = UpdaterStatus.get_instance()
    # install an independent package.

    previous_state = status.state

    # Allow installing only if the updater is in certain safe states.
    if status.state not in [UpdaterStatus.NO_UPDATES,
                            UpdaterStatus.UPDATES_AVAILABLE,
                            UpdaterStatus.UPDATES_INSTALLED]:
        msg = "The install is already running"
        logger.warn(msg)
        progress.abort(msg)
        return False

    if package not in status.updatable_independent_packages:
        msg = "tried to install non-independent package {} using update_ind_pkg".format(package)
        logger.warn(msg)
        progress.abort(msg)
        return False

    status.state = UpdaterStatus.INSTALLING_INDEPENDENT
    status.save()

    update_sources_phase = 'updating-sources'
    installing_idp_phase = 'installing-idp-package'
    progress.split(
        Phase(
            update_sources_phase,
            _("Updating apt sources"),
            10
        ),
        Phase(
            installing_idp_phase,
            _("Installing independent package"),
            90
        )
    )

    apt_handle = AptWrapper.get_instance()

    progress.start(update_sources_phase)
    apt_handle.update(progress)

    progress.start(installing_idp_phase)
    apt_handle.upgrade(package, progress)

    status.state = previous_state
    status.last_update = int(time.time())

    # always check independent packages as NONE as urgent updates to
    # these packages are dealt with by the main updater
    status.updatable_independent_packages = get_ind_packages(Priority.NONE)
    status.is_scheduled = False
    status.save()

    progress.finish(_("Update completed"))
    return True


def install_urgent(progress, status):
    progress.split(
        Phase(
            'installing-urgent',
            _("Installing Hotfix"),
            100,
            is_main=True
        )
    )
    logger.debug("Installing urgent hotfix")
    apt_handle = AptWrapper.get_instance()
    packages_to_update = apt_handle.packages_to_be_upgraded()
    progress.start('installing-urgent')
    install_deb_packages(progress, priority=Priority.URGENT)
    status.is_urgent = False
    try:
        from kano_profile.tracker import track_data
        track_data('updated_hotfix', {
            'packages': packages_to_update
        })
        logger.debug("Tracking Data: '{}'".format(packages_to_update))
    except ImportError as imp_exc:
        logger.error("Couldn't track hotfix installation, failed to import " \
                     "tracking module: [{}]".format(imp_exc))
    except Exception:
        pass


def install_standard(progress, status):
    progress.split(
        Phase(
            'init',
            _("Starting Update"),
            10,
            is_main=True
        ),
        Phase(
            'updating-itself',
            _("Updating Itself"),
            10,
            is_main=True
        ),
        Phase(
            'preupdate',
            _("Running The Preupdate Scripts"),
            10,
            is_main=True
        ),
        Phase(
            'updating-deb-packages',
            _("Updating Deb Packages"),
            30,
            is_main=True
        ),
        Phase(
            'postupdate',
            _("Running The Postupdate Scripts"),
            10,
            is_main=True
        ),
        Phase(
            'aux-tasks',
            _("Performing auxiliary tasks"),
            10,
            is_main=True
        )
    )

    progress.start('init')
    apt_handle = AptWrapper.get_instance()
    apt_handle.clear_cache()
    apt_handle.fix_broken(progress)

    # determine the versions (from and to)
    system_version = get_system_version()
    target_version = get_target_version()

    msg = "Upgrading from {} to {}".format(system_version, target_version)
    logger.info(msg)

    # set up the scenarios and check whether they cover updating
    # from this version
    preup = PreUpdate(system_version)
    postup = PostUpdate(system_version)
    if not (preup.covers_update() and postup.covers_update()):
        title = _("Unfortunately, your version of Kano OS is too old " \
                  "to be updated through the updater.")
        description = _("You will need to download the image of the " \
                        "OS and reflash your SD card.")

        msg = "{}: {}".format(title, description)
        logger.error("Updating from a version that is no longer supported ({})"
                     .format(system_version))
        progress.fail(msg)
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

        logger.info("The updater has been updated, relaunching.")
        progress.relaunch()
        return False

    progress.start('preupdate')
    try:
        preup.run(progress)
    except Relaunch:
        raise
    except Exception as err:
        logger.error("The pre-update scenarios failed.")
        logger.error(err.encode('utf-8'))
        progress.abort("The pre-update tasks failed.")
        raise

    logger.debug("Updating deb packages")
    progress.start('updating-deb-packages')
    install_deb_packages(progress)

    progress.start('postupdate')
    try:
        postup.run(progress)
    except Relaunch:
        raise
    except Exception as err:
        logger.error("The post-update scenarios failed.")
        logger.error(err.encode('utf-8'))
        progress.abort("The post-update tasks failed.")
        raise

    bump_system_version()

    # We don't care too much when these fail
    progress.start('aux-tasks')
    run_aux_tasks(progress)


def check_disk_space(priority):
    '''
    Check for available disk space before updating
    '''

    apt_handle = AptWrapper.get_instance()
    mb_free = get_free_space()
    required_space = apt_handle.get_required_upgrade_space() + SPACE_BUFFER

    # Allowance for installing extra packages in the postupdate scenarios
    # during the update to 3.8.0
    system_version = get_system_version()
    if system_version < OSVersion.from_version_string("Kanux-Beta-3.8.0"):
        required_space += UPGRADE_3_8_0_SPACE

    required_space = max(
        required_space,
        MIN_REQ_SPACE
    )

    if mb_free < required_space:
        err_msg = N_("Only {}MB free, at least {}MB is needed.").format(
            mb_free, required_space
        )

        return False, err_msg

    return True, None


def install_deb_packages(progress, priority=Priority.NONE):
    apt_handle = AptWrapper.get_instance()
    apt_handle.upgrade_all(progress, priority=priority)
