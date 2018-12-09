#
# reporting.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Module providing crash reporting functionality
#


import os


def send_crash_report(title, desc):
    '''
    Attempt to send a crash report. At this point the system may be seriously
    broken so wrap it all in a try for safety.
    '''

    try:
        os.system(
            'kano-feedback-cli --title "{title}" --description "{desc}" --send'
            .format(title=title, desc=desc)
        )
    except Exception:
        pass
