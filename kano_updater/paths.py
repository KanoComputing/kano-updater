# paths.py
#
# Copyright (C) 2015-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Paths used thoughout this project.

import os

SYSTEM_ISSUE_FILE = '/etc/issue'
SYSTEM_VERSION_FILE = '/etc/kanux_version'

STATUS_FILE_PATH = '/var/cache/kano-updater/status.json'

SOURCES_DIR = '/etc/apt/sources.list.d'
KANO_SOURCES_LIST = os.path.join(SOURCES_DIR, 'kano-repos.list')

PYLIBS_DIR = '/usr/local/lib/python2.7/dist-packages'
PYFALLBACK_DIR = '/usr/local/lib/python2.7/dist-packages.pip-fallback'
PIP_CONF = '/usr/share/kano-updater/kano-pip-compat.pth'

# FIXME: Find way to properly handle references to these files owned by the
#        'kano-os-sources' package
OS_SOURCES_REFERENCE = '/usr/share/kano-os-sources/apt/sources.list.d'
REFERENCE_STRETCH_LIST = os.path.join(
    OS_SOURCES_REFERENCE, 'kano-stretch.list'
)
