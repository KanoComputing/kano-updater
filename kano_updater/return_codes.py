# return_codes.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Return codes of binaries used throughout this project.


class RC(object):
    """Return codes of binaries used throughout this project.

    Note:
        ``kano-updater-recovery`` uses it's own RC class, see that source file.
    """

    SUCCESS = 0

    NO_UPDATES_AVAILABLE = 10
    CHECK_QUIET_PERIOD = 11

    UNEXPECTED_ERROR = 20
    WRONG_ARGUMENTS = 21
    INCORRECT_PERMISSIONS = 22
    MULTIPLE_INSTANCES = 23
    NOT_PLUGGED_IN = 24

    NO_NETWORK = 30
    CANNOT_REACH_KANO = 31
    HANGED_INDEFINITELY = 32
    SIG_INTERRUPTED = 33
