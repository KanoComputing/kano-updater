#
# test_apt_wrapper.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the `kano_updater.apt_wrapper.AptWrapper()` class
#


import pytest


def test_apt_wrapper_init(apt):
    from kano_updater.apt_wrapper import AptWrapper
    wrapper = AptWrapper().get_instance()

    assert isinstance(wrapper, AptWrapper)


def test_apt_wrapper_double_init(apt):
    from kano_updater.apt_wrapper import AptWrapper
    dummy_wrapper = AptWrapper.get_instance()

    with pytest.raises(Exception):
        AptWrapper()


def test_upgrade_all(apt):
    from kano_updater.apt_wrapper import AptWrapper
    from kano_updater.progress import CLIProgress

    wrapper = AptWrapper.get_instance()
    progress = CLIProgress()

    for pkg in wrapper._cache:
        if pkg.is_upgradable:
            assert pkg.installed != pkg.candidate
        else:
            assert pkg.installed == pkg.candidate

    wrapper.upgrade_all(progress=progress)

    for pkg in wrapper._cache:
        assert pkg.installed == pkg.candidate


def test_space(apt):
    from kano_updater.apt_wrapper import AptWrapper

    wrapper = AptWrapper.get_instance()
    wrapper._mark_all_for_update()

    install_req = 0
    dl_req = 0

    for pkg in wrapper._cache:
        install_req += pkg.candidate.installed_size / (1024. * 1024.)
        dl_req += pkg.candidate.size / (1024. * 1024.)

    assert wrapper.get_required_upgrade_space() == install_req + dl_req
