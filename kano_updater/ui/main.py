
# main.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Initialisation of the UI
#

from gi.repository import GLib, Gdk, Gtk

from kano_updater.commands.check import check_for_updates

def launch_install_gui():
    from kano_updater.ui.install_window import InstallWindow

    GLib.threads_init()
    Gdk.threads_init()
    Gdk.threads_enter()

    win = InstallWindow()
    win.show()
    Gtk.main()

    Gdk.threads_leave()

def launch_check_gui():
    if check_for_updates():
        from kano_updater.ui.check_window import CheckWindow

        win = CheckWindow()
        win.show()
        Gtk.main()
