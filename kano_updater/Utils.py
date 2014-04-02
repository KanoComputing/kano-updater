#!/usr/bin/env python

# kano-extras Python library
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Utilities for the updater and the pre and post update scripts

from kano.utils import run_print_output_error

def install(pkgs):
    if isinstance(pkgs, list):
        pkgs = ' '.join(pkgs)

    cmd = 'apt-get install -o Dpkg::Options::="--force-confdef" ' + \
          '-o Dpkg::Options::="--force-confold" -y --force-yes ' + str(pkgs)
    print cmd
    run_print_output_error(cmd)

def remove(pkgs):
    pass #TODO


def purge(pkgs):
    pass #TODO
