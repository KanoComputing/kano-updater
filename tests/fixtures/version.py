#
# version.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for acertaining the system version
#


import pytest


@pytest.fixture(scope='function', params=('3.14.1',))
def system_version(fs, request):
    '''
    Provides the system version files required by the updater to establish
    which version of Kano OS the system is starting at
    '''

    version = request.param
    fs.CreateFile(
        '/etc/kanux_version',
        contents='Kanux-Beta-{}-Lovelace'.format(version)
    )
    return version
