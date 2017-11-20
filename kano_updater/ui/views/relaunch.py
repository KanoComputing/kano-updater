# relaunch.py
#
# Copyright (C) 2015-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Restart computer widget


import os
import signal

from gi.repository import Gtk

from kano_updater.ui.views.countdown import Countdown


class Relaunch(Countdown):
    def __init__(self, parent_pid):
        Countdown.__init__(self)

        self._parent_pid = parent_pid

        complete = Gtk.Label(_("Updater updated!"))
        complete.get_style_context().add_class('H1')

        info = Gtk.Label(_("Relaunching..."))
        info.set_justify(Gtk.Justification.CENTER)
        info.get_style_context().add_class('H2')

        self._main_grid.attach(complete, 0, 1, 1, 1)
        self._main_grid.attach(info, 0, 2, 1, 1)

        self.connect('map', self._on_map)

    def _on_map(self, widget=None):
        os.kill(self._parent_pid, signal.SIGUSR1)
