#
# disk.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Functions to manage physical disks
#

import json
import re
import jsonschema

from kano.utils.shell import run_cmd

from kano_updater.expand_fs.schemas import DISK_SCHEMA


DISK_INFO = None
DISK = '/dev/mmcblk0'


def get_sector_count():
    parted_str, dummy_err, dummy_rc = run_cmd(
        'parted {disk} unit s print'.format(disk=DISK)
    )

    parted_regex = re.compile(r'^Disk (/dev/\S+): (\d+)s')
    for parted_line in parted_str.splitlines():
        match = parted_regex.match(parted_line)
        if match:
            device, sectors = match.groups()

            if device == DISK:
                try:
                    return int(sectors)
                except ValueError:
                    pass

    return 0


def get_disk_info():
    global DISK_INFO

    if DISK_INFO:
        return DISK_INFO

    disks_str, dummy_err, dummy_rc = run_cmd(
        'sfdisk --json {disk}'.format(disk=DISK)
    )

    try:
        disk = json.loads(disks_str)
    except ValueError:
        return None

    try:
        jsonschema.validate(disk, DISK_SCHEMA)
    except jsonschema.ValidationError as err:
        return None

    disk['partitiontable']['sectors'] = get_sector_count()

    DISK_INFO = disk['partitiontable']

    return DISK_INFO


def get_last_sector():
    disk_info = get_disk_info()

    return disk_info['sectors'] - 1
