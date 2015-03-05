#
# Interfacing with apt via python-apt
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import apt
import aptsources.sourceslist

from kano_updater.progress import Phase

class AptWrapper(object):
    def __init__(self):
        self._cache = apt.cache.Cache()

        # FIXME the progress parameter is not used
        self._fetch_progress = apt.progress.text.AcquireProgress()
        self._install_progress = apt.progress.base.InstallProgress()

    def update(self, sources_list=None, progress=None):
        src_list = aptsources.sourceslist.SourcesList()

        src_count = 0
        for src in src_list.list:
            if not src.disabled and not src.invalid:
                src_count += len(src.comps) + 1

        apt_progress = AptDownloadProgress('updating-apt-sources',
                                           progress,
                                           src_count)
        self._cache.update(fetch_progress=apt_progress,
                           sources_list=sources_list)

        ops = ['Reading package lists', 'Building dependency tree',
               'Reading state information', 'Building data structures']
        op_progress = AptOpProgress('apt-cache-init', progress, ops)
        self._cache.open(op_progress)

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

        # TODO: Remove for production
        self._cache['cowsay'].mark_install()

        self._cache.commit(self._fetch_progress, self._install_progress)

    def get_package(self, package_name):
        if package_name in self._cache:
            return self._cache[package_name]

    def upgrade_all(self):
        self._mark_all_for_update()
        self._cache.commit(self._fetch_progress, self._install_progress)

    def cache_updates(self, progress):
        self._mark_all_for_update()

        apt_progress = AptDownloadProgress('downloading-apt-packages',
                                           progress,
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


class AptDownloadProgress(apt.progress.base.AcquireProgress):
    """
        An adaptor of apt's AcquireProgress to the updater's progress
        reporting class.
    """

    def __init__(self, phase_name, updater_progress, steps):
        super(AptDownloadProgress, self).__init__()
        self._phase_name = phase_name
        self._updater_progress = updater_progress
        self._steps = steps

        self.items = {}
        self._filesizes = []

    def start(self):
        self._updater_progress.init_steps(self._phase_name, self._steps)
        self._updater_progress.start(self._phase_name)
        super(AptDownloadProgress, self).start()

    def fetch(self, item_desc):
        self._filesizes.append(item_desc.owner.filesize)

    def done(self, item_desc):
        super(AptDownloadProgress, self).done(item_desc)
        msg = "Downloading {} {}".format(item_desc.shortdesc,
                                         item_desc.description)
        self._updater_progress.next_step(self._phase_name, msg)

    def pulse(self, owner):
        return True

    def stop(self):
        super(AptDownloadProgress, self).stop()


class AptOpProgress(apt.progress.base.OpProgress):
    def __init__(self, phase_name, updater_progress, ops=[]):
        super(AptOpProgress, self).__init__()

        self._updater_progress = updater_progress

        phases = map(lambda op: Phase(op, op), ops)
        self._updater_progress.split(phase_name, *phases)

        for op in ops:
            self._updater_progress.init_steps(op, 100)

    def _next_phase(self):
        if len(self._ops) <= 1:
            return

        del self._ops[0]

        new_phase = self._ops[0]
        self._phase_name = new_phase
        self._updater_progress.start(new_phase)
        self._updater_progress.init_steps(new_phase, 100)

    def update(self, percent=None):
        super(AptOpProgress, self).update(percent)

        self._updater_progress.set_step(self.op, self.percent,
                                        self.op)

apt_handle = AptWrapper()
