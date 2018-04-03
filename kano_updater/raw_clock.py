# raw_clock.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module to obtain a clock value which is not disturbed by the boot process
# when it obtains time from ntp.
#
# From http://stackoverflow.com/questions/1205722/how-do-i-get-monotonic-time-durations-in-python


import ctypes
import os


class timespec(ctypes.Structure):
    _fields_ = [
        ('tv_sec', ctypes.c_long),
        ('tv_nsec', ctypes.c_long)
    ]


class raw_clock:
    CLOCK_MONOTONIC_RAW = 4  # see <linux/time.h>
    def __init__(self):
        self.librt = ctypes.CDLL('librt.so.1', use_errno=True)
        self.clock_gettime = self.librt.clock_gettime
        self.clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]


    def monotonic_time(self):
        t = timespec()
        if self.clock_gettime(self.CLOCK_MONOTONIC_RAW, ctypes.pointer(t)) != 0:
            errno_ = ctypes.get_errno()
            raise OSError(errno_, os.strerror(errno_))
        return t.tv_sec + t.tv_nsec * 1e-9
