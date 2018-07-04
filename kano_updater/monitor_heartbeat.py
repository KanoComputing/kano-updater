# monitor_heartbeat.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# logically part of the heartbeat module, but
# causes dependency problems


import os
from kano.logging import logger
import signal


def heartbeat():
    """
    Inform monitor process, if it exists, that we are still alive
    """

    monitor_pid = os.environ.get("MONITOR_PID")
    if monitor_pid:
        try:
            pid = int(monitor_pid)
            os.kill(pid, signal.SIGUSR1)
        except:
            logger.error("Invalid monitor pid {}".format(monitor_pid))
