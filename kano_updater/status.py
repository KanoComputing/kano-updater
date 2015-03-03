#
# Setting/getting the status of the updater
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os
import json

from kano.utils import ensure_dir

from kano_updater.paths import STATUS_FILE_PATH

class UpdaterStatusError(Exception):
    pass


class UpdaterStatus(object):
    NO_UPDATES = 'no-updates'
    UPDATES_AVAILABLE = 'updates-available'
    DOWNLOADING_UPDATES = 'downloading-updates'
    UPDATES_DOWNLOADED = 'updates-downloaded'

    _status_file = STATUS_FILE_PATH

    _valid_states = [
        NO_UPDATES,
        UPDATES_AVAILABLE,
        DOWNLOADING_UPDATES,
        UPDATES_DOWNLOADED
    ]

    def __init__(self):
        self._state = self.NO_UPDATES
        self._last_check = 0
        self._last_update = 0

        ensure_dir(os.path.dirname(self._status_file))
        if not os.path.exists(self._status_file):
            self.save()
        else:
            self.load()

    def load(self):
        with open(self._status_file, 'r') as status_file:
            data = json.load(status_file)

            self._state = data['state']
            self._last_update = data['last_update']
            self._last_check = data['last_check']

    def save(self):
        data = {
            'state': self._state,
            'last_update': self._last_update,
            'last_check': self._last_check
        }

        with open(self._status_file, 'w') as status_file:
            json.dump(data, status_file)

    # -- state
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in self._valid_states:
            msg = "'{}' is not a valid state".format(value)
            raise UpdaterStatusError(msg)

        self._state = value

    # -- last_update
    @property
    def last_update(self):
        return self._last_update

    @last_update.setter
    def last_update(self, value):
        if type(value) is not int:
            msg = "'last_update' must be an Unix timestamp (int)."
            raise UpdaterStatusError(msg)

        self._last_update = value

    # -- last_check
    @property
    def last_check(self):
        return self._last_check

    @last_check.setter
    def last_check(self, value):
        if type(value) is not int:
            msg = "'last_check' must be an Unix timestamp (int)."
            raise UpdaterStatusError(msg)

        self._last_check = value
