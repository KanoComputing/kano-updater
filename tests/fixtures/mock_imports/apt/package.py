#
# package.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fake implementation of the `apt.package` module:
#     apt.alioth.debian.org/python-apt-doc/library/apt.package.html
#


import collections


class Version(object):
    def __init__(self, pkg, version, dl_sz=0, install_sz=0, prio=500):
        '''
        Fake implementation of the `apt.package.Version` class representing an
        available Debian package version.

        Args:
            pkg: Name of the package
            version: Version string of the package
            dl_sz: Download size in MB
            install_sz: Install size in MB
            prio: Apt priority
        '''

        self.pkg = pkg
        self.version = version
        self.size = dl_sz * 1024 * 1024
        self.installed_size = install_sz * 1024 * 1024

        self.policy_priority = prio
        self.architecture = 'armhf'

        self._is_installed = False

    def __str__(self):
        installed_str = ' installed' if self.is_installed else ''
        return 'FakeVersion("{}"{})'.format(self.version, installed_str)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.version < other.version

    def __eq__(self, other):
        return self.version == other.version

    @property
    def is_installed(self):
        return self._is_installed

    @is_installed.setter
    def is_installed(self, val):
        self._is_installed = val


class Package(object):
    def __init__(self, name, versions):
        self.name = name
        self.architecture = 'armhf'

        self._marked_upgrade = False

        self._versions = collections.OrderedDict()
        self.versions = versions

        self.shortname = name

    def __str__(self):
        return 'FakePackage("{}", Versions: {})'.format(
            self.name, [v for v in self.versions.itervalues()]
        )

    def __repr__(self):
        return str(self)

    @property
    def marked_upgrade(self):
        return self._marked_upgrade

    def mark_upgrade(self):
        self._marked_upgrade = True

    def mark_keep(self):
        self._marked_upgrade = False

    @property
    def marked_keep(self):
        return not self.marked_upgrade

    @property
    def marked_delete(self):
        return False

    @property
    def marked_downgrade(self):
        return False

    @property
    def marked_reinstall(self):
        return False

    @property
    def marked_install(self):
        return False

    @property
    def versions(self):
        return self._versions

    @versions.setter
    def versions(self, versions):
        if not isinstance(versions, list):
            versions = [versions]

        min(versions).is_installed = True

        for version in versions:
            self._versions[version.version] = version

    @property
    def candidate(self):
        return max(self.versions.itervalues())

    @property
    def is_upgradable(self):
        return self.installed < self.candidate

    @property
    def installed(self):
        for version in self.versions.itervalues():
            if version.is_installed:
                return version

    def do_upgrade(self):
        '''
        Not part of the API, just a helper for the mock
        '''

        if not self.marked_upgrade:
            return

        self.installed.size = self.candidate.size
        self.installed.installed_size = self.candidate.installed_size

        self.installed.is_installed = False
        self.candidate.is_installed = True
