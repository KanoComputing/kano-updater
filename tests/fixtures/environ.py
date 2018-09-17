#
# environ.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixture to clean environment
#


import pytest
import os


@pytest.fixture(scope='function', params=(True, False))
def monitor_pid():
    """
    ensures environment variable MONITOR_PID is not propagated across tests
    """
    try:        
        del os.environ["MONITOR_PID"]
    except:
        pass

