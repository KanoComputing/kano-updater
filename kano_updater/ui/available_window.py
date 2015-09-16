
# check-for-updates
#
# Copyright (C) 2014-2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Checks for updates of packages that are maintained by Kano
#

import os
from gi.repository import Gtk

from kano.gtk3.buttons import KanoButton, OrangeButton
from kano.gtk3.heading import Heading
from kano.gtk3.apply_styles import apply_common_to_screen

from kano_updater.utils import make_low_prio
from kano_updater.ui.paths import CSS_PATH, IMAGE_PATH

UPDATE_IMAGE = os.path.join(IMAGE_PATH, 'update-screen.gif')


class NotificationWindow(Gtk.Window):
    _HEADER_IMAGE = None
    _IMAGE_WIDTH = 0
    _IMAGE_HEIGHT = 0

    _TITLE = ''
    _HEADING = ''
    _BYLINE = ''
    _ACTION = ''

    def __init__(self):
        Gtk.Window.__init__(self, title=self._TITLE)

        apply_common_to_screen()

        window_height = self._IMAGE_HEIGHT + 220
        self.set_size_request(self._IMAGE_WIDTH, window_height)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.set_icon_name('kano-updater')

        # Put the window above all the existing ones when it starts
        # FIXME: this needs to happen within a 'realized' signal handler
        #        disabled for now
        #self.get_window().raise_()

        image = Gtk.Image()
        image.set_from_file(self._HEADER_IMAGE)

        background = Gtk.EventBox()
        background.set_size_request(self._IMAGE_WIDTH, self._IMAGE_HEIGHT)
        background.add(image)

        # Header
        heading = Heading(self._HEADING, self._BYLINE)
        heading.description.set_line_wrap(True)

        action = KanoButton(self._ACTION.upper())
        action.connect('clicked', self._do_action)
        action.set_halign(Gtk.Align.CENTER)

        later = OrangeButton(_('Later'))
        later.connect('clicked', Gtk.main_quit)
        later.set_halign(Gtk.Align.START)
        later.set_margin_left(40)

        buttons = Gtk.Overlay()
        buttons.add(action)
        buttons.add_overlay(later)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.pack_start(background, False, False, 0)
        box.pack_start(heading.container, False, False, 10)
        box.pack_start(buttons, False, False, 0)

        self.add(box)

        self.show_all()

    def _do_action(self, *_):
        self.destroy()

        self._action()

    def _action(self):
        raise NotImplementedError(_('The action needs to be implemented'))


class UpdatesAvailableWindow(NotificationWindow):
    _HEADER_IMAGE = UPDATE_IMAGE
    _IMAGE_WIDTH = 590
    _IMAGE_HEIGHT = 270

    _TITLE = _('New Update')
    _HEADING = _('Get new powers')
    _BYLINE = _('Download the latest Kano OS')
    _ACTION = _('Download')

    def _action(self):
        from kano_updater.commands.download import download

        Gtk.main_quit()

        while Gtk.events_pending():
            Gtk.main_iteration()

        make_low_prio()
        download()


class UpdatesDownloadedWindow(NotificationWindow):
    _HEADER_IMAGE = UPDATE_IMAGE
    _IMAGE_WIDTH = 590
    _IMAGE_HEIGHT = 270

    _TITLE = _('New Update')
    _HEADING = _('Almost there...')
    _BYLINE = _('Downloaded and ready to go! In a matter\n'
                'of minutes your Kano will be fresher than ever')
    _ACTION = _('Install')

    def _action(self):
        from kano_updater.ui.install_window import InstallWindow

        win = InstallWindow()
        win.show()
