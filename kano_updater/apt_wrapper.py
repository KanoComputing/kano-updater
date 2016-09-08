#
# Interfacing with apt via python-apt
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import apt
import aptsources.sourceslist
import apt_pkg

from kano.logging import logger
from kano.utils import run_cmd_log

from kano_updater.apt_progress_wrapper import AptDownloadProgress, \
    AptOpProgress, AptInstallProgress
from kano_updater.os_version import SYSTEM_VERSION
from kano_updater.progress import Phase
import kano_updater.priority as Priority
from kano_updater.special_packages import independent_install_list

class AptWrapper(object):
    def __init__(self):
        apt.apt_pkg.init_config()

        # We disable downloading translations, because we don't have them
        # in our repos and it always fails.
        apt.apt_pkg.config['Acquire::Languages'] = 'none'
        apt.apt_pkg.config['DPkg::Options::'] = '--force-confdef'
        apt.apt_pkg.config['DPkg::Options::'] = '--force-confold'

        apt.apt_pkg.init_system()

        self._cache = apt.cache.Cache()

    def update(self, progress, sources_list=None):
        src_list = aptsources.sourceslist.SourcesList()

        src_count = 0
        for src in src_list.list:
            if not src.disabled and not src.invalid:
                src_count += len(src.comps) + 1

        updating_sources = "{}-updating-apt-sources".format(
            progress.get_current_phase().name)
        cache_init = "{}-apt-cache-init".format(
            progress.get_current_phase().name)
        progress.split(
            Phase(updating_sources, _("Updating apt sources")),
            Phase(cache_init, _("Initialising apt cache"))
        )

        progress.start(updating_sources)
        apt_progress = AptDownloadProgress(progress, src_count)
        try:
            self._cache.update(fetch_progress=apt_progress,
                               sources_list=sources_list)
        except apt.cache.FetchFailedException:
            err_msg = N_("Failed to update sources")
            logger.error(err_msg)
            progress.fail(_(err_msg))

        progress.start(cache_init)
        ops = [("reading-package-lists", _("Reading package lists")),
               ("building-dependency-tree", _("Building dependency tree")),
               ("reading-state-information", _("Reading state information")),
               ("building-data-structures", _("Building data structures"))]
        op_progress = AptOpProgress(progress, ops)
        self._cache.open(op_progress)

    """
    def install(self, packages, progress=None):
        if not isinstance(packages, list):
            packages = [packages]

        for pkg in self._cache:
            if pkg.shortname in packages:
                pkg.mark_install(purge=True)

        # TODO Needs splitting
        fetch_progress = AptDownloadProgress(progress,
                                             self._cache.install_count)
        inst_progress = AptInstallProgress(progress)
        self._cache.commit(fetch_progress, inst_progress)
        self._cache.open()
        self._cache.clear()
    """

    """
    def remove(self, packages, purge=False, progress=None):
        if not isinstance(packages, list):
            packages = [packages]

        for pkg_name in packages:
            if pkg_name in self._cache:
                pkg = self._cache[pkg_name]
                pkg.mark_delete(purge=purge)

        # TODO needs splitting
        fetch_progress = AptDownloadProgress(progress)
        inst_progress = AptInstallProgress(progress)
        self._cache.commit(fetch_progress, inst_progress)
        self._cache.open()
        self._cache.clear()
    """

    def upgrade(self, packages, progress=None, priority=Priority.NONE):
        if not isinstance(packages, list):
            packages = [packages]

        for pkg_name in packages:
            if pkg_name in self._cache:
                pkg = self._cache[pkg_name]

                if self._is_package_upgradable(pkg, priority=priority):
                    pkg.mark_upgrade()

        phase_name = progress.get_current_phase().name
        download = "{}-downloading".format(phase_name)
        install = "{}-installing".format(phase_name)
        progress.split(
            Phase(download, _("Downloading packages")),
            Phase(install, _("Installing packages"))
        )

        progress.start(download)
        apt_progress = AptDownloadProgress(progress,
                                           self._cache.install_count)
        self._cache.fetch_archives(apt_progress)

        progress.start(install)
        inst_progress = AptInstallProgress(progress)
        self._cache.commit(install_progress=inst_progress)
        self._cache.open()
        self._cache.clear()

    def get_package(self, package_name):
        if package_name in self._cache:
            return self._cache[package_name]

    def upgrade_all(self, progress=None, priority=Priority.NONE):
        if priority != Priority.URGENT:
            self._cache.upgrade(dist_upgrade=True)

        phase_name = progress.get_current_phase().name
        download = "{}-downloading".format(phase_name)
        install = "{}-installing".format(phase_name)
        progress.split(
            Phase(download, _("Downloading packages")),
            Phase(install, _("Installing packages"))
        )

        progress.start(download)
        self.cache_updates(progress, priority=priority)

        progress.start(install)
        inst_progress = AptInstallProgress(progress)
        self._cache.commit(install_progress=inst_progress)
        self._cache.open()
        self._cache.clear()

    def cache_updates(self, progress, priority=Priority.NONE):
        self._mark_all_for_update(priority=priority)

        apt_progress = AptDownloadProgress(progress,
                                           self._cache.install_count)
        self._cache.fetch_archives(apt_progress)

    def _mark_all_for_update(self, priority=Priority.NONE):
        for pkg in self._cache:
            if self._is_package_upgradable(pkg, priority=priority):
                logger.debug("Marking {} ({}) for upgrade".format(
                    pkg.shortname, pkg.candidate.version
                ))
                pkg.mark_upgrade()

    def packages_to_be_upgraded(self):
        ret = {}
        for pkg in self._cache.get_changes():
            ret[pkg.name] = pkg.versions.keys()

        return ret

    @staticmethod
    def _is_package_upgradable(pkg, priority=Priority.NONE):
        if not pkg.is_upgradable:
            return False

        if pkg.candidate.policy_priority < priority.priority:
            return False

        if (
                priority.os_match_required and
                not pkg.candidate.version.startswith(
                    SYSTEM_VERSION.major_version
                )
            ):
            return False

        return True

    def independent_packages_available(self, priority=Priority.STANDARD):
        pkgs = []
        for pkg in self._cache:
            if pkg.name in independent_install_list:
                if self._is_package_upgradable(pkg, priority=priority):
                    pkgs.append(pkg.name)

        return pkgs

    def is_update_available(self, priority=Priority.STANDARD):
        for pkg in self._cache:
            # exclude independent packages, UNLESS this is an urgent update
            if priority == Priority.URGENT or pkg.name not in independent_install_list:
                if self._is_package_upgradable(pkg, priority=priority):
                    return True

        return False

    def clear_cache(self):
        self._cache.clear()
        self._cache.open()

    def fix_broken(self, progress):
        progress.split(
            Phase('dpkg-clean',
                  _("Cleaning dpkg journal")),
            Phase('fix-broken',
                  _("Fixing broken packages"))
        )
        if self._cache.dpkg_journal_dirty:
            progress.start('dpkg-clean')
            logger.info("Cleaning dpkg journal")
            run_cmd_log("dpkg --configure -a")

            self._cache.clear()
            self._cache.open()

        progress.start('fix-broken')

        # Naughty but don't want to re-initialise
        if self._cache._depcache.broken_count:
            try:
                self._cache._depcache.fix_broken()
            except SystemError as err:
                logger.error(err)

            self._cache.clear()
            self._cache.open()


apt_handle = AptWrapper()
