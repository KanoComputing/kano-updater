# network.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Network Utilities
#

import os

from kano.network import is_internet
from kano.logging import logger

from kano_updater.utils.pip import install_ping

REPO_SERVER = 'repo.kano.me'


def is_server_available():
    install_ping()
    import ping

    lost_packet_percent = ping.quiet_ping(REPO_SERVER, timeout=0.2, count=1)[0]

    return not lost_packet_percent

# --------------------------------------

def check_internet():
    if is_internet():
        return True

    logger.warn("No internet connection detected")
    os.system("kano-settings 12")
    return is_internet()
