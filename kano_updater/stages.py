#!/usr/bin/env python

#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

# deps:
# kano.utils: ,
# kano_updater.utils: fix_broken

import os

from kano.utils import zenity_show_progress, run_print_output_error, \
    kill_child_processes, run_cmd, read_file_contents_as_lines, delete_file, \
    delete_dir
from kano_updater.utils import fix_broken

def upgrade_debian():
    error_log = ""
    # setting up apt-get for non-interactive mode
    os.environ['DEBIAN_FRONTEND'] = 'noninteractive'

    # Try to fix any broken packages prior to the upgrade
    error_log += fix_broken("Preparing packages to be upgraded")

    # apt upgrade
    id = zenity_show_progress("Upgrading packages")
    cmd = 'yes "" | apt-get -y -o Dpkg::Options::="--force-confdef" ' + \
          '-o Dpkg::Options::="--force-confold" dist-upgrade'
    _, debian_err, _ = run_print_output_error(cmd)
    error_log += debian_err
    kill_child_processes(id)

    # apt autoremove
    id = zenity_show_progress("Cleaning up packages")
    cmd = 'apt-get -y autoremove --purge'
    run_print_output_error(cmd)

    # apt autoclean
    cmd = 'apt-get -y autoclean'
    run_print_output_error(cmd)
    kill_child_processes(id)

    # Try to fix any broken packages after the upgrade
    error_log += fix_broken("Finalising package upgrade")

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
        return err_packages, error_log

    return None, error_log

def upgrade_python(python_modules_file, appstate_before):
    id = zenity_show_progress("Upgrading Python modules")

    if 'python-pip' in appstate_before or \
       'python-setuptools' in appstate_before:
        # remove old pip and setuptools
        cmd = 'yes "" | apt-get -y purge python-setuptools ' + \
              'python-virtualenv python-pip'
        run_print_output_error(cmd)

    # installing/upgrading pip
    o, _, _ = run_cmd('pip -V')
    if 'pip 1.' in o:
        cmd = 'pip install --upgrade pip'
        run_print_output_error(cmd)
    else:
        cmd = 'wget -q --no-check-certificate ' + \
              'https://raw.github.com/pypa/pip/master/contrib/get-pip.py ' + \
              '-O get-pip.py'
        run_cmd(cmd)

        cmd = 'python get-pip.py'
        run_print_output_error(cmd)

        delete_file('get-pip.py')

    # parse python modules
    python_modules = read_file_contents_as_lines(python_modules_file)

    ok_modules = []
    error_modules = []

    for module in python_modules:
        o, e, rc = run_cmd('pip install --upgrade {}'.format(module))

        if rc == 0:
            if 'Successfully installed' in o:
                ok_modules.append(module)
        else:
            error_modules.append(module)
    kill_child_processes(id)

    return ok_modules, error_modules
