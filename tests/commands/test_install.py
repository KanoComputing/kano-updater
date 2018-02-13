#
# test_install.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the `kano_updater.commands.install` module.
#


from tests.fixtures.progress import PyTestProgress, AbortError


def test_install(apt, pip, state, system_version, free_space, pip_modules,
                 run_cmd, internet, server_available):
    import kano_updater.commands.install

    space_available, space_required = free_space

    progress = PyTestProgress()

    should_succeed = internet and server_available and \
        (space_available >= space_required)

    try:
        res = kano_updater.commands.install.install(
            progress=progress, gui=False
        )

        assert res == should_succeed
    except AbortError:
        assert not should_succeed
