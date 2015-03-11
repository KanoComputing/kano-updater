
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
        complete.get_style_context().add_class('heading')

        info = Gtk.Label(_('Your KANO is up to date and \n'
                           'will automatically restart in 10 seconds'))
        info.set_justify(Gtk.Justification.CENTER)
        style = info.get_style_context()
        style.add_class('heading')
        style.add_class('subheading')

        instructions = Gtk.Label(_('Press ENTER to restart now'))
        style = instructions.get_style_context()
        style.add_class('heading')
        style.add_class('subheading')
        style.add_class('small-print')

        grid.attach(reboot_progress, 0, 0, 1, 1)
        grid.attach(complete, 0, 1, 1, 1)
        grid.attach(info, 0, 2, 1, 1)
        grid.attach(instructions, 0, 3, 1, 1)

        self._start_timer()

    def _start_timer(self, *args):
        Timer(11, self._reboot, ()).start()

    def _reboot(self):
        # TODO Actually reboot
        Gtk.main_quit()
