#
# sourceslist.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fake implementation of the `aptsources.sourceslist` module:
#     apt.alioth.debian.org/python-apt-doc/library/aptsources.sourceslist.html
#


class SourceEntry(object):
    def __init__(self, line, file=None, disabled=False, invalid=False):
        self.line = line
        self.file = file

        self.disabled = disabled
        self.invalid = invalid

        self.comps = ['main', 'contrib', 'non-free', 'rpi']


class SourcesList(object):
    def __init__(self):
        self.list = [
            SourceEntry('repo.kano.me'),
            SourceEntry('dev.kano.me', disabled=True),
            SourceEntry('fake.kano.me', invalid=True),
        ]
