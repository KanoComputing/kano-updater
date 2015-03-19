# system.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# System Utilities
#

import os
import sys
import pwd
import grp
import shutil

from kano.utils import get_user_unsudoed, run_cmd, chown_path, \
    run_print_output_error
from kano.logging import logger

PID_FILE = '/var/run/kano-updater.pid'

def is_running():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as pid_file:
            old_pid = pid_file.read()

        if os.path.exists(os.path.join('/proc', old_pid)):
            return True

    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(os.getpid()))

    return False


def remove_pid_file():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def kill_apps():
    # since kano-updater is run as root, need to inform
    # kanolauncher about user
    user = get_user_unsudoed()
    home = os.path.join('/home/', user)
    variables = 'HOME={} USER={}'.format(home, user)
    run_cmd('{} /usr/bin/kano-launcher /bin/true kano-kill-apps'.format(
        variables))


# TODO: Might be useful in kano.utils
def supress_output(function, *args, **kwargs):
    with open(os.devnull, 'w') as f:
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        sys.stderr = sys.stdout = f

        try:
            function(*args, **kwargs)
        finally:
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr


def make_low_prio():
    # set IO class of this process to Idle
    pid = os.getpid()
    run_cmd("ioprio -c 3 -p {}".format(pid))

    # Set the lowest scheduling priority
    run_cmd("schedtool -D {}".format(pid))
    os.nice(19)

# --------------------------------------

def expand_rootfs():
    cmd = '/usr/bin/expand-rootfs'
    _, _, rc = run_print_output_error(cmd)
    return rc == 0


def check_for_multiple_instances():
    cmd = 'pgrep -f "python /usr/bin/kano-updater" -l | grep -v pgrep'
    o, _, _ = run_cmd(cmd)
    num = len(o.splitlines())
    logger.debug('Total number of kano-updater processes: {}'.format(num))
    if num > 1:
        logger.error('Exiting kano-updater as there is an other instance already running!')
        logger.debug(o)
        sys.exit()


def update_home_folders_from_skel():
    home = '/home'
    home_folders = os.listdir(home)

    for folder in home_folders:
        full_path = os.path.join(home, folder)
        if os.path.isdir(full_path):
            user_name = folder
            try:
                pwd.getpwnam(user_name)
                grp.getgrnam(user_name)
                update_folder_from_skel(user_name)
            except:
                msg = 'Home folder: {} doesn\'t match user: {}!'.format(
                    full_path,
                    user_name
                )
                logger.error(msg)


def update_folder_from_skel(user_name):
    logger.info('Updating home folder of user: {}'.format(user_name))
    src_dir = '/etc/skel'
    dst_dir = os.path.join('/home', user_name)

    dirlinks = []
    filelinks = []
    files = []

    for root, dirs, filenames in os.walk(src_dir):
        for d in dirs:
            path_full = os.path.join(root, d)
            if os.path.islink(path_full):
                dirlinks.append(path_full)

        for f in filenames:
            path_full = os.path.join(root, f)
            if os.path.islink(path_full):
                filelinks.append(path_full)
            else:
                files.append(path_full)

    for path_full in dirlinks + filelinks + files:
        path_rel = os.path.relpath(path_full, src_dir)
        dir_path_rel = os.path.dirname(path_rel)

        dst_path = os.path.join(dst_dir, path_rel)
        dir_dst_path = os.path.join(dst_dir, dir_path_rel)

        # print 'path_full', path_full
        # print 'path_rel', path_rel
        # print 'dir_path_rel', dir_path_rel
        # print 'dst_path', dst_path
        # print 'dir_dst_path', dir_dst_path
        # print

        if os.path.exists(dst_path):
            if os.path.islink(dst_path):
                logger.info('removing link: {}'.format(dst_path))
                os.unlink(dst_path)

            elif os.path.isdir(dst_path):
                logger.info('removing dir: {}'.format(dst_path))
                shutil.rmtree(dst_path)

            elif os.path.isfile(dst_path):
                logger.info('removing file: {}'.format(dst_path))
                os.remove(dst_path)

        # make sure that destination directory exists
        if os.path.exists(dir_dst_path):
            if not os.path.isdir(dir_dst_path):
                os.remove(dir_dst_path)
        else:
            logger.info('making needed dir: {}'.format(dir_dst_path))
            os.makedirs(dir_dst_path)
            chown_path(dir_dst_path, user=user_name, group=user_name)

        # creating links
        if os.path.islink(path_full):
            linkto = os.readlink(path_full)
            msg = 'creating link {} -> {}'.format(dst_path, linkto)
            logger.info(msg)
            os.symlink(linkto, dst_path)
            chown_path(dst_path, user=user_name, group=user_name)

        elif os.path.isfile(path_full):
            msg = 'copying file {} -> {}'.format(path_full, dst_path)
            logger.info(msg)
            shutil.copy(path_full, dst_path)
            chown_path(dst_path, user=user_name, group=user_name)


def reboot(title, description):
    from kano.gtk3 import kano_dialog
    kdialog = kano_dialog.KanoDialog(title, description)
    kdialog.run()
    run_cmd('reboot')


def remove_user_files(files):
    logger.info('utils / remove_user_files files:{}'.format(files))
    for d in os.listdir("/home/"):
        if os.path.isdir("/home/{}/".format(d)):
            for f in files:
                file_path = "/home/{}/{}".format(d, f)
                if os.path.exists(file_path):
                    logger.info('trying to delete file: {}'.format(file_path))
                    try:
                        os.remove(file_path)
                    except:
                        logger.info('could not delete file: {}'.format(file_path))


def rclocal_executable():
    try:
        # Restablish execution bit: -rwxr-xr-x
        os.chmod('/etc/rc.local', 0755)
        return True
    except Exception:
        return False
