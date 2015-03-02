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

    def update(self):
        self._cache.update(fetch_progress=self._progress)

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

        for pkg in self._cache:
            if pkg.shortname in packages:
                pkg.mark_delete(purge=True)

        self._cache.commit(self._fetch_progress, self._install_progress)

    def upgrade(self):
        self._mark_all_for_update()
        self._cache.commit(self._fetch_progress, self._install_progress)

    def cache_updates(self):
        self._mark_all_for_update()
        self._cache.fetch_archives(self._fetch_progress)

    def _mark_all_for_update(self):
        for pkg in self._cache:
            if pkg.is_upgradable:
                pkg.mark_upgrade()


apt_handle = AptWrapper()
