#
# Contains the OSVersion object for versioning the OS
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

from kano.logging import logger

from kano_updater.paths import SYSTEM_ISSUE_FILE, SYSTEM_VERSION_FILE
from kano_updater.version import VERSION


class OSVersion(object):
    @staticmethod
    def from_version_string(vstr):
        try:
            _os, _codename, _number = vstr.split("-")
        except:
            msg = "Unknown version string format '{}'".format(vstr)
            raise Exception(msg)

        return OSVersion(_os, _codename, _number)

    @staticmethod
    def from_version_file(vfile_path):
        with open(vfile_path, "r") as vfile:
            vstr = vfile.read().strip()
            return OSVersion.from_version_string(vstr)

    def __init__(self, os="Kanux", codename=None, version=None):
        self._os = os
        self._codename = codename
        self._number = version

    def to_issue(self):
        return "{} {} {} \\l".format(self._os, self._codename, self._number)

    def to_version_string(self):
        return "{}-{}-{}".format(self._os, self._codename, self._number)

    def __str__(self):
        return self.to_version_string()

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __cmp__(self, other):
        return cmp(str(self), str(other))


TARGET_VERSION = OSVersion.from_version_string(VERSION)


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
