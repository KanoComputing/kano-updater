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


COUNT = 0
EXPECTED_FAILS = 2


def get_raising_function(fail_count, exception):
    '''
    Raises the provided <exception> for the first <fail_count> times
    being run before returning cleanly after this point
    '''

    global COUNT
    global EXPECTED_FAILS

    COUNT = 0
    EXPECTED_FAILS = fail_count

    def fake_cache_update(*args, **kwargs):
        global COUNT
        COUNT += 1

        if COUNT <= EXPECTED_FAILS:
            raise exception

    return fake_cache_update


def run_updating_cache_raising_test(mocker, monkeypatch, fail_count):
    '''
    Tests that the `AptWrapper._update_cache()` function works when
    there are various download errors.

    Helper function for other tests.
    '''

    import kano_updater.monitor_heartbeat
    from kano_updater.retry import RETRIES
    heartbeat = mocker.MagicMock()
    monkeypatch.setattr(kano_updater.retry, 'heartbeat', heartbeat)

    from kano_updater.apt_progress_wrapper import AptDownloadFailException
    cache_update = mocker.MagicMock(
        side_effect=get_raising_function(fail_count, AptDownloadFailException)
    )

    from kano_updater.apt_wrapper import AptWrapper
    from kano_updater.progress import CLIProgress
    progress = CLIProgress()
    wrapper = AptWrapper.get_instance()
    monkeypatch.setattr(wrapper._cache, 'update', cache_update)

    wrapper._update_cache(progress, 5, 5)

    assert cache_update.call_count == min(EXPECTED_FAILS + 1, RETRIES)
    assert heartbeat.call_count == min(EXPECTED_FAILS + 1, RETRIES)


def run_fetch_archives_raising_test(mocker, monkeypatch, fail_count, raise_expected):
    '''
    Tests that the `AptWrapper._fetch_archives()` function works when
    there are various download errors.

    Helper function for other tests.
    '''
    import kano_updater.monitor_heartbeat
    from kano_updater.retry import RETRIES
    heartbeat = mocker.MagicMock()
    monkeypatch.setattr(kano_updater.retry, 'heartbeat', heartbeat)

    from kano_updater.apt_progress_wrapper import AptDownloadFailException
    fetch_archives = mocker.MagicMock(
        side_effect=get_raising_function(fail_count, AptDownloadFailException)
    )

    from kano_updater.apt_wrapper import AptWrapper
    from kano_updater.progress import CLIProgress
    progress = CLIProgress()
    wrapper = AptWrapper.get_instance()
    monkeypatch.setattr(wrapper._cache, 'fetch_archives', fetch_archives)

    if raise_expected:
        with pytest.raises(AptDownloadFailException):
            wrapper._fetch_archives(progress)
    else:
        wrapper._fetch_archives(progress)

    assert fetch_archives.call_count == min(EXPECTED_FAILS + 1, RETRIES)
    assert heartbeat.call_count == min(EXPECTED_FAILS + 1, RETRIES)


def test_updating_cache(apt, mocker, monkeypatch):
    '''
    Tests `AptWrapper._updating_cache()` when download succeeds
    '''
    run_updating_cache_raising_test(mocker, monkeypatch, 0)


def test_updating_cache_no_internet(apt, mocker, monkeypatch):
    '''
    Tests `AptWrapper._updating_cache()` when download fails
    '''
    run_updating_cache_raising_test(mocker, monkeypatch, 5)


def test_updating_cache_flaky_internet(apt, mocker, monkeypatch):
    '''
    Tests `AptWrapper._updating_cache()` when download is flaky
    '''
    run_updating_cache_raising_test(mocker, monkeypatch, 2)


def test_fetch_archives(apt, mocker, monkeypatch):
    '''
    Tests `AptWrapper._fetch_archives()` when download succeeds
    '''
    run_fetch_archives_raising_test(mocker, monkeypatch, 0, False)


def test_fetch_archives_no_internet(apt, mocker, monkeypatch):
    '''
    Tests `AptWrapper._fetch_archives()` when download fails
    '''
    run_fetch_archives_raising_test(mocker, monkeypatch, 5, True)


def test_fetch_archives_flaky_internet(apt, mocker, monkeypatch):
    '''
    Tests `AptWrapper._fetch_archives()` when download is flaky
    '''
    run_fetch_archives_raising_test(mocker, monkeypatch, 2, False)
