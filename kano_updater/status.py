#
# Setting/getting the status of the updater
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os
import json

from kano.utils import ensure_dir
from kano.logging import logger

from kano_updater.paths import STATUS_FILE_PATH


class UpdaterStatusError(Exception):
    pass


class UpdaterStatus(object):
    NO_UPDATES = 'no-updates'
    UPDATES_AVAILABLE = 'updates-available'
    DOWNLOADING_UPDATES = 'downloading-updates'
    UPDATES_DOWNLOADED = 'updates-downloaded'
    INSTALLING_UPDATES = 'installing-updates'
    UPDATES_INSTALLED = 'updates-installed'

    _status_file = STATUS_FILE_PATH

    _valid_states = [
        NO_UPDATES,
        UPDATES_AVAILABLE,
        DOWNLOADING_UPDATES,
        UPDATES_DOWNLOADED,
        INSTALLING_UPDATES,
        UPDATES_INSTALLED
    ]

    _singleton_instance = None

    @staticmethod
    def get_instance():
        if not UpdaterStatus._singleton_instance:
            UpdaterStatus()

        return UpdaterStatus._singleton_instance

    def __init__(self):
        if UpdaterStatus._singleton_instance:
            raise Exception('This class is a singleton!')
        else:
            UpdaterStatus._singleton_instance = self

        self._state = self.NO_UPDATES
        self._last_check = 0
        self._last_update = 0
        self._is_gui_running = False

        ensure_dir(os.path.dirname(self._status_file))
        if not os.path.exists(self._status_file):
            self.save()
        else:
            self.load()

    def load(self):
        with open(self._status_file, 'r') as status_file:
            try:
                data = json.load(status_file)

                # File format sanity check: Try to access the expected keys
                data['state']
                data['last_update']
                data['last_check']
            except Exception:
                # Initialise the file again if it is corrupted
                logger.warn("The status file was corrupted.")
                self.save()
                return

            self._state = data['state']
            self._last_update = data['last_update']
            self._last_check = data['last_check']

            if 'is_gui_running' in data:
                self._is_gui_running = (data['is_gui_running'] == 1)

    def save(self):
        data = {
            'state': self._state,
            'last_update': self._last_update,
            'last_check': self._last_check,
            'is_gui_running': 1 if self._is_gui_running else 0
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
        if not isinstance(value, int):
            msg = "'last_update' must be an Unix timestamp (int)."
            raise UpdaterStatusError(msg)

        self._last_update = value

    # -- last_check
    @property
    def last_check(self):
        return self._last_check

    @last_check.setter
    def last_check(self, value):
        if not isinstance(value, int):
            msg = "'last_check' must be an Unix timestamp (int)."
            raise UpdaterStatusError(msg)

        self._last_check = value

    """
    # -- is_gui_running

    Stored internally as a boolean but saved to file as 0/1 to interface with C
    """
    @property
    def is_gui_running(self):
        return self._is_gui_running

    @is_gui_running.setter
    def is_gui_running(self, value):
        if not isinstance(value, bool):
            msg = "'is_gui_running' must be a boolean value."
            raise UpdaterStatusError(msg)

        self._is_gui_running = value
