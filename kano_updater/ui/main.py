
# main.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Initialisation of the UI
#

import os
import signal

from gi.repository import GObject, Gtk

from kano.utils import run_cmd
from kano.logging import logger

from kano_updater.commands.check import check_for_updates
from kano_updater.commands.clean import clean
from kano_updater.progress import Relaunch
from kano_updater.status import UpdaterStatus
from kano_updater.utils import show_relaunch_splash


relaunch_required_flag = False
splash_pid = None


def relaunch_required():
    global relaunch_required_flag
    global splash_pid

    relaunch_required_flag = True
    splash_pid = show_relaunch_splash()


def launch_install_gui(confirm=True, splash_pid=None):
    from kano_updater.ui.available_window import UpdatesDownloadedWindow
    from kano_updater.ui.install_window import InstallWindow

    GObject.threads_init()

    win = UpdatesDownloadedWindow() if confirm else InstallWindow()
    win.show()

    if splash_pid:
        msg = "Terminating the splash screen (pid={})".format(splash_pid)
        logger.debug(msg)
        os.kill(splash_pid, signal.SIGKILL)

    Gtk.main()

    if relaunch_required_flag:
        r_exc = Relaunch()
        r_exc.pid = splash_pid
        raise r_exc


def launch_check_gui(min_time_between_checks=0):
    if check_for_updates(min_time_between_checks=min_time_between_checks):
        from kano_updater.ui.available_window import UpdatesAvailableWindow

        win = UpdatesAvailableWindow()
        win.show()
        Gtk.main()


def launch_boot_gui():
    old_status = clean()
    if old_status == UpdaterStatus.UPDATES_INSTALLED:
        # TODO: Implement the updater dialog properly
        title = 'Kano OS was updated'
        text = 'The update completed successfully. Enjoy the new version!'
        run_cmd("kano-dialog title=\"{}\" description=\"{}\"".format(title,
                                                                     text))


def launch_relaunch_countdown_gui(parent_pid):
    from kano_updater.ui.relaunch_window import RelaunchWindow

    GObject.threads_init()

    win = RelaunchWindow(parent_pid)
    win.show()
    Gtk.main()
