#
# test_monitor.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the `kano_updater.monitor` module
#


import pytest


def run_monitor(mon_timeout, test_cmd):
    import kano_updater.monitor
    kano_updater.monitor.MONITOR_TIMEOUT = mon_timeout
    rc = kano_updater.monitor.run(test_cmd)

    return rc


def test_return_code():
    import os
    import random
    # When command returns in time,
    # Then rc should be the command's rc
    expected_rc = random.randint(1, 20)
    rc = run_monitor(10, ["./tests/monitor_stub.py", "5", str(expected_rc)])
    assert rc == expected_rc


def test_return_timeout():
    import os
    import random
    import kano_updater.return_codes
    # When command returns in time,
    # Then rc should be HANGED_INDEFINITELY
    command_rc = random.randint(1, 20)
    rc = run_monitor(5, ["./tests/monitor_stub.py", "10", str(command_rc)])
    assert rc == kano_updater.return_codes.RC.HANGED_INDEFINITELY 


def test_forking():
    import os
    import random
    # When command takes longer than timeout but forks,
    # Then rc should be the command's rc
    expected_rc = random.randint(1, 20)
    rc = run_monitor(5, ["./tests/monitor_stub.py", "--forking", "10", str(expected_rc)])
    assert rc == expected_rc


def test_signal():
    import os
    import random
    # When command takes longer than timeout but signals,
    # Then rc should be the command's rc
    expected_rc = random.randint(1, 20)
    rc = run_monitor(5, ["./tests/monitor_stub.py", "--signal", "10", str(expected_rc)])
    assert rc == expected_rc


# TBD:
#   - test gui mode
