# install.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Install widget


import os
import traceback

from gi.repository import Gtk, Gdk

from kano_updater.ui.stage_text import STAGE_TEXT
from kano_updater.ui.paths import FLAPPY_PATH

from kano.utils import has_min_performance, RPI_2_B_SCORE
from kano.logging import logger


class Install(Gtk.Overlay):

    def __init__(self):
        Gtk.Overlay.__init__(self, hexpand=True, vexpand=True)

        self.get_style_context().add_class('install')

        self._pgl = self._create_play_game_label()
        progress = self._create_progress_grid()
        self._psa = self._create_psa()

        self.add_overlay(self._pgl)
        self.add(progress)
        self.add_overlay(self._psa)

        self._is_game_first_launch = True

    def _create_progress_bar(self):
        self._progress_bar = Gtk.ProgressBar(hexpand=False)
        self._progress_bar.set_size_request(375, -1)
        self._progress_bar.set_show_text(False)

        self._progress_bar.set_halign(Gtk.Align.CENTER)
        self._progress_bar.set_valign(Gtk.Align.CENTER)

        self._progress_bar.set_margin_top(8)
        self._progress_bar.set_margin_bottom(8)

        return self._progress_bar

    def _create_play_game_label(self):
        play_game_label = Gtk.Label()
        play_game_label.set_text(_('Do you want to play a cool game instead? PRESS [J] TO LAUNCH!'))
        play_game_label.set_size_request(825, 300)
        play_game_label.set_halign(Gtk.Align.CENTER)
        play_game_label.set_valign(Gtk.Align.START)
        play_game_label.get_style_context().add_class('play-game')

        return play_game_label

    def _create_phase_label(self):
        self._progress_phase = Gtk.Label()
        self._progress_phase.get_style_context().add_class('phase')

        return self._progress_phase

    def _create_subphase_label(self):
        self._progress_subphase = Gtk.Label()
        style = self._progress_subphase.get_style_context()
        style.add_class('subphase')

        return self._progress_subphase

    def _create_phase_percent(self):
        self._percent_display = Gtk.Label()
        style = self._percent_display.get_style_context()
        style.add_class('percent')

        return self._percent_display

    def _create_progress_grid(self):
        progress_grid = Gtk.Grid()
        progress_grid.set_row_spacing(5)

        progress_grid.attach(self._create_phase_label(), 0, 0, 1, 1)
        progress_grid.attach(self._create_subphase_label(), 0, 1, 1, 1)
        progress_grid.attach(self._create_progress_bar(), 0, 2, 1, 1)
        progress_grid.attach(self._create_phase_percent(), 0, 3, 1, 1)

        progress_grid.set_halign(Gtk.Align.CENTER)
        progress_grid.set_valign(Gtk.Align.END)

        progress_grid.get_style_context().add_class('progress')
        progress_grid.set_margin_bottom(80)

        box = Gtk.EventBox(hexpand=True, vexpand=True)
        box.add(progress_grid)

        return box

    def _create_psa(self):
        psa = Gtk.Label()
        psa.set_size_request(825, 300)
        psa.set_max_width_chars(50)
        psa.set_line_wrap(True)
        psa.set_justify(Gtk.Justification.CENTER)
        psa.set_halign(Gtk.Align.CENTER)
        psa.set_valign(Gtk.Align.CENTER)

        style = psa.get_style_context()
        style.add_class('psa')

        return psa

    def update_progress(self, percent, phase_name, msg, sub_msg=''):
        # enabling flappy-judoka launch only after these phases (when a reboot is iminent)
        if phase_name in ['downloading', 'downloading-pip-pkgs', 'init', 'installing-urgent']:
            if has_min_performance(RPI_2_B_SCORE):
                self.get_toplevel().connect('key-release-event', self._launch_game)
                self._pgl.show()

        percent_fraction = percent / 100.
        self._progress_bar.set_fraction(percent_fraction)

        idx = percent_fraction * (len(STAGE_TEXT) - 1)
        current_text = STAGE_TEXT[int(idx)]
        self._psa.set_markup(current_text)

        if self._progress_phase.get_text() != msg:
            self._progress_phase.set_text(msg)

        self._progress_subphase.set_text(sub_msg)
        self._percent_display.set_text(
            "Time flies - {}% already!".format(percent))

    def hide_game_play_label(self):
        # this method needs to be called after show_all
        # TODO: better way of doing this
        self._pgl.hide()

    def _launch_game(self, window=None, event=None):
        try:
            if event and event.get_keyval()[1] in [Gdk.KEY_j, Gdk.KEY_J]:
                os.system('{} &'.format(FLAPPY_PATH))

        except:
            logger.error('Unexpected error in _launch_game()\n{}'
                         .format(traceback.format_exc))
