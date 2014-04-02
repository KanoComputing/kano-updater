#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import sys
from kano_updater.OSVersion import OSVersion

class Update(object):
    def __init__(self, up_type):
        if len(sys.argv) != 3:
            msg = 'Two arguments are required (the old and new versions)\n'
            sys.stderr.write(msg)
            sys.exit(1)

        self._type = up_type
        print 'Runing the {}-update scripts...'.format(up_type)

        self._old = OSVersion.from_version_string(sys.argv[1])
        self._new = OSVersion.from_version_string(sys.argv[2])

    def get_old(self):
        return self._old

    def get_new(self):
        return self._new

    def from_to(self, from_v, to_v):
        run = self._old == OSVersion.from_version_string(from_v) and \
              self._new == OSVersion.from_version_string(to_v)
        if run:
            print "Doing {}-update from {} to {}".format(self._type,
                                                         from_v, to_v)
        return run
