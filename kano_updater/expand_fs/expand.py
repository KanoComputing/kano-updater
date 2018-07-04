#
# expand_rootfs.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Functions to expand the root partition on the disk.
#
# For the regular image, the partition table looks like this:
#
# `sudo fdisk /dev/mmcblk0 --list`
#
#     Device         Boot   Start      End  Sectors  Size Id Type
#     /dev/mmcblk0p1      3457024  3866621   409598  200M  c W95 FAT32 (LBA)
#     /dev/mmcblk0p2      3866624 31116287 27249664   13G 83 Linux
#
# `ls -l /dev/disk/by-label/`
#
#     boot -> ../../mmcblk0p1
#     rootfs -> ../../mmcblk0p2
#
# The resize operation consists of redefining the end of the rootfs partition
# to align with the end of the disk.
#
# The Recovery image has a more complicated partition table:
#
# `sudo fdisk /dev/mmcblk0 --list`
#
#     Device         Boot   Start      End  Sectors  Size Id Type
#     /dev/mmcblk0p1         8192  3386718  3378527  1.6G  e W95 FAT16 (LBA)
#     /dev/mmcblk0p2      3386719 31116287 27729569 13.2G  5 Extended
#     /dev/mmcblk0p5      3391488  3457021    65534   32M 83 Linux
#     /dev/mmcblk0p6      3457024  3866621   409598  200M  c W95 FAT32 (LBA)
#     /dev/mmcblk0p7      3866624 31116287 27249664   13G 83 Linux
#
# `ls -l /dev/disk/by-label/`
#
#     boot -> ../../mmcblk0p6
#     RECOVERY -> ../../mmcblk0p1
#     root -> ../../mmcblk0p7
#     SETTINGS -> ../../mmcblk0p5
#
# The resize operation consists of aligning the end of the Extended partition
# with the end of the disk and moving the end of the rootfs logical partition
# to align with the end of the disk.
#

import datetime
import os
import jsonschema

from kano.utils.shell import run_cmd
from kano.logging import logger

from kano_updater.expand_fs.disk import get_disk_info, get_last_sector
from kano_updater.expand_fs.partitions import get_root_partition, \
    get_partition_table, get_extended_partition, get_partition_number
from kano_updater.expand_fs.return_codes import RC
from kano_updater.expand_fs.schemas import PARTITION_SCHEMA


EXPAND_FLAG = '/etc/root_has_been_expanded'


def expand_partition(partition):
    try:
        jsonschema.validate(partition, PARTITION_SCHEMA)
    except jsonschema.ValidationError:
        return RC.E_INVALID_PARTITION_FORMAT

    partition_number = get_partition_number(partition['node'])

    if partition_number < 0:
        return RC.E_PARTITION_NUMBER_NOT_FOUND

    run_cmd(
        "parted unit s resizepart {partition} {end}".format(
            partition=partition_number,
            end=get_last_sector()
        )
    )

    return RC.SUCCESS


def expand_fs():
    # Check if already expanded
    if os.path.exists(EXPAND_FLAG):
        logger.error('Partition already expanded')
        return RC.E_PARTITION_ALREADY_EXPANDED

    # Figure out which partition is the root filesystem
    root_disk = get_root_partition()

    if not root_disk:
        logger.error('Could not determine which partition is root partition')
        return RC.E_ROOT_FS_NOT_FOUND

    partitions = get_partition_table()

    try:
        root_partition = partitions[root_disk]
    except KeyError:
        logger.error('Root filesystem could not be found in partition table')
        return RC.E_PARTITION_NOT_IN_TABLE

    # Determine if a logical partition exists
    extended_partition = get_extended_partition()

    # TODO: Check that the extended and root partitions lie at the end of the
    #       partition table

    # Expand logical partition
    if extended_partition:
        rc = expand_partition(extended_partition)
        if rc == RC.E_PARTITION_NUMBER_NOT_FOUND:
            logger.error('Could not determine extended partition number')
            return rc


    # Expand root partition
    rc = expand_partition(root_partition)
    if rc == RC.E_PARTITION_NUMBER_NOT_FOUND:
        logger.error('Could not determine root partition number')
        return rc

    # Notify OS of changes
    run_cmd('partprobe {disk}'.format(disk=get_disk_info()['device']))
    run_cmd('resize2fs {rootfs}'.format(rootfs=root_partition['node']))

    with open(EXPAND_FLAG, 'w') as flag_f:
        flag_f.write(datetime.datetime.now().strftime('%c'))

    return RC.SUCCESS
