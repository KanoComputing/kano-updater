#
# pip.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures to simulate the Python pip state on the system
#


import pytest


@pytest.fixture(scope='function')
def pip(monkeypatch):
    '''
    Mock away commands directed at Python pip
    '''

    import kano_updater.utils
    monkeypatch.setattr(kano_updater.utils, 'run_pip_command', lambda x: True)


@pytest.fixture(scope='function')
def pip_modules(fs):
    '''
    Fake the list of Python modules managed by Python pip provided by the
    updater at
        /usr/share/kano-updater/python_modules
    '''

    fs.CreateFile(
        '/usr/share/kano-updater/python_modules',
        contents='pip'
    )
