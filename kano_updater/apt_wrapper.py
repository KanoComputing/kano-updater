#
# Interfacing with apt via python-apt
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import apt


class AptWrapper(object):
    def __init__(self, progress=None):
        self._cache = apt.cache.Cache()

        # FIXME the progress parameter is not used
        self._fetch_progress = apt.progress.text.AcquireProgress()
        self._install_progress = apt.progress.base.InstallProgress()

    def update(self, sources_list=None):
        self._cache.update(fetch_progress=self._fetch_progress,
                           sources_list=sources_list)

    def install(self, packages):
        if type(packages) is not list:
            packages = [packages]

        for pkg in self._cache:
            if pkg.shortname in packages:
                pkg.mark_install(purge=True)

        self._cache.commit(self._fetch_progress, self._install_progress)

    def remove(self, packages, purge=False):
        if type(packages) is not list:
            packages = [packages]

        for pkg_name in packages:
            if pkg_name in self._cache:
                pkg = self._cache[pkg_name]
                pkg.mark_delete(purge=purge)

        self._cache.commit(self._fetch_progress, self._install_progress)

    def upgrade(self, packages):
        if type(packages) is not list:
            packages = [packages]

        for pkg_name in packages:
            if pkg_name in self._cache:
                pkg = self._cache[pkg_name]

                if pkg.is_upgradable:
                    pkg.mark_upgrade()

        self._cache.commit(self._fetch_progress, self._install_progress)

    def get_package(self, package_name):
        if package_name in self._cache:
            return self._cache[package_name]

    def upgrade_all(self):
        self._mark_all_for_update()
        self._cache.commit(self._fetch_progress, self._install_progress)

    def cache_updates(self):
        self._mark_all_for_update()
        self._cache.fetch_archives(self._fetch_progress)

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
