#
# Managing the upgrade procedure
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import pip

from kano_updater.paths import PIP_PACKAGES_LIST

def install(progress=None):
    # make sure the update has been downloaded
    # determine the versions (from and to)
    # set up the scenarios and check whether they cover updating from this version
    # upgrade the updater
    # relaunch the process
    # run the preupdate
    # install pip packages
    # install deb packages
    # run postupdate
    pass


def install_deb_packages():
    pass


def install_pip_packages():
    pip.main(['install', '--upgrade', '-r', PIP_PACKAGES_LIST])
