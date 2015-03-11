
# progress.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Thread-safe progress reporting for Gtk
#

from gi.repository import GLib

from kano_updater.progress import Progress, Relaunch

class GtkProgress(Progress):

    def __init__(self, window):
        super(GtkProgress, self).__init__()
        self._window = window

    def _change(self, phase, msg):
        GLib.idle_add(self._window.update_progress, phase.global_percent,
                      phase.get_main_phase().label, msg)

    def _error(self, phase, msg):
        err_msg = "Error {} - {}".format(phase.label.lower(), msg)
        GLib.idle_add(self._window.error, err_msg)

    def _abort(self, phase, msg):
        print "Aborting {}, {}".format(phase.label, msg)

    def _done(self, msg):
        GLib.idle_add(self._window.update_progress, 100,
                      "Complete!", msg)

    def _relaunch(self):
        GLib.idle_add(self._do_relaunch)

    def _do_relaunch(self):
        raise Relaunch()
