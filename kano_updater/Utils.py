#!/usr/bin/env python

# kano-extras Python library
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Utilities for the updater and the pre and post update scripts

from kano.utils import run_cmd

def install(pkgs):
    cmd = 'apt-get install -o Dpkg::Options::="--force-confdef" ' +
          '-o Dpkg::Options::="--force-confold" -y --force-yes ' +
          ' '.join(pkgs)
    run_cmd(cmd)


def remove(pkgs):
    pass #TODO


def purge(pkgs):
    pass #TODO
