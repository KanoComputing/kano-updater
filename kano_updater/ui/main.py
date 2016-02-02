
# main.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Initialisation of the UI
#

import os
import signal

from kano.utils import run_cmd
from kano.logging import logger

from kano_updater.commands.check import check_for_updates
from kano_updater.commands.clean import clean
from kano_updater.progress import Relaunch
from kano_updater.status import UpdaterStatus
from kano_updater.utils import show_relaunch_splash, remove_pid_file

relaunch_required_flag = False
launched_splash_pid = None


def relaunch_required():
    global relaunch_required_flag
    global launched_splash_pid

    relaunch_required_flag = True
    launched_splash_pid = show_relaunch_splash()


def launch_install_gui(confirm=False, splash_pid=None):
    from gi.repository import GObject, Gtk

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
        r_exc.pid = launched_splash_pid
        raise r_exc


def launch_check_gui():
    from gi.repository import Gtk

    rv = check_for_updates()
    if rv:
        from kano_updater.ui.available_window import UpdatesAvailableWindow

        win = UpdatesAvailableWindow()
        win.show()
        Gtk.main()

    return rv


def launch_boot_gui():
    # FIXME: This window uses Gtk2 which requires the other Gtk imports to be
    #        loaded in the scope of the functions that require them.
    old_status = clean(dry_run=True)
    status = UpdaterStatus.get_instance()

    if old_status == UpdaterStatus.INSTALLING_UPDATES:
        from kano.gtk3.kano_dialog import KanoDialog
        d = KanoDialog(
            'Continue updating',
            'The update you started didn\'t finish. Would you like to '
            'continue?',
            [{"label": "YES", "return_value": True, "color": "green"}],
            orange_info={'name': 'SKIP', 'return_value': False},
        )
        rv = d.run()
        del d

        if rv:
            status.notifications_muted = True
            status.state = UpdaterStatus.UPDATES_AVAILABLE
            status.save()

            remove_pid_file()

            cmd_args = ['kano-updater', 'install', '--gui', '--no-confirm']
            os.execvp('kano-updater', cmd_args)

    elif old_status == UpdaterStatus.UPDATES_INSTALLED:
        try:
            from kano_profile.badges import \
                increment_app_state_variable_with_dialog
            increment_app_state_variable_with_dialog(
                'kano-updater', 'updated', 1)
        except Exception:
            pass

        from kano_updater.ui.changes_dialog import ChangesDialog
        win = ChangesDialog()
        win.run()

    status.save()


def launch_shutdown_gui():
    from gi.repository import GObject, Gtk

    from kano_updater.ui.available_window import UpdateNowShutdownWindow
    from kano_updater.ui.install_window import InstallWindow

    status = UpdaterStatus.get_instance()

    if status.is_scheduled:
        GObject.threads_init()
        win = InstallWindow() if status.is_urgent else UpdateNowShutdownWindow()
        win.show()
        Gtk.main()


def launch_relaunch_countdown_gui(parent_pid):
    from gi.repository import GObject, Gtk
    from kano_updater.ui.relaunch_window import RelaunchWindow

    GObject.threads_init()

    win = RelaunchWindow(parent_pid)
    win.show()
    Gtk.main()
