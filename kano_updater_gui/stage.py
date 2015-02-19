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
from kano_updater_gui.text import STATUS_TITLES, NUMBER_OF_STAGES

STAGE_WIDTH = 150
STAGE_HEIGHT = 110

LABEL_HEIGHT = 50
PROGRESS_HEIGHT = STAGE_HEIGHT - LABEL_HEIGHT

BOX_ARRANGEMENTS = {
    'left': {
        'width': STAGE_WIDTH / 2,
        'align': Gtk.Align.END,
    },
    'centre': {
        'width': STAGE_WIDTH,
        'align': Gtk.Align.CENTER,
    },
    'right': {
        'width': STAGE_WIDTH / 2,
        'align': Gtk.Align.START,
    }
}

def stage(number):
    # Left, right or centre box arrangement?
    if number == 0:
        arrangement = BOX_ARRANGEMENTS['left']
    elif number + 1 == NUMBER_OF_STAGES:
        arrangement = BOX_ARRANGEMENTS['right']
    else:
        arrangement = BOX_ARRANGEMENTS['centre']

    box = Gtk.EventBox(
        width_request = STAGE_WIDTH,
        height_request = STAGE_HEIGHT,
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
        height_request = LABEL_HEIGHT
    )
    label.get_style_context().add_class("waiting")
    grid.add(label)

    overlay = Gtk.Overlay()

    progressbox = Gtk.EventBox(
        width_request = STAGE_WIDTH,
        height_request = PROGRESS_HEIGHT
    )
    progress = Gtk.EventBox(
        width_request = arrangement['width'],
        height_request = 6,
        halign = arrangement['align'],
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
