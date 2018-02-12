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
def internet(request, monkeypatch):
    '''
    Fakes the call to `kano.network.is_internet()` to simulate internet being
    available and not being so
    '''

    global _internet

    _internet = request.param

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
