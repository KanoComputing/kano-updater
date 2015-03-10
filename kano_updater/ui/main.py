
# main.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Initialisation of the UI
#

from gi.repository import GObject, GLib, Gdk, Gtk

from kano_updater.ui.install_window import InstallWindow

def launch_gui():
    # GObject.threads_init()
    GLib.threads_init()
    Gdk.threads_init()
    Gdk.threads_enter()

    win = InstallWindow()
    win.show()
    Gtk.main()

    Gdk.threads_leave()
