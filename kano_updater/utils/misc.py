# misc.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Miscellaneous Utilities
#

import subprocess
import os
import signal

# WARNING do not import GUI modules here (like KanoDialog)

def _handle_sigusr1(signum, frame):
    pass

def show_relaunch_splash():
    cmd = ["kano-updater", "ui", "relaunch-splash", str(os.getpid())]
    p = subprocess.Popen(cmd, shell=False)

    # register a handler for SIGUSR1
    signal.signal(signal.SIGUSR1, _handle_sigusr1)

    # wait until the child process signals that it's ready
    signal.pause()

    return p.pid

# --------------------------------------


def add_text_to_end(text_buffer, text, tag=None):
    end = text_buffer.get_end_iter()
    if tag is None:
        text_buffer.insert(end, text)
    else:
        text_buffer.insert_with_tags(end, text, tag)
