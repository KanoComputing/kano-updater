#
# relaunch_window.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Installer main window
#

import os
from gi.repository import Gtk, Gdk

from kano.gtk3.apply_styles import apply_styling_to_screen

from kano_updater.ui.paths import CSS_PATH
from kano_updater.ui.views.relaunch import Relaunch
from kano_updater.utils import bring_flappy_judoka_to_front


class RelaunchWindow(Gtk.Window):
    CSS_FILE = os.path.join(CSS_PATH, 'updater.css')

    def __init__(self, parent_pid):
        # Apply styling to window
        apply_styling_to_screen(self.CSS_FILE)

        Gtk.Window.__init__(self)
        self.fullscreen()
        self.set_keep_above(True)

        self.set_icon_name('kano-updater')
        self.set_title(_('Updater Splash'))

        self._relaunch_screen = Relaunch(parent_pid)
        self.add(self._relaunch_screen)

        self.show_all()
        self._set_wait_cursor()

        bring_flappy_judoka_to_front()

    def _set_wait_cursor(self):
        cursor = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        self.get_root_window().set_cursor(cursor)
