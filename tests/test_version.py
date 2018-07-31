#
# version.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the version
#


def test_updater_version_in_tests():
    from tests.fixtures.version import VERSIONS
    from kano_updater.version import VERSION

    assert VERSION in [v.to_version_string() for v in VERSIONS]
