#
# __init__.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fake implementation of the `apt` module to mock system calls to apt from
# Python
#

__author__ = 'Kano Computing Ltd.'
__email__ = 'dev@kano.me'

import apt.apt_pkg
import apt.cache
import apt.package
import apt.progress.base
