# pip.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Pip Utilities
#

from kano.utils import run_cmd_log
from kano.logging import logger

from kano_updater.paths import PIP_LOG_FILE


def run_pip_command(pip_args):
    # TODO Incorporate suppress_output when this is working

    _, _, rv = run_cmd_log("pip {} --log {}".format(pip_args, PIP_LOG_FILE))
    return rv == 0


def install_ping():
    try:
        import ping
    except ImportError:
        logger.info('ping not found on the system, installing')
        run_pip_command('install ping')


def install_docopt():
    try:
        import docopt
    except ImportError:
        logger.info("docopt not found on the system, installing")
        run_pip_command('install docopt')
