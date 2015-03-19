# apt.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Apt Utilities
#

import os
import errno

from kano.utils import sed, run_cmd_log, run_cmd
from kano.logging import logger

from kano_updater.apt_wrapper import apt_handle
from kano_updater.progress import DummyProgress
from kano_updater.utils.ui import update_failed


UPDATER_CACHE_DIR = "/var/cache/kano-updater/"
STATUS_FILE = UPDATER_CACHE_DIR + "status"


def migrate_repository(apt_file, old_repo, new_repo):
    try:
        sed(old_repo, new_repo, apt_file, use_regexp=False)
    except IOError as exc:
        logger.warn('Changing repository URL failed ({})'.format(exc))
        return

    # TODO: track progress of this
    apt_handle.clear_cache()
    apt_handle.update(DummyProgress())


# --------------------------------------


def install(pkgs, die_on_err=True):
    if isinstance(pkgs, list):
        pkgs = ' '.join(pkgs)

    cmd = 'apt-get install -o Dpkg::Options::="--force-confdef" ' + \
          '-o Dpkg::Options::="--force-confold" -y --force-yes ' + str(pkgs)
    _, _, rv = run_cmd_log(cmd)

    if die_on_err and rv != 0:
        msg = "Unable to install '{}'".format(pkgs)
        update_failed(msg)
        raise Exception(msg)

    return rv


def remove(pkgs):
    pass  # TODO


def purge(pkgs, die_on_err=False):
    if isinstance(pkgs, list):
        pkgs = ' '.join(pkgs)

    _, _, rv = run_cmd_log('apt-get -y purge ' + str(pkgs))

    if die_on_err and rv != 0:
        msg = "Unable to purge '{}'".format(pkgs)
        update_failed(msg)
        raise Exception(msg)

    return rv


def get_dpkg_dict(include_unpacked=False):
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

        if state == 'ii' or (include_unpacked and state == 'iU'):
            apps_ok[name] = version
        else:
            apps_other[name] = version

    return apps_ok, apps_other


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


def fix_broken(msg):
    # Try to fix incorrectly configured packages
    run_cmd_log("dpkg --configure -a")

    o, _, _ = run_cmd("dpkg -l | grep '^..R'")
    reinstall = []
    for line in o.splitlines():
        pkg_info = line.split()
        try:
            reinstall.append(pkg_info[1])
        except:
            pass

    if reinstall:
        logger.error("Reinstalling broken packages: {}".format(" ".join(reinstall)))
        cmd = 'yes "" | apt-get -y -o Dpkg::Options::="--force-confdef" ' + \
          '-o Dpkg::Options::="--force-confold" install --reinstall {}'.format(" ".join(reinstall))
        run_cmd_log(cmd)

    cmd = 'yes "" | apt-get -y -o Dpkg::Options::="--force-confdef" ' + \
          '-o Dpkg::Options::="--force-confold" install -f'
    run_cmd_log(cmd)


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
