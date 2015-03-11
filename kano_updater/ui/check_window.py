
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
from kano_updater.ui.paths import IMAGE_PATH

UPDATE_IMAGE = os.path.join(IMAGE_PATH, 'update-screen.png')


class CheckWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=_('New Update'))

        apply_common_to_screen()

        self.image_width = 590
        self.image_height = 270
        self.window_height = 500
        self.set_size_request(self.image_width, self.window_height)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.set_icon_name('kano-updater')

        # Make sure this window is always above
        self.set_keep_above(True)

        # Header
        self.heading = Heading(
            _('Time to update!'),
            _('A new update is available'))
        self.heading.description.set_line_wrap(True)

        self.button = KanoButton(_('Download').upper())
        self.button.connect('clicked', self.update)
        self.later = OrangeButton(_('Later'))
        self.later.connect('clicked', Gtk.main_quit)

        self.button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                  spacing=15)
        self.button_box.pack_start(self.button, False, False, 0)
        self.button_box.pack_start(self.later, False, False, 0)

        self.button_alignment = Gtk.Alignment(xalign=0.5, yalign=0.5,
                                              xscale=0, yscale=0)
        self.button_alignment.add(self.button_box)

        self.image = Gtk.Image()
        self.image.set_from_file(UPDATE_IMAGE)

        self.background = Gtk.EventBox()
        self.background.set_size_request(self.image_width, self.image_height)
        self.background.add(self.image)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.box.pack_start(self.background, False, False, 0)
        self.box.pack_start(self.heading.container, False, False, 10)
        self.box.pack_start(self.button_alignment, False, False, 0)

        self.add(self.box)

    def update(self, widget, event):
        download()
