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
        self.pkg = pkg
        self.version = version
        self.size = dl_sz
        self.installed_size = install_sz

        self.policy_priority = prio
        self.architecture = 'armhf'

        self.is_installed = False

    def __str__(self):
        return 'FakeVersion("{}")'.format(self.version)

    def __repr__(self):
        return str(self)


class Package(object):
    def __init__(self, name, versions):
        self.name = name
        self.architecture = 'armhf'

        self.marked_upgrade = False

        self._versions = collections.OrderedDict()
        self.versions = versions

        self.shortname = name

    def __str__(self):
        return 'FakePackage("{}")'.format(self.name)

    def __repr__(self):
        return str(self)

    def mark_upgrade(self):
        self.marked_upgrade = True

    @property
    def versions(self):
        return self._versions

    @versions.setter
    def versions(self, versions):
        if not isinstance(versions, list):
            versions = [versions]

        versions[0].is_installed = True

        for version in versions:
            self._versions[version.version] = version

    @property
    def candidate(self):
        for version in reversed([v for v in self.versions.itervalues()]):
            return version

    @property
    def is_upgradable(self):
        return len(self.versions) > 1

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

        self.installed.is_installed = False
        self.candidate.is_installed = True
