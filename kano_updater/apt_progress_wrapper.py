#
# Interfacing updater progress objects with python-apt progress objects
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os
import sys
import apt
import re

from kano_updater.progress import Phase


class AptDownloadProgress(apt.progress.base.AcquireProgress):
    """
        An adaptor of apt's AcquireProgress to the updater's progress
        reporting class.
    """

    def __init__(self, updater_progress, steps):
        super(AptDownloadProgress, self).__init__()
        self._phase_name = updater_progress.get_current_phase().name
        self._updater_progress = updater_progress
        self._steps = steps

        self.items = {}
        self._filesizes = []

    def start(self):
        self._updater_progress.init_steps(self._phase_name, self._steps)
        super(AptDownloadProgress, self).start()

    def fetch(self, item_desc):
        self._filesizes.append(item_desc.owner.filesize)

    def done(self, item_desc):
        super(AptDownloadProgress, self).done(item_desc)
        msg = _("Downloading {}").format(item_desc.shortdesc)

        # Show the long description too if it's not too long
        if len(item_desc.description) < 40:
            msg = "{} {}".format(msg, item_desc.description)

        self._updater_progress.next_step(self._phase_name, msg)

    def fail(self, item_desc):
        self._updater_progress.fail(item_desc.description)

    # TODO: Remove
    #def pulse(self, owner):
    #    return True

    #def stop(self):
    #    super(AptDownloadProgress, self).stop()


class AptOpProgress(apt.progress.base.OpProgress):
    def __init__(self, updater_progress, ops=[]):
        super(AptOpProgress, self).__init__()

        self._updater_progress = updater_progress
        self._phase_name = updater_progress.get_current_phase().name

        self.ops = [(self._get_op_key(op[0]), op[1]) for op in ops]

        phases = [Phase(op[0], op[1]) for op in self.ops]
        self._updater_progress.split(*phases)

        for op in self.ops:
            self._updater_progress.init_steps(op[0], 100)

    def _get_op_key(self, op_name):
        return self._phase_name + '-' + op_name

    def _next_phase(self):
        if len(self._ops) <= 1:
            return

        del self._ops[0]

        new_phase = self._ops[0]
        self._phase_name = new_phase
        self._updater_progress.start(new_phase)
        self._updater_progress.init_steps(new_phase, 100)

    def update(self, percent=None):
        super(AptOpProgress, self).update(percent)

        phase_label = self.op.decode('utf-8')

        # Find the phase name for the operation
        phase_name = None
        for op in self.ops:
            if op[1] == phase_label:
                phase_name = op[0]
                break

        self._updater_progress.set_step(phase_name,
                                        self.percent, phase_label)


class AptInstallProgress(apt.progress.base.InstallProgress):
    def __init__(self, updater_progress):
        super(AptInstallProgress, self).__init__()

        self._phase_name = updater_progress.get_current_phase().name

        self._updater_progress = updater_progress
        updater_progress.init_steps(self._phase_name, 100)

    def conffile(self, current, new):
        print "conffile", current, new

    def error(self, pkg, errormsg):
        self._updater_progress.fail("{}: {}".format(pkg, errormsg))

    def processing(self, pkg, stage):
        print "processing", pkg, stage

    def dpkg_status_change(self, pkg, status):
        print "dpkg_status_change", pkg, status

    def status_change(self, pkg, percent, status):
        self._updater_progress.set_step(self._phase_name, percent, status)

    #def start_update(self):
    #    print "start_update"

    #def finish_update(self):
    #    #print "finish_update"

    def fork(self):
        """Fork."""

        pid = os.fork()
        if not pid:
            # Silence the crap dpkg prints on stdout without being asked for it
            null = os.open(os.devnull, os.O_RDWR)
            os.dup2(null, sys.stdin.fileno())
            os.dup2(null, sys.stdout.fileno())
            os.dup2(null, sys.stderr.fileno())

        return pid
