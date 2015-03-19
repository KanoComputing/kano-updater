# ui.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# UI Utilities
#

import subprocess
import os
import sys

from kano.utils import is_gui
from kano.logging import logger


def root_check():
    from kano.gtk3 import kano_dialog

    user = os.environ['LOGNAME']
    if user != 'root':
        description = 'kano-updater must be executed with root privileges'
        logger.error(description)

        if is_gui():
            kdialog = kano_dialog.KanoDialog(
                _('Error!'),
                _('kano-updater must be executed with root privileges')
            )
            kdialog.run()
        sys.exit(description)


def update_failed(err):
    from kano.gtk3 import kano_dialog

    logger.error("Update failed: {}".format(err))

    msg = _("We had a problem with the Update. "
          "Make sure you are connected to the Internet, and give it another go.\n\n"
          "If you still have problems, we can help at http://help.kano.me")

    kdialog = kano_dialog.KanoDialog(_("Update error"), msg)
    kdialog.run()


def launch_gui():
    process = subprocess.Popen("kano-updater-gui")
    return process


def launch_gui_if_not_running(process):
    if process.poll() is not None:
        return launch_gui()
    return process


def set_gui_stage(number):
    tmp_filename = "/tmp/updater-progress"
    f = open(tmp_filename, "w+")
    f.write(str(number))
    f.close()


def kill_gui(process):
    if process.poll() is None:
        process.kill()
