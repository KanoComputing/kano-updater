
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

from kano_updater.commands.download import download
from kano_updater.ui.paths import CSS_PATH, IMAGE_PATH

UPDATE_IMAGE = os.path.join(IMAGE_PATH, 'update-screen.png')


class UpdatesAvailableWindow(Gtk.Window):
    IMAGE_WIDTH = 590
    IMAGE_HEIGHT = 270

    def __init__(self):
        Gtk.Window.__init__(self, title=_('New Update'))

        apply_common_to_screen()

        window_height = self.IMAGE_HEIGHT + 200
        self.set_size_request(self.IMAGE_WIDTH, window_height)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.set_icon_name('kano-updater')

        # Make sure this window is always above
        self.set_keep_above(True)

        image = Gtk.Image()
        image.set_from_file(UPDATE_IMAGE)

        background = Gtk.EventBox()
        background.set_size_request(self.IMAGE_WIDTH, self.IMAGE_HEIGHT)
        background.add(image)

        # Header
        heading = Heading(
            _('Time to update!'),
            _('A new update is available'))
        heading.description.set_line_wrap(True)

        download = KanoButton(_('Download').upper())
        download.connect('clicked', self.update)
        download.set_halign(Gtk.Align.CENTER)

        later = OrangeButton(_('Later'))
        later.connect('clicked', Gtk.main_quit)
        later.set_halign(Gtk.Align.START)
        later.set_margin_left(40)

        buttons = Gtk.Overlay()
        buttons.add(download)
        buttons.add_overlay(later)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.pack_start(background, False, False, 0)
        box.pack_start(heading.container, False, False, 10)
        box.pack_start(buttons, False, False, 0)

        self.add(box)

        self.show_all()

    def update(self, *_):
        Gtk.main_quit()

        while Gtk.events_pending():
            Gtk.main_iteration()

        download()
