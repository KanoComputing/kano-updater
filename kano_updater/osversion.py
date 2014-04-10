#!/usr/bin/env python

# osversion.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#


class OSVersion:
    @staticmethod
    def from_version_string(vstr):
        try:
            _os, _codename, _number = vstr.split("-")
        except:
            msg = "Unknown version string format ({})".format(vstr)
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


def bump_system_version(ver, version_file_path, issue_file_path):
    with open(version_file_path, "w") as vfile:
        vfile.write(ver.to_version_string() + "\n")

    with open(issue_file_path, "w") as ifile:
        ifile.write(ver.to_issue() + "\n")
