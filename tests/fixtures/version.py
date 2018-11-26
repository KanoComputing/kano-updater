#
# version.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for acertaining the system version
#


import pytest
from kano_updater.os_version import OSVersion


VERSIONS = [
    OSVersion(devstage='Beta', version='1.0.3'),
    OSVersion(devstage='Beta', version='1.1.0'),
    OSVersion(devstage='Beta', version='1.1.1'),
    OSVersion(devstage='Beta', version='1.2.0'),
    OSVersion(devstage='Beta', version='1.2.1'),
    OSVersion(devstage='Beta', version='1.2.2'),
    OSVersion(devstage='Beta', version='1.2.3'),
    OSVersion(devstage='Beta', version='1.2.4'),
    OSVersion(devstage='Beta', version='1.2.5'),
    OSVersion(devstage='Beta', version='1.3.1'),
    OSVersion(devstage='Beta', version='1.3.2'),
    OSVersion(devstage='Beta', version='1.3.3'),
    OSVersion(devstage='Beta', version='1.3.4'),
    OSVersion(devstage='Beta', version='2.0.0'),
    OSVersion(devstage='Beta', version='2.0.1'),
    OSVersion(devstage='Beta', version='2.1.0'),
    OSVersion(devstage='Beta', version='2.2.0'),
    OSVersion(devstage='Beta', version='2.3.0'),
    OSVersion(devstage='Beta', version='2.4.0'),
    OSVersion(devstage='Beta', version='3.0.0'),
    OSVersion(devstage='Beta', version='3.1.0'),
    OSVersion(devstage='Beta', version='3.2.0'),
    OSVersion(devstage='Beta', version='3.3.0'),
    OSVersion(devstage='Beta', version='3.4.0'),
    OSVersion(devstage='Beta', version='3.5.0'),
    OSVersion(devstage='Beta', version='3.6.0'),
    OSVersion(devstage='Beta', version='3.6.1'),
    OSVersion(devstage='Beta', version='3.7.0'),
    OSVersion(devstage='Beta', version='3.8.0'),
    OSVersion(devstage='Beta', version='3.9.0', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.9.1', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.9.2', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.10.0', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.10.1', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.10.2', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.10.3', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.10.4', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.10.5', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.11.0', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.12.0', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.12.1', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.13.0', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.14.0', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.14.1', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.15.0', name='Lovelace'),
    OSVersion(devstage='Beta', version='3.16.0', name='Lovelace'),
    OSVersion(devstage='Beta', version='4.0.0', name='Hopper'),
    OSVersion(devstage='Beta', version='4.1.0', name='Hopper'),
    OSVersion(devstage='Beta', version='4.1.1', name='Hopper'),
]


def get_upgrade_pairs():
    pairs = []

    for idx, start_version in enumerate(VERSIONS):
        for upgrade_version in VERSIONS[idx:]:
            pairs.append((start_version, upgrade_version))

    return pairs


@pytest.fixture(scope='function', params=VERSIONS[-19:])
def system_version(fs, request):
    '''
    Provides the system version files required by the updater to establish
    which version of Kano OS the system is starting at
    '''

    version = request.param
    fs.create_file(
        '/etc/kanux_version',
        contents=version.to_version_string()
    )
    return version


@pytest.fixture(scope='function', params=VERSIONS)
def available_version(request):
    '''
    Supplies values for each of the supported versions
    '''

    return request.param


@pytest.fixture(scope='function', params=get_upgrade_pairs())
def upgrade_version_pairs(request, monkeypatch):
    '''
    Supplies pairs of versions for each of the supported versions and what they
    could upgrade to
    '''

    start_version, upgrade_version = request.param

    import kano_updater.os_version as os_version
    monkeypatch.setattr(
        os_version, '_g_target_version', upgrade_version
    )

    return start_version, upgrade_version
