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


DISK_LABELS_DIR = '/dev/disk/by-label'
ROOT_DISK = os.path.join(DISK_LABELS_DIR, 'rootfs')
RECOVERY_ROOT_DISK = os.path.join(DISK_LABELS_DIR, 'root')
EXTENDED_PARTITION_TYPE = '5'
PARTITION_REGEX = re.compile(r'/dev/mmcblk0p(\d+)')


def get_partition_table():
    '''
    Load information about the disk's partition table.

    Returns:
        dict: The partition table output from sfdisk.
              When valid, outputs of the form of the
              :const:`kano_updater.expand_fs.schemas.PARTITION_SCHEMA` schema.
              On fail, returns empty dict
    '''

    disk = get_disk_info()

    if not disk:
        return {}

    partitions = disk['partitions']

    return {
        partition['node']: partition for partition in partitions
    }


def get_link_target(link):
    '''
    Gets the absolute path of a link. Assumes that the path is already checked
    to be a link.

    Args:
        link (str): Link file path

    Returns:
        str: Absolute path of file pointed to
    '''

    link_dir = os.path.dirname(link)

    return os.path.abspath(
        os.path.join(link_dir, os.readlink(link))
    )


def get_root_partition():
    '''
    Retrieves the device handle for the root partition.

    Returns:
        str: The root partition device, or an empty string if not found
    '''

    if os.path.exists(ROOT_DISK) and os.path.islink(ROOT_DISK):
        return get_link_target(ROOT_DISK)

    if os.path.exists(RECOVERY_ROOT_DISK) \
            and os.path.islink(RECOVERY_ROOT_DISK):
        return get_link_target(RECOVERY_ROOT_DISK)

    return ''


def get_extended_partition():
    '''
    Retrieves the device handle for the extended partition.

    Returns:
        str: The extended partition device, or an empty string if not found
    '''

    partitions = get_partition_table()

    for partition in partitions.itervalues():
        if partition['type'] == EXTENDED_PARTITION_TYPE:
            return partition

    return ''


def get_partition_number(device):
    '''
    Extracts the partition number from the partition device handle.

    Args:
        device (str): Device handle, e.g. `/dev/mmcblk0p2`

    Returns:
        int: Partition number on the device, e.g. `2` for the above.
             Returns -1 on error.
    '''

    partition_match = PARTITION_REGEX.match(device)

    if not partition_match:
        return -1

    return partition_match.groups()[0]
