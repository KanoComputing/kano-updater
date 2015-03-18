
# restart.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Restart computer widget
#

from gi.repository import Gtk, GdkPixbuf
import os
from threading import Timer

from kano_updater.ui.paths import IMAGE_PATH


class Restart(Gtk.Alignment):
    REBOOT_ANIMATION = os.path.join(IMAGE_PATH, 'circular_progress.gif')

    def __init__(self):
        Gtk.Alignment.__init__(self, xalign=0.5, yalign=0.5, xscale=0, yscale=0)

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        self.add(grid)

        style = self.get_style_context().add_class('restart')

        reboot_animation = GdkPixbuf.PixbufAnimation.new_from_file(
            self.REBOOT_ANIMATION)
        reboot_progress = Gtk.Image()
        reboot_progress.set_from_animation(reboot_animation)

        complete = Gtk.Label(_('Update complete!'))
        complete.get_style_context().add_class('complete')

        info = Gtk.Label(_('Your KANO is up to date and \n'
                           'will automatically restart in 10 seconds'))
        info.set_justify(Gtk.Justification.CENTER)
        info.get_style_context().add_class('countdown')

        instructions = Gtk.Label(_('Press ENTER to restart now'))
        instructions.get_style_context().add_class('restart-now')

        grid.attach(reboot_progress, 0, 0, 1, 1)
        grid.attach(complete, 0, 1, 1, 1)
        grid.attach(info, 0, 2, 1, 1)
        grid.attach(instructions, 0, 3, 1, 1)

        self.connect('show', self._on_show)

    def _on_show(self, widget=None):
        self.get_toplevel().connect('key-press-event', self._reboot)
        self._start_timer()

    def _start_timer(self):
        timer = Timer(11, self._reboot, ())
        timer.daemon = True
        timer.start()

    def _reboot(self, window=None, event=None):
        if event and event.get_keycode()[1] != 36: # ENTER
            return

        os.system('reboot')
