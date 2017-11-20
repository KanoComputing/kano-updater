# finish.py
#
# Copyright (C) 2015-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Restart computer widget


from gi.repository import Gtk
import os
import time
from threading import Timer

from kano_updater.status import UpdaterStatus
from kano_updater.ui.views.countdown import Countdown


class Finish(Countdown):
    def __init__(self):
        Countdown.__init__(self)

        complete = Gtk.Label(_('Update complete!'))
        complete.get_style_context().add_class('H1')

        status = UpdaterStatus.get_instance()
        self._shutdown_scheduled = status.is_shutdown

        if self._shutdown_scheduled:
            finish_method = _("shutdown")
        else:
            finish_method = _("restart")

        info = Gtk.Label(_(
            "Your Kano is up to date and \n"
            "will automatically {} in 10 seconds"
            .format(finish_method))
        )
        info.set_justify(Gtk.Justification.CENTER)
        info.get_style_context().add_class('H2')

        instructions = Gtk.Label(_("Press ENTER to {} now".format(finish_method)))
        instructions.get_style_context().add_class('H3')
        instructions.set_margin_top(50)

        self._main_grid.attach(complete, 0, 1, 1, 1)
        self._main_grid.attach(info, 0, 2, 1, 1)
        self._main_grid.attach(instructions, 0, 3, 1, 1)

        self.connect('show', self._on_show)

    def _on_show(self, widget=None):
        self.get_toplevel().connect('key-press-event', self._finish)
        self._start_timer()

    def _start_timer(self):
        timer = Timer(11, self._finish, ())
        timer.daemon = True
        timer.start()

    def _finish(self, window=None, event=None):
        if event and event.get_keycode()[1] != 36:  # ENTER
            return

        if self._shutdown_scheduled:
            os.system('systemctl poweroff')
        else:
            os.system('systemctl reboot')

        # Terminate the updater to allow for automated tests
        # Note that sys.exit() does not work, and os._exit() does work
        # but its does not call signal handlers.
        time.sleep(10)
        os._exit(0)
