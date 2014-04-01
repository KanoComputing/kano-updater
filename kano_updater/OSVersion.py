#!/usr/bin/env python

# kano-extras Python library
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2

class OSVersion:
    def __init__(self, os=None, codename=None, version=None):
        self._os = os
        self._codename = codename
        self._number = version

    def from_version_file(self, vfile_path):
        with open(vfile_path, "r") as vfile:
            vstr = vfile.read().strip()
            try:
                self._os, self._codename, self._number = vstr.split("-")
            except:
                msg = "Unknown version string format ({})".format(vstr)
                raise Exception()

        return self

    def to_issue(self):
        return "{} {} {} \\l".format(self._os, self._codename, self._number)

    def to_version_string(self):
        return "{}-{}-{}".format(self._os, self._codename, self._number)

def bump_system_version(ver, version_file_path, issue_file_path):
    with open(version_file_path, "w") as vfile:
        vfile.write(ver.to_version_string() + "\n")

    with open(issue_file_path, "w") as ifile:
        ifile.write(ver.to_issue() + "\n")
