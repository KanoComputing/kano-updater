#!/usr/bin/env python

# utils.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Utilities for the updater and the pre and post update scripts
#

import os
import sys
import errno
from kano.logging import logger
from kano.utils import run_print_output_error, run_cmd, run_print_output_error,\
    zenity_show_progress, kill_child_processes, run_cmd_log, is_gui

UPDATER_CACHE_DIR = "/var/cache/kano-updater/"
STATUS_FILE = UPDATER_CACHE_DIR + "status"

def install(pkgs, die_on_err=True):
    if isinstance(pkgs, list):
        pkgs = ' '.join(pkgs)

    cmd = 'apt-get install -o Dpkg::Options::="--force-confdef" ' + \
          '-o Dpkg::Options::="--force-confold" -y --force-yes ' + str(pkgs)
    _, _, rv = run_cmd_log(cmd)

    if die_on_err and rv != 0:
        update_failed("Unable to install '{}'".format(pkgs))

    return rv

def remove(pkgs):
    pass  # TODO

def purge(pkgs, die_on_err=False):
    if isinstance(pkgs, list):
        pkgs = ' '.join(pkgs)

    _, _, rv = run_cmd_log('apt-get -y purge ' + str(pkgs))

    if die_on_err and rv != 0:
        update_failed("Unable to purge '{}'".format(pkgs))

    return rv

def update_failed(err):
    logger.error("Update failed: {}".format(err))

    msg = "The update couldn't be finished at the moment. " + \
          "Please try again later.\n\n" + \
          "If this problem persists, please consider reporting this issue " + \
          "via the\nFeedback tool. We'll be happy to help!"

    if is_gui():
        from kano.gtk3 import kano_dialog
        kdialog = kano_dialog.KanoDialog("Update error", msg)
        kdialog.run()
    else:
        print "Update error: {}".format(msg)
        answer = raw_input()

    sys.exit(1)

def get_dpkg_dict():
    apps_ok = dict()
    apps_other = dict()

    cmd = 'dpkg -l'
    o, _, _ = run_cmd(cmd)
    lines = o.splitlines()
    for l in lines[5:]:
        parts = l.split()
        state = parts[0]
        name = parts[1]
        version = parts[2]

        if state == 'ii':
            apps_ok[name] = version
        else:
            apps_other[name] = version

    return apps_ok, apps_other

def fix_broken(msg):
    cmd = 'yes "" | apt-get -y -o Dpkg::Options::="--force-confdef" ' + \
          '-o Dpkg::Options::="--force-confold" install -f'
    run_cmd_log(cmd)

def expand_rootfs():
    cmd = '/usr/bin/expand-rootfs'
    _, _, rc = run_print_output_error(cmd)
    return rc == 0

def get_installed_version(pkg):
    out, _, _ = run_cmd('dpkg-query -s kano-updater | grep "Version:"')
    return out.strip()[9:]

def get_update_status():
    status = {"last_update": 0, "update_available": 0, "last_check": 0}
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as sf:
            for line in sf:
                name, value = line.strip().split("=")
                status[name] = int(value)

    return status

def set_update_status(status):
    try:
        os.mkdir(UPDATER_CACHE_DIR)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(UPDATER_CACHE_DIR):
            pass
        else:
            raise

    with open(STATUS_FILE, "w") as sf:
        for name, value in status.iteritems():
            sf.write("{}={}\n".format(name, value))

def reboot_required(watched, changed):
    for pkg in changed:
        if pkg in watched:
            return True

    return False

def reboot(title, description):
    if is_gui():
        from kano.gtk3 import kano_dialog
        kdialog = kano_dialog.KanoDialog(title, description)
        kdialog.run()
    else:
        print title
        print 'Press any key to continue'
        answer = raw_input()
    run_cmd('reboot')

def remove_user_files(files):
    for d in os.listdir("/home/"):
        if os.path.isdir("/home/{}/".format(d)):
            for f in files:
                file_path = "/home/{}/{}".format(d, f)
                try:
                    os.unlink(file_path)
                except:
                    pass
