#
# disk_config.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Fixture to simulate different disk configurations
#

import json
import os
import re
import pytest


DISKS_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'disks'
)
DISKS = {}

EXTENSIONS = [
    '.parted-dump',
    '.sfdisk-dump',
    '.expected',
    '.links'
]

for disk_file in os.listdir(DISKS_DIR):
    name, ext = os.path.splitext(disk_file)

    if ext not in EXTENSIONS:
        continue

    if name not in DISKS:
        DISKS[name] = {}

    disk_path = os.path.join(DISKS_DIR, disk_file)
    with open(disk_path, 'r') as disk_f:
        DISKS[name][ext.strip('.')] = disk_f.read()


@pytest.fixture(scope='function', params=DISKS.itervalues())
def disk_config(request, fs):
    '''
    Simulate different disk configurations.

    Each disk configuration is identified by the root filename, where
    extensions with the same file prefix are utilised as members belonging to
    the same disk. These files are in the `tests/fixtures/disks` directory.

    `tests/fixtures/disks/<disk>.sfdisk-dump`

        This should contain the output of:

        ```
        sfdisk --json /dev/mmcblk0
        ```

    `tests/fixtures/disks/<disk>.parted-dump`

        This should contain the output of:

        ```
        parted /dev/mmcblk0 unit s print
        ```

    `tests/fixtures/disks/<disk>.links`

        List of symlinks to be created for the disk, one per line, in the format

        ```
        <link-file> -> <path-totarget>
        ```

    `tests/fixtures/disks/<disk>.expected`

        JSON file containing keys:

         - `commands` (`str[]`): List of commands expected to be run
    '''

    disk_paths = request.param

    disk_info = json.loads(disk_paths.get('sfdisk-dump'))

    parted_regex = re.compile(r'^Disk (/dev/\S+): (\d+)s')
    for parted_line in disk_paths.get('parted-dump').splitlines():
        match = parted_regex.match(parted_line)
        if match:
            device, sectors = match.groups()

            if disk_info['partitiontable']['device'] == device:
                disk_info['partitiontable']['sectors'] = sectors

            break

    expected_info = json.loads(disk_paths.get('expected'))

    fs.create_dir('/etc')

    for links in disk_paths.get('links', '').splitlines():
        link, target = links.split(' -> ')

        link_dir = os.path.dirname(link)
        abs_target = target if os.path.isabs(target) \
                else os.path.abspath(os.path.join(link_dir, target))

        fs.create_file(abs_target)
        fs.create_symlink(link, target)

    return {
        'expected': expected_info,
        'info': disk_info,
        'dumps': disk_paths
    }
