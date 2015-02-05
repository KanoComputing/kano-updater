#!/usr/bin/env python

# stage.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# The stage indicators
#

from gi.repository import Gtk

from kano_updater_gui.paths import IMAGE_PATH
from kano_updater_gui.text_en import STATUS_TITLES

def stage(number):
    box = Gtk.EventBox(
        width_request = 150,
        height_request = 110,
        expand = False
    )
    box.get_style_context().add_class("waiting")

    grid = Gtk.Grid(
        orientation = Gtk.Orientation.VERTICAL,
        expand = True
    )

    label = Gtk.Label(
        STATUS_TITLES[number].upper(),
        justify = Gtk.Justification.CENTER,
        halign = Gtk.Align.FILL,
        valign = Gtk.Align.CENTER,
        vexpand = True,
        height_request = 50
    )
    label.get_style_context().add_class("waiting")
    grid.add(label)

    overlay = Gtk.Overlay()

    progressbox = Gtk.EventBox(
        width_request = 150,
        height_request = 60
    )
    progress = Gtk.EventBox(
        width_request = [
             75,
            150,
            150,
            150,
             75
        ][number],
        height_request = 6,
        halign = [
            Gtk.Align.END,
            Gtk.Align.CENTER,
            Gtk.Align.CENTER,
            Gtk.Align.CENTER,
            Gtk.Align.START
        ][number],
        valign = Gtk.Align.CENTER
    )
    progress.get_style_context().add_class("progress")
    progressbox.add(progress)

    overlay.add(progressbox)

    checkmark = Gtk.Image(
        halign = Gtk.Align.FILL,
        valign = Gtk.Align.FILL
    )
    checkmark.set_from_file("{}/waiting.png".format(IMAGE_PATH))
    overlay.add_overlay(checkmark)

    spinner = Gtk.Spinner(
        halign = Gtk.Align.CENTER,
        valign = Gtk.Align.CENTER
    )
    spinner.hide()
    overlay.add_overlay(spinner)

    grid.add(overlay)
    box.add(grid)

    return (box, label, checkmark, spinner)
