#
# free_space.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for faking free disk space
#


import pytest


REQUIRED_SPACE = -10000

SPACES = (
    0,
    1535,  # Limit such that 1.5 GB (1536 MB) needed to be free
    999999
)

space = 0


@pytest.fixture(scope='function', params=SPACES)
def free_space(apt, request, monkeypatch):
    '''
    Simulate varying levels of disk space usage by mocking the
    `kano.utils.disk.get_free_space()` function which retrieves free disk space
    '''

    global space

    space = request.param

    if space < 0:
        space += apt.required_space + apt.required_download - REQUIRED_SPACE

    import kano.utils.disk
    monkeypatch.setattr(
        kano.utils.disk, 'get_free_space', lambda: space
    )

    return space
