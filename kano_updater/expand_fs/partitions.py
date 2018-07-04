#
# partitions.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Functions to manage partitions
#

import os
import re

from kano_updater.expand_fs.disk import get_disk_info


ROOT_DISK = '/dev/disks/by-label/rootfs'
RECOVERY_ROOT_DISK = '/dev/disks/by-label/root'
EXTENDED_PARTITION_TYPE = '5'
PARTITION_REGEX = re.compile(r'/dev/mmcblk0p(\d+)')


def get_partition_table():
    disk = get_disk_info()

    partitions = disk['partitions']

    return {
        partition['node']: partition for partition in partitions
    }


def get_link_target(link):
    link_dir = os.path.dirname(link)

    return os.path.abspath(
        os.path.join(link_dir, os.readlink(link))
    )


def get_root_partition():
    if os.path.exists(ROOT_DISK) and os.path.islink(ROOT_DISK):
        return get_link_target(ROOT_DISK)

    if os.path.exists(RECOVERY_ROOT_DISK) \
            and os.path.islink(RECOVERY_ROOT_DISK):
        return get_link_target(RECOVERY_ROOT_DISK)

    return None


def get_extended_partition():
    partitions = get_partition_table()

    for partition in partitions.itervalues():
        if partition['type'] == EXTENDED_PARTITION_TYPE:
            return partition

    return None


def get_partition_number(device):
    partition_match = PARTITION_REGEX.match(device)

    if not partition_match:
        return -1

    return partition_match.groups()[0]
