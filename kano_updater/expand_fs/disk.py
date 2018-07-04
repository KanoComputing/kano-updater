#
# disk.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Functions to manage physical disks
#

import json
import jsonschema

from kano.utils.shell import run_cmd
from kano.logging import logger

from kano_updater.expand_fs.schemas import DISK_SCHEMA


DISK_INFO = {}
DISK = '/dev/mmcblk0'


def get_disk_info():
    '''
    Load information about the current disk and its partition table.

    Returns:
        dict: The partition table output from sfdisk.
              When valid, outputs of the form of the
              :const:`kano_updater.expand_fs.schemas.DISK_SCHEMA` schema.
              On fail, returns empty dict
    '''

    global DISK_INFO

    if DISK_INFO:
        return DISK_INFO

    cmd = 'sfdisk --json {disk}'.format(disk=DISK)
    disks_str, dummy_err, dummy_rc = run_cmd(cmd)

    try:
        disk = json.loads(disks_str)
    except ValueError:
        logger.error('Could not get disk info: {cmd}'.format(cmd=cmd))
        return {}

    try:
        jsonschema.validate(disk, DISK_SCHEMA)
    except jsonschema.ValidationError:
        logger.error(
            'Output from {cmd} does not match disk schema.\n'
            'Expected: {expected}\n'
            'Got: {got}\n'
            .format(cmd=cmd, expected=DISK_SCHEMA, got=disk)
        )
        return {}

    DISK_INFO = disk['partitiontable']

    return DISK_INFO
