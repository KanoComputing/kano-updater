#
# network.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for faking internet status
#


import pytest


_internet = False
_server_available = False


@pytest.fixture(scope='function', params=(True, False))
def internet(fs, request, monkeypatch):
    '''
    Fakes the call to `kano.network.is_internet()` to simulate internet being
    available and not being so
    '''

    global _internet

    _internet = request.param

    # TODO: kano-toolset/kano/paths.py throws an exception when it cannot find
    # a project dir. This creates problems when using other fixtures with
    # pyfakefs since the import below will be affected. Create the dir here
    # next to the import from kano-toolset to avoid the exception.
    fs.create_dir('/usr/share/kano/media')

    import kano.network
    monkeypatch.setattr(kano.network, 'is_internet', lambda: _internet)

    return _internet


@pytest.fixture(scope='function', params=(True, False))
def server_available(request, monkeypatch):
    '''
    Fakes the call to `kano_updater.utils.is_server_available()` to simulate
    server connection being established and not being so
    '''

    global _server_available
    _server_available = request.param

    import kano_updater.utils
    monkeypatch.setattr(
        kano_updater.utils, 'is_server_available', lambda: _server_available
    )

    return _server_available
