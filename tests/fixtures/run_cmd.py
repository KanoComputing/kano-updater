#
# run_cmd.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fake implementation of the run_cmd() functions to mock away unwanted system
# calls
#


import pytest


@pytest.fixture(scope='function')
def run_cmd(monkeypatch):
    '''
    Mocks `kano.utils.shell.run_cmd()` and `kano.utils.shell.run_cmd_log()`
    away so that they do nothing.
    '''

    import kano.utils.shell

    monkeypatch.setattr(
        kano.utils.shell, 'run_cmd_log', lambda x: (True, '', '')
    )

    monkeypatch.setattr(
        kano.utils.shell, 'run_cmd', lambda x: (True, '', '')
    )
