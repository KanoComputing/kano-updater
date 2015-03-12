
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
    from kano_updater.ui.available_window import UpdatesDownloadedWindow

    GLib.threads_init()
    Gdk.threads_init()
    Gdk.threads_enter()

    win = UpdatesDownloadedWindow()
    win.show()
    Gtk.main()

    Gdk.threads_leave()

def launch_check_gui(min_time_between_checks=0):
    if check_for_updates(min_time_between_checks=min_time_between_checks):
        from kano_updater.ui.available_window import UpdatesAvailableWindow

        win = UpdatesAvailableWindow()
        win.show()
        Gtk.main()
