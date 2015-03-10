
# install_window.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Installer main window
#

import os
from gi.repository import Gtk
from threading import Thread

from kano.gtk3.apply_styles import apply_styling_to_screen

from kano_updater.ui.paths import CSS_PATH
from kano_updater.commands.install import install
from kano_updater.ui.progress import GtkProgress


class InstallWindow(Gtk.Window):
    CSS_FILE = os.path.join(CSS_PATH, 'updater.css')

    def __init__(self):
        # Apply styling to window
        apply_styling_to_screen(self.CSS_FILE)

        Gtk.Window.__init__(self)
        # self.fullscreen()
        self.set_keep_above(True)

        self.set_icon_name('kano-updater')
        self.set_title(_('Updater'))

        align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        self.add(align)

        grid = Gtk.Grid()
        align.add(grid)

        self._progress_phase = Gtk.Label()
        self._progress_phase.get_style_context().add_class('phase')

        self._progress_subphase = Gtk.Label()
        style = self._progress_subphase.get_style_context()
        style.add_class('phase')
        style.add_class('subphase')

        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_show_text(False)

        close = Gtk.Button('Close')
        close.connect('clicked', self.close_window)

        grid.attach(self._progress_phase, 0, 0, 1, 1)
        grid.attach(self._progress_subphase, 0, 1, 1, 1)
        grid.attach(self._progress_bar, 0, 2, 1, 1)
        grid.attach(close, 0, 100, 1, 1)

        self.show_all()

        self.connect('delete-event', self.close_window)

        self._start_install()

    def _start_install(self):
        progress = GtkProgress(self)
        install_thread = Thread(target=install, args=(progress,))
        # FIXME: What to do when the gui is killed and the thread is still running?
        install_thread.daemon = True
        install_thread.start()

    def close_window(self, widget=None, event=None):
        Gtk.main_quit()

    def update_progress(self, percent, msg, sub_msg=''):
        self._progress_bar.set_fraction(percent / 100.)
        self._progress_phase.set_text(msg)
        self._progress_subphase.set_text(sub_msg)
