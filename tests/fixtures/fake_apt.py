#
# fake_apt.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for injecting the stub Python `apt` package which simulates the
# Python apt bindings
#


import os
import pytest


MOCK_IMPORTS_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'mock_imports'
)


@pytest.fixture(scope='function')
def apt(monkeypatch):
    '''
    Injects a stub replacement for the Python `apt` package.

    Returns an instance of `apt.cache.Cache()`
    '''

    monkeypatch.syspath_prepend(MOCK_IMPORTS_DIR)

    import kano_updater.apt_wrapper
    kano_updater.apt_wrapper.AptWrapper._singleton_instance = None

    import apt
    return apt.cache.Cache()
