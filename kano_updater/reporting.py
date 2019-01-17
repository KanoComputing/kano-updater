#
# reporting.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module providing crash reporting functionality
#


import os

from kano.logging import logger


def send_crash_report(title, desc):
    '''
    Attempt to send a crash report. At this point the system may be seriously
    broken so wrap it all in a try for safety.
    '''

    logger.info('Sending crash report: {}: {}'.format(title, desc))
    logger.flush()

    try:
        os.system(
            'kano-feedback-cli --title "{title}" --description "{desc}" --send'
            .format(title=title, desc=desc)
        )
    except Exception:
        pass
