#
# Contains the OSVersion object for versioning the OS
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from distutils.version import LooseVersion

from kano.logging import logger

from kano_updater.paths import SYSTEM_ISSUE_FILE, SYSTEM_VERSION_FILE
from kano_updater.version import VERSION


class OSVersion(object):
    @staticmethod
    def _split_helper(os, devstage, number, name=None, variant=None, *args):
        if args:
            logger.error("DEV ERROR: Too many values in version string!")
        return os, devstage, number, name, variant

    @staticmethod
    def from_version_string(vstr):
        try:
            os, devstage, number, name, variant = OSVersion._split_helper(*vstr.split("-"))
        except:
            msg = "Unknown version string format '{}'".format(vstr)
            raise Exception(msg)

        return OSVersion(os, devstage, number, name, variant)

    @staticmethod
    def from_version_file(vfile_path):
        with open(vfile_path, 'r') as vfile:
            vstr = vfile.read().strip()
            return OSVersion.from_version_string(vstr)

    def __init__(self, os='Kanux', devstage=None, version=None, name=None, variant=None):
        self._os = os
        self._devstage = devstage
        self._number = version
        self._name = name
        self._variant = variant

        try:
            self._major_version = '.'.join(version.split('.')[0:2])
        except:
            self._major_version = version

    def to_issue(self):
        vstr = "{} {} {}".format(self._os, self._devstage, self._number)
        # Add the name and variant to the string only if they exist.
        vstr += ' ' + self._name if self._name else ''
        vstr += ' ' + self._variant if self._variant else ''
        vstr += ' \\l'
        return vstr

    def to_version_string(self):
        vstr = "{}-{}-{}".format(self._os, self._devstage, self._number)
        # Add the name and variant to the string only if they exist.
        vstr += '-' + self._name if self._name else ''
        vstr += '-' + self._variant if self._variant else ''
        return vstr

    @property
    def major_version(self):
        return self._major_version

    @property
    def version(self):
        return self._number

    @property
    def name(self):
        return self._name

    @property
    def variant(self):
        return self._variant

    def __str__(self):
        return self.to_version_string()

    def __cmp__(self, other):
        this_version = LooseVersion(self.version)
        other_version = LooseVersion(other.version)

        if this_version < other_version:
            return -1
        elif this_version == other_version:
            return 0
        else:
            return 1


TARGET_VERSION = OSVersion.from_version_string(VERSION)
SYSTEM_VERSION = OSVersion.from_version_file(SYSTEM_VERSION_FILE)


def bump_system_version():
    # Store the version change
    with open(SYSTEM_VERSION_FILE, 'r') as v_file:
        system_version = v_file.read().strip()

    logger.info("Changed the version of the OS from {} to {}".format(
        system_version, TARGET_VERSION.to_version_string()))

    try:
        from kano_profile.tracker import track_data
        track_data('updated', {
            'from': system_version,
            'to': VERSION
        })
    except Exception:
        pass

    # Update stored version
    with open(SYSTEM_VERSION_FILE, 'w') as vfile:
        vfile.write(TARGET_VERSION.to_version_string() + "\n")

    with open(SYSTEM_ISSUE_FILE, 'w') as ifile:
        ifile.write(TARGET_VERSION.to_issue() + "\n")
