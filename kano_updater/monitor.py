# monitor.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module to allow us to detect when a process is stuck.


import subprocess
from collections import defaultdict
import sys
import time
import signal
import os

from kano_updater.signal_handling import SignalPoll
import kano_updater.utils
import kano_updater.return_codes

MONITOR_TIMEOUT = 20 * 60


class MonitorPids(object):
    """
    Class for monitoring a subprocess tree. If the (recursive) set of child
    processes changes, we assume it is still making progress.
    """
    def __init__(self, top_pid):
        self.top_pid = top_pid
        self.curr_children = set()

    def _get_children(self):
        """
        Returns:
           a set() of all children (recursively) of self.top_pid (inclusive)
        """
        try:
            stdout = subprocess.check_output(["/bin/ps", "-eo", "ppid,pid"])
            # ps configured to output lines of the form "parent_pid child_pid"
            coll = defaultdict(set)

            for line in stdout.split('\n'):
                items = line.split()
                if len(items) >= 2:
                    ppid, pid = items[:2]
                    # Ignore the heading line
                    if ppid == 'PPID':
                        continue
                try:
                    coll[int(ppid)].add(int(pid))
                except:
                    pass  # ignore int conversion failure

            def transitive_closure(pids):
                """
                Perform a transitive closure to collect all children
                Args:
                   pids (set of int): partically closed set
                Returns:
                   transitive closure
                """
                curr = pids.copy()
                for p in pids:
                    curr = curr.union(transitive_closure(coll[p]))
                return curr
            return transitive_closure(set([self.top_pid]))

        except subprocess.CalledProcessError:
            return set()

    def is_changed(self):
        """
        Returns:
          True if we believe it is making progress otherwise False
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

    Args:
         watchproc (subprocess.Popen): process to watch
         timeout (int): time in seconds to wait without seeing activity
                        before decalring the process stuck

    Returns:
         true if we timed out and false if the process finished


    """
    watchpid = watchproc.pid

    spoll = SignalPoll(signal.SIGUSR1)

    lastEvent = time.time()

    pids = MonitorPids(watchpid)

    while True:
        now = time.time()
        # check for child events
        changed = pids.is_changed()
        if watchproc.poll() is not None:
            return False

        signalled = spoll.poll()
        if changed or signalled:
            lastEvent = now

        if lastEvent + timeout < now:
            return True

        time.sleep(1)


def run(cmdargs):
    """
    Run and monitor a command
    Args:
        cmdargs (list of string): command and args to run
    Returns:
       error code (integer)
    """
    os.environ["MONITOR_PID"] = str(os.getpid())
    subproc = subprocess.Popen(cmdargs,
                               shell=False)

    if not monitor(subproc, MONITOR_TIMEOUT):
        return subproc.returncode

    kano_updater.utils.track_data_and_sync('updater-hanged-indefinitely', dict())
    kano_updater.utils.clear_tracking_uuid()

    if '--gui' in cmdargs:
        from kano.gtk3 import kano_dialog
        kdialog = kano_dialog.KanoDialog(
            _("Update error"),
            _("The updater seems to have got stuck. Press OK to reboot"))
        kdialog.run()
        os.system('systemctl reboot')

        # for test purposes:
        time.sleep(10)
        os._exit(kano_updater.return_codes.RC.HANGED_INDEFINITELY)

    return kano_updater.return_codes.RC.HANGED_INDEFINITELY


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
    global MONITOR_TIMEOUT
    MONITOR_TIMEOUT = int(argv[1])
    return run(argv[2:])


if __name__ == '__main__':
    exit(manual_test_main(sys.argv))
