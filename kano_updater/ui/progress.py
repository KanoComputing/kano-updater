# progress.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Thread-safe progress reporting for Gtk


from gi.repository import GLib, Gtk

from kano_updater.progress import Progress
from kano_updater.ui.main import relaunch_required
from kano_updater.utils import kill_flappy_judoka


class GtkProgress(Progress):

    def __init__(self, window):
        super(GtkProgress, self).__init__()
        self._window = window

    def _change(self, phase, msg):
        GLib.idle_add(self._window.update_progress, phase.global_percent,
                      phase.get_main_phase().label, phase.get_main_phase().name, msg)

    def _error(self, phase, msg):
        err_msg = "Error {} - {}".format(phase.label.lower(), msg)
        GLib.idle_add(self._window.error, err_msg)

    def _abort(self, phase, msg):
        kill_flappy_judoka()
        err_msg = "{} - {}".format(phase.label.lower(), msg)
        GLib.idle_add(self._window.error, err_msg)

    def _done(self, msg):
        GLib.idle_add(self._window.update_progress, 100,
                      "Complete!", '', msg)

    def _prompt(self, msg, question, answers):
        GLib.idle_add(self._window.user_prompt, msg, question, answers)

        # Wait for the answer from the user
        self._window.user_input_lock.acquire()
        answer = self._window.user_input

        # Reinitialise user_input_lock
        self._window.user_input_lock.release()
        GLib.idle_add(self._window.reset_user_input)

        return answer

    def _relaunch(self):
        GLib.idle_add(self._do_relaunch)

    def _do_relaunch(self):
        relaunch_required()
        Gtk.main_quit()
