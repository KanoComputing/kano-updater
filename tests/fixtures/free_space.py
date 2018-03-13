#
# free_space.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for faking free disk space
#


import pytest
from kano_updater.disk_requirements import SPACE_BUFFER, MIN_REQ_SPACE


REQUIRED_SPACE = -10000

SPACES = (
    0,
    1535,  # Limit used to be such that 1.5 GB (1536 MB) needed to be free
    REQUIRED_SPACE,  # Exact space requred
    REQUIRED_SPACE - 1,  # Not quite enough
    MIN_REQ_SPACE,
    999999
)

space_available = 0


@pytest.fixture(scope='function', params=SPACES)
def free_space(apt, request, monkeypatch):
    '''
    Simulate varying levels of disk space usage by mocking the
    `kano.utils.disk.get_free_space()` function which retrieves free disk space
    '''

    global space_available

    space_available = request.param
    space_required = apt.required_test_space + SPACE_BUFFER

    if space_available < 0:
        space_available += space_required - REQUIRED_SPACE

    import kano.utils.disk
    monkeypatch.setattr(
        kano.utils.disk, 'get_free_space', lambda: space_available
    )

    return space_available, space_required
