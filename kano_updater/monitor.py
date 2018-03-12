# monitor.py
#
# Copyright (C) 2014-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module to allow us to detect when a process is stuck.

# Also heartbeat() function for a monitored process
# to notify the monitor that it is proceeding normally.

import subprocess
from collections import defaultdict
import sys
import time
import signal
import os
from kano.logging import logger
import kano_updater.utils

MONITOR_TIMEOUT = 20 * 60
TIMEOUT_RC = 105


class monitorPids:
    """
    Class for monitoring a subprocess tree. If the (recursive) set of child
    processes changes, we assume it is still making progress.
    """
    def __init__(self, top_pid):
        self.top_pid = top_pid
        self.curr_children = set()

    def _get_children(self):
        """
        return a set() of all children (recursively) of
        self.top_pid (inclusive)
        """
        try:
            stdout = subprocess.check_output(["/bin/ps", "-eo", "ppid,pid"])
            coll = defaultdict(set)

            for line in stdout.split('\n'):
                items = line.split()
                if len(items) >= 2:
                    ppid, pid = items[:2]
                    if ppid == 'PPID':
                        continue
            try:
                coll[int(ppid)].add(int(pid))
            except:
                pass  # ignore int conversion failure

            def closure(pids):
                curr = pids.copy()
                for p in pids:
                    curr = curr.union(closure(coll[p]))
                return curr
            return closure(set([self.top_pid]))

        except subprocess.CalledProcessError:
            return set()

    def isChanged(self):
        """
        return True if we believe it is making progress
        otherwise False
        """
        changed = False
        new_children = self._get_children()

        if self.curr_children != new_children:
            self.curr_children = new_children
            changed = True
        return changed


def monitor(watchproc, timeout):
    """
    Monitor a process tree. If the (recursive) set of child processes changes
    or we are sent a SIGUSR1, we note that it is making progress.
    if it has not made progress for `timeout` seconds, or the process
    finished, exit.

    Returns true if we timed out and false if the process finished


    """
    watchpid = watchproc.pid

    spoll = kano_updater.utils.signalPoll(signal.SIGUSR1)

    lastEvent = time.time()

    pids = monitorPids(watchpid)

    while True:
        now = time.time()
        # check for child events
        changed = pids.isChanged()
        if watchproc.poll() is not None:
            return False

        signalled = spoll.poll()
        if changed or signalled:
            lastEvent = now

        if lastEvent + timeout < now:
            return True

        time.sleep(1)


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


def run(cmdargs):
    os.environ["MONITOR_PID"] = str(os.getpid())
    subproc = subprocess.Popen(cmdargs,
                               shell=False)

    if not monitor(subproc, MONITOR_TIMEOUT):
        return subproc.returncode
    else:
        if '--gui' in cmdargs:
            from kano.gtk3 import kano_dialog
            kdialog = kano_dialog.KanoDialog(
                _("Update error"),
                _("The updater seems to have got stuck. Press OK to reboot"))
            kdialog.run()
            os.system('systemctl reboot')

        else:
            return TIMEOUT_RC


def manual_test_main(argv):
    import kano_i18n.init

    if __name__ == '__main__' and __package__ is None:
        DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if DIR_PATH != '/usr':
            sys.path.insert(0, DIR_PATH)
            LOCALE_PATH = os.path.join(DIR_PATH, 'locale')
        else:
            LOCALE_PATH = None

    kano_i18n.init.install('kano-updater', LOCALE_PATH)
    watchpid = int(argv[1])
    timeout = int(argv[2])
    monitor(watchpid, timeout)

if __name__ == '__main__':
    
    exit(manual_test_main(sys.argv))
