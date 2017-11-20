# countdown.py
#
# Copyright (C) 2015-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The base view for the Restart and Relaunch views that come with a countdown


from gi.repository import Gtk, GdkPixbuf
import os

from kano_updater.ui.paths import IMAGE_PATH


class Countdown(Gtk.Alignment):
    REBOOT_ANIMATION = os.path.join(IMAGE_PATH, 'loader.gif')

    def __init__(self):
        Gtk.Alignment.__init__(self, xalign=0.5, yalign=0.5, xscale=0, yscale=0)

        self._main_grid = Gtk.Grid()
        self._main_grid.set_row_spacing(5)
        self.add(self._main_grid)

        reboot_animation = GdkPixbuf.PixbufAnimation.new_from_file(self.REBOOT_ANIMATION)
        reboot_progress = Gtk.Image()
        reboot_progress.set_from_animation(reboot_animation)
        reboot_progress.set_margin_bottom(20)

        self._main_grid.attach(reboot_progress, 0, 0, 1, 1)
