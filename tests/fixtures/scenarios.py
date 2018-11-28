#
# scenarios.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for scenarios
#

import pytest


@pytest.fixture
def add_scenario_verifier(monkeypatch, apt):
    '''
    Mocks out the Scenarios::add_scenario() function to verify that the
    supplied versions are valid
    '''

    from tests.fixtures.version import VERSIONS
    version_strings = [v.to_version_string() for v in VERSIONS]

    from kano_updater.scenarios import Scenarios

    def add_scenario_version_tester(dummy_self, from_v, to_v, dummy_func):
        assert from_v in version_strings
        assert to_v in version_strings

    monkeypatch.setattr(Scenarios, 'add_scenario', add_scenario_version_tester)
