#
# debian.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for generating an installed Debian environment
#


import os
import pytest

OS_SRCS_PKG_TEMPLATE = 'debian/kano-os-sources.{suffix}'
OS_SRCS_PKG_INSTALL = OS_SRCS_PKG_TEMPLATE.format(suffix='install')
OS_SRCS_PKG_LINKS = OS_SRCS_PKG_TEMPLATE.format(suffix='links')

REAL_OPEN = open
REAL_OS = os

@pytest.fixture
def apt_sources_install(fs):
    # Copy kano-os-sources.install to the fake fs
    with REAL_OPEN(OS_SRCS_PKG_INSTALL, 'r') as src_install_f:
        installs = src_install_f.readlines()

    for install in installs:
        src, dst = install.strip().rstrip().split(' ')
        dst = os.path.join(os.path.sep, dst)

        # For destinations marked clearly as directories, the source should be
        # copies into it
        if dst.endswith(os.path.sep):
            dst = os.path.join(dst, os.path.basename(src))

        if REAL_OS.path.isfile(src):
            print 'Exposing file {} to {}'.format(src, dst)
            fs.add_real_file(src, target_path=dst)
        elif REAL_OS.path.isdir(src):
            print 'Exposing directory {} to {}'.format(src, dst)
            fs.add_real_directory(src, target_path=dst)
        else:
            print '{} is neither a file nor a directory'.format(src)

    # Create the kano-os-sources.links in the fake fs
    with REAL_OPEN(OS_SRCS_PKG_LINKS, 'r') as src_links_f:
        links = src_links_f.readlines()

    for link in links:
        src, dst = link.strip().rstrip().split(' ')
        src = os.path.join(os.path.sep, src)
        dst = os.path.join(os.path.sep, dst)

        print 'Creating link {} -> {}'.format(src, dst)
        fs.create_symlink(dst, src)

    return fs
