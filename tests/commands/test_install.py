#
# test_install.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the `kano_updater.commands.install` module.
#


import pytest
from tests.fixtures.progress import PyTestProgress, AbortError
import tests.fixtures.autologin_checks
from kano_updater.os_version import get_target_version


def test_install(apt, state, system_version, free_space,
                 run_cmd, internet, server_available, autologin_checks):
    import kano_updater.commands.install

    space_available, space_required = free_space

    progress = PyTestProgress()

    should_succeed = internet and server_available and \
        (space_available >= space_required)

    relaunch_expected = system_version <= get_target_version()
    rc_warning = (
        'NOTE: Return value from install() is now coupled to whether the '
        'updater requires a relaunch.'
    )

    try:
        res = kano_updater.commands.install.install(
            progress=progress, gui=False
        )

        assert(
            res == should_succeed and
            should_succeed == tests.fixtures.autologin_checks.all_checks(autologin_checks)
        )

        if relaunch_expected and should_succeed:
            pytest.fail(
                "Updater should have relaunched but didn't\n\n" +
                rc_warning
            )
    except AbortError:
        assert not should_succeed
    except AssertionError:
        if relaunch_expected:
            pytest.xfail(rc_warning)
        else:
            raise
