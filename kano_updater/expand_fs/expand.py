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


import jsonschema

from kano.utils.shell import run_cmd
from kano.logging import logger

from kano_updater.expand_fs.disk import DISK, get_disk_info
from kano_updater.expand_fs.partitions import get_root_partition, \
    get_partition_table, get_extended_partition, get_partition_number
from kano_updater.expand_fs.return_codes import RC
from kano_updater.expand_fs.schemas import PARTITION_SCHEMA


def expand_partition(partition):
    '''
    Expands the given partition to the maximum available size.

    Args:
        partition (dict): Partition to expand. Must be of the form of
                          :const:`kano_updater.expand_fs.schemas.DISK_SCHEMA`

    Returns:
        int: Success code for the operation as defined by members of
             :class:`kano_updater.expand_fs.return_codes.RC`
    '''

    try:
        jsonschema.validate(partition, PARTITION_SCHEMA)
    except jsonschema.ValidationError:
        logger.error(
            'Partiton supplied for expand does not match schema.\n'
            'Expected: {expected}\n'
            'Got: {got}\n'
            .format(expected=PARTITION_SCHEMA, got=partition)
        )
        return RC.E_INVALID_PARTITION_FORMAT

    partition_number = get_partition_number(partition['node'])

    if partition_number < 0:
        logger.error('Could not determine extended partition number')
        return RC.E_PARTITION_NUMBER_NOT_FOUND

    # TODO: Check that the extended and root partitions lie at the end of the
    #       partition table

    # Run parted command first as a script and if that fails due to it asking
    # a question, revert to command which auto-answers yes
    cmd = (
        "parted {disk} --script unit % resizepart {partition} 100 || "
        "parted {disk} unit % resizepart {partition} Yes 100"
        .format(
            disk=DISK,
            partition=partition_number,
        )
    )
    dummy_out, dummy_err, rc = run_cmd(cmd)

    if rc != 0:
        logger.error('Partition expand command failed: {cmd}'.format(cmd=cmd))
        return RC.E_PARTITION_EXPAND_FAILED

    return RC.SUCCESS


def expand_fs():
    '''
    Expands the root filesystem partition to the maximum available size and,
    with it, any extended partition container.

    Returns:
        int: Success code for the operation as defined by members of
             :class:`kano_updater.expand_fs.return_codes.RC`
    '''

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

    # Expand logical partition
    if extended_partition:
        rc = expand_partition(extended_partition)
        if rc != RC.SUCCESS:
            return rc

    # Expand root partition
    rc = expand_partition(root_partition)
    if rc != RC.SUCCESS:
        return rc

    # Notify OS of changes
    run_cmd('partprobe {disk}'.format(disk=get_disk_info()['device']))
    run_cmd('resize2fs {rootfs}'.format(rootfs=root_partition['node']))

    return RC.SUCCESS
