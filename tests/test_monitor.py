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

def run_monitor_wrap(mon_timeout, test_cmd):
    import subprocess
    return subprocess.call(["./tests/monitor_wrap.py"]+test_cmd, shell=False)


def test_return_code(monitor_pid, apt):
    import os
    import random
    # When command returns in time,
    # Then rc should be the command's rc
    expected_rc = random.randint(1, 20)
    rc = run_monitor(10, ["./tests/monitor_stub.py", "5", str(expected_rc)])
    assert rc == expected_rc


def test_return_timeout(monitor_pid, apt):
    import os
    import random
    import kano_updater.return_codes
    # When command returns in time,
    # Then rc should be HANGED_INDEFINITELY
    command_rc = random.randint(1, 20)
    rc = run_monitor(5, ["./tests/monitor_stub.py", "10", str(command_rc)])
    assert rc == kano_updater.return_codes.RC.HANGED_INDEFINITELY 


def test_forking(monitor_pid, apt):
    import os
    import random
    # When command takes longer than timeout but forks,
    # Then rc should be the command's rc
    expected_rc = random.randint(1, 20)
    rc = run_monitor(5, ["./tests/monitor_stub.py", "--forking", "10", str(expected_rc)])
    assert rc == expected_rc


def test_signal(monitor_pid, apt):
    import os
    import random
    # When command takes longer than timeout but signals,
    # Then rc should be the command's rc
    expected_rc = random.randint(1, 20)
    rc = run_monitor(5, ["./tests/monitor_stub.py", "--signal", "10", str(expected_rc)])
    assert rc == expected_rc


def test_no_monitor(monitor_pid, apt):
    import os
    import random
    os.environ["MONITOR_PID"] = str(os.getpid())
    # When MONITOR_PID is already set, don't execute monitor behavior

    command_rc = random.randint(1, 20)
    rc = run_monitor_wrap(5, ["./tests/monitor_stub.py", "10", str(command_rc)])
    assert rc == command_rc  # would be HANGED_INDEFINITELY except that we are not monitoring


def test_monitor_term(monitor_pid, apt):

    import random
    import subprocess
    import time
    import signal
    # When we send a term signal to the monitor process, it sends it to the
    # child process.
    # Note that this test assumes that the monitor process correctly
    # reports the child process exit code
    command_rc = random.randint(1, 20)
    proc = subprocess.Popen(["./tests/monitor_stub.py", "10", str(command_rc)])
    time.sleep(2)
    proc.terminate()
    proc.wait()
    rc = proc.returncode
    assert rc == -signal.SIGTERM

# TBD:
#   - test gui mode
