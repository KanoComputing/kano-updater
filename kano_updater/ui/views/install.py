# install.py
#
# Copyright (C) 2015-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Install widget


import os
import traceback

from gi.repository import Gtk, Gdk

from kano_updater.ui.paths import IMAGE_PATH, FLAPPY_PATH

from kano.utils import has_min_performance, RPI_2_B_SCORE
from kano.logging import logger


class Install(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self, hexpand=True, vexpand=True)

        self.percent_completed_label = None
        self.progress_subphase_label = None
        self.play_game_label = None

        self.is_at_least_rpi2 = has_min_performance(RPI_2_B_SCORE)
        self.is_game_first_launch = True
        self.game_allowed_states = [
            'downloading', 'downloading-pip-pkgs', 'init', 'installing-urgent'
        ]

        self.get_style_context().add_class('install')

        self.add(self._create_progress_grid())
        self.add_overlay(self._create_warning_icon())
        self.add_overlay(self._create_warning_label())

    def update_progress(self, percent, phase_name, msg, sub_msg=''):
        # Enabling flappy-judoka launch only during these phases (when a reboot is iminent)
        if phase_name in self.game_allowed_states and self.is_at_least_rpi2:
            self.get_toplevel().connect('key-release-event', self._launch_game)
            self.play_game_label.show()

        self.progress_subphase_label.set_text(sub_msg + '...')

        self.percent_completed_label.set_text(_("{}% Complete").format(percent))

    def hide_game_play_label(self):
        """ Hide the label with instructions to launch the game """
        # this method needs to be called after show_all
        # TODO: better way of doing this
        self.play_game_label.hide()

    def _create_progress_grid(self):
        """ Helper which creates the central animation, progress & game launch labels """
        progress_grid = Gtk.Grid()
        progress_grid.set_row_spacing(5)

        progress_grid.attach(self._create_animation(), 0, 0, 1, 1)
        progress_grid.attach(self._create_percent_label(), 0, 1, 1, 1)
        progress_grid.attach(self._create_subphase_label(), 0, 2, 1, 1)
        progress_grid.attach(self._create_play_game_label(), 0, 3, 1, 1)

        progress_grid.set_halign(Gtk.Align.CENTER)
        progress_grid.set_valign(Gtk.Align.CENTER)

        box = Gtk.EventBox(hexpand=True, vexpand=True)
        box.add(progress_grid)

        return box

    def _create_animation(self):
        """ Helper which creates a widget for the gif animation """
        animation = Gtk.EventBox()
        animation.add(Gtk.Image.new_from_file(os.path.join(IMAGE_PATH, "loader.gif")))
        animation.set_margin_bottom(20)
        return animation

    def _create_percent_label(self):
        """ Helper which creates a label for % completed """
        self.percent_completed_label = Gtk.Label()
        self.percent_completed_label.get_style_context().add_class('H1')
        return self.percent_completed_label

    def _create_subphase_label(self):
        """ Helper which creates a label for the apt progress updates """
        self.progress_subphase_label = Gtk.Label()
        self.progress_subphase_label.get_style_context().add_class('H2')
        return self.progress_subphase_label

    def _create_play_game_label(self):
        """ Helper which creates a label with instructions to launch a game """
        self.play_game_label = Gtk.Label()
        self.play_game_label.set_text(_("Press [ J ] to play a game"))
        self.play_game_label.get_style_context().add_class('H3')
        self.play_game_label.set_margin_top(50)
        return self.play_game_label

    def _create_warning_icon(self):
        """ Helper which creates the bolt icon widget """
        icon = Gtk.Image.new_from_file(os.path.join(IMAGE_PATH, "bolt-icon.png"))
        icon.set_halign(Gtk.Align.CENTER)
        icon.set_valign(Gtk.Align.END)
        icon.set_margin_bottom(60)
        return icon

    def _create_warning_label(self):
        """ Helper which creates a label with a warning message about power """
        label = Gtk.Label()
        label.set_text(_("Your computer needs to be plugged in and turned on while updating"))
        label.get_style_context().add_class('H2')
        label.set_margin_bottom(25)
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.END)
        return label

    def _launch_game(self, window=None, event=None):
        """ Key release event handler for this view which only launches the game """
        try:
            if event and event.get_keyval()[1] in [Gdk.KEY_j, Gdk.KEY_J]:
                os.system('{} &'.format(FLAPPY_PATH))
        except:
            logger.error(
                "Unexpected error in _launch_game()\n{}".format(traceback.format_exc())
            )
