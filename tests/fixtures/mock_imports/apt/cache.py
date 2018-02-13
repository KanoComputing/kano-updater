#
# cache.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fake implementation of the `apt.cache` module:
#     apt.alioth.debian.org/python-apt-doc/library/apt.cache.html
#


import re
from apt.package import Package, Version

from kano_updater.version import VERSION


class FetchFailedException(Exception):
    pass


VERSION_RE = re.compile(r'.*-(\d+\.\d+\.\d+)-.*')
LATEST_VERSION = VERSION_RE.match(VERSION).groups()[0]


class Cache(object):
    def __init__(self):
        self.__depcache = None
        self.packages = {
            'kano-updater': Package('kano-updater', [
                Version('kano-updater', '3.14.1'),
                Version('kano-updater', LATEST_VERSION, 12, 13),
            ]),
            'test-pkg-1': Package('test-pkg-1', [
                Version('test-pkg-1', '1.0-0'),
                Version('test-pkg-1', '1.3-4', 23, 33),
            ]),
            'test-pkg-2': Package('test-pkg-2', [
                Version('test-pkg-2', '1.1-1'),
                Version('test-pkg-2', '2.3-4', 84, 0),
            ]),
            'test-pkg-3': Package('test-pkg-3', [
                Version('test-pkg-3', '3.0-0'),
                Version('test-pkg-3', '3.3-4', 0, 46),
            ]),
            'test-pkg-4': Package('test-pkg-4', [
                Version('test-pkg-4', '4.3-1'),
                Version('test-pkg-4', '4.3-4', 99, 265, prio=2000),
            ]),
            'test-pkg-5': Package('test-pkg-5', [
                Version('test-pkg-5', '5.3-4'),
            ]),
        }

    def __getitem__(self, key):
        return self.packages[key]

    def __iter__(self):
        for pkg in self.packages.itervalues():
            yield pkg

        raise StopIteration

    def __contains__(self, item):
        for pkg in self:
            if pkg.name == item:
                return True

        return False

    def upgrade(self, dist_upgrade=False):
        for pkg in self:
            if pkg.is_upgradable:
                pkg.mark_upgrade()

    def update(self, fetch_progress=None, sources_list=None):
        pass

    @property
    def install_count(self):
        return len([
            pkg for pkg in self.packages.itervalues() if pkg.is_upgradable
        ])

    @property
    def required_download(self):
        sz = 0

        for pkg in self:
            if pkg.marked_upgrade:
                sz += pkg.candidate.size

        return sz

    @property
    def required_space(self):
        sz = 0

        for pkg in self:
            if pkg.marked_upgrade:
                sz += pkg.candidate.installed_size

        return sz

    @property
    def required_test_space(self):
        '''
        Property only used for tests and should not be used in production code

        Reports space required in MB but note that the packages themselves
        report in bytes.
        '''

        sz = 0

        for pkg in self:
            sz += pkg.candidate.size + pkg.candidate.installed_size

        return sz / (1024. * 1024.)

    def fetch_archives(self, progress):
        pass

    def commit(self, install_progress=None):
        for pkg in self.packages.itervalues():
            pkg.do_upgrade()

    def open(self, op_progress=None):
        pass

    def clear(self):
        pass

    @property
    def dpkg_journal_dirty(self):
        return False

    @property
    def broken_count(self):
        return 0

    @property
    def _depcache(self):
        if not self.__depcache:
            self.__depcache = Cache()

        return self.__depcache
