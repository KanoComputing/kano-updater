# -*- coding: utf-8 -*-

# conf.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This file contains configuration specific to this project.
#
# See the master configuration at kano-doc/res/docs-config/default_conf.py


from os.path import abspath, dirname, join
import sys


REPO_DIR = abspath(join(abspath(dirname(__name__)), '..', '..'))
KANO_DOC_CONFIG_DIR = join('kano-doc', 'res', 'docs-config')


# -- kano-doc master configuration --------------------------------------------

# Local and Jenkins paths to the default_conf.
sys.path.insert(0, abspath(join(REPO_DIR, '..', KANO_DOC_CONFIG_DIR)))
sys.path.insert(0, abspath(join(REPO_DIR, KANO_DOC_CONFIG_DIR)))

from default_conf import *


# -- Project configuration ----------------------------------------------------

# Add include paths for autodoc to import the code locally.
sys.path.insert(0, REPO_DIR)


# -- Kano OS configuration ----------------------------------------------------

# Load the _() and N_() functions from kano-i18n since the package is mocked.
import __builtin__
__builtin__.__dict__['_'] = lambda x: x
__builtin__.__dict__['N_'] = lambda x: x


# -- General configuration ----------------------------------------------------

# General information about the project.
project = u'kano-updater'


# -- Options for autodoc ------------------------------------------------------

# This is a list of external dependencies in this project. All these modules
# will be imported and break the doc build. Mock all of them instead.
autodoc_mock_imports = [
    'pytest',
    'apt',
    'aptsources',
    'apt_pkg',
    'gi',
    'kano',
    'kano_init',
    'kano_i18n',
    'kano_peripherals'
]


# -- Options for HTMLHelp output ----------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'kano-updaterdoc'
