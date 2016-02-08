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
        logger.debug('Getting status instance')
        if not UpdaterStatus._singleton_instance:
            UpdaterStatus()

        return UpdaterStatus._singleton_instance

    def __init__(self):
        logger.debug('Creating new status instance')
        if UpdaterStatus._singleton_instance:
            raise Exception('This class is a singleton!')
        else:
            UpdaterStatus._singleton_instance = self

        self._state = self.NO_UPDATES
        self._last_check = 0
        self._last_check_urgent = 0
        self._last_update = 0
        self._first_boot_countdown = 0
        self._is_urgent = False
        self._is_scheduled = False
        self._notifications_muted = False
        self._is_shutdown = False

        ensure_dir(os.path.dirname(self._status_file))
        if not os.path.exists(self._status_file):
            self.save()
        else:
            self.load()

    def load(self):
        logger.debug('Loading status instance from file')
        with open(self._status_file, 'r') as status_file:
            try:
                data = json.load(status_file)

                # File format sanity check: Try to access the expected keys
                data['state']
                data['last_update']
                data['last_check']
                data['last_check_urgent']
                data['first_boot_countdown']
                data['is_urgent']
                data['is_scheduled']
                data['is_shutdown']
            except Exception:
                # Initialise the file again if it is corrupted
                logger.warn("The status file was corrupted.")
                self.save()
                return

            self._state = data['state']
            self._last_update = data['last_update']
            self._last_check = data['last_check']
            self._last_check_urgent = data['last_check_urgent']
            self._first_boot_countdown = data['first_boot_countdown']
            self._is_urgent = (data['is_urgent'] == 1)
            self._is_scheduled = (data['is_scheduled'] == 1)
            self._is_shutdown = (data['is_shutdown'] == 1)

            if 'notifications_muted' in data:
                self._notifications_muted = (data['notifications_muted'] == 1)

    def save(self):
        logger.debug('Saving status instance')
        data = {
            'state': self._state,
            'last_update': self._last_update,
            'last_check': self._last_check,
            'last_check_urgent': self._last_check_urgent,
            'first_boot_countdown': self._first_boot_countdown,
            'is_urgent': 1 if self._is_urgent else 0,
            'is_scheduled': 1 if self._is_scheduled else 0,
            'is_shutdown': 1 if self._is_shutdown else 0,
            'notifications_muted': 1 if self._notifications_muted else 0
        }

        with open(self._status_file, 'w') as status_file:
            json.dump(data, status_file, indent=4)

    # -- state
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value not in self._valid_states:
            msg = "'{}' is not a valid state".format(value)
            logger.debug(msg)
            raise UpdaterStatusError(msg)

        logger.debug("Setting the status' state to: {}".format(value))
        self._state = value

    # -- scheduling
    @property
    def is_scheduled(self):
        return self._is_scheduled

    @is_scheduled.setter
    def is_scheduled(self, value):
        if not isinstance(value, bool):
            msg = "'is_scheduled' must be a boolean value."
            raise UpdaterStatusError(msg)

        logger.debug("Setting the status' is_scheduled to: {}".format(value))
        self._is_scheduled = value

    # -- last_update
    @property
    def last_update(self):
        return self._last_update

    @last_update.setter
    def last_update(self, value):
        if not isinstance(value, int):
            msg = "'last_update' must be an Unix timestamp (int)."
            raise UpdaterStatusError(msg)

        logger.debug("Setting the status' last_update to: {}".format(value))
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

        logger.debug("Setting the status' last_check to: {}".format(value))
        self._last_check = value

    # -- is_urgent - flag used to distinguish between update priority levels
    @property
    def is_urgent(self):
        return self._is_urgent

    @is_urgent.setter
    def is_urgent(self, value):
        if not isinstance(value, bool):
            msg = "'is_urgent' must be a boolean value."
            raise UpdaterStatusError(msg)

        logger.debug("Setting the status' is_urgent to: {}".format(value))
        self._is_urgent = value

    # -- last_check_urgent - used for very urgent updates
    @property
    def last_check_urgent(self):
        return self._last_check

    @last_check_urgent.setter
    def last_check_urgent(self, value):
        if not isinstance(value, int):
            msg = "'last_check_urgent' must be an Unix timestamp (int)."
            raise UpdaterStatusError(msg)

        logger.debug("Setting the status' last_check_urgent to: {}"
                     .format(value))
        self._last_check_urgent = value

    # -- first_boot_countdown - used to stop updates for a set amount of time
    @property
    def first_boot_countdown(self):
        return self._first_boot_countdown

    @first_boot_countdown.setter
    def first_boot_countdown(self, value):
        if not isinstance(value, int):
            msg = "'first_boot_countdown' must be an Unix timestamp (int)."
            raise UpdaterStatusError(msg)

        logger.debug("Setting the status' first_boot_countdown to: {}"
                     .format(value))
        self._first_boot_countdown = value

    """
    # -- notifications_muted

    Stored internally as a boolean but saved to file as 0/1 to interface with C
    """
    @property
    def notifications_muted(self):
        return self._notifications_muted

    @notifications_muted.setter
    def notifications_muted(self, value):
        if not isinstance(value, bool):
            msg = "'notifications_muted' must be a boolean value."
            raise UpdaterStatusError(msg)

        logger.debug("Setting the status' notifications_muted to: {}"
                     .format(value))
        self._notifications_muted = value

    # -- is_shutdown - used to determine whether to finish install with reboot or shutdown
    @property
    def is_shutdown(self):
        return self._is_shutdown

    @is_shutdown.setter
    def is_shutdown(self, value):
        if not isinstance(value, bool):
            msg = "'is_shutdown' must be a boolean value."
            raise UpdaterStatusError(msg)

        logger.debug("Setting the status' is_shutdown to: {}".format(value))
        self._is_shutdown = value
