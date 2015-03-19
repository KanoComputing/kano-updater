#!/usr/bin/env python

# stages.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# deps:
# kano.utils: ,
# kano_updater.utils: fix_broken

import os

from kano.utils import run_cmd, read_file_contents_as_lines, \
    delete_file, delete_dir, run_cmd_log, run_print_output_error

python_modules_file = '/usr/share/kano-updater/python_modules'


# Send the gui process as an argument so we can check if it's still running
# and relaunch if necessary

def upgrade_debian(gui_process):
    from kano_updater.utils.apt import fix_broken
    from kano_updater.utils.ui import launch_gui_if_not_running, set_gui_stage

    # setting up apt-get for non-interactive mode
    os.environ['DEBIAN_FRONTEND'] = 'noninteractive'

    # Try to fix any broken packages prior to the upgrade
    fix_broken("Preparing packages to be upgraded")

    # apt upgrade
    gui_process = launch_gui_if_not_running(gui_process)
    set_gui_stage(4)

    # try to download all files first, retry in a loop
    for i in xrange(5):
        _, _, rc = run_cmd_log('apt-get -y -d dist-upgrade')
        if rc == 0:
            break
        elif i == 4:
            return -1

    set_gui_stage(5)

    # do the actual update using the downloaded files
    cmd = 'yes "" | apt-get -y -o Dpkg::Options::="--force-confdef" ' + \
          '-o Dpkg::Options::="--force-confold" dist-upgrade'
    _, debian_err, _ = run_cmd_log(cmd)

    # apt autoremove
    gui_process = launch_gui_if_not_running(gui_process)
    set_gui_stage(6)

    cmd = 'apt-get -y autoremove --purge'
    run_cmd_log(cmd)

    # apt autoclean
    cmd = 'apt-get -y autoclean'
    run_cmd_log(cmd)

    # Try to fix any broken packages after the upgrade
    fix_broken("Finalising package upgrade")

    # parsing debian error log
    if debian_err:
        err_split = debian_err.splitlines()
        dirs_delete = []
        err_packages = []

        for l in err_split:
            if 'dpkg: warning: unable to delete old directory' in l:
                parts = l.split("'")
                dirs_delete.append(parts[1].strip())

            if 'dpkg: error processing' in l:
                parts = l.split('/var/cache/apt/archives/')
                packagename = parts[1].split()[0].strip()[:-4]
                err_packages.append(packagename)

        # remove left-over non-empty directories
        for dir in dirs_delete:
            delete_dir(dir)

        # return err_packages
        return err_packages

    return None


def upgrade_python(appstate_before, visible=False):

    def visible_run(cmd):
        if visible:
            return run_print_output_error(cmd)
        else:
            return run_cmd_log(cmd)

    if not os.path.exists(python_modules_file):
        if visible:
            print 'python module file doesn\'t exists'
        return [], []

    if 'python-pip' in appstate_before or \
       'python-setuptools' in appstate_before:
        # remove old pip and setuptools
        cmd = 'yes "" | apt-get -y purge python-setuptools ' + \
              'python-virtualenv python-pip'
        visible_run(cmd)

    # installing/upgrading pip
    o, _, _ = run_cmd('pip -V')
    if 'pip 1.' in o:
        cmd = 'pip install --upgrade pip'
        visible_run(cmd)
    else:
        cmd = 'wget -q --no-check-certificate ' + \
              'https://raw.github.com/pypa/pip/master/contrib/get-pip.py ' + \
              '-O get-pip.py'
        visible_run(cmd)

        cmd = 'python get-pip.py'
        visible_run(cmd)

        delete_file('get-pip.py')

    # parse python modules
    python_modules = read_file_contents_as_lines(python_modules_file)

    ok_modules = []
    error_modules = []

    for module in python_modules:
        o, e, rc = visible_run('pip install --upgrade {}'.format(module))

        if rc == 0:
            if 'Successfully installed' in o:
                ok_modules.append(module)
        else:
            error_modules.append(module)

    return ok_modules, error_modules
