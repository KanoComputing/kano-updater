# signal_handling.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module to handle signals
#

import signal

class SignalPoll(object):
    # A class to allow using signals without globals

    def __init__(self, sig_num):
        self.sig_num = sig_num
        self.signalled = False
        signal.signal(self.sig_num, self._handle)

    def _handle(self, sig_num, stack):
        if sig_num == self.sig_num:
            self.signalled = True

    def poll(self):
        res = self.signalled
        self.signalled = False
        return res
