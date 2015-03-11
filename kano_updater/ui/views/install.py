
# install.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Install widget
#

from gi.repository import Gtk
from kano_updater.ui.stage_text import STAGE_TEXT

class Install(Gtk.Alignment):

    def __init__(self):
        Gtk.Alignment.__init__(self, xalign=0.5, yalign=1.0, xscale=0, yscale=0)

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        self.add(grid)

        style = self.get_style_context().add_class('install')

        self._progress_phase = Gtk.Label()
        self._progress_phase.get_style_context().add_class('heading')

        self._progress_subphase = Gtk.Label()
        style = self._progress_subphase.get_style_context()
        style.add_class('heading')
        style.add_class('subheading')

        self._progress_bar = Gtk.ProgressBar(hexpand=False)
        self._progress_bar.set_size_request(375, -1)
        self._progress_bar.set_show_text(False)
        bar_align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        bar_align.add(self._progress_bar)

        self._percent_display = Gtk.Label()
        style = self._percent_display.get_style_context()
        style.add_class('heading')
        style.add_class('subheading')
        style.add_class('small-print')

        self._psa = Gtk.Label()
        self._psa.set_size_request(525, 300)
        self._psa.set_max_width_chars(50)
        self._psa.set_line_wrap(True)
        self._psa.set_justify(Gtk.Justification.CENTER)
        style = self._psa.get_style_context()
        style.add_class('heading')
        style.add_class('subheading')
        style.add_class('psa')
        psa_align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        psa_align.add(self._psa)

        grid.attach(self._progress_phase, 0, 0, 1, 1)
        grid.attach(self._progress_subphase, 0, 1, 1, 1)
        grid.attach(bar_align, 0, 2, 1, 1)
        grid.attach(self._percent_display, 0, 3, 1, 1)
        grid.attach(psa_align, 0, 4, 1, 1)

    def update_progress(self, percent, msg, sub_msg=''):
        self._progress_bar.set_fraction(percent / 100.)

        if self._progress_phase.get_text() != msg:
            self._psa.set_markup(STAGE_TEXT.get_next())
            self._progress_phase.set_text(msg)

        self._progress_subphase.set_text(sub_msg)
        self._percent_display.set_text(
            "Time flies - {}% already!".format(percent))
