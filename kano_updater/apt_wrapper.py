#
# Interfacing with apt via python-apt
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import apt
import aptsources.sourceslist

from kano_updater.apt_progress_wrapper import AptDownloadProgress, \
    AptOpProgress, AptInstallProgress
from kano_updater.progress import Phase


class AptWrapper(object):
    def __init__(self):
        apt.apt_pkg.init()
        self._cache = apt.cache.Cache()

    def update(self, sources_list=None, progress=None):
        src_list = aptsources.sourceslist.SourcesList()

        src_count = 0
        for src in src_list.list:
            if not src.disabled and not src.invalid:
                src_count += len(src.comps) + 1

        progress.split(
            Phase('updating-apt-sources', 'Updating apt sources'),
            Phase('apt-cache-init', 'Initialising apt cache')
        )

        progress.start('updating-apt-sources')
        apt_progress = AptDownloadProgress(progress, src_count)
        self._cache.update(fetch_progress=apt_progress,
                           sources_list=sources_list)

        progress.start('apt-cache-init')
        ops = ['Reading package lists', 'Building dependency tree',
               'Reading state information', 'Building data structures']
        op_progress = AptOpProgress(progress, ops)
        self._cache.open(op_progress)

    """
    def install(self, packages, progress=None):
        if type(packages) is not list:
            packages = [packages]

        for pkg in self._cache:
            if pkg.shortname in packages:
                pkg.mark_install(purge=True)

        # TODO Needs splitting
        fetch_progress = AptDownloadProgress(progress,
                                             self._cache.install_count)
        inst_progress = AptInstallProgress(progress)
        self._cache.commit(fetch_progress, inst_progress)
    """

    """
    def remove(self, packages, purge=False, progress=None):
        if type(packages) is not list:
            packages = [packages]

        for pkg_name in packages:
            if pkg_name in self._cache:
                pkg = self._cache[pkg_name]
                pkg.mark_delete(purge=purge)

        # TODO needs splitting
        fetch_progress = AptDownloadProgress(progress)
        inst_progress = AptInstallProgress(progress)
        self._cache.commit(fetch_progress, inst_progress)
    """

    def upgrade(self, packages, progress=None):
        if type(packages) is not list:
            packages = [packages]

        for pkg_name in packages:
            if pkg_name in self._cache:
                pkg = self._cache[pkg_name]

                if pkg.is_upgradable:
                    pkg.mark_upgrade()

        # TODO: Remove for production
        self._cache['cowsay'].mark_install()
        self._cache['xcowsay'].mark_install()

        phase_name = progress.get_current_phase().name
        download = "{}-downloading".format(phase_name)
        install = "{}-installing".format(phase_name)
        progress.split(
            Phase(download, "Downloading packages"),
            Phase(install, "Installing packages")
        )

        progress.start(download)
        self.cache_updates(progress)

        inst_progress = AptInstallProgress(progress)
        self._cache.commit(install_progress=inst_progress)

    def get_package(self, package_name):
        if package_name in self._cache:
            return self._cache[package_name]

    def upgrade_all(self, progress=None):
        self._mark_all_for_update()

        phase_name = progress.get_current_phase().name
        download = "{}-downloading".format(phase_name)
        install = "{}-installing".format(phase_name)
        progress.split(
            Phase(download, "Downloading packages"),
            Phase(install, "Installing packages")
        )

        progress.start(download)
        self.cache_updates(progress)

        inst_progress = AptInstallProgress(progress)
        self._cache.commit(install_progress=inst_progress)

    def cache_updates(self, progress):
        self._mark_all_for_update()

        apt_progress = AptDownloadProgress(progress,
                                           self._cache.install_count)
        self._cache.fetch_archives(apt_progress)

    def _mark_all_for_update(self):
        for pkg in self._cache:
            if pkg.is_upgradable:
                pkg.mark_upgrade()

    def is_update_avaliable(self):
        for pkg in self._cache:
            if pkg.is_upgradable:
                return True

        return False


apt_handle = AptWrapper()
