
# main_window.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Updater main window
#

import os
from gi.repository import Gtk

from kano.gtk3.apply_styles import apply_styling_to_screen

from kano_updater.ui.paths import CSS_PATH


class MainWindow(Gtk.Window):
    CSS_FILE = os.path.join(CSS_PATH, 'updater.css')

    def __init__(self):
        # Apply styling to window
        apply_styling_to_screen(self.CSS_FILE)

        Gtk.Window.__init__(self)
        self.set_resizable(False)
        self.maximize()
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(False)
        # Make sure this window is always above
        self.set_keep_above(True)

        self.set_icon_name('kano-updater')
        self.set_title(_('Updater'))

        grid = Gtk.Grid()
        self.add(grid)

        self.show_all()

        self.connect('delete-event', self.close_window)
