#
# Priority objects
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

class Priority(object):

    def __init__(self, priority, os_match_required=False):
        self._priority = priority
        self._os_match_required = os_match_required

    @property
    def priority(self):
        return self._priority

    @property
    def os_match_required(self):
        return self._os_match_required

    def __eq__(self, other):
        return self.priority == other.priority

    def __ne__(self, other):
        return self.priority != other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)


NONE = Priority(0)
STANDARD = Priority(500)
URGENT = Priority(900, os_match_required=True)
