#
# return_codes.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Set of return codes
#

class RC(object):
    SUCCESS = 0
    E_PARTITION_ALREADY_EXPANDED = 1
    E_ROOTFS_DOES_NOT_EXIST = 2
    E_ROOT_FS_NOT_FOUND = 3
    E_ROOT_FS_NOT_FINAL_PARTITION = 4
    E_PARTITION_EXPAND_FAILED = 5
    E_PARTITION_NOT_IN_TABLE = 6
    E_PARTITION_NOT_IN_TABLE = 6
    E_INVALID_PARTITION_FORMAT = 7
    E_PARTITION_NUMBER_NOT_FOUND = 8
