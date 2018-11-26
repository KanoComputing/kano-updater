#
# state.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to mock the updater state file
#


import json
import pytest


STATUS_TEMPLATE = {
    "state": "no-updates",
    "is_scheduled": 0,
    "last_check_urgent": 0,
    "ind_pkg": [],
    "notifications_muted": 0,
    "is_urgent": 0,
    "last_check": 0,
    "is_shutdown": 0,
    "first_boot_countdown": 0,
    "last_update": 0
}


@pytest.fixture(scope='function', params=('updates-available',))
def state(fs, request):
    '''
    Creates a fake version of the updater's state file configured in varying
    states
    '''

    state = request.param
    state_file = STATUS_TEMPLATE.copy()
    state_file['state'] = state

    fs.create_file(
        '/var/cache/kano-updater/status.json',
        contents=json.dumps(state_file)
    )

    return state
