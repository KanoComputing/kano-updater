#
# crash_reporting.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixture to provide crash reports
#


import pytest


@pytest.fixture(scope='function')
def send_crash_report(mocker, monkeypatch):
    '''
    Provide a mock implementation of the
    `kano_updater.reporting.send_crash_report()` function
    '''

    import kano_updater.reporting

    send_report = mocker.MagicMock()
    monkeypatch.setattr(
        kano_updater.reporting, 'send_crash_report', send_report
    )

    return send_report
