#
# relaunch.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Restart computer widget
#

from gi.repository import Gtk

from kano_updater.ui.views.countdown import Countdown

class Relaunch(Countdown):
    def __init__(self):
        Countdown.__init__(self)

        complete = Gtk.Label(_('Relaunching the Updater'))
        complete.get_style_context().add_class('complete')

        info = Gtk.Label(_('The Updater updated itself and is now '
                           'starting again.'))
        info.set_justify(Gtk.Justification.CENTER)
        info.get_style_context().add_class('countdown')

        self._main_grid.attach(complete, 0, 1, 1, 1)
        self._main_grid.attach(info, 0, 2, 1, 1)
