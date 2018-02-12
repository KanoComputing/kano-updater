#
# progress.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Updater progress objects tailored to run through Pytest
#


from kano_updater.progress import CLIProgress


class AbortError(Exception):
    '''
    An exception indicating that the update is aborting. Can be caught to
    determine that the updater correctly (or incorrectly) failed.
    '''

    pass


class PyTestProgress(CLIProgress):
    '''
    Updater progress object tailored to run through Pytest. Can be passed in
    place of any updater *Progress object.
    '''

    def _abort(self, phase, msg):
        raise AbortError(msg)

    def _prompt(self, msg, question, answers):
        return answers[-1]
