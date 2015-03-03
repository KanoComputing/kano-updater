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
from kano_updater.version import OSVersion, bump_system_version, TARGET_VERSION
from kano_updater.scenarios import PreUpdate, PostUpdate
from kano_updater.apt_wrapper import apt_handle
from kano_updater.triggered_tasks import run_triggered_tasks


class InstallError(Exception):
    pass


def install(progress=None):
    do_install(progress)


def do_install(progress=None):
    # FIXME Sort out exception handling

    status = UpdaterStatus()
    logger.debug("Installing update (updater state = {})".format(status.state))

    # make sure the update has been downloaded
    if not status.state == UpdaterStatus.UPDATES_DOWNLOADED:
        if status.state == UpdaterStatus.NO_UPDATES:
            # check for updates?
            pass
        elif status.state == UpdaterStatus.UPDATES_AVAILABLE:
            # download updates?
            pass
        elif status.state == UpdaterStatus.DOWNLOADING_UPDATES:
            # notify user and exit
            pass


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

        raise InstallError("{}: {}".format(title, description))


    old_updater = apt_handle.get_package('kano-updater')

    logger.debug("Updating itself")
    apt_handle.upgrade('kano-updater')

    # relaunch the process
    new_updater = apt_handle.get_package('kano-updater')
    if old_updater.installed.version != new_updater.installed.version:
        # Need to relaunch updater
        logger.debug("The updater has been updated, relaunching.")
        pass

    try:
        preup.run()
    except Exception as e:
        logger.error("The pre-update scenarios failed.")
        sys.exit(e)

    install_pip_packages()
    install_deb_packages()

    try:
        postup.run()
    except Exception as e:
        logger.error("The post-update scenarios failed.")
        sys.exit(e)

    bump_system_version()

    run_triggered_tasks()

    # save status - available and no-updates
    status.state = UpdaterStatus.NO_UPDATES
    status.last_update = int(time.time())
    status.save()


def install_deb_packages():
    apt_handle.upgrade_all()


def install_pip_packages():
    pip.main(['install', '--upgrade', '-r', PIP_PACKAGES_LIST])
