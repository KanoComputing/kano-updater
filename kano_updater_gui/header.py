#!/usr/bin/env python

# header.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Header widget
#

from gi.repository import Gtk

from kano_updater_gui.paths import IMAGE_PATH
from kano_updater_gui.text_en import STATUS_TITLES, STAGE_TITLES, STAGE_BODIES


class Header(Gtk.EventBox):

    def __init__(self, number):
        Gtk.EventBox.__init__(
            self,
            width_request = len(STATUS_TITLES) * 150,
            height_request = 340
        )
        self.get_style_context().add_class("header{:d}".format(number + 1))

        grid = Gtk.Grid(
            orientation = Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER
        )

        headline = Gtk.Label(
            STAGE_TITLES[number].upper(),
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.START,
            margin_top = 25,
            margin_left = 50,
            margin_right = 50
        )
        headline.get_style_context().add_class("headline")
        grid.add(headline)

        poster_grid = Gtk.Grid(
            orientation = Gtk.Orientation.VERTICAL,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.CENTER,
            vexpand = True,
            margin_top = 10,
            margin_bottom = 10,
            margin_left = 50,
            margin_right = 50
        )

        poster_label = Gtk.Label(
            justify = Gtk.Justification.CENTER,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.END,
            margin_bottom = 5
        )
        poster_label.set_markup(STAGE_BODIES[number])
        poster_label.set_line_wrap(True)
        poster_label.get_style_context().add_class("poster")
        poster_grid.add(poster_label)

        grid.add(poster_grid)

        if number == 4:
            soc_media_grid = Gtk.Grid(
                orientation = Gtk.Orientation.HORIZONTAL,
                halign = Gtk.Align.CENTER,
                valign = Gtk.Align.END,
                column_spacing = 10,
                margin_top = 5
            )

            facebook_icon = Gtk.Image()
            facebook_icon.set_from_file("{}/facebook.png".format(IMAGE_PATH))
            soc_media_grid.add(facebook_icon)

            facebook_label = Gtk.Label(
                "KanoComputing",
                margin_right = 20
            )
            facebook_label.get_style_context().add_class("social")
            soc_media_grid.add(facebook_label)

            twitter_icon = Gtk.Image()
            twitter_icon.set_from_file("{}/twitter.png".format(IMAGE_PATH))
            soc_media_grid.add(twitter_icon)

            twitter_label = Gtk.Label("@TeamKano")
            twitter_label.get_style_context().add_class("social")
            soc_media_grid.add(twitter_label)

            poster_grid.add(soc_media_grid)

        psa_grid = Gtk.Grid(
            orientation = Gtk.Orientation.HORIZONTAL,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.END,
            column_spacing = 10,
            margin_left = 50,
            margin_right = 50,
            margin_bottom = 25
        )

        if number < 5:
            psa_bang = Gtk.Image()
            psa_bang.set_from_file("{}/bang.png".format(IMAGE_PATH))
            psa_grid.add(psa_bang)

        psa_label = Gtk.Label(
            (u"Do not disconnect your Kano"
            if number < 5 else
            u"Please stand by").upper()
        )
        psa_label.get_style_context().add_class("psa")
        psa_grid.add(psa_label)

        grid.add(psa_grid)

        self.add(grid)

