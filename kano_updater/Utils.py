#!/usr/bin/env python

# kano-extras Python library
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Utilities for the updater and the pre and post update scripts

from kano_updater.OSVersion import OSVersion

class Update(object):
    def __init__(self, old_ver, new_ver):
        self._old = OSVersion.from_version_string(old_ver)
        self._new = OSVersion.from_version_string(new_ver)

    def get_old(self):
        return self._old

    def get_new(self):
        return self._new

    def from(self, v):
        return From(self, v)

    def to(self, v):
        return To(self, v)

class From(object):
    def __init__(self, up,  from_v):
        self._up = up
        self._from = OSVersion.from_version_string(from_v)

    def to(self, v):
        return self._up.get_old() == self._from and \
               self._up.get_new() == OSVersion.from_version_string(v)

class To(object):
    def __init__(self, up,  to_v):
        self._up = up
        self._to = OSVersion.from_version_string(to_v)

    def from(self, v):
        return self._up.get_new() == self._to and \
               self._up.get_old() == OSVersion.from_version_string(v)
